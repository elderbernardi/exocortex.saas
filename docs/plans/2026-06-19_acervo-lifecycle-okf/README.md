# Implementation Plan: Acervo Cognitivo Lifecycle, Deprecation & OKF Alignment

**Status:** Draft (pending executive approval)
**Created:** 2026-06-19
**Priority:** P0
**GitHub Issue:** (to be created upon approval)

---

## Purpose

This plan defines a complete, agent-readable implementation of knowledge lifecycle management for the Exocórtex Acervo Cognitivo. It covers: frontmatter standardization aligned to the Open Knowledge Format (OKF v0.1), semantic deprecation, quarantine-based cleanup with autonomous syndic operation, and migration of canonical microversos.

**Every artifact in this plan is written in English** so that sub-agents (any LLM, any model) can read, understand, and execute tasks without language ambiguity. Skills produced under this plan must pass the `excrtx-quality-skilljudge` rubric (D1–D5, verdict `PASS`) before promotion.

---

## Problem Statement

The Acervo Cognitivo accumulates knowledge without distinguishing permanent truth from transient state. Five concrete problems:

1. **No timestamps** — files don't record creation or last-access dates; impossible to distinguish current from stale.
2. **No deprecation** — transient facts (model defaults, port numbers, prices) remain active indefinitely.
3. **No semantic conflict resolution** — a new memory that contradicts an older one coexists without signaling; the agent may retrieve the wrong version.
4. **No periodic cleanup** — the acervo grows monotonically; no review cycle to prune, deprecate, or consolidate.
5. **No standardized schema** — frontmatter varies across microversos; not compatible with OKF v0.1.

---

## Solution Architecture (Summary)

| Component | Mechanism | ADR |
|-----------|-----------|-----|
| Frontmatter schema | OKF v0.1 canonical fields + Acervo extensions | ADR-013 |
| Deprecation policy | Binary classification (perene vs. volátil) + semantic revision on insert | ADR-014 |
| Quarantine lifecycle | 3-phase: scan → quarantine → purge; autonomous syndic | ADR-015 |
| Semantic revision on insert | Detect overlap → compare truth → deprecate predecessor | ADR-016 |
| OKF compatibility | Superset of OKF v0.1; canonical fields mandatory | ADR-017 |
| Autonomous syndic | `manut` profile cron job; no Draft-First for quarantine/purge | ADR-018 |

---

## Task Breakdown

Tasks are ordered by dependency. Each task file is self-contained — a sub-agent can read only that file plus the referenced ADRs and execute.

| # | Task | Depends On | Produces | Verification |
|---|------|------------|----------|--------------|
| 01 | Define frontmatter schema spec | ADR-013, ADR-017 | `docs/plans/.../schema-spec.md` | Spec reviewed, fields documented |
| 02 | Define `log.md` convention | ADR-013 | `docs/plans/.../log-convention.md` | Convention documented with examples |
| 03 | Build frontmatter validator script | Task 01 | `scripts/validate_frontmatter.py` | Script runs on sample files, exits 0 on valid, 1 on invalid |
| 04 | Write `excrtx-memory-deprecate` skill | Task 01, ADR-014, ADR-016 | `skills/excrtx-memory-deprecate/SKILL.md` | D1 check passes; full judge verdict = PASS |
| 05 | Write `excrtx-memory-quarantine` skill | Task 01, ADR-015 | `skills/excrtx-memory-quarantine/SKILL.md` | D1 check passes; full judge verdict = PASS |
| 06 | Write `excrtx-memory-syndic` skill | Task 04, Task 05, ADR-018 | `skills/excrtx-memory-syndic/SKILL.md` | D1 check passes; full judge verdict = PASS |
| 07 | Build quarantine directory structure | ADR-015 | `$ACERVO/.quarantine/` + `.purge_log` | Directory exists, purge log initialized |
| 08 | Migrate canonical microversos | Task 01, Task 03 | All microverso files have new frontmatter | Validator passes on 100% of files |
| 09 | Create syndic cron job | Task 06 | Cron entry in Hermes | Cron listed, dry-run produces report |
| 10 | Documentation updates | Task 08, Task 09 | Updated docs across repo | All docs reflect new schema and lifecycle |

---

## Skill Judgment Pipeline

All skills produced under this plan follow this mandatory pipeline:

```
Draft SKILL.md
    ↓
D1 Structural Check (deterministic, no LLM)
    ↓ PASS
D2–D5 LLM Judge (5-dimension rubric)
    ↓ verdict = PASS
Integration test (skill exercised against real acervo files)
    ↓ test passes
Promote to bundle (skill-bundles/exocortex-alpha.yaml)
    ↓
Compile SOUL_SEED.md (python3 scripts/compile_soul.py)
```

**Rules:**
- D1 failing → fix mechanically (Tier 1 remediation), no LLM needed
- Verdict `IMPROVE` → apply judge recommendations, re-run full sweep
- Verdict `REWRITE` → structural rewrite required
- **No skill is promoted without verdict `PASS` + integration test**
- Judge model should differ from authoring model when possible (bias mitigation)

---

## Agent Coordination

Two files govern cross-agent coordination:

| File | Purpose | Updated By |
|------|---------|------------|
| `AGENT_MEMORY.md` | Shared context between agents working on this plan | Every agent that completes a task |
| `PROGRESS.md` | Task status tracker (pending/in_progress/done/blocked) | Agent that starts/completes a task |

**Protocol:**
1. Before starting a task, read `AGENT_MEMORY.md` for accumulated context.
2. Before starting, update `PROGRESS.md` to mark task as `in_progress`.
3. After completing, append findings/decisions to `AGENT_MEMORY.md`.
4. After completing, update `PROGRESS.md` to mark task as `done` with verification evidence.

---

## Reference: OKF v0.1

- [Google Cloud Blog Post](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
- Published 2026-06-12 by Sam McVeety and Amir Hormati
- Core idea: knowledge as directory of markdown + YAML frontmatter; `type` is the only mandatory field; concepts link via normal markdown links
- Three principles: minimally opinionated, producer/consumer independence, format not platform

## Reference: Existing Acervo Skills

- `excrtx-memory-manager` — unified read/write/search/promote across 4 layers
- `excrtx-memory-newmicro` — create new microversos
- `excrtx-memory-mvinstall` — install microverso from template
- `excrtx-quality-skilljudge` — LLM-as-judge for skill quality
- `excrtx-quality-gate` — executor quality gate (prose + visual)
- `excrtx-harness-kanban` — session state and resumption tracking
