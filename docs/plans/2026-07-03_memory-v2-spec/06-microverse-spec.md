# 06 — Microverse Specification

## 1. What a microverso is (and is not)

A microverso is a **cognitive namespace**: the unit of scope resolution, retrieval isolation, and context loading. It is:

- a **cognitive boundary** — always (thoughts about client A don't leak into client B);
- an **operational namespace** — always (paths, indexes, logs, scope guard);
- a **sensitivity boundary** — only when declared (`sensitivity: restricted`);
- **not a security boundary** in the cryptographic sense — one subject, one trust domain, one filesystem. Pretending otherwise would be theater.

It answers question A.3: `micro/{slug}` is the right abstraction *because it matches how the executive already thinks* (by client/project/area — PARA's one durable insight) *and* gives the LLM a hard scope filter (P6). Where it fails today is overlap (a deal touching two clients), lifecycle (no dormant/archived state), and drift (groups referencing dead slugs) — all addressed below.

## 2. Types (question G.1)

```yaml
micro_type: client | company | project | function | life-area |
            research | product | campaign | operation | system
```

Rules of thumb: **person → never a microverso** (people are entities; a person-microverso dies the moment the relationship spans domains). **Campaign/deal → usually a `context` head inside its client's microverso**; promote to microverso only when it accumulates ≥3 natures of real content (P9's lazy-structure test, applied upward).

## 3. Manifest v2 (`microverso.yaml`)

```yaml
apiVersion: excrtx/v2
kind: Microverso
metadata:
  name: comercial                # slug: kebab-case, stable forever (links depend on it)
  title: "Diretoria Comercial — GPQ"
  micro_type: function
  description: "..."
  tags: [comercial, gpq]
status: active                   # active | dormant | archived | retired
sensitivity: normal              # normal | restricted
relates_to: [clientes, bi-inteligencia-comercial]   # soft edges, no content sharing
sharing:
  default: isolated              # isolated | group-readable
  groups: [DOMAINS]              # memberships (must exist in shared/groups.yaml)
  expose: [persona, contracts]   # natures other scopes MAY read via cross-ref
entities_home: true              # this microverso maintains domain entity detail pages
lifecycle:
  created_at: 2026-05-27
  review_after: 2026-12-01       # syndic pings: still active?
# requires/compat/tree/hooks/provenance — unchanged from package-spec v1
```

## 4. Lifecycle (questions G.3–G.6)

| Transition | Trigger | Effect |
|---|---|---|
| **create** | 2+ real objects with no home, or a new durable domain. Never create for a single note (goes to the closest existing scope or `global/`) | `excrtx-memory-newmicro`: core-6 dirs only (`_meta`, `context`, `knowledge`, `decisions`, `episodes`, `raw`); registry entry |
| **active → dormant** | no writes in 60d (syndic flags; executive confirms) | retrieval de-weighted, excluded from briefing, still searchable |
| **dormant → archived** | executive decision (project ended, client gone) | `status: archived` on manifest; excluded from default retrieval; contents keep own statuses; `.mvpkg` export recommended |
| **merge** | sustained >30% cross-ref density between two scopes, or executive judgment | new/absorbing slug; files move with `canonical_from` stamps; old slug leaves a tombstone `microverso.yaml (status: retired, merged_into:)` so links resolve |
| **split** | a `context` head inside a scope outgrows it (own decisions+episodes+entities) | promote to new microverso; cross-refs replace in-place content |
| **temporary** | event/deal with known end | normal microverso + `lifecycle.review_after` = end date; archived on review, not deleted |

Tombstones make slugs permanent: **a slug is never reused.**

## 5. Overlap: clients-inside-company, cross-client projects (G.7–G.9)

- **Clients inside a company function**: today `clientes/` is one microverso. Keep it until an individual client accumulates real volume; then that client becomes its own microverso and `clientes/` keeps only the portfolio view. Client *entities* exist in the registry from day one regardless — entities are cheap, microversos are not.
- **A project crossing clients**: the project gets its own microverso; client-specific facts stay in client scopes; the project holds project facts + cross-refs. The routing question is always "**who would be harmed/confused if this fact appeared in the other scope?**" — that's the primary-home test.
- **Duplication prevention**: unmarked duplication is forbidden; `canonical_from` marks deliberate copies; the consolidation loop's dedup audit (04 §4) compares title/entity/tag collisions across scopes and flags.

## 6. `shared/` v2 (G.10–G.12)

`shared/` is a **bridge, not a commons**. Its contents:

- `groups.yaml` — the *single* machine-readable group registry (replaces both conflicting `groups.md` files):
  ```yaml
  groups:
    DOMAINS:  {members: [comercial, ia-automacao, bi-inteligencia-comercial], purpose: "..."}
    CLIENTES: {members: [clientes], purpose: "..."}
  # validation: every member must exist in micro/ with status ≠ retired
  ```
- `entities/` — the global entity registry (05): people/orgs/products that exist across scopes. Domain-private detail stays in `micro/*/entities/`.
- `cross-refs/` — pointer objects (`{a}--{b}--{tema}.md`, ≤15 lines, v0.2 frontmatter): "scope A, see scope B about X". Never content, always pointers.
- `glossario.md` — cross-domain vocabulary.

**Cross-access resolution:** a task scoped to A may read B's content iff (a) B `expose`s that nature, or (b) A and B share a group and the object isn't `restricted`, or (c) the executive asks explicitly. Every cross-read journals a `SCOPE-CROSS` event — leakage becomes measurable (10-evaluation.md), which is the honest version of "prevention".

## 7. Active-scope resolution (G.14)

```text
resolve_scope(input, session):
  1. explicit mention of slug/alias           → that microverso
  2. entity match (input names entities whose home is unambiguous)
  3. channel/session anchor (task rooms are anchored at creation — EX-06)
  4. classifier over microverso titles+descriptions+context heads
  5. confidence < threshold → ASK (one short question; never guess a scope
     for a WRITE; reads may proceed at global/ scope)
Writes: hard-fail without a resolved scope (existing runtime guard, kept).
```

## 8. Groups vs the graph (G.13)

Groups are *retrieval conveniences* (scope unions for briefing/search), never authority boundaries. Membership lives only in `groups.yaml`, validated against the registry — the current drift (groups naming dead microversos) becomes a CI failure, not a surprise.
