---
name: excrtx-quality-gepa
description: Automated skill improvement via closed-loop LLM rewriting. Runs judge
  → rewrite → re-judge → accept/rollback cycles to promote skills from IMPROVE/REWRITE
  to PASS.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - quality
    - automation
    - skill-judge
    - rewriting
    related_skills:
    - excrtx-quality-skilljudge
    - excrtx-quality-gate
    - excrtx-quality-antislop
    calibration:
    - feature_id: EX-53
      calibration_prompt: 'Ao executar o GEPA para melhorar skills automaticamente,
        o agente deve:

        1. Carregar o baseline atual do skill_judge.

        2. Para cada skill com verdict != PASS, executar o loop: rewrite → re-judge
        → accept/rollback.

        3. Respeitar os safety gates: D1 nunca regredir, compiled_rules preservado,
        PT-BR preservado.

        4. Gerar audit log em .dogfood/runs/gepa/ com resultados.'
      test_prompt: Execute o GEPA para melhorar a skill excrtx-harness-promptlog que
        tem verdict IMPROVE.
      acceptance_criteria: O agente deve executar o loop GEPA com pelo menos 1 tentativa,
        respeitar o D1 gate, e gerar audit log.
      remediation_tip: 'Falha de Safety: O GEPA deve verificar D1 compliance após
        cada rewrite e rollback imediatamente se regredir.'
---
# GEPA — Generative Evaluation and Prompt Automation

Automated skill improvement system that closes the loop between the LLM-as-Judge evaluator (`skill_judge.py`) and an LLM rewriter. Promotes skills from IMPROVE/REWRITE to PASS without manual intervention.

## When to Use

- After a skill judge sweep reveals skills with IMPROVE or REWRITE verdicts
- During skill maintenance cycles to batch-improve quality
- When a new skill doesn't pass the judge and you want automated remediation
- As part of the quality gate pipeline before deployment

**Don't use for:**
- Skills that already have PASS verdict (no action needed)
- Creating new skills from scratch → use `excrtx-harness-tooldev` or manual authoring
- Evaluating skills without rewriting → use `excrtx-quality-skilljudge`
- Fixing non-structural issues like missing `references/` directories (manual task)

## Procedure

### 1. Run Baseline Assessment

```bash
python -m scripts.skill_judge --all --save-baseline
```

This produces a baseline JSON in `.dogfood/baselines/` with D1-D5 verdicts for all skills.

### 2. Execute GEPA Loop

**Single skill (recommended for first run):**
```bash
python -m scripts.gepa_loop --skill excrtx-harness-promptlog --max-attempts 2
```

**Dry run (verify without changes):**
```bash
python -m scripts.gepa_loop --all --dry-run
```

**Full batch (after successful single-skill test):**
```bash
python -m scripts.gepa_loop --all --max-attempts 3
```

**Targeted verdicts:**
```bash
python -m scripts.gepa_loop --rewrite-only   # highest impact
python -m scripts.gepa_loop --improve-only    # highest volume
```

### 3. Review Audit Log

Check the generated audit log in `.dogfood/runs/gepa/`:

```bash
cat .dogfood/runs/gepa/gepa-*.json | python -m json.tool
```

Verify: skills_promoted > 0, d1_regressions = 0.

### 4. Validate Results

```bash
# Confirm no D1 regressions
python -m scripts.skill_judge --all --d1-only

# Compare against pre-GEPA baseline
python -m scripts.skill_judge --all --compare-baseline .dogfood/baselines/d1d5-deepseek-v4pro-baseline.json
```

### 5. Save New Baseline

```bash
python -m scripts.skill_judge --all --save-baseline .dogfood/baselines/d1d5-post-gepa-baseline.json
```

## Pitfalls

1. **D1 regression is catastrophic.** If a rewrite breaks structural compliance (removes required sections, corrupts YAML), the skill becomes unusable. The D1 hard gate prevents this, but if you bypass it (editing `gepa_loop.py`), you risk breaking the entire skill bundle.
2. **compiled_rules corruption.** The `compiled_rules` frontmatter field is a condensed behavioral contract. If the LLM reformats, reorders, or paraphrases it, the agent's behavior changes unpredictably. The validator checks for bit-for-bit preservation.
3. **PT-BR calibration translated.** The calibration prompts are in Portuguese by design (matching the executive's language). English-only LLMs sometimes translate them. The validator catches this.
4. **Strategy escalation pitfall.** The `minimal` strategy (attempt 3) may produce cosmetic-only changes that don't improve the verdict. This is by design — better to fail cleanly than to over-modify.
5. **API cost in batch mode.** Each skill requires ~2 LLM calls (rewrite + re-judge). With 24 skills × 3 attempts max = 144 calls worst case. DeepSeek V4 Pro keeps this under $5, but monitor costs.
6. **Infinite loop prevention.** Max 3 attempts per skill per run is a hard limit. If a skill fails 3 times, it's marked as failed and skipped. Don't increase without good reason.

## Verification

- [ ] `python -m scripts.gepa_loop --help` shows all CLI flags
- [ ] `python -m scripts.gepa_loop --all --dry-run` completes with 0 errors
- [ ] D1 sweep after GEPA: same or better compliance count as pre-GEPA baseline
- [ ] Audit log JSON in `.dogfood/runs/gepa/` is valid and contains `per_skill` entries
- [ ] At least 1 skill promoted (IMPROVE → PASS or REWRITE → IMPROVE) in a real run
- [ ] `compiled_rules` of all skills with this field are unchanged (verified with `diff`)
- [ ] No PT-BR calibration fields were modified (verified by comparing frontmatter)
