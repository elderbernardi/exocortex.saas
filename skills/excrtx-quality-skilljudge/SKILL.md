---
name: excrtx-quality-skilljudge
description: LLM-as-Judge framework for evaluating and improving agent skill files. Runs a 5-dimension rubric (structural
  compliance, instructional clarity, behavioral alignment, harness fitness, token economy) against SKILL.md files, produces
  categorical verdicts, and generates actionable remediation. Replicable across any Hermes-compatible skill set.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - quality
    - judge
    - llm-as-judge
    - skill-evaluation
    - rubric
    related_skills:
    - excrtx-quality-gate
    - excrtx-quality-antislop
    calibration:
    - feature_id: EX-54
      calibration_prompt: 'Você avalia skills usando rubric de 5 dimensões: D1 Structural (determinístico), D2 Clarity, D3
        Alignment, D4 Fitness, D5 Economy. Verdicts: all best=PASS, 1-2 middle=IMPROVE, any worst=REWRITE.'
      test_prompt: Explique as 5 dimensões do rubric de avaliação de skills e como o verdict geral é calculado a partir das
        labels dimensionais.
      acceptance_criteria: O agente deve listar D1 a D5 com labels categóricas corretas e demonstrar a tabela de verdicts
        (all best=PASS, 1-2 middle=IMPROVE, any worst=REWRITE).
      remediation_tip: 'FALHA: Rubric incompleta ou verdict incorreto. As 5 dimensões são: D1 Structural Compliance (gate
        determinístico, sem LLM), D2 Instructional Clarity, D3 Behavioral Alignment, D4 Harness Fitness, D5 Token Economy.
        O verdict geral segue: todos ''best''=PASS, 1-2 ''middle''=IMPROVE, qualquer ''worst''=REWRITE. Consulte .dogfood/schemas/skill-judge-rubric.md.'
---
# Skill Judge — LLM-as-Judge Framework for Agent Skills

> Evaluate skill quality systematically, not by gut feeling. Categorical verdicts over numeric scores. Chain-of-thought reasoning before every label.

## When to Use

Activate when:
- A new skill is created and needs quality validation before deployment
- An existing skill set needs a compliance audit (batch sweep)
- Skills are being refactored or migrated to a new runtime
- A Self-Evolution pipeline needs a fitness function for skill optimization
- The user says "judge my skills", "evaluate skills", "audit skills", "skill quality"
- The user says (PT-BR): "julgue minhas skills", "avalie qualidade das skills", "auditoria de skills", "qualidade de skills"

**Don't use for:** Evaluating agent runtime behavior (use session traces). Evaluating LLM output quality (use excrtx-quality-antislop). Evaluating code quality (use code-review or linters).

## Procedure

### 1. Prepare the Rubric

Before judging, ensure a rubric exists. The rubric defines 5 evaluation dimensions with categorical labels. See `references/rubric-template.md` for the full template.

**The 5 Dimensions:**

| # | Dimension | Labels (best → worst) | What It Measures |
|---|---|---|---|
| D1 | Structural Compliance | `COMPLIANT` / `PARTIAL` / `NON_COMPLIANT` | Canonical format: frontmatter, required sections, size |
| D2 | Instructional Clarity | `CLEAR` / `AMBIGUOUS` / `VAGUE` | Agent can follow without guessing |
| D3 | Behavioral Alignment | `ALIGNED` / `PARTIAL` / `MISALIGNED` | Respects behavioral contract |
| D4 | Harness Fitness | `PRODUCTION_READY` / `NEEDS_HARDENING` / `PROTOTYPE` | Testable verification, real pitfalls |
| D5 | Token Economy | `EFFICIENT` / `ACCEPTABLE` / `BLOATED` | Max info per token, no debris |

**Customization per skill set:**
- D3 alignment criteria change based on the system's behavioral contract (e.g., SOUL_SEED.md, HARNESS.md, or equivalent persona definition)
- D1 structural requirements can be tightened or relaxed based on the runtime's skill loading mechanism
- Add language-specific rules for multilingual skill sets (e.g., body in target language, frontmatter in English)

### 2. Run Deterministic Pre-Checks (D1)

D1 structural compliance is checked WITHOUT an LLM — it's fully deterministic:

```
Parse YAML frontmatter → Check required fields → Scan for section headings → Detect artifacts
```

**Required fields checklist:**
- [ ] `name` present and kebab-case
- [ ] `description` present, ≤1024 chars, in search language (usually English)
- [ ] `version` present and semver
- [ ] `metadata.hermes.tags` present with meaningful tags

**Required sections checklist:**
- [ ] H1 title heading
- [ ] `## When to Use` (or alias: `## Trigger`)
- [ ] `## Procedure` (or alias: `## Protocol`, `## Steps`)
- [ ] `## Pitfalls` (or alias: `## Common Pitfalls`, `## Anti-Patterns`)
- [ ] `## Verification` (or alias: `## Verification Checklist`)

**Artifact detection:**
- [ ] No line-numbering artifacts (`^\d+\|` prefixes in markdown)
- [ ] No formatting debris (orphan code fences, broken tables)
- [ ] Total file ≤100KB, body ≤20KB recommended

**Label assignment:**
- `COMPLIANT`: 0 issues
- `PARTIAL`: 1–2 non-critical issues (e.g., missing Pitfalls but has Verification)
- `NON_COMPLIANT`: 3+ issues or missing critical elements (no Procedure, no frontmatter fields)

### 3. Run LLM Judge (D2–D5)

Send the skill content + rubric + behavioral context to an LLM for qualitative evaluation. The judge model should be different from the model that wrote the skills (bias mitigation).

**Judge prompt structure (four-part):**

1. **System role**: "You are an expert evaluator of agent skills for {system_name}."
2. **Criterion definitions**: Injected from rubric with labels and examples
3. **Chain-of-thought instruction**: "For each dimension, explain your reasoning BEFORE assigning the label."
4. **Output format**: Structured JSON with `{dimension, reasoning, label, issues[], recommendations[]}`

**Key rules for the LLM judge:**
- Categorical labels only — no numeric 1-10 scores (they cause mean-reversion)
- CoT reasoning is MANDATORY before each label (prevents snap judgments)
- Each issue must have a concrete, actionable recommendation
- The judge must understand the behavioral contract (inject SOUL_SEED.md or equivalent)
- Multilingual body text is scored NEUTRAL when the skill set targets non-English users

### 4. Compute Overall Verdict

| Condition | Verdict |
|---|---|
| All dimensions at best label | `PASS` |
| 1–2 dimensions at middle label, none at worst | `IMPROVE` |
| Any dimension at worst label, or 3+ at middle | `REWRITE` |

### 5. Generate Remediation Queue

Sort skills by verdict severity, then by fix complexity:

**Three remediation tiers:**

| Tier | Fix Type | Method | Review? |
|---|---|---|---|
| **Tier 1** | Mechanical | Batch `sed` / Python: strip artifacts, add fields, rename sections | No — safe to auto-apply |
| **Tier 2** | Section additions | LLM generates draft sections (Pitfalls, Verification, counter-triggers) | Yes — per batch |
| **Tier 3** | Structural rewrites | Manual rewrite of skills flagged as REWRITE | Yes — per skill |

### 6. Apply Fixes and Re-Sweep

After applying fixes:

1. Re-run the judge sweep
2. Compare against baseline using `--compare-baseline`
3. Verify: 0 regressions, N improvements
4. Save the new baseline for future regression prevention

### 7. Wire Into CI / Dogfood Pipeline

For regression prevention:

```bash
# In test runner or CI:
python scripts/skill_judge.py --all --d1-only --compare-baseline .dogfood/baselines/skill-judge-baseline.json
```

Any skill that regresses (verdict goes from PASS → IMPROVE or worse) fails the pipeline.

## Pitfalls

- **Numeric scoring trap**: Never use 1-10 scales. LLMs suffer from mean-reversion (clustering around 7-8). Categorical labels (`COMPLIANT`/`PARTIAL`/`NON_COMPLIANT`) are more reliable and actionable.
- **Judge-generator alignment**: If the same model writes AND judges the skills, self-enhancement bias inflates scores. Use a different model or add rubric calibration with human-graded examples.
- **Overtightening D1**: Some skill sets have valid custom fields (e.g., `compiled_rules` in Exocortex). The rubric must accommodate custom extensions — flag them as non-standard, don't penalize.
- **Language policy blindness**: Multilingual skill sets need explicit language rules. Body text in the user's language may be intentional. The judge must distinguish between frontmatter language (search-optimized) and body language (user-optimized).
- **Tier 1 false confidence**: Mechanical fixes (line-number stripping, field additions) are safe but superficial. A skill can be COMPLIANT on D1 and still VAGUE on D2. Always run the full D2–D5 sweep.
- **Baseline drift**: Save baselines after each remediation session. Without baselines, you can't detect regressions.
- **Counter-trigger neglect**: Skills without "Don't use for:" sections cause false activations. Counter-triggers are as important as positive triggers for agent precision.

## Verification

- [ ] Rubric defines all 5 dimensions with categorical labels (no numeric scales)
- [ ] D1 pre-checks run deterministically (no LLM needed)
- [ ] D2–D5 judge prompt includes CoT instruction + structured JSON output
- [ ] Overall verdict computed correctly from dimensional labels
- [ ] Baseline comparison detects regressions and improvements
- [ ] Remediation queue prioritized by severity (REWRITE > IMPROVE > PASS)
- [ ] Tier 1 fixes are safe to auto-apply (no semantic changes)
- [ ] Judge respects language policy (multilingual body text not penalized)
- [ ] Custom fields (e.g., `compiled_rules`) not penalized by D1 checks
