# LLM Judge Prompt Template

> Use this template to construct the prompt sent to the LLM judge for D2–D5 evaluation.
> D1 (structural) is checked deterministically — no LLM needed.

---

## System Message

```
You are an expert evaluator of agent skills for {system_name}.
Your task is to evaluate a skill file against a structured rubric with 4 qualitative dimensions.
You must provide categorical labels — NOT numeric scores.
You must explain your reasoning (chain-of-thought) BEFORE assigning each label.
```

---

## User Message Structure

```markdown
## Context

{system_name} is a {brief_description}.
The behavioral contract for this system is defined in: {behavioral_contract_source}.
Language policy: {language_policy}.

## Behavioral Contract (excerpt)

{behavioral_contract_text — first 3000 chars}

## Evaluation Rubric

{rubric_text — from rubric-template.md}

## Skill Under Evaluation

### Frontmatter
```yaml
{skill_frontmatter_yaml}
```

### Body
{skill_body_text — first 15000 chars}

## Related Skills for Context
{related_skills_list — names only, for dependency awareness}

## Instructions

For each dimension (D2 through D5), you MUST:
1. State your reasoning — explain WHY before scoring
2. Assign a categorical label from the rubric
3. List specific issues found (concrete, quotable from the skill text)
4. Provide actionable recommendations (specific enough to implement)

## Output Format

Respond with ONLY valid JSON (no markdown fencing, no commentary):

{
  "D2_clarity": {
    "label": "CLEAR|AMBIGUOUS|VAGUE",
    "reasoning": "Your chain-of-thought analysis",
    "issues": ["issue1", "issue2"],
    "recommendations": ["fix1", "fix2"]
  },
  "D3_alignment": {
    "label": "ALIGNED|PARTIAL|MISALIGNED",
    "reasoning": "...",
    "issues": [],
    "recommendations": []
  },
  "D4_fitness": {
    "label": "PRODUCTION_READY|NEEDS_HARDENING|PROTOTYPE",
    "reasoning": "...",
    "issues": [],
    "recommendations": []
  },
  "D5_economy": {
    "label": "EFFICIENT|ACCEPTABLE|BLOATED",
    "reasoning": "...",
    "issues": [],
    "recommendations": []
  }
}
```

---

## Calibration Notes

### Bias Mitigation

1. **Self-enhancement bias**: Use a different model for judging than the one that wrote the skills. If not possible, add explicit calibration examples.
2. **Verbosity bias**: LLMs tend to rate longer skills higher. The rubric explicitly penalizes bloat in D5.
3. **Position bias**: When comparing skills pairwise, swap order between runs.
4. **Leniency drift**: Periodically re-calibrate by manually grading 5-10 skills and comparing with LLM verdicts.

### Calibration Protocol

1. Manually grade 10+ skills across the quality spectrum (good, medium, bad)
2. Run the LLM judge on the same skills
3. Compare labels — adjust rubric criteria where disagreement occurs
4. Add the manually-graded examples as few-shot calibration (optional but effective)

### Few-Shot Example (optional)

If calibration shows the judge is too lenient, add a few-shot example in the system message:

```
Here is an example of a VAGUE skill and why it scored VAGUE on D2:

[Example skill text]

D2 Analysis: The procedure section says "configure the system" without specifying
which configuration file, what values, or what command to run. This forces the
agent to guess, which produces inconsistent behavior. Label: VAGUE.
```
