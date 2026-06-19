# Agent Memory — Acervo Lifecycle Plan

> Shared context file for all agents working on the Acervo Lifecycle, Deprecation & OKF Alignment plan.
> **Read this before starting any task.** Append your findings after completing a task.
> **Never edit existing entries.** Append-only.

---

## Plan Context

- **Plan:** Acervo Cognitivo Lifecycle, Deprecation & OKF Alignment
- **Created:** 2026-06-19
- **Executive:** Elder Bernardi
- **GitHub Issue:** (to be created)
- **Repository:** `/home/elder/projetos/projetob/exocortex.saas`
- **Acervo:** `/home/elder/.hermes/acervo`
- **Plan directory:** `docs/plans/2026-06-19_acervo-lifecycle-okf/`

## Key Decisions (from ADRs)

- **ADR-013:** Frontmatter schema is a superset of OKF v0.1. OKF canonical fields mandatory + Acervo lifecycle extensions.
- **ADR-014:** Binary classification: `perene` (permanent) vs `volátil` (transient). Only volátil files can be auto-deprecated.
- **ADR-015:** Quarantine is a 3-phase lifecycle: scan → quarantine (30-day window) → purge. No direct deletion.
- **ADR-016:** Semantic revision on insert detects contradictions and deprecates the old file. Conservative: flag ambiguity, don't deprecate.
- **ADR-017:** Acervo is OKF-conformant by design (superset strategy). No export tool needed for conformance.
- **ADR-018:** Syndic is autonomous under `manut` profile. No Draft-First for quarantine/purge. 30-day window is the safety net.

## Existing Acervo Structure

```
$ACERVO/ = /home/elder/.hermes/acervo
├── macro/          # Identity (SOUL.md, valores, estilo)
├── global/         # Universal (branding, context, contracts, decisions, knowledge, persona, prompts, raw, reflections, skills, templates, tools, workflows, _meta, _archive)
├── micro/          # 10 microversos: comercial, ensino, estudio-criativo, excrtx, exocortex-dev, exocortex-ops, gabinete, hermes-setup, projeto-alpha, sales-ai, _template
├── shared/         # Cross-domain
├── _artifacts/
├── _inbox/
├── _routines/
├── _tasks/
└── _automations/
```

## Existing Frontmatter Pattern (pre-migration)

```yaml
---
title: Some Title
created: 2026-06-11
updated: 2026-06-11
nature: decisions
type: fact
tags: [dev, exocortex]
confidence: high
---
```

**Missing fields after migration:** `type` (OKF concept type, not the old `type: fact`), `description`, `timestamp`, `class`, `created_at`, `last_accessed_at`.

**Note:** The existing `type` field (e.g., `type: fact`) is NOT the OKF `type` field. The OKF `type` is the concept type (`decision`, `memory`, `reflection`, etc.). The old `type` field collides with OKF `type` and must be renamed to `excrtx_type` during migration to avoid collision.

## Skill Judge System

- Script: `scripts/skill_judge.py`
- D1 (structural): deterministic, no LLM
- D2–D5 (clarity, alignment, fitness, economy): LLM judge
- Verdicts: `PASS` (all best), `IMPROVE` (1–2 middle), `REWRITE` (any worst)
- **Skills must reach `PASS` before promotion to bundle**
- After promoting: run `python3 scripts/compile_soul.py`

## Agent Log

<!-- Append your findings here after completing tasks. Format: -->
<!-- ### YYYY-MM-DD — Agent (Task XX) -->
<!-- - Finding 1 -->
<!-- - Finding 2 -->

### 2026-06-19 — Exocórtex Orchestrator (Plan Creation)
- Created plan structure with 6 ADRs, 9 task files, this memory file, and PROGRESS.md
- ADRs cover: frontmatter schema (013), deprecation policy (014), quarantine lifecycle (015), semantic revision (016), OKF compatibility (017), autonomous syndic (018)
- Existing `type` field in frontmatter collides with OKF `type` — migration must rename old `type` to `excrtx_type`
- Acervo has 10 microversos + global natures to migrate
- Skill judge system is in place (`scripts/skill_judge.py`) — all 3 new skills must pass D1–D5

### 2026-06-19 — Sub-agent-01 (Task 01: Schema Spec)
- Created `docs/plans/2026-06-19_acervo-lifecycle-okf/schema-spec.md` (515 lines, 28.7 KB)
- Documented all fields across 6 categories: OKF canonical (5), Acervo extension (4), deprecation (3), quarantine (3), legacy retained (4), OKF optional (1)
- Provided 4 complete examples: volatile knowledge, deprecated memory, promoted artifact, quarantined file
- Documented migration rules for all legacy fields including the critical `type`→`excrtx_type` rename and `created`→`timestamp`+`created_at` split
- Defined derivation logic for: OKF `type` (from directory/nature mapping), `class` (from directory), `description` (from body), `timestamp`/`created_at` (from `created` field → git log → file mtime → run date)
- Defined 49 validation rules (41 ERROR + 8 WARN), each with deterministic ID (V-001 through V-076)
- Key finding: real-world `nature` values are mixed English/Portuguese (e.g., `conhecimento`, `reflexoes`, `ferramentas`) — documented PT equivalents in the type derivation table
- Key finding: old `type` values in the wild include `fact`, `rule`, `workflow`, `tool`, `profile`, `lesson`, `context`, `project`, `domain`, `role`, `prompt` — all preserved verbatim in `excrtx_type` during migration
- Added mutual exclusion rule (V-071): a file cannot be simultaneously deprecated and quarantined
- Added cross-field consistency rule (V-070): `timestamp` (date-only) must equal date portion of `created_at`
