# 01 — Phase 0: Current-System Diagnosis

> **Spec:** Exocórtex Memory System v2 · **Date:** 2026-07-03 · **Status:** Complete (verified against installer @ `chore/acervo-sanitization-docbrain-sync` and live runtime at `~/.hermes` + `~/exocortex`)

This is the honest baseline. Everything below was verified on disk, not assumed.

---

## 1. What exists today (and works)

The current architecture is **substantially better than most agent-memory systems in production**. Credit where due:

| Component | State | Evidence |
|---|---|---|
| 4-layer Acervo (`macro/global/micro/shared`) | Working | Live at `~/exocortex/acervo`, 5 physical microversos |
| OKF v0.1 frontmatter schema | Canonical, validated | `docs/plans/2026-06-19_acervo-lifecycle-okf/SCHEMA.md`, ~50 rules in `scripts/validate_frontmatter.py` |
| Lifecycle (`perene`/`volátil` → deprecate → quarantine 30d → purge) | Specified + skills implemented | ADR-014/015/018; `excrtx-memory-{deprecate,quarantine,syndic}` |
| Memory routing model | Accepted + live | ADR-019/020/021; `memory-routing-contract.md`; Hindsight in `memory_mode: tools`, `auto_recall: false` |
| AcervoIndex (Hindsight = pointer index, never copy) | Implemented | `acervo_hindsight_index.py`; daily reconcile cron `acervo-index-reconcile` |
| Fast-memory budgets | Enforced by runtime | `MEMORY.md` ≤ 2 200 chars (currently 592), `USER.md` ≤ 1 375 (write-gated by `memory` tool) |
| Semantic control plane | Implemented | `acervoctl.py` prepare/commit + `acervo_mcp_server.py` (ADR-022-dev) |
| Write pipeline | Implemented in skill | Domain Filter → runtime scope guard → frontmatter → semantic revision → log → index → Hindsight hook |

The June 2026 reform ("memory excellence") landed its central insight, which v2 **preserves as axiom**:

> *Hindsight aponta. Acervo decide. `MEMORY.md` só inicializa.*

## 2. Conceptual defects (design level)

These are not bugs; they are places where the model itself is too weak for a ten-year system.

**D1 — Triple classification (`type` / `excrtx_type` / `nature`).** Every file carries up to three overlapping type axes. `type` (6 OKF values) and `nature` (11 dirs, EN + PT vocabularies, no enum validation) answer different questions badly; `excrtx_type` is a frozen migration artifact. SCHEMA.md itself predicts consolidation ("A future ADR may consolidate `nature` into `type`"). Cost: every writer must decide three fields; every retriever must reconcile them.

**D2 — No temporal model of truth.** The schema records *transaction* time (`created_at`, `deprecated_at`) but not *valid* time. "In March we believed X; in May we discovered Y" cannot be represented — only destructive supersedence (`deprecated: true` + prose reason). There is no `valid_from`/`valid_until`/`observed_at`, no structured `supersedes`/`superseded_by` (only a free-text convention inside `deprecated_reason`), and therefore no safe way for an LLM to distinguish past belief from current truth except by reading prose.

**D3 — No epistemic status.** `confidence: low|medium|high` exists, but the system cannot distinguish **fact / interpretation / hypothesis / decision / preference / rule / intention**. A hunch and a signed contract carry the same metadata weight. This is the single largest source of potential "manufactured coherence": retrieval flattens epistemic diversity into uniform-looking context.

**D4 — Episodes are homeless.** Conversations live in `state.db` (literal, via `session_search`) and as Hindsight auto-retained observations (every 2 turns, lossy, unaudited). There is no consolidation step that turns a significant session into a canonical, citable **episode** in the Acervo. Consequence: "where did we leave off", "what happened in the meeting with X" depends on a non-canonical, non-auditable store — precisely what ADR-019 said must not happen.

**D5 — Contradiction is only destructive.** `excrtx-memory-deprecate` handles *replacement* (new fact supersedes old volatile fact). It cannot represent *live disagreement* (two sources say different things; both matter), and it flags ambiguity to a log no one is required to read. Contradiction needs to be a first-class, queryable state — not an edge case of deprecation.

**D6 — Entities don't exist.** People, companies, products appear only as free-text tags. No entity registry, no aliasing (Guimarães / GPQ / "a empresa"), no entity-first retrieval. Relational memory (who is who, who prefers what, interaction history) — the thing an executive asks about most — has no home other than prose in `context/`.

**D7 — `shared/` is underspecified and already inconsistent.** Two `groups.md` files with different taxonomies (perene DOMAINS/PROJECTS/ROLES/CRIACAO vs volátil CLIENTS/PROJECTS); groups reference microversos that don't exist (`sales-ai`, `gabinete`, `cliente-alfa`); cross-refs template still carries pre-OKF frontmatter in `shared/_meta/SCHEMA.md`. The bridge layer — the answer to "how do domains coexist" — is the least governed part of the system.

**D8 — Prospective memory is absent.** Commitments, deadlines, "remind me", open loops: split between kanban.db, cron jobs, and prose. Nothing in the Acervo models an *intention with a due condition*, so the briefing workflow reconstructs pendências heuristically each time.

**D9 — docBrain is an undecided second brain.** A second Markdown KB with its own raw layer, provenance model, wiki, and linter coexists with the Acervo. `excrtx-adapter-docbrain-acervo` bridges outputs, but no decision says which system owns ingested external documents. Two canonical stores = eventual divergence.

## 3. Implementation drift (spec ≠ code ≠ disk)

Verified discrepancies that v2's Phase 1 must fix regardless of any redesign:

1. **Validator severity is binary.** `schema-spec.md` defines V-004/022/025/026/072/075 as WARN; `validate_frontmatter.py` emits *everything* as ERROR (the WARN print branch is dead code). Docs promise "41 ERROR + 8 WARN"; code fails on all.
2. **Missing physical infrastructure.** `.quarantine/`, `global/tools/state/` (Hindsight manifest home), `_inbox/`, `_tasks/`, `_routines/`, `_automations/` are referenced across CLAUDE.md/README/skills/validator exclusions but **do not exist** in the installer's acervo (live acervo has `.quarantine/` only).
3. **`soul.md` vs `SOUL.md` vs `SOUL_SEED.md`.** `macro/` ships both `SOUL.md` (constitution, referenced by CLAUDE.md) and `soul.md` (boot-loaded by memory-manager). Plus the repo-root compiled `SOUL_SEED.md`. Three "souls", two casings, validator excludes `macro/` so nothing checks them.
4. **Registry drift.** `global/_meta/microversos.yaml` says `installed: []` while 5 microversos exist on disk (created by template-copy, not mvinstall). The append-only registry records a fiction.
5. **Indexer vs ADR-020.** ADR says deprecated entries "não entram no índice"; the indexer transmits them with `status: deprecated` + `superseded_by`. (The implementation is actually *better* than the ADR — recall should know a thing is dead — but the spec must say so.)
6. **11 natures vs 7 indexable.** `prompts/`, `persona/`, `skills/`, `templates/` are never semantically indexed; nowhere reconciled with the "11 Natures" framing.
7. **Undocumented fields in the wild.** `kind`, `scope_mode`, `scope_slug`, `authority`, `status`, `canonical_from`, `updated`, `from/to/subject/created` appear in real files, absent from SCHEMA.md, ignored by the validator.
8. **Dead references.** `excrtx-memory-manager` cites `references/acervo-control-plane-cli.md` (dir absent); `acervo/README.md` links ADR-001..005 to an out-of-tree path (`../projetos/pessoal/exocortex.saas/...`); ADR-001..005 exist nowhere as files.
9. **Duplicated lifecycle constants.** The 90/180/30-day thresholds are restated in three skills (manager, syndic, quarantine) — no single source.
10. **Stale meta.** `acervo/README.md` is itself `volátil`, unread since 2026-05-27, and documents pre-OKF cross-ref frontmatter.

## 4. Runtime constraints v2 must respect (verified)

1. **Tools-first context.** Nothing enters the prompt automatically except SOUL, `MEMORY.md`/`USER.md`, and boot-loaded Acervo indexes. All recall is explicit tool calls (`hindsight_recall/reflect`, `session_search`, Acervo reads).
2. **Hard budgets.** MEMORY.md 2 200 chars / USER.md 1 375 chars (all-or-nothing write gate); Hindsight recall capped (`recall_max_tokens: 1200`, budget `low`).
3. **Fixed authority ladder.** SOUL > contratos > Acervo > session_search > Hindsight > fast memory. Providers never canonicalize.
4. **Fixed tool surface.** `memory(add|replace|remove)`, `hindsight_retain/recall/reflect`, `session_search`, `acervo` MCP / `acervoctl`, skills. Redesign works through these, not around them.
5. **Storage reality.** Acervo = Markdown; Hindsight = Dockerized Postgres on `localhost:8888` (has been down; anything critical must degrade gracefully to filesystem search); sessions = SQLite `state.db`; kanban = SQLite.
6. **Governance gates.** Draft-First for external actions and provider changes; lifecycle deletion only via deprecate → quarantine → purge; semantic mutations via `acervoctl`/MCP.
7. **Cadence.** Auto-retain every 2 turns (async), nudge every 10, compression at 0.7 context use, syndic weekly, index-reconcile daily.

## 5. What the reform left open (from the live progress file)

`micro/exocortex-ops/context/memory-excellence-progress.md` status: `installer-provisioned`. Open items: Fase 8 (evaluation battery) never ran; write-hook and reconcile-cron never validated against a live Hindsight (blocked on server + LLM credential); recall-quality metrics (irrelevance < 20%) unmeasured.

## 6. Verdict

**Preserve:** Markdown-first canonical truth; 4 layers; pointer-index doctrine (ADR-020); tools-first recall (ADR-019); fast-layer budget (ADR-021); lifecycle non-deletion; Draft-First; the control-plane direction (acervoctl/MCP).

**Redesign:** the object model (one type axis, temporal validity, epistemic status, structured supersedence); episodes and consolidation; entities and relational memory; `shared/`; prospective memory; contradiction as state; the microverso manifest (type/status/sharing policy).

**Repair:** the ten drift items in §3 — they are cheap, and every one of them erodes the trust the whole system depends on.

The remaining documents of this spec define the target system.
