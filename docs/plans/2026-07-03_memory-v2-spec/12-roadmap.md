# 12 — Implementation Roadmap

> Phases are cumulative and independently shippable; each ends with its own verification (EX-49). Effort in agent-sessions (one focused Hermes/Claude session ≈ half a day). Order matters: repairs before schema, schema before pipelines, pipelines before intelligence.

## Phase 0 — Repair & baseline *(effort: 1–2 sessions · risk: low)*

Fix the §3-of-01 drift list. No design changes.

- Create missing dirs (installer + live): `.quarantine/`, `global/tools/state/`, `_inbox/`.
- Fix validator WARN tier (make V-004/022/025/026/072/075 actually WARN); align SCHEMA.md counts.
- Delete/merge `macro/soul.md` vs `SOUL.md` (keep `SOUL.md` constitution; boot ritual updated); single `shared/groups` source; purge dead slugs; populate `microversos.yaml` from disk.
- Fix dead references (memory-manager `references/`, README ADR links); extract lifecycle constants (90/180/30) to one contract file.
- Run `validate_frontmatter.py --dir acervo` clean; record baseline metrics (file counts, index entries, MEMORY.md usage).
- **Test:** validator exit 0; `acervo_hindsight_index.py report` zero errors.

## Phase 1 — Schema v0.2 + catalog *(effort: 3–4 sessions · risk: medium — touches every file)*

- Write `SCHEMA-v0.2.md` (from 13-artifacts) as canonical; ADR-023 accepted.
- `migrate_frontmatter.py` v2: derive `status`, default `epistemic` by type, `schema: acervo/v0.2`; idempotent; dry-run first.
- Validator v0.2: new fields, enum `type` (14 values), dir↔type match, real WARN tier, structured `supersedes` paths must exist.
- `catalog.sqlite` builder (extend indexer scan): objects + links + FTS5; `acervoctl reindex` + `acervoctl doctor` (drift/broken links/orphans).
- **Test:** migrate fixture + live acervo dry-run; catalog row count == file count; `doctor` clean.

## Phase 2 — Safe ingestion & write pipeline *(effort: 3–4 sessions · risk: medium)*

- `_inbox/` triage flow live (rtn_inbox_triage upgraded from report-only to propose+commit-on-approval).
- Trust gate + risk gate in memory-manager/acervoctl (draft status path).
- Conflict protocol verbs (supersede/dispute/coexist) replacing deprecate-only; `conflict` objects; digest surface for open disputes.
- New object types write-ready: `episode`, `entity` (+ `shared/entities/` registry + alias check), `intention`.
- **Test:** fixture scenarios — untrusted web content stays draft; price change auto-supersedes; contradicting contract creates dispute; intention appears in briefing.

## Phase 3 — Hybrid retrieval *(effort: 2–3 sessions · risk: low)*

- `retrieve_context`/`pack_context` per 07 in acervoctl + memory-manager; routing table; budgets; U-curve packing; pointer-stub degradation; staleness flags; citation format.
- Degradation ladder + rung logging.
- **Run H2 experiment** (3-way golden set) before tuning weights.
- **Test:** golden set ≥ targets on fixture; fallback run with Hindsight stopped.

## Phase 4 — Consolidation & lifecycle v2 *(effort: 3 sessions · risk: medium — background writes)*

- Episode distillation daily job (significance gate H9); entity refresh; intentions sweep; dedup audit; `review_after` sweep.
- Syndic keeps quarantine/purge; gains consolidation steps + use-decay signal (H12 logging starts).
- Weekly maintenance digest (09 §3) assembled and delivered via Telegram.
- **Test:** seeded session → episode + intention + entity line next morning; digest arrives; all writes journaled + git-diffable.

## Phase 5 — Graph & ontology (conditional) *(effort: 2 sessions · risk: low)*

- Only if H4 metric triggers: PPR-lite traversal over catalog links for multi-hop.
- Entity dedup/merge tooling; quarterly vocabulary review ritual (H11).
- **Test:** multi-hop golden categories.

## Phase 6 — Evaluation & self-improvement *(effort: 2–3 sessions · risk: low)*

- Build `tests/memory-eval/` (fixture + golden + runner) — note: fixture is needed *earlier* for Phase 2/3 tests; build fixture in Phase 1, full harness here.
- CI gate in installer; monthly live run cron; metrics filed as acervo knowledge.
- H7 (auto-commit audit), H12 (usefulness loop) begin reporting.
- **Test:** the harness itself runs in CI and blocks a deliberately-broken retrieval PR.

## Phase 7 — Advanced human/agent interface *(effort: 2 sessions · risk: low)*

- Briefing v2 (intentions+episodes+disputes); modo decisão / modo pesquisa postures; temporal queries surfaced in Telegram ("o que acreditávamos em março?").
- Docs for the executive (1-page, PT-BR: "como sua memória funciona").
- **Test:** golden conversational scenarios via `hermes chat -q`.

## Dependencies & cut criteria

```
P0 → P1 → P2 → P3 → P4 → P6 → P7
              (P5 conditional on H4, anytime after P3)
```

Cut criteria (what "done enough to stop" means): after **P3** the system already answers better than v1 (measured); after **P4** it maintains itself; **P6** makes claims about it honest. P5/P7 are quality-of-life. If effort must be cut, cut P5 first, then P7 — never P6: an unmeasured memory system is a story, not a system.

## Migration safety

Every phase: branch + dry-run on fixture → live acervo backup (`.mvpkg` export or git tag) → apply → `doctor` + eval → journal entry in `micro/exocortex-ops/`. Rollback = git revert + reindex (possible precisely because Plane 2 is derived — P1 pays for itself here).
