# Acervo Frontmatter Schema v0.2 — Field Reference

> **Status:** Proposed (becomes canonical when ADR-023 is accepted; supersedes `docs/plans/2026-06-19_acervo-lifecycle-okf/SCHEMA.md` v1.0.0).
> Rationale and object semantics: `../05-object-model.md`. Still a valid OKF v0.1 superset (`timestamp` emitted at export).

## Tier 0 — mandatory on every object

| Field | Type | Constraint |
|---|---|---|
| `schema` | string | `acervo/v0.2` |
| `type` | enum | `context knowledge decision episode entity intention workflow contract reflection persona prompt template tool skill artifact conflict` — **must match home directory** (V2-020) |
| `title` | string | ≤200 chars, no newline, passes title-as-API test (advisory) |
| `description` | string | ≤160 chars, single line |
| `tags` | list[str] | may be `[]` |
| `created_at` | datetime | `YYYY-MM-DDTHH:MM:SSZ` UTC |
| `class` | enum | `perene` \| `volátil` |
| `status` | enum | `draft` \| `active` \| `superseded` \| `deprecated` \| `quarantined` \| `archived` |

## Tier 1 — required for `knowledge` `context` `decision` `reflection` `entity` `conflict` (WARN if absent on others)

| Field | Type | Notes |
|---|---|---|
| `epistemic` | enum | `fact observation interpretation hypothesis decision preference rule intention` |
| `confidence` | enum | `high` \| `likely` \| `possible` \| `low` |
| `sources` | list[{type, ref}] | type ∈ `conversation email document web agent-inference executive`; ref = URL/path/`session://` |
| `observed_at` | date | when the world showed it |
| `extraction` | enum | `executive` \| `agent` \| `pipeline` |

## Tier 2 — optional everywhere

| Field | Type | Notes |
|---|---|---|
| `valid_from` / `valid_until` | date | world-validity window; absent `valid_until` = open |
| `entities` | list[slug] | resolved against entity registry aliases |
| `supersedes` | list[path] | set by author/pipeline |
| `superseded_by` | path | **pipeline-only** (never by hand) |
| `disputed_by` | path | pipeline-only; open conflict object |
| `relates_to` | list[path] | soft links |
| `canonical_from` | path | marked duplication |
| `sensitivity` | enum | `normal` \| `restricted` |
| `review_after` | date | syndic revisit |
| `aliases` | list[str] | **entity objects only**, mandatory there |
| `due` / `trigger` / `owed_to` | date / str / slug | **intention objects only** |
| `nature` | string | legacy alias; if present must equal directory (WARN otherwise). Auto-filled; do not hand-author |

## Conditional (unchanged from v1.0.0)

`last_accessed_at`, `promoted_at`; deprecation trio (`deprecated`, `deprecated_at`, `deprecated_reason`); quarantine trio (`quarantined_at`, `quarantine_reason`, `quarantine_expires_at`). V-071 (deprecated XOR quarantined) stands; both imply matching `status`.

## Frozen / removed

- `excrtx_type` — frozen: valid on pre-v0.2 files, forbidden on new writes (WARN).
- `timestamp` — no longer authored; derived from `created_at` at OKF export.
- `updated`, `created`, `from`, `to`, `subject` — legacy cross-ref fields; migrate to Tier 0/2 equivalents.

## Cross-field rules (delta)

| Rule | Sev |
|---|---|
| V2-020 `type` ↔ directory match | ERROR |
| V2-030 `status: superseded` ⇒ `superseded_by` present, and vice versa | ERROR |
| V2-031 `supersedes` targets exist and are `status: superseded` (post-commit) | ERROR (doctor) |
| V2-032 `status: deprecated` ⇔ `deprecated: true` trio | ERROR |
| V2-040 Tier 1 present for the five epistemic types | ERROR (new files) / WARN (migrated) |
| V2-041 `valid_until < valid_from` | ERROR |
| V2-050 `entity` without `aliases` | ERROR |
| V2-051 `intention` without `due` or `trigger` | WARN |
| V2-060 secret-shaped strings in any field/body | ERROR (trust gate) |
| V2-070 title fails kebab-file ↔ title coherence | WARN |
