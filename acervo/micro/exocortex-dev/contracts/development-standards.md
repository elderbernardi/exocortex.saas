---
schema: acervo/v0.2
type: contract
title: Exocortex.IA Development & Quality Standards
description: This document establishes the official coding conventions, skill design specifications, and automated verification ru...
tags: [dev, exocortex, standards, skill, qa]
timestamp: 2026-06-11
class: perene
status: active
created_at: 2026-06-11T00:00:00Z
last_accessed_at: 2026-06-11T00:00:00Z
updated: 2026-06-11
excrtx_type: rule
nature: contracts
confidence: high
created: 2026-06-11
---

# Exocortex.IA Development & Quality Standards

This document establishes the official coding conventions, skill design specifications, and automated verification rules for developing or updating components of the Exocortex.IA ecosystem.

---

## 1. Clean Code Principles (Core)

- **Directness**: Write simple, self-explanatory code. Avoid creating complex layers of abstraction unless requested.
- **Comments Policy**: Do not write comments describing *what* code is doing; document *why* complex or non-obvious logic was introduced (e.g., specific Hermes bugs, API page limits).
- **Docstrings & Annotations**:
    - **Python**: Use Google-style docstrings for all modules, classes, and functions.
    - **Node.js**: Use clear JSDoc comments to document function parameters and return types.

---

## 2. Custom Skill Specifications (`SKILL.md`)

All custom skills (`skills/excrtx-*/SKILL.md`) must follow a strict file structure to ensure they are discovered and compiled correctly by the build scripts.

### A. Frontmatter Template
Every skill must declare the following metadata fields:

```yaml
---
name: excrtx-domain-action           # kebab-case prefix: excrtx-
description: A short English summary # Enforce English for searchability
version: 1.0.0
category: excrtx
platforms: [linux]                   # OR [macos] or [linux, macos]
metadata:
  hermes:
    tags: [exocortex, tag1, tag2]
    related_skills: [excrtx-related-skill]
compiled_rules: |                    # YAML multiline scalar
  1. Internal behavior instructions...
  2. More rules...
---
```

### B. Required Skill Sections
The body of the `SKILL.md` must contain these exact headings (case-insensitive):
1.  `## When to Use` (or `## Trigger`): Clear description of when the LLM should load this skill.
2.  `## Procedure`: Step-by-step instructions for executing the skill's capability.
3.  `## Pitfalls`: Common errors, model drifts, or API limitations.
4.  `## Verification`: Checklist with `- [ ]` tasks to verify correct execution.

---

## 3. Skill Compiler (`compile_soul.py`)

- **Goal**: Read the `compiled_rules:` multiline block in the YAML frontmatter of all `excrtx-*` skills and inject them into `SOUL_SEED.md` between `<!-- COMPILED_RULES_START -->` and `<!-- COMPILED_RULES_END -->` tags.
- **Idempotency**: The script is idempotent. Running it repeatedly produces the same file output.
- **Rule of Thumb**: After making ANY modifications to a skill's rules, you **must** run:
  ```bash
  python3 scripts/compile_soul.py
  ```

---

## 4. Quality Evaluation Gate (`skill_judge.py`)

Exocortex uses an automated LLM-as-judge pipeline (`scripts/skill_judge.py`) to grade skills across five quality dimensions:

| Dimension | Checked By | Category | Criteria |
| :--- | :--- | :--- | :--- |
| **D1: Structural** | Deterministic script | Structural | Name validation, YAML compliance, English description, required sections check. |
| **D2: Clarity** | LLM Judge | Semantic | Clarity of the instructions, readability, absence of ambiguity. |
| **D3: Alignment** | LLM Judge | Alignment | Consistency with the `SOUL_SEED.md` behavioral contract. |
| **D4: Fitness** | LLM Judge | Engineering | Hardening against API edge cases, input validation, and system boundaries. |
| **D5: Economy** | LLM Judge | Token Efficiency | Compactness of prompt instructions (avoiding bloat). |

### Quality Verdicts & Actions
- **`PASS`**: The skill is compliant and ready for production deployment.
- **`IMPROVE`**: The skill has minor issues (usually missing platform info or minor description warnings). Requires refinement of non-critical items.
- **`REWRITE`**: Critical structural sections are missing, or LLM judge flagged serious logic regressions. Merging is **blocked** until resolved.

Running audits locally during development:
```bash
# Audit a single skill
python3 scripts/skill_judge.py --skill excrtx-behavior-vetor

# Dry run deterministic D1 check only (no LLM keys required)
python3 scripts/skill_judge.py --skill excrtx-behavior-vetor --d1-only
```
