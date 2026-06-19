# Frontmatter Schema Specification

> **Version:** 1.0.0
> **Date:** 2026-06-19
> **Status:** Proposed
> **Authors:** Elder Bernardi, Exocórtex Orchestrator
> **Source ADRs:** [ADR-013](ADR-013-frontmatter-schema-okf.md), [ADR-017](ADR-017-okf-compatibility.md)
> **Consumed by:** Task 03 (validator script), Task 04 (deprecate skill), Task 05 (quarantine skill), Task 08 (migration script)

---

## Overview

The Acervo Cognitivo frontmatter schema is a **superset** of the Open Knowledge Format (OKF v0.1). Every Acervo markdown file carries YAML frontmatter with two tiers of fields:

1. **OKF Canonical** — mandatory on every file. Guarantees interoperability with any OKF-compatible consumer.
2. **Acervo Extension** — lifecycle governance fields (class, timestamps, deprecation, quarantine). Invisible to OKF consumers; essential to the Acervo's autonomous lifecycle management.

A third group — **Legacy Retained** fields — are carried forward from the pre-migration schema and coexist with the new fields without conflict.

---

## 1. Field Reference Table

### 1.1 OKF Canonical Fields (mandatory on every file)

| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| `type` | string | **Yes** | Must be one of: `decision`, `memory`, `reflection`, `context`, `knowledge`, `artifact`. This is the **OKF concept type**, not the legacy Acervo type. | `type: memory` |
| `title` | string | **Yes** | Non-empty. Max 200 characters. Must not contain newlines. | `title: Default LLM model is MiniMax-M3` |
| `description` | string | **Yes** | Non-empty. Should be a single line (no newlines). Recommended max 120 characters. | `description: Current default model for Exocórtex operations` |
| `tags` | list[string] | **Yes** | Must be a YAML list. Can be empty (`[]`). Each tag is a non-empty string. | `tags: [model, config, minimax]` |
| `timestamp` | string (ISO 8601 date) | **Yes** | Format: `YYYY-MM-DD`. Date-only granularity (no time component). Must equal the date portion of `created_at`. | `timestamp: 2026-06-19` |

### 1.2 Acervo Extension Fields (lifecycle governance)

| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| `class` | string | **Yes** | Must be `perene` or `volátil`. Governs lifecycle: `perene` = never auto-deprecated; `volátil` = deprecation candidate. | `class: volátil` |
| `created_at` | string (ISO 8601 datetime) | **Yes** | Format: `YYYY-MM-DDTHH:MM:SSZ` (UTC, `Z` suffix). Must be a valid datetime. Date portion must equal `timestamp`. | `created_at: 2026-06-19T10:30:00Z` |
| `last_accessed_at` | string (ISO 8601 datetime) | No | Format: `YYYY-MM-DDTHH:MM:SSZ`. Updated by agent at runtime when the file is read. Absent on freshly created files until first agent read. | `last_accessed_at: 2026-06-19T14:00:00Z` |
| `promoted_at` | string (ISO 8601 datetime) | Conditional | Format: `YYYY-MM-DDTHH:MM:SSZ`. Present only when a file was explicitly promoted from `volátil` to `perene`. **Presence overrides `class`** — file is treated as `perene` at runtime regardless of the `class` field value. | `promoted_at: 2026-06-19T12:00:00Z` |

### 1.3 Deprecation Fields (conditional — present only when deprecated)

| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| `deprecated` | boolean | Conditional | Must be `true` when the file is deprecated. If present as `false`, the file is not deprecated and `deprecated_at` / `deprecated_reason` must be absent. | `deprecated: true` |
| `deprecated_at` | string (ISO 8601 datetime) | Conditional | Format: `YYYY-MM-DDTHH:MM:SSZ`. **Required when `deprecated: true`.** Must not be present when `deprecated` is absent or `false`. | `deprecated_at: 2026-06-19T10:30:00Z` |
| `deprecated_reason` | string | Conditional | Non-empty. **Required when `deprecated: true`.** Should reference the superseding file path when applicable. Must not be present when `deprecated` is absent or `false`. | `deprecated_reason: "Superseded by memories/modelo-default-v2.md"` |

### 1.4 Quarantine Fields (conditional — present only when quarantined)

| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| `quarantined_at` | string (ISO 8601 datetime) | Conditional | Format: `YYYY-MM-DDTHH:MM:SSZ`. Presence indicates the file is in quarantine. A file cannot be simultaneously deprecated and quarantined. | `quarantined_at: 2026-06-19T03:00:00Z` |
| `quarantine_reason` | string | Conditional | Non-empty. **Required when `quarantined_at` is present.** | `quarantine_reason: "Not accessed in 92 days"` |
| `quarantine_expires_at` | string (ISO 8601 datetime) | Conditional | Format: `YYYY-MM-DDTHH:MM:SSZ`. **Required when `quarantined_at` is present.** Purge date — must be ≥ `quarantined_at`. Convention: exactly 30 days after `quarantined_at`. | `quarantine_expires_at: 2026-07-19T03:00:00Z` |

### 1.5 Legacy Retained Fields (optional, carried forward from pre-migration schema)

| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| `excrtx_type` | string | No | The **old** Acervo `type` field (e.g., `fact`, `rule`, `workflow`, `tool`, `profile`, `lesson`, `context`, `project`, `domain`, `role`, `prompt`). Renamed from `type` during migration to avoid collision with the OKF `type` field. No vocabulary constraint — preserves whatever value the original file had. | `excrtx_type: fact` |
| `nature` | string | No | Directory routing key used by `excrtx-memory-manager`. Coexists with OKF `type` — they serve different purposes (`type` = concept type; `nature` = directory routing). Values in the wild include both English and Portuguese: `context`, `knowledge`, `decisions`, `contracts`, `workflows`, `tools`, `skills`, `persona`, `reflexoes`, `conhecimento`, `instrucoes`, `ferramentas`, `contexto`, `processos`. | `nature: knowledge` |
| `confidence` | string | No | Knowledge quality signal. Should be one of: `low`, `medium`, `high`. | `confidence: high` |
| `sources` | list[string] | No | Provenance tracking. List of source URLs or references. | `sources: ["https://example.com/source"]` |

### 1.6 OKF Optional Fields (not in Acervo by default)

| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| `resource` | string | No | Defined by OKF v0.1 for external resource references. Not used by default in the Acervo. Can be added per-file when an external resource URI is relevant. OKF consumers may use it; the Acervo ignores it. | `resource: https://api.example.com/data` |

---

## 2. Complete Examples

### 2.1 New Volatile Knowledge

A freshly created knowledge file. No deprecation, no quarantine, no promotion. `last_accessed_at` is absent because no agent has read it yet.

```yaml
---
# OKF Canonical (mandatory)
type: knowledge
title: Exocórtex uses Hermes Agent as runtime
description: Hermes provides the CLI, memory, and tool execution layer for Exocórtex
tags: [architecture, hermes, runtime]
timestamp: 2026-06-19

# Acervo Extension (lifecycle)
class: volátil
created_at: 2026-06-19T10:30:00Z

# Legacy (retained)
nature: knowledge
confidence: high
---

Exocórtex is a configuration and skill package built on top of the Hermes Agent
runtime. Hermes provides the execution layer (CLI, memory system, tool dispatch);
Exocórtex provides the identity, methodology, and behavioral skills.
```

### 2.2 Deprecated Memory

A memory file that has been superseded by a newer version. The `deprecated: true` flag and accompanying fields are present. The body contains a supersede link per the OKF linking convention (ADR-017).

```yaml
---
# OKF Canonical (mandatory)
type: memory
title: Default LLM model is DeepSeek-V3
description: Previous default model, now superseded by MiniMax-M3
tags: [model, config, deepseek]
timestamp: 2026-05-01

# Acervo Extension (lifecycle)
class: volátil
created_at: 2026-05-01T09:00:00Z

# Deprecation (conditional)
deprecated: true
deprecated_at: 2026-06-19T10:30:00Z
deprecated_reason: "Superseded by memories/modelo-default-v2.md — MiniMax-M3 is now default"

# Legacy (retained)
nature: knowledge
confidence: high
---

Superseded by: [modelo-default-v2](../memories/modelo-default-v2.md)

DeepSeek-V3 was the default model from 2026-05-01 until 2026-06-19, when it was
replaced by MiniMax-M3 for improved reasoning performance.
```

### 2.3 Promoted Artifact

A file that was originally `volátil` but has been explicitly promoted to `perene`. The `promoted_at` field is present. Note: `class` may still read `volátil` (the original value) — the presence of `promoted_at` overrides it at runtime. However, best practice is to also update `class: perene` at promotion time, as shown here.

```yaml
---
# OKF Canonical (mandatory)
type: artifact
title: Skill creation workflow
description: Standard procedure for creating and validating new Exocórtex skills
tags: [workflow, skills, skill-judge, convention]
timestamp: 2026-03-15

# Acervo Extension (lifecycle)
class: perene
created_at: 2026-03-15T08:00:00Z
last_accessed_at: 2026-06-19T16:45:00Z
promoted_at: 2026-06-01T10:00:00Z

# Legacy (retained)
nature: workflows
---

## Procedure

1. Create `skills/excrtx-<name>/SKILL.md` with required frontmatter.
2. Write body sections: `## When to Use`, `## Procedure`, `## Pitfalls`, `## Verification`.
3. Run `python3 scripts/skill_judge.py --skill excrtx-<name> --d1-only` for structural check.
4. Run full judge: `python3 scripts/skill_judge.py --skill excrtx-<name>`.
5. Verdict must be `PASS` before promoting to bundle.
6. After promoting: `python3 scripts/compile_soul.py`.

Promoted to perene on 2026-06-01 — this workflow is foundational and stable.
```

### 2.4 Quarantined File

A volatile file that has not been accessed in 92 days. The syndic (ADR-018) moved it to quarantine. All three quarantine fields are present. The file has 30 days until purge.

```yaml
---
# OKF Canonical (mandatory)
type: context
title: Exocortex-Dev sprint status — March 2026
description: Sprint context snapshot from March 2026, now stale
tags: [sprint, status, exocortex-dev, stale]
timestamp: 2026-03-01

# Acervo Extension (lifecycle)
class: volátil
created_at: 2026-03-01T07:00:00Z
last_accessed_at: 2026-03-15T11:20:00Z

# Quarantine (conditional)
quarantined_at: 2026-06-19T03:00:00Z
quarantine_reason: "Not accessed in 92 days (last read 2026-03-15)"
quarantine_expires_at: 2026-07-19T03:00:00Z

# Legacy (retained)
nature: context
---

## Sprint 2026-03 Status

This context snapshot was created at the start of the March 2026 sprint.
It is now stale and has been quarantined by the syndic.

**Quarantine expires:** 2026-07-19. If still needed, promote to `perene` before expiry.
```

---

## 3. Migration Rules

This section documents how each legacy frontmatter field maps to the new schema. The migration script (Task 08) will implement these rules.

### 3.1 Field Mapping Table

| Old Field | New Field | Action | Notes |
|-----------|-----------|--------|-------|
| `type` (e.g., `type: fact`) | `excrtx_type` | **Rename** | **Collision with OKF `type`.** The old value is preserved verbatim in `excrtx_type`. A new OKF `type` field is derived (see §3.2). |
| `title` | `title` | Retain | Direct match with OKF canonical field. No change needed. |
| `created` | `timestamp` + `created_at` | **Split** | `created` (date-only) → `timestamp` (date-only, OKF). `created_at` (datetime) is derived from `created` at `T00:00:00Z`, or from git log if `created` is missing (see §3.4). |
| `updated` | `last_accessed_at` | **Rename** | Semantic shift: old `updated` meant "last modified"; new `last_accessed_at` means "last read by agent". The old value is used as the initial value. If `updated` is missing, `last_accessed_at` is left absent. |
| `nature` | `nature` | Retain | Still used by `excrtx-memory-manager` for directory routing. Coexists with OKF `type`. No change. |
| `tags` | `tags` | Retain | Direct match with OKF canonical field. If missing, default to `[]`. |
| `confidence` | `confidence` | Retain | Optional quality signal. No change. |
| `sources` | `sources` | Retain | Optional provenance tracking. No change. |
| _(missing)_ | `type` | **Derive** | OKF concept type. Derived from directory path and/or `nature`. See §3.2. |
| _(missing)_ | `description` | **Derive** | One-line summary. Derived from body content. See §3.3. |
| _(missing)_ | `class` | **Derive** | Lifecycle class. Derived from directory path. See §3.3. |
| _(missing)_ | `timestamp` | **Derive** | From `created` field or git log. See §3.4. |
| _(missing)_ | `created_at` | **Derive** | From `created` field or git log. See §3.4. |

### 3.2 Derivation: OKF `type` (Concept Type)

The OKF `type` field is the concept type (`decision`, `memory`, `reflection`, `context`, `knowledge`, `artifact`). It does **not** correspond to the old Acervo `type` (which is renamed to `excrtx_type`). The new `type` is derived from the file's directory path within the microverso:

| Directory Path Pattern | OKF `type` | Rationale |
|------------------------|------------|-----------|
| `decisions/` | `decision` | Explicit decisions |
| `knowledge/` | `knowledge` | Factual knowledge entries |
| `reflections/` | `reflection` | Reflective notes |
| `context/` | `context` | Contextual state snapshots |
| `memories/` | `memory` | Individual memory entries |
| `workflows/` | `artifact` | Process artifacts |
| `tools/` | `artifact` | Tool documentation artifacts |
| `contracts/` | `decision` | Contracts are binding decisions/standards |
| `persona/` | `context` | Persona/identity context |
| `prompts/` | `artifact` | Prompt templates are artifacts |
| `skills/` | `artifact` | Skill documentation artifacts |
| `raw/` | `knowledge` | Raw knowledge inputs |
| `_meta/` | `context` | Structural metadata (index, SCHEMA) |
| `index.md` (any dir) | `context` | Progressive disclosure index |
| `log.md` (any dir) | `context` | Chronological log |
| `_seed.md` (any dir) | `context` | Template seed files |
| Default / unknown | `knowledge` | Safe fallback for unclassified files |

**Portuguese `nature` equivalents** (used when directory path is ambiguous but `nature` is present):

| `nature` value (PT) | Equivalent directory | OKF `type` |
|---------------------|----------------------|------------|
| `conhecimento` | `knowledge/` | `knowledge` |
| `contexto` | `context/` | `context` |
| `reflexoes` | `reflections/` | `reflection` |
| `processos` | `workflows/` | `artifact` |
| `ferramentas` | `tools/` | `artifact` |
| `instrucoes` | `contracts/` | `decision` |

**Resolution priority:** Directory path → `nature` value → default (`knowledge`).

### 3.3 Derivation: `class` and `description`

#### `class` Default Derivation

When `class` is absent (which it will be on all pre-migration files), derive from directory path:

| Directory Path Pattern | Default `class` | Rationale |
|------------------------|-----------------|-----------|
| `decisions/` | `perene` | Decisions are durable governance |
| `reflections/` | `perene` | Reflections are intentional, durable |
| `contracts/` | `perene` | Contracts are binding standards |
| `persona/` | `perene` | Identity is foundational |
| `_meta/` | `perene` | Structural files (index, SCHEMA) |
| `index.md` | `perene` | Structural |
| `log.md` | `perene` | Chronological record |
| `_seed.md` | `perene` | Template seeds |
| `knowledge/` | `volátil` | Knowledge may become stale |
| `context/` | `volátil` | Context is point-in-time |
| `memories/` | `volátil` | Individual memories are transient |
| `workflows/` | `volátil` | Processes evolve |
| `tools/` | `volátil` | Tools change |
| `prompts/` | `volátil` | Prompts change |
| `skills/` | `volátil` | Skills evolve |
| `raw/` | `volátil` | Raw inputs are transient |
| Default / unknown | `volátil` | Safe default — can be deprecated if stale |

**Resolution priority:** Directory path → default (`volátil`).

#### `description` Default Derivation

When `description` is absent, derive from the markdown body:

1. **First non-empty, non-heading line** of the body (skipping lines that start with `#`).
2. If the body is empty or contains only headings, use the `title` value.
3. Truncate to 120 characters. If truncated, append `...`.
4. Strip any leading `>` (blockquote markers) or `-` (list markers) from the extracted line.

**Example:**
```markdown
# Architecture Overview

Exocórtex is a configuration and skill package built on top of Hermes.
```
→ `description: "Exocórtex is a configuration and skill package built on top of Hermes."`

### 3.4 Derivation: `timestamp` and `created_at` from Git Log

When `created` is absent (or when the migration wants to verify accuracy), derive timestamps from the git history of the file.

#### Method

```bash
# Get the author date of the first commit that added the file
git log --diff-filter=A --follow --format=%aI -- "<file_path>" | tail -1
```

- `%aI` outputs strict ISO 8601 format: `YYYY-MM-DDTHH:MM:SS+HH:MM` (or `Z` for UTC).
- `--diff-filter=A` filters to the Add event (first commit that introduced the file).
- `--follow` tracks the file across renames.
- `tail -1` takes the oldest commit if multiple Add events exist (e.g., file was deleted and re-added).

#### Derivation

| Field | Value |
|-------|-------|
| `created_at` | Full datetime from git. Normalize timezone to UTC (`Z` suffix). |
| `timestamp` | Date portion of `created_at` (`YYYY-MM-DD`). |

#### Fallback Chain

1. **`created` field present** → `timestamp` = `created` value; `created_at` = `created` value + `T00:00:00Z`.
2. **`created` absent, file tracked by git** → use `git log --diff-filter=A` as above.
3. **File not tracked by git** (untracked/new) → use file mtime: `stat -c %Y "<file_path>"` (Unix epoch) → convert to UTC ISO 8601.
4. **All methods fail** → use migration run date: current UTC datetime. Log a warning.

#### Normalization

- All datetimes are stored in UTC with `Z` suffix (no timezone offset).
- If git returns `2026-06-11T14:30:00-03:00`, normalize to `2026-06-11T17:30:00Z`.
- `timestamp` is always the date portion of `created_at` — they must be consistent.

### 3.5 Migration Edge Cases

| Edge Case | Handling |
|-----------|----------|
| File has no frontmatter at all | Create full frontmatter block. Derive all fields. `excrtx_type` is absent (no old type to preserve). |
| File has frontmatter but missing `---` closing delimiter | Fix the delimiter during migration. Log a warning. |
| `type` field value already matches an OKF type (e.g., old `type: context`) | Rename to `excrtx_type: context`. Derive new `type` from directory. The two fields may have the same string value — this is correct (different semantics). |
| File is in `_meta/` or is `_seed.md` | Migrate normally. These files get `class: perene` and `type: context` by default. |
| `created` field has datetime granularity (e.g., `2026-06-11T10:30:00Z`) | Extract date portion for `timestamp`. Use full value for `created_at` (already datetime). |
| `created` field has non-standard format | Attempt to parse with `dateutil.parser`. If parsing fails, fall back to git log. Log a warning. |
| `tags` is a string instead of a list | Convert to single-element list: `tags: "dev"` → `tags: [dev]`. |
| `tags` is missing | Default to `tags: []`. |
| `confidence` has non-standard value (not `low`/`medium`/`high`) | Retain as-is. Validator will flag as a warning (not error). |
| File is already deprecated in the old schema (no formal field, just body text) | Do not auto-set `deprecated: true`. Flag for manual review. |

---

## 4. Validation Rules

This section lists all deterministic validation rules that the validator script (Task 03) will enforce. Each rule has an ID, a description, and a severity (`ERROR` blocks validation; `WARN` is informational).

### 4.1 Structural Rules

| ID | Rule | Severity |
|----|------|----------|
| V-001 | File must start with `---\n` (YAML frontmatter opening delimiter). | ERROR |
| V-002 | File must contain a closing `---` delimiter after the opening one. | ERROR |
| V-003 | Frontmatter must be valid YAML (parseable by a standard YAML parser). | ERROR |
| V-004 | File body (after frontmatter) must be valid markdown (non-empty body recommended). | WARN |

### 4.2 OKF Canonical Field Presence Rules

| ID | Rule | Severity |
|----|------|----------|
| V-010 | `type` field must be present. | ERROR |
| V-011 | `title` field must be present. | ERROR |
| V-012 | `description` field must be present. | ERROR |
| V-013 | `tags` field must be present. | ERROR |
| V-014 | `timestamp` field must be present. | ERROR |

### 4.3 OKF Canonical Field Value Rules

| ID | Rule | Severity |
|----|------|----------|
| V-020 | `type` must be one of: `decision`, `memory`, `reflection`, `context`, `knowledge`, `artifact`. | ERROR |
| V-021 | `title` must be a non-empty string. | ERROR |
| V-022 | `title` must not exceed 200 characters. | WARN |
| V-023 | `title` must not contain newlines. | ERROR |
| V-024 | `description` must be a non-empty string. | ERROR |
| V-025 | `description` must not contain newlines. | WARN |
| V-026 | `description` should not exceed 120 characters. | WARN |
| V-027 | `tags` must be a YAML list (not a scalar string). | ERROR |
| V-028 | Each element in `tags` must be a non-empty string. | ERROR |
| V-029 | `timestamp` must match format `YYYY-MM-DD` (valid ISO 8601 date). | ERROR |
| V-030 | `timestamp` must be a valid calendar date (e.g., not `2026-02-31`). | ERROR |

### 4.4 Acervo Extension Field Rules

| ID | Rule | Severity |
|----|------|----------|
| V-040 | `class` field must be present. | ERROR |
| V-041 | `class` must be `perene` or `volátil`. | ERROR |
| V-042 | `created_at` field must be present. | ERROR |
| V-043 | `created_at` must match format `YYYY-MM-DDTHH:MM:SSZ` (ISO 8601 datetime, UTC). | ERROR |
| V-044 | `created_at` must be a valid datetime. | ERROR |
| V-045 | `last_accessed_at`, if present, must match format `YYYY-MM-DDTHH:MM:SSZ`. | ERROR |
| V-046 | `promoted_at`, if present, must match format `YYYY-MM-DDTHH:MM:SSZ`. | ERROR |

### 4.5 Deprecation Field Rules

| ID | Rule | Severity |
|----|------|----------|
| V-050 | `deprecated`, if present, must be a boolean (`true` or `false`). | ERROR |
| V-051 | If `deprecated: true`, then `deprecated_at` must be present. | ERROR |
| V-052 | If `deprecated: true`, then `deprecated_reason` must be present. | ERROR |
| V-053 | If `deprecated: true`, then `deprecated_at` must match `YYYY-MM-DDTHH:MM:SSZ`. | ERROR |
| V-054 | If `deprecated: true`, then `deprecated_reason` must be a non-empty string. | ERROR |
| V-055 | If `deprecated` is absent or `false`, then `deprecated_at` must NOT be present. | ERROR |
| V-056 | If `deprecated` is absent or `false`, then `deprecated_reason` must NOT be present. | ERROR |

### 4.6 Quarantine Field Rules

| ID | Rule | Severity |
|----|------|----------|
| V-060 | `quarantined_at`, if present, must match `YYYY-MM-DDTHH:MM:SSZ`. | ERROR |
| V-061 | If `quarantined_at` is present, then `quarantine_reason` must be present. | ERROR |
| V-062 | If `quarantined_at` is present, then `quarantine_expires_at` must be present. | ERROR |
| V-063 | `quarantine_reason`, if present, must be a non-empty string. | ERROR |
| V-064 | `quarantine_expires_at`, if present, must match `YYYY-MM-DDTHH:MM:SSZ`. | ERROR |
| V-065 | `quarantine_expires_at` must be ≥ `quarantined_at` (not in the past). | ERROR |
| V-067 | If `quarantined_at` is absent, then `quarantine_reason` must NOT be present. | ERROR |
| V-068 | If `quarantined_at` is absent, then `quarantine_expires_at` must NOT be present. | ERROR |

### 4.7 Cross-Field Consistency Rules

| ID | Rule | Severity |
|----|------|----------|
| V-070 | The date portion of `created_at` must equal `timestamp`. | ERROR |
| V-071 | A file must NOT be simultaneously deprecated and quarantined. If `deprecated: true` and `quarantined_at` is present → ERROR. | ERROR |
| V-072 | If `promoted_at` is present, the file is treated as `perene` at runtime regardless of `class`. (Informational — no validation error, but validator emits a `WARN` if `class` is `volátil` and `promoted_at` is present, suggesting `class` should be updated to `perene` for consistency.) | WARN |
| V-073 | `excrtx_type`, if present, must be a string. (No vocabulary constraint — preserves legacy values.) | ERROR |
| V-074 | `nature`, if present, must be a string. | ERROR |
| V-075 | `confidence`, if present, should be one of: `low`, `medium`, `high`. | WARN |
| V-076 | `sources`, if present, must be a YAML list. | ERROR |

### 4.8 Validation Summary

| Category | ERROR Rules | WARN Rules |
|----------|-------------|------------|
| Structural (V-001–V-004) | 3 | 1 |
| OKF Presence (V-010–V-014) | 5 | 0 |
| OKF Values (V-020–V-030) | 8 | 3 |
| Acervo Extension (V-040–V-046) | 6 | 1 |
| Deprecation (V-050–V-056) | 7 | 0 |
| Quarantine (V-060–V-068) | 8 | 0 |
| Cross-Field (V-070–V-076) | 4 | 3 |
| **Total** | **41** | **8** |

**Validator exit code:** `0` = all rules pass (WARN allowed). `1` = one or more ERROR rules failed.

---

## Appendix A: Field Dependency Diagram

```
                    ┌─────────────────────────────────────┐
                    │         OKF Canonical (mandatory)    │
                    │  type · title · description · tags   │
                    │            · timestamp               │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │     Acervo Extension (mandatory)     │
                    │       class · created_at             │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
   ┌──────────▼─────────┐  ┌───────▼────────┐  ┌───────▼────────┐
   │  Optional lifecycle │  │  Deprecation   │  │  Quarantine    │
   │  last_accessed_at   │  │  deprecated    │  │  quarantined_at│
   │  promoted_at        │  │  deprecated_at │  │  quarantine_*  │
   └─────────────────────┘  └────────────────┘  └────────────────┘
              │                    │                    │
              │     ┌──────────────┴──────────────┐     │
              │     │  MUTUAL EXCLUSION (V-071)   │     │
              │     │  deprecated XOR quarantined │     │
              │     └─────────────────────────────┘     │
              │                                         │
   ┌──────────▼─────────────────────────────────────────▼──┐
   │              Legacy Retained (optional)                │
   │  excrtx_type · nature · confidence · sources           │
   └────────────────────────────────────────────────────────┘
```

## Appendix B: ISO 8601 Format Reference

All datetime fields in this schema use ISO 8601 in UTC with the `Z` suffix:

| Field Type | Format | Regex | Example |
|------------|--------|-------|---------|
| Date | `YYYY-MM-DD` | `^\d{4}-\d{2}-\d{2}$` | `2026-06-19` |
| Datetime | `YYYY-MM-DDTHH:MM:SSZ` | `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$` | `2026-06-19T10:30:00Z` |

**No timezone offsets allowed** — all datetimes must be normalized to UTC (`Z`). The migration script converts any offset-based timestamps to UTC during normalization.
