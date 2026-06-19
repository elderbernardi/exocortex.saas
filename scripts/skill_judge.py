#!/usr/bin/env python3
"""
Exocortex Skill Judge — LLM-as-Judge evaluation for SKILL.md files.

Usage:
    python scripts/skill_judge.py --all                          # sweep all skills
    python scripts/skill_judge.py --skill excrtx-behavior-vetor  # single skill
    python scripts/skill_judge.py --p0                           # P0 behavioral skills only
    python scripts/skill_judge.py --all --compare-baseline FILE  # compare against baseline
    python scripts/skill_judge.py --all --output FILE            # save results to file
"""
import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
RUBRIC_PATH = REPO_ROOT / ".dogfood" / "schemas" / "skill-judge-rubric.md"
SOUL_SEED_PATH = REPO_ROOT / "SOUL_SEED.md"
FEATURES_PATH = REPO_ROOT / "FEATURES.md"
DEFAULT_BASELINE_PATH = REPO_ROOT / ".dogfood" / "baselines" / "skill-judge-baseline.json"
PRODUCTION_SKILLS_REQUIRING_GATE = {
    "excrtx-produce-artifacts",
    "excrtx-produce-slides",
    "excrtx-produce-oficios",
}

# P0 behavioral skills + their related skills for context
P0_SKILLS = [
    "excrtx-behavior-vetor",
    "excrtx-behavior-canvas",
    "excrtx-govern-draftfirst",
    "excrtx-behavior-accuracy",
]
P0_RELATED = [
    "excrtx-behavior-briefing",
    "excrtx-govern-tools",
    "excrtx-quality-antislop",
    "excrtx-quality-gate",
]

# Hermes canonical required sections (case-insensitive matching)
REQUIRED_SECTIONS = {
    "trigger_or_when": [r"##\s+when\s+to\s+use", r"##\s+trigger"],
    "procedure": [r"##\s+procedure"],
    "pitfalls": [r"##\s+pitfalls", r"##\s+common\s+pitfalls"],
    "verification": [r"##\s+verifica", r"##\s+verification\s+checklist"],
}

LABEL_RANK = {
    "best": 0,
    "middle": 1,
    "worst": 2,
}

D1_LABELS = ["COMPLIANT", "PARTIAL", "NON_COMPLIANT"]
D2_LABELS = ["CLEAR", "AMBIGUOUS", "VAGUE"]
D3_LABELS = ["ALIGNED", "PARTIAL", "MISALIGNED"]
D4_LABELS = ["PRODUCTION_READY", "NEEDS_HARDENING", "PROTOTYPE"]
D5_LABELS = ["EFFICIENT", "ACCEPTABLE", "BLOATED"]

VERDICTS = ["PASS", "IMPROVE", "REWRITE"]

# LLM judge model preferences
# Primary: OpenCode Zen gateway (OPENCODE_API_KEY) — broad model access via one key
# Fallbacks: DeepSeek V4 Pro direct, OpenRouter
JUDGE_MODEL_DEEPSEEK = "deepseek-v4-pro"
JUDGE_MODEL_OPENROUTER = "anthropic/claude-sonnet-4"
JUDGE_MODEL_OPENROUTER_DS = "deepseek/deepseek-chat"

# OpenCode Zen gateway (https://opencode.ai/zen). Authenticated with OPENCODE_API_KEY.
# Model is configurable via OPENCODE_MODEL or --model. The requested `minimax-m3`
# is only published as `minimax-m3-free`, whose free promotion has ended (paid
# variants require account credits); `nemotron-3-ultra-free` is the default that
# remains available on a free key. See `python3 scripts/skill_judge.py --list-models`.
OPENCODE_API_URL = "https://opencode.ai/zen/v1/chat/completions"
OPENCODE_MODELS_URL = "https://opencode.ai/zen/v1/models"
OPENCODE_MODEL = os.environ.get("OPENCODE_MODEL", "nemotron-3-ultra-free")

# API endpoints
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


# ─────────────────────────────────────────────────────────────────────
# Frontmatter Parsing
# ─────────────────────────────────────────────────────────────────────

def parse_skill(path: Path) -> dict:
    """Parse a SKILL.md into frontmatter dict + body string."""
    raw = path.read_text(encoding="utf-8")

    # Strip line-numbering artifacts for parsing (but flag them)
    has_line_numbers = bool(re.search(r"^\d+\|", raw, re.MULTILINE))

    # Parse frontmatter — handle line-numbered frontmatter
    clean = re.sub(r"^\d+\|", "", raw, flags=re.MULTILINE)

    if not clean.lstrip().startswith("---"):
        return {"frontmatter": {}, "body": clean, "raw": raw, "has_line_numbers": has_line_numbers, "path": str(path)}

    # Find closing ---
    match = re.search(r"\n---\s*\n", clean[3:])
    if not match:
        return {"frontmatter": {}, "body": clean, "raw": raw, "has_line_numbers": has_line_numbers, "path": str(path)}

    fm_text = clean[3:match.start() + 3]
    body = clean[match.end() + 3:]

    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}

    return {
        "frontmatter": fm,
        "body": body,
        "raw": raw,
        "has_line_numbers": has_line_numbers,
        "path": str(path),
        "size_bytes": len(raw.encode("utf-8")),
        "body_size_bytes": len(body.encode("utf-8")),
    }


# ─────────────────────────────────────────────────────────────────────
# D1: Structural Compliance (deterministic)
# ─────────────────────────────────────────────────────────────────────

def check_d1_structural(parsed: dict) -> dict:
    """Deterministic structural compliance check."""
    fm = parsed["frontmatter"]
    body = parsed["body"]
    issues = []
    recommendations = []

    # Frontmatter fields
    if not fm.get("name"):
        issues.append("Missing 'name' in frontmatter")
    elif not re.match(r"^[a-z0-9-]+$", fm["name"]):
        issues.append(f"Name '{fm['name']}' is not kebab-case")

    desc = fm.get("description", "")
    if not desc:
        issues.append("Missing 'description' in frontmatter")
    elif isinstance(desc, str):
        if len(desc) > 1024:
            issues.append(f"Description too long ({len(desc)} chars, max 1024)")
        # Check if description is in Portuguese (heuristic: common PT words)
        pt_signals = ["quando", "para", "como", "ação", "criar", "configurar", "gerenciar", "registrar"]
        desc_lower = desc.lower()
        pt_count = sum(1 for w in pt_signals if w in desc_lower)
        if pt_count >= 3:
            issues.append("Description appears to be in PT-BR (should be English for Hermes search)")
            recommendations.append("Translate frontmatter description to English")

    if not fm.get("version"):
        issues.append("Missing 'version' in frontmatter")

    # Tags
    hermes_meta = (fm.get("metadata") or {}).get("hermes") or {}
    if not hermes_meta.get("tags"):
        issues.append("Missing metadata.hermes.tags")
        recommendations.append("Add meaningful tags for skill discovery")

    # Category
    if not fm.get("category") and not hermes_meta.get("category"):
        issues.append("Missing 'category' field")
        recommendations.append("Add 'category: excrtx' to frontmatter")

    # Runtime gate metadata
    gate = fm.get("gate")
    skill_name = fm.get("name")
    if skill_name in PRODUCTION_SKILLS_REQUIRING_GATE and not gate:
        issues.append("Missing 'gate' block for production skill")
        recommendations.append("Add gate.require_quality_gate and gate.max_context_tokens to frontmatter")
    elif gate is not None:
        if not isinstance(gate, dict):
            issues.append("'gate' frontmatter must be a mapping")
            recommendations.append("Use YAML mapping syntax for gate metadata")
        else:
            if "require_quality_gate" not in gate:
                issues.append("Missing gate.require_quality_gate")
            elif not isinstance(gate.get("require_quality_gate"), bool):
                issues.append("gate.require_quality_gate must be boolean")

            if "max_context_tokens" not in gate:
                issues.append("Missing gate.max_context_tokens")
            else:
                max_context_tokens = gate.get("max_context_tokens")
                if not isinstance(max_context_tokens, int) or max_context_tokens <= 0:
                    issues.append("gate.max_context_tokens must be a positive integer")

    # Line-numbering artifacts
    if parsed["has_line_numbers"]:
        issues.append("Line-numbering artifacts detected (^\\d+|)")
        recommendations.append("Strip line-numbering prefixes from markdown body")

    # Required sections
    body_lower = body.lower()
    sections_found = {}
    for section_key, patterns in REQUIRED_SECTIONS.items():
        found = any(re.search(p, body_lower) for p in patterns)
        sections_found[section_key] = found
        if not found:
            issues.append(f"Missing section: {section_key}")

    # H1 title
    if not re.search(r"^#\s+\S", body, re.MULTILINE):
        issues.append("Missing H1 title heading")

    # Size check
    if parsed["size_bytes"] > 100_000:
        issues.append(f"File too large ({parsed['size_bytes']} bytes, max 100KB)")
    if parsed["body_size_bytes"] > 20_000:
        recommendations.append(f"Body is {parsed['body_size_bytes']} bytes — consider extracting to references/")

    # Platforms
    if not fm.get("platforms"):
        recommendations.append("Add 'platforms: [linux]' to frontmatter")

    # Related skills
    if not hermes_meta.get("related_skills"):
        recommendations.append("Consider adding 'related_skills' to metadata.hermes")

    # Determine label
    critical_missing = sum(1 for s, found in sections_found.items() if not found)
    has_name = bool(fm.get("name"))
    has_desc = bool(fm.get("description"))
    has_version = bool(fm.get("version"))
    fm_missing = sum(1 for x in [has_name, has_desc, has_version] if not x)

    total_issues = len(issues)
    if total_issues == 0:
        label = "COMPLIANT"
    elif total_issues <= 2 and critical_missing <= 1 and fm_missing == 0:
        label = "PARTIAL"
    else:
        label = "NON_COMPLIANT"

    reasoning = f"Found {total_issues} issues. Sections present: {sections_found}. " \
                f"Frontmatter fields: name={has_name}, desc={has_desc}, version={has_version}. " \
                f"Line numbers: {parsed['has_line_numbers']}. Size: {parsed['size_bytes']}B."

    return {
        "label": label,
        "reasoning": reasoning,
        "issues": issues,
        "recommendations": recommendations,
        "sections_found": sections_found,
    }


# ─────────────────────────────────────────────────────────────────────
# D2-D5: LLM Judge (requires external call or inline evaluation)
# ─────────────────────────────────────────────────────────────────────

def build_judge_prompt(parsed: dict, rubric_text: str, soul_context: str, related_skills: list[str] | None = None) -> str:
    """Build the LLM judge prompt for D2-D5 evaluation."""
    fm = parsed["frontmatter"]
    body = parsed["body"]
    skill_name = fm.get("name", "unknown")

    related_context = ""
    if related_skills:
        related_context = f"\n\n## Related Skills for Context\nThis skill has dependency relationships with: {', '.join(related_skills)}"

    prompt = f"""You are an expert evaluator of Hermes Agent skills for the Exocortex cognitive extension system.

## Your Task
Evaluate the skill `{skill_name}` across 4 dimensions (D2-D5). D1 structural compliance has already been checked deterministically.

## Important Context
- Exocortex is a PT-BR user-oriented system. PT-BR body text is EXPECTED for user-facing skills.
- PT-BR examples in signal tables and trigger phrases are CORRECT behavior for Brazilian Portuguese user interaction.
- The `compiled_rules` field is a valid custom Exocortex extension, not a format violation.
- The executive (user) communicates in Brazilian Portuguese.

## Behavioral Contract (from SOUL_SEED.md)
{soul_context[:3000]}

## Evaluation Rubric
{rubric_text}

## Skill Content
### Frontmatter
```yaml
{yaml.dump(fm, allow_unicode=True, default_flow_style=False)}
```

### Body
{body[:15000]}
{related_context}

## Instructions
For each dimension (D2 through D5), you MUST:
1. State your reasoning (chain-of-thought) — explain WHY before scoring
2. Assign a categorical label from the rubric
3. List specific issues found
4. Provide actionable recommendations

## Output Format
Respond with ONLY valid JSON (no markdown fencing):
{{
  "D2_clarity": {{
    "label": "CLEAR|AMBIGUOUS|VAGUE",
    "reasoning": "Your chain-of-thought analysis",
    "issues": ["issue1", "issue2"],
    "recommendations": ["fix1", "fix2"]
  }},
  "D3_alignment": {{
    "label": "ALIGNED|PARTIAL|MISALIGNED",
    "reasoning": "...",
    "issues": [],
    "recommendations": []
  }},
  "D4_fitness": {{
    "label": "PRODUCTION_READY|NEEDS_HARDENING|PROTOTYPE",
    "reasoning": "...",
    "issues": [],
    "recommendations": []
  }},
  "D5_economy": {{
    "label": "EFFICIENT|ACCEPTABLE|BLOATED",
    "reasoning": "...",
    "issues": [],
    "recommendations": []
  }}
}}"""
    return prompt


def compute_overall_verdict(d1: dict, llm_dims: dict) -> str:
    """Compute overall verdict from dimensional labels."""
    all_labels = {
        "D1": d1["label"],
        "D2": llm_dims.get("D2_clarity", {}).get("label", "VAGUE"),
        "D3": llm_dims.get("D3_alignment", {}).get("label", "MISALIGNED"),
        "D4": llm_dims.get("D4_fitness", {}).get("label", "PROTOTYPE"),
        "D5": llm_dims.get("D5_economy", {}).get("label", "BLOATED"),
    }

    label_sets = {
        "D1": D1_LABELS,
        "D2": D2_LABELS,
        "D3": D3_LABELS,
        "D4": D4_LABELS,
        "D5": D5_LABELS,
    }

    worst_count = 0
    middle_count = 0
    for dim, label in all_labels.items():
        labels = label_sets[dim]
        if label == labels[0]:
            pass  # best
        elif label == labels[1]:
            middle_count += 1
        else:
            worst_count += 1

    if worst_count > 0 or middle_count >= 3:
        return "REWRITE"
    elif middle_count > 0:
        return "IMPROVE"
    else:
        return "PASS"


def collect_priority_fixes(d1: dict, llm_dims: dict) -> list[str]:
    """Collect highest-priority fixes across all dimensions."""
    fixes = []
    for issue in d1.get("issues", []):
        if "line-numbering" in issue.lower():
            fixes.append(f"[D1-MECHANICAL] {issue}")
        elif "missing" in issue.lower() and "section" in issue.lower():
            fixes.append(f"[D1-SECTION] {issue}")
        elif "description" in issue.lower() and "pt-br" in issue.lower():
            fixes.append(f"[D1-TRANSLATE] {issue}")

    for dim_key in ["D2_clarity", "D3_alignment", "D4_fitness", "D5_economy"]:
        dim = llm_dims.get(dim_key, {})
        for rec in dim.get("recommendations", []):
            fixes.append(f"[{dim_key.upper()}] {rec}")

    return fixes


# ─────────────────────────────────────────────────────────────────────
# Sweep + Reporting
# ─────────────────────────────────────────────────────────────────────

def discover_skills(skills_dir: Path, filter_names: list[str] | None = None) -> list[Path]:
    """Discover all excrtx skill directories."""
    skills = sorted(skills_dir.glob("excrtx-*/SKILL.md"))
    if filter_names:
        skills = [s for s in skills if s.parent.name in filter_names]
    return skills


def generate_report(results: list[dict]) -> str:
    """Generate human-readable report from judge results."""
    lines = ["# Skill Judge — Baseline Report\n"]
    lines.append(f"**Skills evaluated:** {len(results)}\n")

    # Summary table
    lines.append("## Summary\n")
    lines.append("| Skill | D1 | D2 | D3 | D4 | D5 | Verdict |")
    lines.append("|---|---|---|---|---|---|---|")

    verdict_counts = {"PASS": 0, "IMPROVE": 0, "REWRITE": 0}
    for r in sorted(results, key=lambda x: VERDICTS.index(x["overall_verdict"]), reverse=True):
        d = r["dimensions"]
        name = r["skill_name"]
        v = r["overall_verdict"]
        verdict_counts[v] = verdict_counts.get(v, 0) + 1
        emoji = {"PASS": "✅", "IMPROVE": "⚠️", "REWRITE": "🔴"}.get(v, "❓")
        lines.append(
            f"| `{name}` | {d['D1_structural']['label']} | "
            f"{d.get('D2_clarity', {}).get('label', '—')} | "
            f"{d.get('D3_alignment', {}).get('label', '—')} | "
            f"{d.get('D4_fitness', {}).get('label', '—')} | "
            f"{d.get('D5_economy', {}).get('label', '—')} | "
            f"{emoji} {v} |"
        )

    lines.append(f"\n**Totals:** PASS={verdict_counts['PASS']}, IMPROVE={verdict_counts['IMPROVE']}, REWRITE={verdict_counts['REWRITE']}\n")

    # Per-skill details
    lines.append("## Per-Skill Details\n")
    for r in sorted(results, key=lambda x: VERDICTS.index(x["overall_verdict"]), reverse=True):
        name = r["skill_name"]
        v = r["overall_verdict"]
        lines.append(f"### {name} — {v}\n")

        if r["priority_fixes"]:
            lines.append("**Priority fixes:**")
            for fix in r["priority_fixes"]:
                lines.append(f"- {fix}")
            lines.append("")

        # D1 details
        d1 = r["dimensions"]["D1_structural"]
        if d1["issues"]:
            lines.append(f"**D1 Structural ({d1['label']}):** {', '.join(d1['issues'])}")

        # LLM dimension details
        for dim_key in ["D2_clarity", "D3_alignment", "D4_fitness", "D5_economy"]:
            dim = r["dimensions"].get(dim_key)
            if dim and dim.get("issues"):
                lines.append(f"**{dim_key} ({dim['label']}):** {dim['reasoning'][:200]}")

        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# LLM API Integration
# ─────────────────────────────────────────────────────────────────────

def _get_api_key() -> str | None:
    """Retrieve OpenRouter API key from env or .secrets file."""
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    # Try .secrets files
    for secrets_path in [
        REPO_ROOT / ".secrets",
        Path.home() / ".secrets",
    ]:
        if secrets_path.is_file():
            try:
                for line in secrets_path.read_text(encoding="utf-8").splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'").strip('"')
                        if k in ("OPENROUTER_API_KEY", "OPENAI_API_KEY") and v:
                            return v
            except Exception:
                pass
    return None


def _get_deepseek_key() -> str | None:
    """Retrieve DeepSeek API key from env or .secrets file."""
    key = os.environ.get("DEEPSEEK_API_KEY")
    if key:
        return key

    for secrets_path in [
        REPO_ROOT / ".secrets",
        Path.home() / ".secrets",
    ]:
        if secrets_path.is_file():
            try:
                for line in secrets_path.read_text(encoding="utf-8").splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'").strip('"')
                        if k == "DEEPSEEK_API_KEY" and v:
                            return v
            except Exception:
                pass
    return None


def _get_opencode_key() -> str | None:
    """Retrieve the OpenCode Zen gateway API key from env or .secrets file."""
    key = os.environ.get("OPENCODE_API_KEY")
    if key and key != "***":
        return key

    for secrets_path in [
        REPO_ROOT / ".secrets",
        Path.home() / ".secrets",
    ]:
        if secrets_path.is_file():
            try:
                for line in secrets_path.read_text(encoding="utf-8").splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'").strip('"')
                        if k == "OPENCODE_API_KEY" and v and v != "***":
                            return v
            except Exception:
                pass
    return None


def _get_opencode_go_key() -> str | None:
    """Retrieve OpenCode Go API key from the Hermes gateway process environment."""
    # Try env first
    key = os.environ.get("OPENCODE_GO_API_KEY")
    if key and key != "***":
        return key

    # Read from Hermes gateway process environment
    import glob
    for proc_path in glob.glob("/proc/*/cmdline"):
        try:
            with open(proc_path, "rb") as f:
                cmdline = f.read().decode("utf-8", errors="replace")
            if "hermes" in cmdline.lower() and "gateway" in cmdline.lower():
                pid = proc_path.split("/")[2]
                env_path = f"/proc/{pid}/environ"
                with open(env_path, "rb") as f:
                    env_data = f.read().decode("utf-8", errors="replace")
                for var in env_data.split("\0"):
                    if var.startswith("OPENCODE_GO_API_KEY="):
                        val = var.split("=", 1)[1]
                        if val and val != "***":
                            return val
        except (PermissionError, FileNotFoundError, IndexError):
            continue
    return None


# OpenCode Go API endpoint (alternative to DeepSeek)
OPENCODE_GO_API_URL = "https://opencode.ai/zen/go/v1/chat/completions"
OPENCODE_GO_MODEL = "glm-5.2"


def _call_llm_api(prompt: str, api_url: str, api_key: str, model: str, max_tokens: int = 4000, timeout: int = 90) -> str | None:
    """Make a single LLM API call. Returns response text or None on failure."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "python-httpx/0.27.0",
    }
    system_prompt = (
        "You are an expert skill quality judge for the Exocortex cognitive system. "
        "You evaluate skills across 4 dimensions (D2-D5) using STRICT categorical labels.\n\n"
        "GRADING RULES (apply consistently):\n"
        "- D2 CLEAR: Agent can execute the full procedure autonomously from this text alone\n"
        "- D2 AMBIGUOUS: Agent could execute but would guess on 1-2 steps\n"
        "- D2 VAGUE: Agent would frequently guess or produce incorrect behavior\n"
        "- D3 ALIGNED: Fully respects behavioral contract\n"
        "- D3 PARTIAL: Generally aligned but missing 1-2 governance references\n"
        "- D3 MISALIGNED: Contradicts or ignores key behavioral rules\n"
        "- D4 PRODUCTION_READY: Verification is testable, pitfalls are real, references exist\n"
        "- D4 NEEDS_HARDENING: Has verification but weak, or missing real pitfalls\n"
        "- D4 PROTOTYPE: No testable verification, no pitfalls, or references missing\n"
        "- D5 EFFICIENT: Tight, well-organized, no waste\n"
        "- D5 ACCEPTABLE: Some redundancy but within reasonable bounds\n"
        "- D5 BLOATED: Significant redundancy, debris, or unnecessary duplication\n\n"
        "IMPORTANT: PT-BR body text is EXPECTED for user-facing skills. Do NOT penalize it.\n"
        "IMPORTANT: compiled_rules is a valid custom extension. Do NOT treat it as a violation.\n\n"
        "Respond ONLY with valid JSON. No markdown fences, no commentary."
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }

    # DeepSeek: enforce JSON output for clean parsing
    is_deepseek = "deepseek.com" in api_url or "deepseek" in model.lower()
    if is_deepseek:
        payload["response_format"] = {"type": "json_object"}

    data = json.dumps(payload).encode("utf-8")

    try:
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            choice = body.get("choices", [{}])[0]
            message = choice.get("message", {})
            # DeepSeek V4 may return reasoning in reasoning_content; we want content
            content = message.get("content", "")
            return content
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception) as e:
        print(f"    ⚠️ LLM API error ({model}): {e}", file=sys.stderr)
        return None


def _parse_llm_response(response_text: str) -> dict:
    """Parse LLM JSON response into D2-D5 dimensional labels."""
    # Strip markdown code fences if present
    clean = response_text.strip()
    # Handle ```json ... ``` wrapping
    clean = re.sub(r'^```(?:json)?\s*', '', clean)
    clean = re.sub(r'\s*```\s*$', '', clean)
    # Strip any leading/trailing non-JSON text (e.g., reasoning prefix)
    clean = clean.strip()

    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        # Try to extract the outermost JSON object containing D2_clarity
        # Use brace matching for nested objects
        start = clean.find('{')
        if start == -1:
            return {}
        depth = 0
        end = start
        for i in range(start, len(clean)):
            if clean[i] == '{':
                depth += 1
            elif clean[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        candidate = clean[start:end]
        if '"D2_clarity"' in candidate:
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                return {}
        else:
            return {}

    # Extract dimensional results
    dims = {}
    for dim_key in ["D2_clarity", "D3_alignment", "D4_fitness", "D5_economy"]:
        dim_data = parsed.get(dim_key) or parsed.get("dimensions", {}).get(dim_key)
        if dim_data and isinstance(dim_data, dict):
            label = dim_data.get("label", "")
            # Validate label is one of the expected values
            valid_labels = {
                "D2_clarity": D2_LABELS,
                "D3_alignment": D3_LABELS,
                "D4_fitness": D4_LABELS,
                "D5_economy": D5_LABELS,
            }
            if label in valid_labels.get(dim_key, []):
                dims[dim_key] = {
                    "label": label,
                    "reasoning": dim_data.get("reasoning", ""),
                    "issues": dim_data.get("issues", []),
                    "recommendations": dim_data.get("recommendations", []),
                }
    return dims


def call_llm_judge(prompt: str) -> dict:
    """Call the LLM judge API.

    Provider order:
      1. OpenCode Zen gateway (OPENCODE_API_KEY) — configured primary, model OPENCODE_MODEL
      2. DeepSeek direct API (DEEPSEEK_API_KEY)
      3. OpenCode Go gateway (glm)

    Returns D2-D5 dimensional labels dict, or empty dict on total failure.
    """
    # Primary: OpenCode Zen gateway. Reasoning models (e.g. nemotron) need extra
    # output budget so the JSON verdict survives after the reasoning trace.
    opencode_key = _get_opencode_key()
    if opencode_key:
        response = _call_llm_api(prompt, OPENCODE_API_URL, opencode_key, OPENCODE_MODEL, max_tokens=8000, timeout=300)
        if response:
            dims = _parse_llm_response(response)
            if dims:
                return dims

    # Fallback: DeepSeek direct API (fast, cheap)
    deepseek_key = _get_deepseek_key()
    if deepseek_key:
        response = _call_llm_api(prompt, DEEPSEEK_API_URL, deepseek_key, JUDGE_MODEL_DEEPSEEK)
        if response:
            dims = _parse_llm_response(response)
            if dims:
                return dims

    # Fallback: OpenCode Go (glm-5.2)
    opencode_go_key = _get_opencode_go_key()
    if opencode_go_key:
        response = _call_llm_api(prompt, OPENCODE_GO_API_URL, opencode_go_key, OPENCODE_GO_MODEL)
        if response:
            dims = _parse_llm_response(response)
            if dims:
                return dims

    return {}


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Exocortex Skill Judge")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--all", action="store_true", help="Evaluate all skills")
    group.add_argument("--p0", action="store_true", help="Evaluate P0 behavioral skills + related")
    group.add_argument("--skill", type=str, help="Evaluate a single skill by name")
    parser.add_argument("--output", type=str, help="Save JSON results to file")
    parser.add_argument(
        "--save-baseline",
        nargs="?",
        const=str(DEFAULT_BASELINE_PATH),
        help="Save current results as a baseline JSON (optional path, default: .dogfood/baselines/skill-judge-baseline.json)",
    )
    parser.add_argument("--report", type=str, help="Save human-readable report to file")
    parser.add_argument("--compare-baseline", type=str, help="Compare against baseline JSON")
    parser.add_argument("--d1-only", action="store_true", help="Only run deterministic D1 checks (no LLM)")
    parser.add_argument("--model", type=str, default=None, help="Override the OpenCode Zen judge model (e.g., nemotron-3-ultra-free)")
    parser.add_argument("--list-models", action="store_true", help="List OpenCode Zen models available to OPENCODE_API_KEY and exit")
    args = parser.parse_args()

    if args.list_models:
        key = _get_opencode_key()
        if not key:
            print("OPENCODE_API_KEY not set.", file=sys.stderr)
            sys.exit(1)
        try:
            req = urllib.request.Request(
                OPENCODE_MODELS_URL,
                headers={"Authorization": f"Bearer {key}", "User-Agent": "python-httpx/0.27.0"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                models = json.loads(resp.read().decode("utf-8")).get("data", [])
            for m in models:
                print(m.get("id"))
        except Exception as e:
            print(f"Failed to list models: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    if not (args.all or args.p0 or args.skill):
        parser.error("one of the arguments --all --p0 --skill is required")

    # CLI --model overrides the OpenCode Zen judge model (the configured primary)
    if args.model:
        global OPENCODE_MODEL
        OPENCODE_MODEL = args.model

    # Determine which skills to evaluate
    if args.all:
        skill_paths = discover_skills(SKILLS_DIR)
    elif args.p0:
        skill_paths = discover_skills(SKILLS_DIR, P0_SKILLS + P0_RELATED)
    else:
        skill_paths = discover_skills(SKILLS_DIR, [args.skill])

    if not skill_paths:
        print("No skills found.", file=sys.stderr)
        sys.exit(1)

    print(f"Evaluating {len(skill_paths)} skills...", file=sys.stderr)

    # Load context
    soul_context = ""
    if SOUL_SEED_PATH.exists():
        soul_context = SOUL_SEED_PATH.read_text(encoding="utf-8")[:3000]

    rubric_text = ""
    if RUBRIC_PATH.exists():
        rubric_text = RUBRIC_PATH.read_text(encoding="utf-8")

    results = []
    for skill_path in skill_paths:
        skill_name = skill_path.parent.name
        print(f"  Judging: {skill_name}...", file=sys.stderr)

        parsed = parse_skill(skill_path)
        d1 = check_d1_structural(parsed)

        if args.d1_only:
            # D1-only mode: no LLM needed
            llm_dims = {}
            verdict = "PASS" if d1["label"] == "COMPLIANT" else ("IMPROVE" if d1["label"] == "PARTIAL" else "REWRITE")
        else:
            # Build prompt and call LLM judge
            prompt = build_judge_prompt(parsed, rubric_text, soul_context)
            llm_dims = call_llm_judge(prompt)
            if not llm_dims:
                print(f"    ⚠️ No LLM response for {skill_name}, using D1-only verdict", file=sys.stderr)
                verdict = "PASS" if d1["label"] == "COMPLIANT" else ("IMPROVE" if d1["label"] == "PARTIAL" else "REWRITE")
            else:
                verdict = compute_overall_verdict(d1, llm_dims)

        result = {
            "skill_name": skill_name,
            "skill_path": str(skill_path),
            "dimensions": {
                "D1_structural": d1,
                **{k: v for k, v in llm_dims.items()},
            },
            "overall_verdict": verdict,
            "priority_fixes": collect_priority_fixes(d1, llm_dims),
            "judge_prompt": build_judge_prompt(parsed, rubric_text, soul_context) if not args.d1_only else None,
        }
        results.append(result)

    # Output
    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Results saved to {args.output}", file=sys.stderr)

    if args.save_baseline:
        baseline_path = Path(args.save_baseline)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Baseline saved to {baseline_path}", file=sys.stderr)

    if args.report:
        report = generate_report(results)
        Path(args.report).write_text(report, encoding="utf-8")
        print(f"Report saved to {args.report}", file=sys.stderr)

    # Compare against baseline
    if args.compare_baseline:
        baseline_path = Path(args.compare_baseline)
        if baseline_path.exists():
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            baseline_map = {r["skill_name"]: r for r in baseline}
            regressions = []
            improvements = []
            for r in results:
                b = baseline_map.get(r["skill_name"])
                if not b:
                    continue
                b_idx = VERDICTS.index(b["overall_verdict"])
                r_idx = VERDICTS.index(r["overall_verdict"])
                if r_idx > b_idx:
                    regressions.append(f"{r['skill_name']}: {b['overall_verdict']} → {r['overall_verdict']}")
                elif r_idx < b_idx:
                    improvements.append(f"{r['skill_name']}: {b['overall_verdict']} → {r['overall_verdict']}")

            if regressions:
                print(f"\n❌ REGRESSIONS ({len(regressions)}):", file=sys.stderr)
                for reg in regressions:
                    print(f"  - {reg}", file=sys.stderr)
                sys.exit(1)
            elif improvements:
                print(f"\n✅ IMPROVEMENTS ({len(improvements)}):", file=sys.stderr)
                for imp in improvements:
                    print(f"  - {imp}", file=sys.stderr)
            else:
                print("\n✅ No regressions. Verdicts unchanged.", file=sys.stderr)
        else:
            print(f"Baseline file not found: {args.compare_baseline}", file=sys.stderr)

    # Print summary
    for r in results:
        emoji = {"PASS": "✅", "IMPROVE": "⚠️", "REWRITE": "🔴"}.get(r["overall_verdict"], "❓")
        d1_label = r["dimensions"]["D1_structural"]["label"]
        print(f"  {emoji} {r['skill_name']}: D1={d1_label} → {r['overall_verdict']}")

    return results


if __name__ == "__main__":
    main()
