# GEPA: Automated Skill Rewriting via LLM-as-Judge

## Summary

Implement **GEPA (Generative Evaluation and Prompt Automation)** — a closed-loop system that automatically rewrites skills based on LLM-as-Judge D2-D5 verdicts, targeting IMPROVE and REWRITE skills for promotion to PASS without manual intervention.

## Motivation

The current LLM-as-Judge harness (`scripts/skill_judge.py`) evaluates skills across 5 dimensions (D1-D5) and produces PASS/IMPROVE/REWRITE verdicts. Remediation is still manual — an operator reads the priority fixes and rewrites the skill by hand. GEPA closes this loop:

```
skill_judge.py → verdict + priority_fixes → GEPA rewriter → modified SKILL.md → re-judge → accept/reject
```

## Architecture

### Core Components

| Component | Purpose |
|-----------|---------|
| `scripts/gepa_rewriter.py` | Reads judge verdict + original SKILL.md, generates improved version |
| `scripts/gepa_loop.py` | Orchestrator: judge → rewrite → re-judge → accept/rollback |
| DSPy pipeline (optional) | Structured prompt optimization for consistent rewrites |

### Workflow

1. **Judge** — Run `skill_judge.py` on target skill → get D2-D5 scores + priority fixes
2. **Rewrite** — Feed original SKILL.md + priority fixes to LLM → get rewritten SKILL.md
3. **Re-judge** — Run `skill_judge.py` on rewritten version
4. **Accept/Reject gate:**
   - If verdict improved (REWRITE→IMPROVE or IMPROVE→PASS): accept + commit
   - If verdict unchanged or degraded: rollback + log failure
   - If D1 regresses: hard reject (structural compliance is non-negotiable)
5. **Iterate** — Up to N attempts with different rewriting strategies

### Constraints

- D1 must never regress (structural compliance is gated)
- `compiled_rules` field must be preserved exactly
- PT-BR calibration prompts must not be modified
- Frontmatter YAML must remain valid after rewrite
- Max 3 rewrite attempts per skill per run

### LLM Configuration

- Primary: DeepSeek V4 Pro (`deepseek-v4-pro`)
- Fallback: DeepSeek via OpenRouter
- Context: Full SKILL.md + rubric excerpt + priority fixes

## Acceptance Criteria

- [x] `gepa_loop.py` can auto-promote at least 1 IMPROVE skill to PASS in a single run
- [x] D1 regression baseline remains 43/43 COMPLIANT after any GEPA run
- [x] Failed rewrites are cleanly rolled back (git checkout / file restore)
- [x] Audit log records: skill, attempt count, before/after verdicts, LLM model used
- [x] Unit tests cover: accept gate, reject gate, D1 hard-reject, rollback

## Priority

**P0** — This is the next evolution of the skill quality pipeline.

## Labels

`enhancement`, `skill-judge`, `automation`, `p0`

## References

- `scripts/skill_judge.py` — existing judge
- `.dogfood/schemas/skill-judge-rubric.md` — D1-D5 rubric
- `.dogfood/baselines/` — frozen baselines
