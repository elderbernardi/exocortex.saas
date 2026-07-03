# 04 — Proposed Architecture

> The v2 architecture is an evolution of ADR-019/020/021, not a replacement: same authority ladder, same pointer-index doctrine, same budgets. What changes: a unified object model (05), an explicit index plane, episodes/entities/intentions as first-class stores, and a consolidation loop.

## 1. The four planes

```text
┌────────────────────────────────────────────────────────────────────┐
│ PLANE 0 · BOOTSTRAP (always in prompt, hard-budgeted)              │
│   SOUL.md · USER.md (≤1375c) · MEMORY.md (≤2200c)                  │
│   macro/ constitution · global/_meta/index.md                      │
├────────────────────────────────────────────────────────────────────┤
│ PLANE 1 · CANONICAL TRUTH (Markdown, git-versioned, human-first)   │
│   acervo/                                                          │
│     macro/           constitution, values, style                   │
│     global/          universal rules, contracts, tools, workflows  │
│     micro/{slug}/    microversos (see 06)                          │
│     shared/          bridges: groups, entities, cross-refs,        │
│                      glossary                                      │
│     _inbox/          ingestion queue (pre-memory)                  │
│     _artifacts/      produced documents                            │
│     .quarantine/     lifecycle exit lane                           │
├────────────────────────────────────────────────────────────────────┤
│ PLANE 2 · DERIVED INDEXES (rebuildable; never authoritative)       │
│   catalog.sqlite     frontmatter of every object + links + FTS5    │
│   Hindsight          AcervoIndex pointers + operational obs.       │
│   _meta/index.md     per-container MOC (generated)                 │
│   entity adjacency   derived from entities:/[[wikilinks]]          │
├────────────────────────────────────────────────────────────────────┤
│ PLANE 3 · EVIDENCE (immutable; queried, never trusted as belief)   │
│   raw/ per microverso · session state.db (session_search)          │
│   _inbox originals · git history · _meta/log.md journals           │
└────────────────────────────────────────────────────────────────────┘
```

Authority (unchanged from ADR-019): `SOUL > contracts > Acervo canonical > session_search (literal) > Hindsight > fast memory`. Planes 2–3 never override Plane 1.

Research grounding (02-research-map.md): verbatim-canonical + extracted-index is the pattern both first-party labs converged on (Anthropic memory tool / Claude Code MEMORY.md; Letta memory blocks), and plain-file agents *beat* extraction pipelines on accuracy at personal scale (Letta filesystem-agent benchmark). Extraction pipelines measured inside show <60% recall (HaluMem) — which is why Plane 2 is disposable and Plane 1/3 keep everything.

## 2. Storage decision (question B)

| Alternative | Verdict | Why |
|---|---|---|
| 1. Markdown + frontmatter | **Canonical (keep)** | Human-auditable, git-versioned, survives tooling death, agent-editable with plain tools. Weak at queries/aggregation → covered by ③ |
| 2. Relational DB as truth | Rejected | Black box for the executive; schema migrations become truth migrations; loses git |
| 3. Graph DB as truth | Rejected | Highest maintenance, lowest auditability; personal-scale gains achievable with wikilinks + derived adjacency (HippoRAG-2/LazyGraphRAG lesson: cheap graphs win) |
| 4. Vector DB as truth | Rejected | Embeddings are a cache of meaning, not meaning. Model upgrades force re-embedding — fatal for a canonical store |
| 5. Append-only event log as truth | Rejected as primary | Perfect audit, terrible operational reads; humans don't think in logs. Kept as journal (Plane 3) |
| 6. **Hybrid: FS + SQLite catalog + vector + light graph** | **Adopted as derived plane** | Each engine does what it's good at; all rebuildable from ① |
| 7. Agent-managed KB (opaque) | Rejected | Violates P1/P10 |

**catalog.sqlite** (new, Phase 1): one row per object (all frontmatter fields + path + hash + mtime), `links(from,to,kind)` (wikilinks, supersedes, disputes, entity mentions), FTS5 over title/description/body. Built by extending the existing indexer scan; enables metadata queries (`status=active AND microverso=comercial AND type=decision`), link integrity checks, and the grep-independent fallback when Hindsight is down. It is a cache: `rm catalog.sqlite && acervoctl reindex` must always work.

**Hindsight** stays exactly per ADR-020 (pointers + summaries, `document_id=acervo:{path}`, `update_mode=replace`) and additionally receives episodes' summaries (§4). Its own auto-retained observations remain Plane 3 evidence: useful for recall, never citable as truth.

## 3. Write path (one pipeline, three surfaces)

All mutations converge on the same pipeline regardless of surface (`acervoctl` CLI, `acervo` MCP, `excrtx-memory-manager` skill):

```text
candidate
  → resolve_scope            (layer + microverso; hard-fail if ambiguous)
  → classify                 (type, class, epistemic, sensitivity)
  → trust gate               (untrusted-source? → propose, never auto-commit)
  → risk gate                (macro/global/contracts/decisions → DRAFT;
                              micro volatile → governed auto-commit)
  → detect_conflict          (supersede | dispute | coexist — see 08)
  → write canonical file     (schema v0.2 frontmatter)
  → journal                  (_meta/log.md + event line)
  → derived-index hooks      (catalog upsert → index.md regen → Hindsight
                              index-file; each best-effort, drift caught
                              by daily reconcile)
```

The **trust gate** is new and non-negotiable: content originating from fetched web pages, inbound email, or third-party documents may only *propose* memory (lands as `status: draft` in `_inbox/` triage), because persisted prompt-injection is a documented attack class (SpAIware, AgentPoison). Only executive-originated or agent-verified content auto-commits.

## 4. The consolidation loop (new)

Currently the syndic only *removes* (quarantine/purge). v2 adds the complementary process — **consolidation** — as a scheduled background pass (`manut` profile, after the daily index-reconcile), mirroring what Letta calls sleep-time compute and OpenAI calls Dreaming, but with git-auditable output instead of opaque rewrites:

1. **Episode distillation** — significant sessions (decision made, commitment made, artifact delivered, or executive-flagged) become `episodes/` objects: summary, participants (entities), decisions extracted, open loops, `session://` pointer. Transcript stays in state.db.
2. **Claim reconciliation** — new volatile knowledge vs existing: supersede/dispute/coexist backlog that write-time flagged as ambiguous.
3. **Entity refresh** — new mentions accrue to entity pages (aliases, last-interaction, open commitments).
4. **Summary refresh** — regenerate `_meta/index.md` MOCs and any `summary:` fields whose source hash changed.
5. **Decay sweep** — existing syndic rules (stale volatile → quarantine) unchanged.

Everything consolidation writes is a normal governed write (same pipeline, journaled, git-diffable) — preserving the audit trail that OpenAI's Dreaming was criticized for losing.

## 5. Read path

Defined fully in 07-retrieval-policy.md. Skeleton:

```text
task → classify vector (execução/evolução/manutenção)
     → resolve_scope
     → route: entity? temporal? literal? semantic? procedural?
     → candidates: catalog filter ∩ (hindsight_recall ∥ FTS5 ∥ grep)
     → rank: scope-match > authority > validity > recency > similarity
     → read 1–5 canonical files (Plane 1)
     → pack to budget with citations + epistemic labels
```

Degradation ladder: Hindsight down → catalog FTS5 → ripgrep over acervo. Each step logs which ladder rung answered (observability for the eval battery).

## 6. Security & sensitivity

- Microverso isolation = cognitive boundary by default (P6); microversos may declare `sensitivity: restricted` in `microverso.yaml` → their content never enters cross-scope retrieval or briefings without explicit executive request, and never leaves in artifacts.
- Secrets never enter any plane (existing rule; enforced by a validator pattern check for common secret shapes at the trust gate).
- All cross-scope reads journaled (`SCOPE-CROSS` event) — contamination becomes measurable (10-evaluation.md).

## 7. Versioning

- Objects: git history is the version store; `schema: acervo/v0.2` in frontmatter versions the contract; migrations are scripts (`scripts/migrate_frontmatter.py` pattern) + an ADR each.
- Indexes: `catalog.sqlite` carries `schema_version` pragma; rebuilt on mismatch.
- The spec itself: this plan dir; adopted via ADR-023.

## 8. Component inventory (delta from v1)

| Component | Status in v2 |
|---|---|
| `excrtx-memory-manager` | Updated: v0.2 schema, trust gate, conflict verbs, episode/entity/intention ops |
| `excrtx-memory-deprecate` | Renamed conceptually → conflict handler: supersede/dispute/coexist |
| `excrtx-memory-quarantine`, `-syndic` | Unchanged mechanics; syndic gains consolidation steps |
| `acervo_hindsight_index.py` | Extended: also writes catalog.sqlite; indexes episodes/entities |
| `validate_frontmatter.py` | v0.2 rules; real WARN tier; enum for nature; link integrity via catalog |
| `acervoctl` / `acervo` MCP | Gains: `resolve-scope`, `conflict`, `episode`, `entity`, `intent`, `reindex`, `doctor` |
| NEW `catalog.sqlite` builder | Phase 1 |
| NEW consolidation routine | Phase 4 |
| NEW eval battery | Phase 6 (`tests/memory-eval/`) |
| docBrain | Demoted to ingestion engine: its wiki = working area; promotion to Acervo via existing adapter is the only canonical path (ends the two-brains ambiguity) |
