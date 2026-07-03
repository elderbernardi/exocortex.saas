# 05 — Memory Object Model & Schema v0.2

## 1. The atomic unit (question A.1)

**The atom is the memory object: one Markdown file asserting one thing about one scope, with typed frontmatter.** Not the chunk (retrieval artifact), not the claim (too granular to sustain — H3), not the document-blob (can't supersede precisely). A well-formed object satisfies the *title-as-API test*: its filename+title alone tell both a human and an agent what it asserts (`preco-tabela-2026-q3.md`, not `notas-reuniao-3.md`).

**Organization (question A.2) is faceted, not hierarchical.** One physical axis + five metadata facets:

| Facet | Carrier | Answers |
|---|---|---|
| **Scope** | directory: `macro/ global/ micro/{slug}/ shared/` | whose universe? (primary axis — matches how the executive thinks: by domain) |
| **Type** | directory-within-scope + `type:` (must match) | what kind of object? |
| **Time** | `created_at` (transaction) / `observed_at`, `valid_from/until` (world) | when true, when learned? |
| **Epistemic** | `epistemic:` + `confidence:` | how do we know, how sure? |
| **Entities** | `entities:` + `[[wikilinks]]` | who/what is involved? |
| **Lifecycle** | `status:` + `class:` | is it current? |

Human domain first (scope), cognitive type second (directory), everything else metadata — humans navigate by domain, agents filter by facet; same files (P10).

## 2. Schema v0.2 (frontmatter)

Supersedes OKF-superset v1.0.0 (ADR-013). Still a valid OKF superset. Three tiers by obligation:

```yaml
---
# ── Tier 0 · identity — MANDATORY on every object (hand-writable in 30s)
schema: acervo/v0.2
type: knowledge          # closed vocab, §3 — replaces the type/excrtx_type/nature triple
title: Tabela de preços 2026-Q3 aprovada com reajuste de 8%
description: Reajuste aprovado em 2026-06-28; vigora o trimestre Q3
tags: [pricing, comercial]
created_at: 2026-07-03T14:00:00Z      # transaction time (git confirms)
class: volátil           # perene | volátil  (lifecycle eligibility, unchanged)
status: active           # draft | active | superseded | deprecated | quarantined | archived

# ── Tier 1 · epistemic — REQUIRED for knowledge/context/decision/reflection/entity
epistemic: fact          # fact|observation|interpretation|hypothesis|decision|preference|rule|intention
confidence: high         # high | likely | possible | low   (Kesselman-style, small on purpose)
sources:                 # provenance (PROV-lite): where + how + who
  - type: conversation   # conversation|email|document|web|agent-inference|executive
    ref: "session://tg-2026-06-28#dec-1"
observed_at: 2026-06-28  # when the world showed this (valid-time anchor)
valid_from: 2026-07-01   # optional; when the fact starts holding
valid_until: 2026-09-30  # optional; null/absent = open-ended
extraction: agent        # executive | agent | pipeline  (who distilled it)

# ── Tier 2 · relations — OPTIONAL everywhere
entities: [gpq, joao-silva]        # slugs resolved via entity registry
supersedes: [knowledge/preco-tabela-2026-q2.md]
superseded_by: null                # set by the write pipeline, never by hand
disputed_by: null                  # path of an open conflict object
relates_to: []                     # soft links (also expressible as [[wikilinks]] in body)
canonical_from: null               # marked duplication (P-rejected-1)
sensitivity: normal                # normal | restricted
review_after: 2026-09-30           # syndic revisit date (replaces pure staleness guessing)

# ── Conditional lifecycle detail (unchanged from v1: deprecation/quarantine fields,
#    last_accessed_at, promoted_at)
---
```

**Deltas from v1.0.0:** ① one `type` axis — `nature` becomes a derived alias of the directory (validator enforces dir↔type match; field optional, auto-filled); `excrtx_type` frozen read-only. ② `status` scalar (retrieval filters on one field instead of inferring from 3 conditional blocks). ③ `superseded ≠ deprecated`: *was true, replaced* vs *wrong/junk*. ④ bitemporal-lite (`observed_at`, `valid_from/until`; git = transaction history). ⑤ epistemic tier. ⑥ structured `supersedes/superseded_by/disputed_by` (v1 had only prose in `deprecated_reason`). ⑦ `timestamp` dropped as authoritative — auto-derived from `created_at` at OKF export time only. ⑧ `sensitivity`, `review_after`, `extraction`. Owner is omitted deliberately: single-subject system; the responsible agent goes in the journal, not every file.

**Migration** is mechanical (script + ADR-023): `status` derives from existing conditional fields; `epistemic` defaults by type (`decision→decision`, `reflection→interpretation`, `knowledge/context→fact` with `confidence` carried over); missing Tier-1 on old files → WARN, not ERROR.

## 3. Object catalog

`type` vocabulary, home directory, and rules. (14 natures; **created lazily** — P9; core-6 marked ●)

| `type` | Home | Function | Granularity | Lifecycle & rules |
|---|---|---|---|---|
| `context` ● | `context/` | Current state of a domain: priorities, stakeholders, "where we are" | One aspect per file; `current-state.md` per microverso is the head page | `volátil` by default. **Rewritten in place** (it models the present); history = git + episodes. Read at scope activation |
| `knowledge` ● | `knowledge/` | Durable facts, concepts, references | One assertion-cluster per file; claim anchors (`^c1`) optional where disputes are likely | Supersede on change (never edit a fact into a different fact); `valid_*` required for anything priced/dated/versioned |
| `decision` ● | `decisions/` | Decisions with rationale + rejected alternatives | One decision per file (ADR discipline) | **Immutable once `status: active`.** Change = new decision + `supersedes`. Never auto-deprecated (perene by default). Body sections: Contexto/Decisão/Alternativas rejeitadas/Consequências/Revisão |
| `episode` ● NEW | `episodes/` | What happened: meetings, significant sessions, trips, negotiations | One event per file, `YYYY-MM-DD-slug.md` | Written by consolidation (04 §4) or on request; immutable after review window; carries `entities`, decisions extracted, open loops, `session://` pointer. Verbatim stays in Plane 3 |
| `entity` NEW | `shared/entities/` (registry) + `micro/*/entities/` (domain detail) | People, orgs, products: who they are, aliases, relationship, interaction history | One file per entity — the canonical ID; `aliases:` mandatory | Living document: profile section rewritten, interaction log **append-only** (journal+projection in one file). Check-aliases-before-create duty; merge = one absorbs, other becomes alias stub |
| `intention` NEW | `intentions/` | Prospective memory: commitments, promises, follow-ups with due/trigger | One commitment per file | `status: active → done|dropped|expired`; fields `due:`, `trigger:`, `owed_to:` (entity). Kanban stays the execution board; intentions are the canonical commitments the briefing reads. Done intentions archive, never delete (they're relationship history) |
| `workflow` ● | `workflows/` | Procedures, SOPs, routines | One procedure per file | Versioned in place while `draft`; supersede once `active`. Promotion path to Hermes skill when automated |
| `contract` | `contracts/` | Binding rules: "always X", "never Y", conditional policies | One rule-set per scope-topic | Perene; changes require executive approval (Draft-First); highest Acervo authority |
| `reflection` ● | `reflections/` | Lessons, patterns, after-action reviews | One insight per file | `epistemic: interpretation` forced; promotion path: reflection → contract/workflow when confirmed (with executive) |
| `persona` | `persona/` | Voice/tone per domain | Small; one voice per microverso | Perene-ish; style examples verbatim (P8) |
| `prompt` / `template` / `tool` / `skill` | respective dirs | Reusable operational assets | asset-sized | Procedural memory; versioned in place; not semantically indexed by default (matches current 7-nature index scope + episodes/entities/intentions added) |
| `artifact` | `_artifacts/` | Produced deliverables | whole documents | Immutable outputs + manifest; promotion to knowledge/decision explicit |
| `conflict` NEW | `knowledge/` (with `type: conflict`) | A live contradiction, first-class | One dispute per file: claim A + claim B, each with source/date/confidence | `status: active` (open) → `superseded` (resolved → becomes/links a decision). Both disputants carry `disputed_by:` → retrieval attaches the dispute banner (P5) |
| `index` | `_meta/index.md` | MOC per container | generated | Derived (Plane 2), regenerated by consolidation; hand-curation only in `global/_meta/index.md` head section |
| `source` | `raw/`, `_inbox/` | Immutable evidence | as captured | Never edited, never trusted as belief, never semantically indexed; referenced by `sources:` |

**Preferences** are not a type: durable executive preferences live in `USER.md` (budgeted) and `macro/`; domain preferences are `knowledge` with `epistemic: preference`. **Summary** is not a type: summaries are `description:` fields, index entries, and episode bodies — always pointing to their source (P8). **Deprecation/quarantine items** are states (`status:`), not objects.

## 4. Relations (question A.4)

The graph is deliberately thin — five typed edges, all in frontmatter, all derivable into `catalog.sqlite`:

```text
supersedes / superseded_by   — truth replacement chain (temporal)
disputed_by                  — live contradiction (epistemic)
entities                     — object ↔ entity participation (relational)
relates_to + [[wikilinks]]   — associative (Zettelkasten links)
canonical_from               — marked duplication (provenance)
```

Macroverso governs (never linked-to as data); microversos scope; projects usually *are* microversos or `context` heads inside one; people/companies are entities; conversations distill to episodes; tasks live in kanban with intentions as their canonical shadow; calendar stays in Google (integration reads it; briefing joins it with intentions); files are sources or artifacts.

## 5. How the LLM uses each object (read rules)

| Task signal | Load |
|---|---|
| scope activation | `context/current-state.md` + microverso index |
| "what do we know about X" | knowledge (status: active, valid now) + dispute banners |
| "why did we choose X" | decision chain (follow `supersedes` backwards on request only) |
| "what happened with/when" | episodes (time-filtered) → session_search for literal quotes |
| "who is X / relationship" | entity page first (aliases make grep hit), then their episodes |
| "what's pending / promised" | intentions (active, due-sorted) + kanban |
| "how do I do X" | workflow/skill; never reconstruct a procedure from episodes if a workflow exists |
| drafting in domain voice | persona + 2–3 recent artifacts as style evidence |

Default retrieval filter, always: `status ∈ {active}` and `valid_until ≥ today | null`, scope-resolved. Historical states load only on explicit temporal queries ("o que acreditávamos em março?") — and are then labeled as historical in the packed context. This is the mechanism that stops the LLM from mixing past and present (question A.5).
