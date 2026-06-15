#!/usr/bin/env python3
"""
GEPA Rewriter — Generates improved SKILL.md versions based on judge verdicts.

Part of the GEPA (Generative Evaluation and Prompt Automation) system.
Reads a judge verdict + original SKILL.md and produces an improved version.

Usage (as module):
    from scripts.gepa_rewriter import rewrite_skill, RewriteResult
    result = rewrite_skill("excrtx-foo", path, judge_result, rubric, soul)
"""
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Reuse infrastructure from skill_judge — no duplication
from scripts.skill_judge import (
    parse_skill,
    check_d1_structural,
    REQUIRED_SECTIONS,
    _get_api_key,
    _get_deepseek_key,
    _call_llm_api,
    DEEPSEEK_API_URL,
    OPENROUTER_API_URL,
    JUDGE_MODEL_DEEPSEEK,
    JUDGE_MODEL_OPENROUTER,
    JUDGE_MODEL_OPENROUTER_DS,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
RUBRIC_PATH = REPO_ROOT / ".dogfood" / "schemas" / "skill-judge-rubric.md"

# Rewrite strategies in escalation order
STRATEGIES = ["targeted", "comprehensive", "minimal"]

# Max tokens for rewrite output
REWRITE_MAX_TOKENS = 8000


@dataclass
class RewriteResult:
    """Result of a skill rewrite attempt."""
    success: bool
    new_content: str = ""
    changes_summary: str = ""
    validation_errors: list[str] = field(default_factory=list)
    strategy_used: str = ""
    llm_model: str = ""


def _extract_compiled_rules(raw_text: str) -> str | None:
    """Extract compiled_rules value from raw SKILL.md text for preservation check."""
    parsed = parse_skill_frontmatter_raw(raw_text)
    fm = parsed.get("frontmatter", {})
    return fm.get("compiled_rules")


def parse_skill_frontmatter_raw(raw_text: str) -> dict:
    """Parse frontmatter from raw text without Path dependency."""
    clean = re.sub(r"^\d+\|", "", raw_text, flags=re.MULTILINE)
    if not clean.lstrip().startswith("---"):
        return {"frontmatter": {}, "body": clean}
    match = re.search(r"\n---\s*\n", clean[3:])
    if not match:
        return {"frontmatter": {}, "body": clean}
    fm_text = clean[3:match.start() + 3]
    body = clean[match.end() + 3:]
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}
    return {"frontmatter": fm, "body": body}


def _build_targeted_prompt(
    skill_name: str,
    original_content: str,
    priority_fixes: list[str],
    rubric_excerpt: str,
    soul_context: str,
) -> str:
    """Build a targeted rewrite prompt focusing on specific priority_fixes."""
    fixes_text = "\n".join(f"- {fix}" for fix in priority_fixes)

    return f"""You are an expert skill rewriter for the Exocortex cognitive extension system built on the Hermes Agent runtime.

## Your Task
Rewrite the skill `{skill_name}` to address the specific issues identified by the quality judge. Apply ONLY the fixes listed below — do not change anything else.

## Priority Fixes to Apply
{fixes_text}

## Rubric Reference
{rubric_excerpt[:2000]}

## Behavioral Context
{soul_context[:1500]}

## CRITICAL PRESERVATION RULES
1. **compiled_rules**: If the original has a `compiled_rules` field in the frontmatter, copy it EXACTLY — byte for byte. Do NOT modify, reformat, or reorder it.
2. **PT-BR calibration**: Fields `calibration_prompt`, `test_prompt`, `acceptance_criteria`, `remediation_tip` in frontmatter metadata MUST be preserved exactly as-is (they are in Brazilian Portuguese by design).
3. **Frontmatter name and version**: Keep the original `name` and `version` fields unchanged.
4. **YAML validity**: The frontmatter MUST be valid YAML between `---` delimiters.
5. **Required sections**: The body MUST contain: ## When to Use (or ## Trigger), ## Procedure, ## Pitfalls, ## Verification
6. **H1 title**: The body MUST start with a `# Title` heading.
7. **PT-BR body text**: PT-BR body text is EXPECTED for user-facing skills. Do NOT translate it to English.
8. **English frontmatter description**: The `description` field in frontmatter MUST be in English (for Hermes search).

## Original Skill Content
```markdown
{original_content}
```

## Instructions
Output the COMPLETE rewritten SKILL.md (frontmatter + body). Do NOT output partial content.
Output ONLY the markdown content — no commentary, no code fences wrapping the output.
Start your output with `---` (the frontmatter delimiter)."""


def _build_comprehensive_prompt(
    skill_name: str,
    original_content: str,
    priority_fixes: list[str],
    dimensional_labels: dict,
    rubric_excerpt: str,
    soul_context: str,
) -> str:
    """Build a comprehensive rewrite prompt that rewrites affected sections."""
    fixes_text = "\n".join(f"- {fix}" for fix in priority_fixes)

    weak_dims = []
    for dim_key, dim_data in dimensional_labels.items():
        if dim_key == "D1_structural":
            continue
        label = dim_data.get("label", "")
        if label not in ("COMPLIANT", "CLEAR", "ALIGNED", "PRODUCTION_READY", "EFFICIENT"):
            weak_dims.append(f"- **{dim_key}** ({label}): {dim_data.get('reasoning', '')[:200]}")

    weak_text = "\n".join(weak_dims) if weak_dims else "No weak dimensions identified."

    return f"""You are an expert skill rewriter for the Exocortex cognitive extension system built on the Hermes Agent runtime.

## Your Task
Comprehensively improve the skill `{skill_name}`. Rewrite the sections that are weak according to the judge evaluation. You have more freedom than a targeted fix — improve clarity, add missing content, restructure where needed.

## Weak Dimensions
{weak_text}

## Specific Fixes Required
{fixes_text}

## Rubric Reference
{rubric_excerpt[:2000]}

## Behavioral Context
{soul_context[:1500]}

## CRITICAL PRESERVATION RULES
1. **compiled_rules**: If the original has a `compiled_rules` field in the frontmatter, copy it EXACTLY — byte for byte.
2. **PT-BR calibration**: Fields `calibration_prompt`, `test_prompt`, `acceptance_criteria`, `remediation_tip` in frontmatter metadata MUST be preserved exactly.
3. **Frontmatter name and version**: Keep the original `name` and `version` fields unchanged.
4. **YAML validity**: The frontmatter MUST be valid YAML between `---` delimiters.
5. **Required sections**: The body MUST contain: ## When to Use (or ## Trigger), ## Procedure, ## Pitfalls, ## Verification
6. **H1 title**: The body MUST start with a `# Title` heading.
7. **PT-BR body text**: PT-BR body text is EXPECTED for user-facing skills. Do NOT translate it to English.
8. **English frontmatter description**: The `description` field MUST be in English.

## Original Skill Content
```markdown
{original_content}
```

## Instructions
Output the COMPLETE rewritten SKILL.md (frontmatter + body).
Output ONLY the markdown content — no commentary, no code fences wrapping the output.
Start your output with `---` (the frontmatter delimiter)."""


def _build_minimal_prompt(
    skill_name: str,
    original_content: str,
    priority_fixes: list[str],
) -> str:
    """Build a minimal rewrite prompt for mechanical fixes only."""
    mechanical_fixes = [f for f in priority_fixes if any(kw in f.upper() for kw in [
        "D1", "SECTION", "MISSING", "TRANSLATE", "DUPLICATE", "REMOVE", "ADD",
        "COUNTER-TRIGGER", "DON'T USE FOR",
    ])]
    if not mechanical_fixes:
        mechanical_fixes = priority_fixes[:3]

    fixes_text = "\n".join(f"- {fix}" for fix in mechanical_fixes)

    return f"""You are a precise text editor. Apply ONLY the listed mechanical fixes to this skill file. Make minimal changes.

## Fixes to Apply
{fixes_text}

## RULES
- Preserve ALL existing content not affected by the fixes
- Keep frontmatter YAML valid
- Keep compiled_rules EXACTLY as-is
- Keep all PT-BR text as-is
- Do NOT restructure, rephrase, or improve anything beyond the listed fixes

## Original Content
```markdown
{original_content}
```

## Instructions
Output the COMPLETE file with fixes applied. Start with `---`."""


def build_rewrite_prompt(
    skill_name: str,
    original_content: str,
    judge_result: dict,
    rubric_text: str,
    soul_context: str,
    strategy: str = "targeted",
) -> str:
    """Build a rewrite prompt based on the selected strategy."""
    priority_fixes = judge_result.get("priority_fixes", [])
    dimensions = judge_result.get("dimensions", {})

    if strategy == "targeted":
        return _build_targeted_prompt(
            skill_name, original_content, priority_fixes, rubric_text, soul_context
        )
    elif strategy == "comprehensive":
        return _build_comprehensive_prompt(
            skill_name, original_content, priority_fixes, dimensions, rubric_text, soul_context
        )
    elif strategy == "minimal":
        return _build_minimal_prompt(skill_name, original_content, priority_fixes)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def validate_rewrite(original_content: str, rewritten_content: str) -> list[str]:
    """Validate a rewritten SKILL.md against preservation and structural rules.

    Returns list of validation errors (empty = valid).
    """
    errors = []

    # 1. Strip any wrapping code fences from LLM output
    content = rewritten_content.strip()
    content = re.sub(r'^```(?:markdown|md)?\s*\n', '', content)
    content = re.sub(r'\n```\s*$', '', content)
    content = content.strip()

    # 2. Must start with frontmatter delimiter
    if not content.startswith("---"):
        errors.append("Missing frontmatter delimiter (must start with ---)")
        return errors

    # 3. Parse frontmatter
    match = re.search(r"\n---\s*\n", content[3:])
    if not match:
        errors.append("Missing closing frontmatter delimiter (---)")
        return errors

    fm_text = content[3:match.start() + 3]
    body = content[match.end() + 3:]

    try:
        new_fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML frontmatter: {e}")
        return errors

    # 4. Parse original for comparison
    orig_parsed = parse_skill_frontmatter_raw(original_content)
    orig_fm = orig_parsed.get("frontmatter", {})

    # 5. Name preserved
    if new_fm.get("name") != orig_fm.get("name"):
        errors.append(f"Name changed: '{orig_fm.get('name')}' → '{new_fm.get('name')}'")

    # 6. Version preserved
    if new_fm.get("version") != orig_fm.get("version"):
        errors.append(f"Version changed: '{orig_fm.get('version')}' → '{new_fm.get('version')}'")

    # 7. compiled_rules preserved (bit-for-bit)
    orig_cr = orig_fm.get("compiled_rules")
    new_cr = new_fm.get("compiled_rules")
    if orig_cr is not None:
        if new_cr is None:
            errors.append("compiled_rules was removed")
        elif str(orig_cr) != str(new_cr):
            errors.append("compiled_rules was modified (must be preserved exactly)")

    # 8. Calibration fields preserved
    orig_meta = (orig_fm.get("metadata") or {}).get("hermes") or {}
    new_meta = (new_fm.get("metadata") or {}).get("hermes") or {}
    orig_cal = orig_meta.get("calibration", [])
    new_cal = new_meta.get("calibration", [])
    if orig_cal and not new_cal:
        errors.append("calibration metadata was removed")
    elif orig_cal and new_cal:
        # Check that PT-BR calibration fields are preserved
        for i, orig_entry in enumerate(orig_cal):
            if i >= len(new_cal):
                errors.append(f"calibration entry {i} was removed")
                break
            for field_name in ["calibration_prompt", "test_prompt", "acceptance_criteria", "remediation_tip"]:
                orig_val = orig_entry.get(field_name, "")
                new_val = new_cal[i].get(field_name, "")
                if orig_val and orig_val != new_val:
                    errors.append(f"calibration.{field_name} was modified (must be preserved)")

    # 9. Required sections in body
    body_lower = body.lower()
    for section_key, patterns in REQUIRED_SECTIONS.items():
        found = any(re.search(p, body_lower) for p in patterns)
        if not found:
            errors.append(f"Missing required section: {section_key}")

    # 10. H1 title
    if not re.search(r"^#\s+\S", body, re.MULTILINE):
        errors.append("Missing H1 title heading")

    return errors


def _call_rewrite_llm(prompt: str) -> tuple[str | None, str]:
    """Call the LLM for rewriting. Returns (response, model_used)."""
    # Primary: DeepSeek direct
    deepseek_key = _get_deepseek_key()
    if deepseek_key:
        response = _call_llm_api(prompt, DEEPSEEK_API_URL, deepseek_key, JUDGE_MODEL_DEEPSEEK)
        if response:
            return response, JUDGE_MODEL_DEEPSEEK

    # Fallback 1: OpenRouter (Claude)
    openrouter_key = _get_api_key()
    if openrouter_key:
        response = _call_llm_api(prompt, OPENROUTER_API_URL, openrouter_key, JUDGE_MODEL_OPENROUTER)
        if response:
            return response, JUDGE_MODEL_OPENROUTER

    # Fallback 2: DeepSeek via OpenRouter
    if openrouter_key:
        response = _call_llm_api(prompt, OPENROUTER_API_URL, openrouter_key, JUDGE_MODEL_OPENROUTER_DS)
        if response:
            return response, JUDGE_MODEL_OPENROUTER_DS

    return None, "none"


def _clean_llm_output(raw: str) -> str:
    """Clean LLM output to extract pure SKILL.md content."""
    content = raw.strip()
    # Remove wrapping code fences
    content = re.sub(r'^```(?:markdown|md|yaml)?\s*\n', '', content)
    content = re.sub(r'\n```\s*$', '', content)
    content = content.strip()
    # Ensure starts with ---
    if not content.startswith("---"):
        idx = content.find("---")
        if idx != -1:
            content = content[idx:]
    return content


def rewrite_skill(
    skill_name: str,
    skill_path: Path,
    judge_result: dict,
    rubric_text: str,
    soul_context: str,
    strategy: str = "targeted",
) -> RewriteResult:
    """Rewrite a single skill based on judge verdict.

    Args:
        skill_name: Skill directory name (e.g., 'excrtx-behavior-vetor')
        skill_path: Path to SKILL.md
        judge_result: Full judge output dict for this skill
        rubric_text: Contents of skill-judge-rubric.md
        soul_context: Contents of SOUL_SEED.md (truncated)
        strategy: One of 'targeted', 'comprehensive', 'minimal'

    Returns:
        RewriteResult with success status and new content
    """
    original_content = skill_path.read_text(encoding="utf-8")

    # Build prompt
    prompt = build_rewrite_prompt(
        skill_name, original_content, judge_result, rubric_text, soul_context, strategy
    )

    # Call LLM
    print(f"    🔄 Rewriting {skill_name} (strategy: {strategy})...", file=sys.stderr)
    response, model_used = _call_rewrite_llm(prompt)

    if not response:
        return RewriteResult(
            success=False,
            validation_errors=["All LLM providers failed"],
            strategy_used=strategy,
            llm_model="none",
        )

    # Clean output
    new_content = _clean_llm_output(response)

    # Validate
    validation_errors = validate_rewrite(original_content, new_content)
    if validation_errors:
        return RewriteResult(
            success=False,
            new_content=new_content,
            validation_errors=validation_errors,
            strategy_used=strategy,
            llm_model=model_used,
        )

    # Generate changes summary
    orig_lines = original_content.splitlines()
    new_lines = new_content.splitlines()
    summary = f"Rewrote {skill_name}: {len(orig_lines)} → {len(new_lines)} lines (strategy: {strategy}, model: {model_used})"

    return RewriteResult(
        success=True,
        new_content=new_content,
        changes_summary=summary,
        strategy_used=strategy,
        llm_model=model_used,
    )
