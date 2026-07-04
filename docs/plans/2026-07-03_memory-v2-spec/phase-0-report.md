# Phase 0 — Execution Report

> **Executed:** 2026-07-04 · **Scope:** installer only (live instance read-only, per agreed boundary) · **Status:** ✅ complete
> Reference: [12-roadmap.md](12-roadmap.md) Phase 0 · Drift list: [01-diagnosis.md](01-diagnosis.md) §3

## Repairs applied (drift item → fix)

| # | Drift item (01 §3) | Fix |
|---|---|---|
| 1 | Validator severity binary (all ERROR) | V-004/022/025/026/072/075 now emit **WARN** (per schema-spec per-rule tables); exit 0 with WARN-only. SCHEMA.md §4 corrected to the real counts: **43 ERROR + 6 WARN (49 rules)**. New test `tests/test_validate_frontmatter_severity.py` (3 tests) |
| 2 | Missing infra dirs | Created `acervo/.quarantine/` (README + `.purge_log`), `acervo/_inbox/` (README + `.gitkeep`), `acervo/global/tools/state/` (README + `.gitkeep`). `.gitignore` fixed: was ignoring all of `state/`, now only `state/*.json` |
| 3 | `soul.md` vs `SOUL.md` | Unique identity-skeleton content merged into `macro/SOUL.md` ("Estrutura da Identidade Raiz"); lowercase `soul.md` **deleted**; 10 references updated (memory-manager boot ritual, README, FEATURES.md EX-01, behavior-canvas, calibrate-hermes.py — dead fallback removed, sync-repairs, validator comment, roadmap, audit findings note). `_fixture/` untouched |
| 4 | Registry drift (`installed: []`) | `global/_meta/microversos.yaml` populated with the 5 physical microversos (comercial, estudio-criativo, excrtx, exocortex-dev, exocortex-ops), format matching `microverso_install.py::register()` exactly; digests = sha256 of each manifest (documented deviation: manifests lack `provenance.content_digest`) |
| 7 | Two conflicting `groups.md` | `shared/groups.md` = single canonical source ("5 microversos ativos"; dead slugs `sales-ai`/`gabinete` removed with reintroduction note); `shared/knowledge/groups.md` deprecated per convention (`deprecated: true` + reason); `shared/_meta/index.md`/`log.md` updated |
| 8 | Dead references | `skills/excrtx-memory-manager/references/acervo-control-plane-cli.md` **created** from `acervoctl.py`'s real argparse (6 verbs, prepare/commit flow, ADR-022 pointer); README's 5 dead out-of-tree ADR-001..005 links → plain-text historical notes |
| 9 | Lifecycle constants ×3 | `acervo/global/contracts/memory-lifecycle-constants.md` created (7 constants: 90/180/30 days, ~150/~200 lines, 2200/1375 chars, with used-by + source ADRs); the 3 skills now reference it (+1 line each; `compiled_rules` untouched) |

Items 5 (indexer vs ADR-020 nuance), 6 (11 vs 7 natures), 10 (stale acervo README rewrite) are **spec-level** reconciliations — addressed by the v2 documents themselves, scheduled with Phase 1 (they change canon, not drift).

## Verification (raw outputs)

```
$ python3 scripts/validate_frontmatter.py --dir acervo
... all files PASS ... exit=0            # 164 validated, 41 skipped (excluded dirs)

$ python3 -m pytest tests/test_validate_frontmatter.py \
    tests/test_validate_frontmatter_severity.py tests/test_migrate_frontmatter.py -q
29 passed in 2.14s

Full suite: 311 passed, 20 failed, 1 skipped — all 20 failures pre-existing and
unrelated (live-network/env-dependent: last30days, reclameaqui, setup smokes);
zero failures in validator/migration/severity tests.
```

## Baseline captured (2026-07-04, live instance read-only)

| Metric | Value |
|---|---|
| Installer acervo .md files | 200 (macro 4 · global 21 · micro 149 · shared 7) |
| Live acervo .md files | 278 (macro 11 · global 36 · micro 224 · shared 7) |
| Live `.quarantine/` | 0 files |
| **`MEMORY.md` usage (live)** | **2 220 / 2 200 chars = 100% — OVER budget** (ADR-021 target 35–50%; was 592 after the June reform → regressed) |
| `USER.md` usage (live) | 1 028 / 1 375 = 74% (target 50–70%; slightly over) |
| AcervoIndex manifest (live) | 6 entries · last scan 2026-07-02T04:51:30Z (progress file claimed 20 → drifted) |
| Hindsight (live) | **UP** — `{"status":"healthy","database":"connected"}` on :8888 |
| Live acervo git-versioned? | **NO** — `~/exocortex` is not a git repo (risk flagged for any live migration) |

## Follow-ups surfaced (live instance — gated, need explicit go)

1. **MEMORY.md re-consolidation** (100% of budget; ADR-021 Fase-3 procedure re-run).
2. **`git init` no acervo vivo** before any Phase 1 migration touches it.
3. AcervoIndex re-scan (6 entries vs 198+ indexable; Hindsight is up now, unblocking the never-validated write-hook/reconcile tests).
