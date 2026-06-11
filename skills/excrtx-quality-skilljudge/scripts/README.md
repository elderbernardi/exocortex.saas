# Skill Judge Script — Usage Guide

> Deterministic D1 structural evaluator for SKILL.md files.
> For D2–D5 (LLM-based), use the prompt template in `references/judge-prompt-template.md`.

## Quick Start

```bash
# Run D1 check on all skills
python skills/excrtx-quality-skilljudge/scripts/skill_judge.py --all --d1-only

# Run D1 check on P0 skills only
python skills/excrtx-quality-skilljudge/scripts/skill_judge.py --p0 --d1-only

# Save results and report
python skills/excrtx-quality-skilljudge/scripts/skill_judge.py --all --d1-only \
  --output baseline.json \
  --report baseline-report.md

# Compare against a previous baseline (detect regressions)
python skills/excrtx-quality-skilljudge/scripts/skill_judge.py --all --d1-only \
  --compare-baseline baseline.json
```

## Adapting to Your Skill Set

The script expects skills in a `skills/` directory with `SKILL.md` files. To adapt:

1. **Change the skills directory**: Modify the `SKILLS_DIR` constant at the top of the script.
2. **Change P0 skills list**: Modify the `P0_SKILLS` constant to match your priority skills.
3. **Adjust D1 checks**: The `check_d1_structural()` function checks for Hermes-canonical sections. Modify the required section list if your format differs.
4. **Add custom field checks**: If your skills use custom frontmatter fields (like `compiled_rules`), add validation logic.

## Output Format

### JSON Baseline (`--output`)

```json
{
  "skill_name": {
    "d1": {
      "label": "COMPLIANT|PARTIAL|NON_COMPLIANT",
      "issues": ["..."],
      "recommendations": ["..."]
    }
  }
}
```

### Markdown Report (`--report`)

Human-readable report with per-skill results, issue frequency tables, and remediation recommendations.

### Comparison (`--compare-baseline`)

Shows improvements and regressions versus a previous baseline:

```
✅ IMPROVEMENTS (3):
  - skill-a: REWRITE → PASS
  - skill-b: IMPROVE → PASS
🔴 REGRESSIONS (0):
```
