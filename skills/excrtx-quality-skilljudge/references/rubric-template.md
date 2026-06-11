# Skill Judge Rubric Template

> Adapt this template for your specific skill set and behavioral contract.
> Replace `{system_name}`, `{behavioral_contract}`, and `{language_policy}` with your values.

---

## How to Customize

1. **Copy this file** to your `.dogfood/schemas/` or equivalent
2. **Edit D3 criteria** to match your system's behavioral contract
3. **Edit language rules** if your skill set is multilingual
4. **Add custom field rules** if your skills use non-standard frontmatter
5. **Calibrate** by manually grading 10+ skills and adjusting criteria

---

## Dimensions

### D1: Structural Compliance

**What it measures:** Does the SKILL.md follow the Hermes Agent canonical format?

**Criteria:**
- Frontmatter has `name` (kebab-case), `description` (≤1024 chars), `version` (semver)
- `metadata.hermes.tags` present with meaningful tags
- No formatting artifacts (line-numbering, orphan fences)
- Body has H1 title heading
- Body has `## When to Use` section (with counter-triggers)
- Body has `## Procedure` section with numbered steps
- Body has `## Pitfalls` section
- Body has `## Verification` section (checklist preferred)
- Total file ≤100KB, body ≤20KB recommended

**Labels:**
- `COMPLIANT`: All criteria met
- `PARTIAL`: Missing 1–2 non-critical criteria
- `NON_COMPLIANT`: Missing 3+ criteria or missing critical elements

**Customization points:**
- Add `platforms` requirement if your skills are OS-specific
- Add `related_skills` requirement if dependency chains exist
- Add `category` requirement if you organize skills by domain
- Allow custom frontmatter fields (list them here as accepted extensions)

---

### D2: Instructional Clarity

**What it measures:** Can the agent follow these instructions without guessing?

**Criteria:**
- Procedure steps are concrete and actionable (commands, paths, tool names)
- Each step has a clear input and expected output
- When to Use section includes positive triggers AND counter-triggers
- Edge cases addressed (what happens when X fails?)
- Steps are numbered and sequenced logically
- Tables used for structured data
- Code blocks used for exact commands, paths, or formats

**Labels:**
- `CLEAR`: Agent can execute the full procedure autonomously
- `AMBIGUOUS`: Agent could execute but would need to make 1–2 assumptions
- `VAGUE`: Agent would frequently guess or produce incorrect behavior

---

### D3: Behavioral Alignment (CUSTOMIZE THIS)

**What it measures:** Does the skill respect the system's behavioral contract?

> ⚠️ **This dimension is system-specific.** Replace the criteria below with your system's contract.

**Example criteria (Exocortex):**
- Respects Draft-First protocol (external actions → DRAFT)
- Vector classification awareness (Exec/Evol/Manut) when relevant
- Tool governance rules acknowledged
- Quality gates referenced where applicable
- Operates within the memory architecture model
- Respects executive authority

**{language_policy} rules:**
- {target_language} body text is EXPECTED for user-facing skills
- {target_language} examples in trigger tables are CORRECT
- Custom fields (e.g., `compiled_rules`) are valid extensions

**Labels:**
- `ALIGNED`: Fully respects the behavioral contract
- `PARTIAL`: Generally aligned but missing 1–2 governance references
- `MISALIGNED`: Contradicts or ignores key behavioral rules

---

### D4: Harness Fitness

**What it measures:** Is the skill ready for production use?

**Criteria:**
- Verification section has testable criteria (checkboxes with specific conditions)
- Pitfalls reflect real production learnings (not hypothetical)
- Custom fields synchronized with body content
- `references/` directory has supporting material when needed
- Skill size within context budget
- `related_skills` declared when dependency chains exist

**Labels:**
- `PRODUCTION_READY`: Verification is testable, pitfalls are real
- `NEEDS_HARDENING`: Has verification but weak, or missing real pitfalls
- `PROTOTYPE`: No testable verification, no pitfalls

---

### D5: Token Economy

**What it measures:** Maximum information per token?

**Criteria:**
- No redundant sections or repeated content
- Tables used over prose where structured data exists
- No formatting artifacts or debris
- Description is dense and search-optimized
- Body doesn't duplicate content in `references/`

**Labels:**
- `EFFICIENT`: Tight, well-organized, no waste
- `ACCEPTABLE`: Some redundancy but reasonable
- `BLOATED`: Significant redundancy, debris, or duplication

---

## Overall Verdict

| Condition | Verdict |
|---|---|
| All dimensions at best label | `PASS` |
| 1–2 at middle label, none at worst | `IMPROVE` |
| Any at worst label, or 3+ at middle | `REWRITE` |

---

## Output Format

```json
{
  "skill_name": "example-skill",
  "dimensions": {
    "D1_structural": {
      "label": "COMPLIANT",
      "reasoning": "Chain-of-thought analysis...",
      "issues": [],
      "recommendations": []
    },
    "D2_clarity": { "label": "CLEAR", "reasoning": "...", "issues": [], "recommendations": [] },
    "D3_alignment": { "label": "ALIGNED", "reasoning": "...", "issues": [], "recommendations": [] },
    "D4_fitness": { "label": "PRODUCTION_READY", "reasoning": "...", "issues": [], "recommendations": [] },
    "D5_economy": { "label": "EFFICIENT", "reasoning": "...", "issues": [], "recommendations": [] }
  },
  "overall_verdict": "PASS",
  "priority_fixes": [],
  "related_skills_context": []
}
```
