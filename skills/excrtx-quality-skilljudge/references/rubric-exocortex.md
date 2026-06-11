# Skill Judge Rubric — Exocortex over Hermes

> Evaluation rubric for LLM-as-Judge skill assessment.
> Scores are categorical labels, NOT numeric. CoT reasoning is mandatory before each label.

## Dimensions

### D1: Structural Compliance (Hermes Canonical Format)

**What it measures:** Does the SKILL.md follow the Hermes Agent canonical format?

**Criteria:**
- Frontmatter has `name` (kebab-case), `description` (English, ≤1024 chars), `version` (semver)
- `metadata.hermes.tags` present with meaningful tags
- No line-numbering artifacts (`^\d+\|` prefixes in markdown body)
- Body has H1 title heading
- Body has `## When to Use` or `## Trigger` section
- Body has `## Procedure` section with numbered steps
- Body has `## Pitfalls` or `## Common Pitfalls` section
- Body has `## Verification` section (checklist preferred)
- Total file size ≤100KB, body ≤20KB recommended

**Labels:**
- `COMPLIANT`: All criteria met
- `PARTIAL`: Missing 1-2 non-critical criteria (e.g., missing Pitfalls but has Verification)
- `NON_COMPLIANT`: Missing 3+ criteria or missing critical elements (no Procedure, no frontmatter fields)

---

### D2: Instructional Clarity (Agent Effectiveness)

**What it measures:** Can the Hermes agent follow these instructions without guessing or requiring external context?

**Criteria:**
- Procedure steps are concrete and actionable (commands, paths, tool names)
- Each step has a clear input and expected output
- Trigger section includes positive triggers AND counter-triggers ("Don't use for:")
- Edge cases are addressed (what happens when X fails?)
- Steps are numbered and sequenced logically (dependencies before dependents)
- Tables used for structured data (action taxonomies, signal mappings)
- Code blocks used for exact commands, paths, or formats

**Labels:**
- `CLEAR`: Agent can execute the full procedure autonomously from this text alone
- `AMBIGUOUS`: Agent could execute but would need to make assumptions on 1-2 steps
- `VAGUE`: Agent would frequently guess or produce incorrect behavior

---

### D3: Behavioral Alignment (Exocortex Contract)

**What it measures:** Does the skill respect the Exocortex behavioral contract defined in SOUL_SEED.md and HARNESS.md?

**Criteria:**
- Respects Draft-First protocol where applicable (external actions → DRAFT)
- Vector classification awareness (Exec/Evol/Manut) when relevant
- Tool governance rules acknowledged (logging, classification)
- Anti-slop quality gates referenced where applicable
- Operates within the Acervo Cognitivo 4-layer model when accessing memory
- Respects executive authority (no autonomous external actions)

**Exocortex-specific rules:**
- PT-BR body text is EXPECTED for user-facing skills (onboarding, communication, briefing)
- PT-BR examples in signal tables (e.g., "envie", "faça", "agende") are CORRECT
- `compiled_rules` field is a valid custom extension (not penalized)
- Skills must not duplicate governance logic already owned by another skill

**Labels:**
- `ALIGNED`: Fully respects the behavioral contract
- `PARTIAL`: Generally aligned but missing 1-2 governance references
- `MISALIGNED`: Contradicts or ignores key behavioral rules

---

### D4: Harness Fitness (Production Readiness)

**What it measures:** Is the skill ready for production use in the dogfood pipeline?

**Criteria:**
- Verification section has testable criteria (checkboxes with specific, verifiable conditions)
- Pitfalls reflect real production learnings (not hypothetical)
- `compiled_rules` (when present) is synchronized with body content
- `references/` directory has supporting material when the skill references external docs
- Skill size is within budget for bundle context windows
- `related_skills` declared in frontmatter when dependency chains exist

**Labels:**
- `PRODUCTION_READY`: Verification is testable, pitfalls are real, references exist
- `NEEDS_HARDENING`: Has verification but it's weak, or missing real pitfalls
- `PROTOTYPE`: No testable verification, no pitfalls, or references missing

---

### D5: Token Economy (Context Efficiency)

**What it measures:** Does the skill communicate maximum information in minimum tokens?

**Criteria:**
- No redundant sections or repeated content
- Tables used over prose where structured data exists
- No line-numbering artifacts or formatting debris
- Description is dense and search-optimized
- Body doesn't duplicate content available in `references/` directory
- `compiled_rules` doesn't unnecessarily duplicate full body (acceptable for strategic harness skills that reduce context)

**Labels:**
- `EFFICIENT`: Tight, well-organized, no waste
- `ACCEPTABLE`: Some redundancy but within reasonable bounds
- `BLOATED`: Significant redundancy, debris, or unnecessary duplication

---

## Overall Verdict

Computed from dimensional labels:

| Condition | Verdict |
|---|---|
| All dimensions at best label | `PASS` |
| 1-2 dimensions at middle label, none at worst | `IMPROVE` |
| Any dimension at worst label, or 3+ at middle | `REWRITE` |

## Output Format

```json
{
  "skill_name": "excrtx-example",
  "dimensions": {
    "D1_structural": {"label": "COMPLIANT", "reasoning": "...", "issues": [], "recommendations": []},
    "D2_clarity": {"label": "CLEAR", "reasoning": "...", "issues": [], "recommendations": []},
    "D3_alignment": {"label": "ALIGNED", "reasoning": "...", "issues": [], "recommendations": []},
    "D4_fitness": {"label": "PRODUCTION_READY", "reasoning": "...", "issues": [], "recommendations": []},
    "D5_economy": {"label": "EFFICIENT", "reasoning": "...", "issues": [], "recommendations": []}
  },
  "overall_verdict": "PASS",
  "priority_fixes": [],
  "related_skills_context": ["excrtx-other-skill"]
}
```
