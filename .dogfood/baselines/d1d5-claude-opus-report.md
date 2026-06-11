# Skill Judge — Baseline Report

**Skills evaluated:** 40

## Summary

| Skill | D1 | D2 | D3 | D4 | D5 | Verdict |
|---|---|---|---|---|---|---|
| `excrtx-assess-repofit` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-assess-selftest` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-behavior-canvas` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-govern-draftfirst` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-govern-tools` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-harness-core` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-harness-hermesops` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-harness-imbroke` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-harness-kanban` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-harness-promptlog` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-harness-surfaces` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-harness-tooldev` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-hermes-extensions` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-integrate-browser` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-integrate-docbrain` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-integrate-gdrive` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-integrate-nlmops` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-integrate-oauth` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-memory-intake` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-memory-manager` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-memory-mvinstall` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-memory-mvsetup` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-memory-opsmemory` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-memory-wikiadapt` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-onboard-interview` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-onboard-welcome` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-produce-artifacts` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-produce-slides` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-quality-designsys` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-quality-gate` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-quality-skilljudge` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-quality-taste` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-behavior-accuracy` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-briefing` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-vetor` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-codexint` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-nlmroute` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-newmicro` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-produce-oficios` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-antislop` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |

**Totals:** PASS=8, IMPROVE=32, REWRITE=0

## Per-Skill Details

### excrtx-assess-repofit — IMPROVE


### excrtx-assess-selftest — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add more objective checkpoints to the self-test protocol
- [D4_FITNESS] Add concrete test fixtures with expected outputs

**D2_clarity (AMBIGUOUS):** Self-test concept is clear but procedure relies on agent self-assessment which is inherently subjective. Code block shows expected output format.
**D4_fitness (NEEDS_HARDENING):** No references directory. Verification section exists but self-testing is hard to make deterministic.

### excrtx-behavior-canvas — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add brief inline descriptions for v0.4 schema fields
- [D5_ECONOMY] Consider extracting v0.4 schema details to references/

**D2_clarity (AMBIGUOUS):** Procedure has numbered steps but v0.4 schema fields are complex. Some steps reference internal concepts (sharing_constraints, macroverso.status) without defining them inline. An agent unfamiliar with 
**D5_economy (ACCEPTABLE):** 8889B body is moderately large for a behavioral skill. The v0.4 schema section could be extracted to references/ but is needed for inline reference. Some rules could be tables.

### excrtx-govern-draftfirst — IMPROVE

**D5_economy (ACCEPTABLE):** 7744B body is justified by the complexity of the protocol. Taxonomy tables are dense and useful. Some overlap between the overview and the detailed procedure steps.

### excrtx-govern-tools — IMPROVE


### excrtx-harness-core — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add counter-triggers
- [D2_CLARITY] Add inline script usage examples
- [D4_FITNESS] Add script documentation to body or references/

**D2_clarity (AMBIGUOUS):** Core harness concept documented but procedure relies on external scripts without inline explanation. No counter-triggers.
**D4_fitness (NEEDS_HARDENING):** References directory exists but scripts are external. Verification section could be more specific.

### excrtx-harness-hermesops — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add counter-triggers
- [D2_CLARITY] Make trilho selection explicit
- [D4_FITNESS] Add trilho-specific test cases

**D2_clarity (AMBIGUOUS):** Trilho A (CLI) and Trilho B (Delegation) documented but selection criteria are implicit. No counter-triggers.
**D4_fitness (NEEDS_HARDENING):** References directory exists but trilho system needs clearer verification criteria.

### excrtx-harness-imbroke — IMPROVE

**D5_economy (ACCEPTABLE):** 9610B body approaches 10KB. Justified by the complexity of the cost management system.

### excrtx-harness-kanban — IMPROVE


### excrtx-harness-promptlog — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add counter-triggers
- [D2_CLARITY] Expand procedure with logging examples
- [D4_FITNESS] Expand with logging format examples and integration points

**D2_clarity (AMBIGUOUS):** 5 sections is very thin. Procedure is minimal. No counter-triggers. Logging format shown but few details.
**D4_fitness (NEEDS_HARDENING):** No references directory. 1095B body is too thin for production readiness. Verification exists but minimal.

### excrtx-harness-surfaces — IMPROVE

**Priority fixes:**
- [D5_ECONOMY] Extract individual surface specs to references/

**D5_economy (ACCEPTABLE):** 17996B body is close to 20KB limit. Consider extracting some surface definitions to references/.

### excrtx-harness-tooldev — IMPROVE

**Priority fixes:**
- [D4_FITNESS] Add references/ with tool template examples

**D4_fitness (NEEDS_HARDENING):** No references directory. Verification exists but tool development is a broad topic.

### excrtx-hermes-extensions — IMPROVE


### excrtx-integrate-browser — IMPROVE


### excrtx-integrate-docbrain — IMPROVE


### excrtx-integrate-gdrive — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add inline summary of OAuth setup flow
- [D4_FITNESS] Expand procedure with inline troubleshooting steps

**D2_clarity (AMBIGUOUS):** 9 sections but procedure is sparse. OAuth setup referenced but details are in external scripts, not in the SKILL.md body.
**D4_fitness (NEEDS_HARDENING):** References directory exists but the skill body is thin (1891B). Verification depends on external OAuth state.

### excrtx-integrate-nlmops — IMPROVE

**Priority fixes:**
- [D4_FITNESS] Add references/ with NLM workflow diagrams

**D4_fitness (NEEDS_HARDENING):** No references directory. Verification exists but NLM dependency makes testing difficult without auth.

### excrtx-integrate-oauth — IMPROVE


### excrtx-memory-intake — IMPROVE

**Priority fixes:**
- [D5_ECONOMY] Extract IntakeEnvelope schema to references/

**D5_economy (ACCEPTABLE):** 11491B body exceeds 10KB recommended size. The pipeline documentation is thorough but could be more concise.

### excrtx-memory-manager — IMPROVE

**Priority fixes:**
- [D5_ECONOMY] Consider extracting the directory structure template to references/

**D5_economy (ACCEPTABLE):** 10361B body is on the larger side but justified by the complexity of the 4-layer model. Some sections could be slimmed.

### excrtx-memory-mvinstall — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add excrtx/v1 schema summary to body or reference
- [D4_FITNESS] Create references/excrtx-v1-schema.md

**D2_clarity (AMBIGUOUS):** Schema excrtx/v1 referenced but not fully defined inline. Installation procedure exists but some steps assume familiarity with the package format.
**D4_fitness (NEEDS_HARDENING):** No references directory. Schema definition is implied but not documented.

### excrtx-memory-mvsetup — IMPROVE


### excrtx-memory-opsmemory — IMPROVE


### excrtx-memory-wikiadapt — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add brief inline summary of the target ontology or link to reference
- [D4_FITNESS] Add ontology reference document to references/

**D2_clarity (AMBIGUOUS):** Procedure references Ontologia Multifocal v2 without defining it inline. Agent needs external context to understand the ontology mapping.
**D4_fitness (NEEDS_HARDENING):** References directory exists but the ontology mapping itself is not testable without the ontology definition.

### excrtx-onboard-interview — IMPROVE

**Priority fixes:**
- [D4_FITNESS] Add references/ with example interview flows

**D4_fitness (NEEDS_HARDENING):** No references directory. Interview blocks could benefit from example responses.

### excrtx-onboard-welcome — IMPROVE


### excrtx-produce-artifacts — IMPROVE

**Priority fixes:**
- [D5_ECONOMY] Consider splitting into core + views reference

**D5_economy (ACCEPTABLE):** 16769B body exceeds 10KB but the artifact management system is complex enough to justify it. References used for delegation.

### excrtx-produce-slides — IMPROVE

**Priority fixes:**
- [D5_ECONOMY] Consider extracting script usage docs to references/

**D5_economy (ACCEPTABLE):** 14039B body exceeds 10KB but slide production is inherently complex with multiple export formats.

### excrtx-quality-designsys — IMPROVE


### excrtx-quality-gate — IMPROVE


### excrtx-quality-skilljudge — IMPROVE


### excrtx-quality-taste — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add brief summaries of each sub-skill's procedure

**D2_clarity (AMBIGUOUS):** References 3 sub-skills (gpt-taste, brandkit, brutalist) but their content and procedures are in sub-files, not in the main SKILL.md body. Agent needs to read additional files.

### excrtx-behavior-accuracy — PASS


### excrtx-behavior-briefing — PASS


### excrtx-behavior-vetor — PASS


### excrtx-harness-codexint — PASS


### excrtx-integrate-nlmroute — PASS


### excrtx-memory-newmicro — PASS


### excrtx-produce-oficios — PASS


### excrtx-quality-antislop — PASS

