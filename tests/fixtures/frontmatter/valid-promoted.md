---
# OKF Canonical (mandatory)
type: artifact
title: Skill creation workflow
description: Standard procedure for creating and validating new Exocórtex skills
tags: [workflow, skills, skill-judge, convention]
timestamp: 2026-03-15

# Acervo Extension (lifecycle)
class: perene
created_at: 2026-03-15T08:00:00Z
last_accessed_at: 2026-06-19T16:45:00Z
promoted_at: 2026-06-01T10:00:00Z

# Legacy (retained)
nature: workflows
---

## Procedure

1. Create `skills/excrtx-<name>/SKILL.md` with required frontmatter.
2. Write body sections: `## When to Use`, `## Procedure`, `## Pitfalls`, `## Verification`.
3. Run `python3 scripts/skill_judge.py --skill excrtx-<name> --d1-only` for structural check.
4. Run full judge: `python3 scripts/skill_judge.py --skill excrtx-<name>`.
5. Verdict must be `PASS` before promoting to bundle.

Promoted to perene on 2026-06-01 — this workflow is foundational and stable.
