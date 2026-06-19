# Task 02: Define `log.md` Convention

**Status:** pending
**Depends on:** ADR-013
**Produces:** `docs/plans/2026-06-19_acervo-lifecycle-okf/log-convention.md`

## Context

OKF defines `log.md` as an optional chronological history file. The Acervo already uses `log.md` per microverso, but the format is inconsistent. This task standardizes the format so the syndic and deprecation skills can parse and append reliably.

## Deliverable

Create `docs/plans/2026-06-19_acervo-lifecycle-okf/log-convention.md` containing:

### Section 1: Format Spec

`log.md` is append-only, organized by date (newest at top or bottom — pick one and document). Each entry is a bullet list item under a date heading.

```markdown
# Log

## 2026-06-19

- CREATED: knowledge/modelo-default-v2.md (volátil) — MiniMax-M3 is default
- DEPRECATED: knowledge/modelo-default-v1.md — superseded by modelo-default-v2.md
- PROMOTED: artifacts/exocortex-architecture.md → perene
- QUARANTINED: knowledge/old-pricing.md — not accessed in 92 days
- PURGED: knowledge/config-port-v1.md — quarantine expired (30 days)
- RESTORED: knowledge/needed-config.md — restored from quarantine by executive

## 2026-06-18

- CREATED: decisions/adr-013-frontmatter-schema.md (perene)
- UPDATED: context/current-state.md — added OKF alignment info
```

### Section 2: Entry Types

| Entry Type | Format | Who Writes |
|------------|--------|------------|
| `CREATED` | `CREATED: <relative-path> (<class>) — <one-line description>` | Any agent writing a new file |
| `UPDATED` | `UPDATED: <relative-path> — <what changed>` | Any agent modifying a file |
| `DEPRECATED` | `DEPRECATED: <relative-path> — <reason>` | Semantic revision skill |
| `PROMOTED` | `PROMOTED: <relative-path> → perene` | Executive or promotion skill |
| `QUARANTINED` | `QUARANTINED: <relative-path> — <reason>` | Syndic |
| `PURGED` | `PURGED: <relative-path> — quarantine expired (30 days)` | Syndic |
| `RESTORED` | `RESTORED: <relative-path> — restored from quarantine by executive` | Executive or restore skill |

### Section 3: Location Rules

- Each microverso has one `log.md`.
- Location: `micro/{slug}/_meta/log.md` if `_meta/` exists, otherwise `micro/{slug}/log.md` (check first, never assume).
- `global/` has its own `global/log.md`.
- `shared/` has its own `shared/log.md`.
- `macro/` does NOT have a log — identity changes are tracked in git.

### Section 4: Append Protocol

Agents must:
1. Read the current `log.md` (or create if missing).
2. Find or create today's date heading (`## YYYY-MM-DD`).
3. Append the entry as a bullet item.
4. Write the file back.
5. Never reorder, edit, or delete existing entries — append-only.

## Verification

- [ ] Convention file exists at expected path
- [ ] All 7 entry types documented with format
- [ ] Location rules cover `_meta/` variant
- [ ] Append protocol is clear and unambiguous
- [ ] Example log.md provided
