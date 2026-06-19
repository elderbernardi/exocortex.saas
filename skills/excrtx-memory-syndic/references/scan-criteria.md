# Scan Criteria & Immunity Rules — Detailed Reference

Detailed field-level reference for the syndic's scan criteria and immunity
rules. Extracted from `SKILL.md` to keep the skill body compact. The brief
summaries in `SKILL.md` preserve the decision thresholds; this file holds the
full tables, reason strings, and edge cases.

## Scan Criteria

Three candidate types. A file may match more than one; the first match
determines its classification (priority: stale-volatile → long-deprecated →
consolidation).

### Stale Volatile

| Field | Condition |
|-------|-----------|
| `class` | `volátil` |
| `last_accessed_at` | Present AND older than 90 days from current UTC date |
| `promoted_at` | Absent (promoted files are immune) |
| `quarantined_at` | Absent (already in quarantine) |
| `deprecated` | Not `true` (deprecated files use the long-deprecated criterion) |

**Reason string for quarantine:** `"Not accessed in N days (last read YYYY-MM-DD)"`
where `N` is the day count between `last_accessed_at` and today, and `YYYY-MM-DD`
is the date portion of `last_accessed_at`.

**Edge case — `last_accessed_at` absent:** If the file has no `last_accessed_at`
field (never read by an agent since creation), fall back to `created_at`. If
`created_at` is also absent (malformed frontmatter), skip the file and flag it
for review — do not quarantine on missing data.

### Long-Deprecated

| Field | Condition |
|-------|-----------|
| `deprecated` | `true` |
| `deprecated_at` | Present AND older than 180 days from current UTC date |
| `quarantined_at` | Absent (already in quarantine) |

**Note on perene:** Perene files and files with `promoted_at` are immune to
quarantine regardless of deprecation status (see Immunity Rules below).
If a perene file is somehow `deprecated: true`, it remains immune — flag it in
the report, do not quarantine.

**Reason string for quarantine:** `"Long-deprecated (deprecated_at YYYY-MM-DD), quarantine window opened"`
where `YYYY-MM-DD` is the date portion of `deprecated_at`.

**Note:** the quarantine skill will strip the `deprecated`/`deprecated_at`/
`deprecated_reason` fields when quarantining (V-071: a file cannot be
simultaneously deprecated and quarantined). The reason string preserves the
history.

### Consolidation Candidates

| Signal | Threshold |
|--------|-----------|
| Tag overlap | 2+ tags shared between 2+ files in the same container |
| Title similarity | Semantically similar titles (same subject/entity) |
| Entity matching | Same key entity (model name, tool name, port, config key) in file bodies |

Consolidation candidates are **flagged for the report only**. The syndic never
auto-quarantines them. The executive reviews the report and decides.

## Immunity Rules

The following files are **never** quarantined by the syndic. They are excluded
at Step 2 (Immunity Filter) before scan criteria are evaluated.

| Immunity | How to check | Why |
|----------|--------------|-----|
| `class: perene` | frontmatter `class == "perene"` | Perene files are durable governance — never auto-deprecated or removed (ADR-014). |
| `promoted_at` present | frontmatter has a `promoted_at` field (any value) | `promoted_at` overrides `class` at runtime (V-072) — the file is treated as `perene` even if `class` still reads `volátil`. Promotion is an explicit executive act protecting the file. |
| `raw/` directory | path contains a `raw/` segment | Raw sources are immutable by contract — never modified, never removed (ADR-014). |
| `macro/` layer | path starts with `macro/` | The Macroverso is identity — always permanent, tracked in git, never quarantined. `macro/` has no `log.md`. |

**Check order:** `promoted_at` → `class` → path segments (`raw/`, `macro/`).
Check `promoted_at` *before* `class`, because a `volátil` file with
`promoted_at` is immune despite its `class` value.

**Even if a perene or promoted file is marked `deprecated: true`**, it remains
immune to quarantine. Deprecation of a perene file is an explicit executive act;
the syndic does not compound it with quarantine. Flag such files in the report
if encountered, but do not quarantine them.
