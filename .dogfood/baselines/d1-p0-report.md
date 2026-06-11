# Skill Judge — P0 Baseline Report (D1-D5)

**Skills evaluated:** 8 (4 P0 + 4 related)
**Judge model:** Claude Opus (inline session evaluation)
**Date:** 2026-06-10

## Summary

| Skill | D1 | D2 | D3 | D4 | D5 | Verdict |
|---|---|---|---|---|---|---|
| `excrtx-behavior-vetor` | PARTIAL | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-behavior-canvas` | PARTIAL | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-govern-draftfirst` | NON_COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | 🔴 REWRITE |
| `excrtx-behavior-accuracy` | PARTIAL | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-behavior-briefing` | PARTIAL | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-govern-tools` | NON_COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | 🔴 REWRITE |
| `excrtx-quality-antislop` | NON_COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | 🔴 REWRITE |
| `excrtx-quality-gate` | PARTIAL | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |

**Totals:** PASS=0, IMPROVE=5, REWRITE=3

---

## Per-Skill Details

### excrtx-behavior-vetor — ⚠️ IMPROVE

**D1 Structural (PARTIAL):**
- Missing `## Pitfalls` section (uses `## Rules` instead)
- Uses `## Trigger` instead of `## When to Use` (acceptable alias, minor)
- Missing `platforms: [linux]`, `related_skills`

**D2 Clarity (CLEAR):**
- Excellent signal-to-vector mapping table with PT-BR examples
- Procedure steps are concrete and numbered
- Logging format is specified exactly
- Routing table is clear and actionable

**D3 Alignment (ALIGNED):**
- Correctly references Draft-First for external actions
- Socratic Mode for Evolution vector is well-specified
- Respects executive authority (force vector override)
- Vector classification is the core Exocortex contract — this skill IS the contract

**D4 Fitness (PRODUCTION_READY):**
- Verification checklist has 4 testable scenarios
- Rules section covers edge cases (force, reclassify, never expose)
- Logging format enables trace verification

**D5 Economy (EFFICIENT):**
- Tables used effectively, no redundancy
- Skill is 78 lines, well within budget

**Priority fixes:**
- [D1-SECTION] Rename `## Rules` to `## Pitfalls` or add separate Pitfalls section
- [D1] Add `related_skills: [excrtx-behavior-canvas, excrtx-govern-draftfirst]`
- [D1] Add `platforms: [linux]`

---

### excrtx-behavior-canvas — ⚠️ IMPROVE

**D1 Structural (PARTIAL):**
- Line-numbering artifacts detected throughout
- Uses `## Trigger` (acceptable alias)
- Missing `related_skills`

**D2 Clarity (AMBIGUOUS):**
- The concept of "Cognitive Canvas" is described but the procedure for generating one is buried in section numbering
- Line-numbering artifacts make it harder for the agent to parse the markdown
- The 7 canvas fields are listed but the priority ordering logic could be clearer
- Missing explicit "Don't use for" counter-triggers

**D3 Alignment (ALIGNED):**
- Correctly positions as the second filter after vector classification
- References other skills (antislop, taste) for quality enforcement
- Canvas logging format aligns with acervo structure

**D4 Fitness (NEEDS_HARDENING):**
- Verification exists but is 3 generic checkboxes
- Pitfalls section present but could be more specific to production failures
- No references directory despite complex logic

**D5 Economy (ACCEPTABLE):**
- Line-numbering artifacts waste tokens
- Some redundancy between "Regras" and the procedure steps

**Priority fixes:**
- [D1-MECHANICAL] Strip line-numbering artifacts
- [D2-CLARITY] Add counter-triggers to Trigger section
- [D4-FITNESS] Expand verification with specific testable scenarios
- [D1] Add `related_skills: [excrtx-behavior-vetor, excrtx-quality-gate]`

---

### excrtx-govern-draftfirst — 🔴 REWRITE

**D1 Structural (NON_COMPLIANT):**
- Line-numbering artifacts throughout (partially stripped in earlier edit)
- PT-BR description in frontmatter
- Missing `## Pitfalls` section entirely
- Line numbering creates broken frontmatter (mixed numbered/unnumbered lines)

**D2 Clarity (CLEAR):**
- Excellent taxonomy tables (internal vs external actions)
- Draft format template is explicit
- Channel classification (self-delivery, communication, publication) is clear
- Approval flow table is well-structured

**D3 Alignment (ALIGNED):**
- This IS the core Draft-First contract — perfectly aligned
- Covers edge cases: executive override, degraded mode, selective publication
- References other operational docs correctly

**D4 Fitness (PRODUCTION_READY):**
- Verification has 10 testable scenarios — excellent
- Degraded mode handling is production-learned
- Selective publication reference exists in `references/`

**D5 Economy (ACCEPTABLE):**
- Line-numbering artifacts waste context
- Some repetition between Taxonomia and Procedure sections

**Priority fixes:**
- [D1-MECHANICAL] Strip ALL line-numbering artifacts (critical — breaks frontmatter parsing)
- [D1-TRANSLATE] Translate description to English
- [D1-SECTION] Add `## Pitfalls` section (production-learned failures)
- [D1] Add `related_skills: [excrtx-behavior-vetor, excrtx-behavior-accuracy]`

---

### excrtx-behavior-accuracy — ⚠️ IMPROVE

**D1 Structural (PARTIAL):**
- Uses `## Triggers` (non-standard, should be `## When to Use`)
- Missing `platforms: [linux]`, `related_skills`
- Has both `## Anti-Patterns` and `## Verification Checklist` — good

**D2 Clarity (CLEAR):**
- Excellent: concrete verification commands per action type
- Report format examples (correct vs incorrect) are very clear
- Anti-patterns are explicitly listed with "NEVER DO"
- Integration with Draft-First is explained

**D3 Alignment (ALIGNED):**
- Directly supports the Draft-First + verify contract
- References `excrtx-govern-draftfirst` integration
- PT-BR examples are appropriate for user-facing verification prompts

**D4 Fitness (PRODUCTION_READY):**
- Verification checklist is testable (4 binary questions)
- Anti-patterns come from real production failures
- "Mentor" section adds cultural context

**D5 Economy (EFFICIENT):**
- Well-organized, tables and code blocks used effectively
- 167 lines — reasonable for the complexity

**Priority fixes:**
- [D1] Rename `## Triggers` to `## When to Use`
- [D1] Add `related_skills: [excrtx-govern-draftfirst, excrtx-govern-tools]`
- [D1] Add `platforms: [linux]`

---

### excrtx-behavior-briefing — ⚠️ IMPROVE

**D1 Structural (PARTIAL):**
- Line-numbering artifacts detected
- PT-BR description in frontmatter
- Missing `related_skills`

**D2 Clarity (AMBIGUOUS):**
- Procedure steps are numbered but some are abstract ("consolidar pendências")
- Missing specific commands or tool calls for briefing generation
- Missing counter-triggers

**D3 Alignment (ALIGNED):**
- Cross-microverso consolidation follows acervo architecture
- References vector classification and pending drafts

**D4 Fitness (NEEDS_HARDENING):**
- Verification exists but is generic
- Pitfalls section could be stronger
- Missing reference to actual briefing template

**D5 Economy (ACCEPTABLE):**
- Line-numbering artifacts present
- Could be tighter

**Priority fixes:**
- [D1-MECHANICAL] Strip line-numbering artifacts
- [D1-TRANSLATE] Translate description to English
- [D2-CLARITY] Make procedure steps more actionable (specify exact data sources)

---

### excrtx-govern-tools — 🔴 REWRITE

**D1 Structural (NON_COMPLIANT):**
- Missing `## Pitfalls` section
- Missing `## Verification` section
- Missing `related_skills`

**D2 Clarity (CLEAR):**
- Tool classification table (passive/active/external) is excellent
- Logging format is specified
- Mandatory rules are concrete

**D3 Alignment (ALIGNED):**
- Directly implements tool governance contract
- References Draft-First for external tools

**D4 Fitness (NEEDS_HARDENING):**
- No verification section at all
- No documented pitfalls from production use
- Has references directory with good material

**D5 Economy (ACCEPTABLE):**
- Well-organized but missing sections reduce completeness

**Priority fixes:**
- [D1-SECTION] Add `## Pitfalls` with real production failures
- [D1-SECTION] Add `## Verification` with testable checklist
- [D1] Add `related_skills: [excrtx-govern-draftfirst, excrtx-behavior-accuracy]`

---

### excrtx-quality-antislop — 🔴 REWRITE

**D1 Structural (NON_COMPLIANT):**
- Missing `## Pitfalls` section
- Missing `## Verification` section
- Missing `metadata.hermes.tags` (need to verify)
- Uses standalone sections without standard naming

**D2 Clarity (CLEAR):**
- Slop pattern list is concrete and actionable
- Replacement examples are clear
- Rules are binary: remove/replace, no ambiguity

**D3 Alignment (ALIGNED):**
- Core quality gate referenced by `excrtx-quality-gate`
- Anti-slop patterns are well-defined for PT-BR context

**D4 Fitness (PRODUCTION_READY):**
- Pattern list is the production reference
- Missing formal verification section but patterns are inherently testable

**D5 Economy (EFFICIENT):**
- Dense, pattern-focused, no waste

**Priority fixes:**
- [D1-SECTION] Add `## Pitfalls` (e.g., false positives, context-dependent patterns)
- [D1-SECTION] Add `## Verification` checklist
- [D1] Add `related_skills: [excrtx-quality-gate, excrtx-quality-taste]`

---

### excrtx-quality-gate — ⚠️ IMPROVE

**D1 Structural (PARTIAL):**
- Missing `## Pitfalls` section
- Missing `related_skills`
- Has Procedure and Verification — good

**D2 Clarity (CLEAR):**
- Orchestration logic is clear: route prose → antislop, visual → taste
- Executor agent responsibility is explicit
- Rules are concrete

**D3 Alignment (ALIGNED):**
- Correctly delegates to sub-skills
- Executor-only correction rule prevents orchestrator interference

**D4 Fitness (PRODUCTION_READY):**
- Verification is testable
- Clear integration points

**D5 Economy (EFFICIENT):**
- Compact orchestrator — appropriately minimal

**Priority fixes:**
- [D1-SECTION] Add `## Pitfalls` (e.g., executor vs orchestrator confusion)
- [D1] Add `related_skills: [excrtx-quality-antislop, excrtx-quality-taste]`

---

## Top Issues by Frequency

| Issue | Count | Fix Type |
|---|---|---|
| Missing `## Pitfalls` section | 6/8 | Tier 2 — add per skill |
| Missing `related_skills` in frontmatter | 8/8 | Tier 1 — batch |
| Missing `platforms: [linux]` | 8/8 | Tier 1 — batch |
| Line-numbering artifacts | 3/8 | Tier 1 — batch sed |
| PT-BR frontmatter description | 2/8 | Tier 2 — translate |
| Non-standard section names (`Trigger` vs `When to Use`) | 3/8 | Tier 1 — rename |
| Missing counter-triggers in trigger section | 6/8 | Tier 2 — add |
| Missing `## Verification` section | 2/8 | Tier 2 — add |
