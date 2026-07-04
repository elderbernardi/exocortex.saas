# Acervo Frontmatter Schema — Canonical Reference

> **Version:** 1.0.0  ·  **Status:** Canonical (source of truth)
> **Decision:** [ADR-013](ADR-013-frontmatter-schema-okf.md)  ·  **Detailed spec:** [schema-spec.md](schema-spec.md)
> **OKF compatibility:** [ADR-017](ADR-017-okf-compatibility.md)

The Acervo Cognitivo frontmatter schema is a **superset** of the [Open Knowledge Format (OKF v0.1)](https://okf.dev). Every Acervo markdown file carries YAML frontmatter with two mandatory tiers plus conditional lifecycle fields:

1. **OKF Canonical** — mandatory on every file; guarantees interoperability with any OKF consumer.
2. **Acervo Extension** — lifecycle governance (`class`, timestamps, deprecation, quarantine).
3. **Legacy Retained** — carried forward from the pre-migration schema; coexists without conflict.

---

## 1. Field Reference

### 1.1 OKF Canonical (mandatory on every file)

| Field | Type | Constraints | Example |
|-------|------|-------------|---------|
| `type` | string | One of: `decision`, `memory`, `reflection`, `context`, `knowledge`, `artifact`. **OKF concept type** — not the legacy Acervo type. | `type: memory` |
| `title` | string | Non-empty. Max 200 chars. No newlines. | `title: Default LLM model is MiniMax-M3` |
| `description` | string | Non-empty. Single line recommended. ≤ 120 chars. | `description: Current default model for Exocórtex operations` |
| `tags` | list[string] | YAML list. May be empty (`[]`). | `tags: [model, config, minimax]` |
| `timestamp` | ISO 8601 date | `YYYY-MM-DD`. Must equal date portion of `created_at`. | `timestamp: 2026-06-19` |

### 1.2 Acervo Extension (lifecycle governance)

| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| `class` | string | **Yes** | `perene` or `volátil`. Governs lifecycle: `perene` = never auto-deprecated; `volátil` = deprecation candidate. | `class: volátil` |
| `created_at` | ISO 8601 datetime | **Yes** | `YYYY-MM-DDTHH:MM:SSZ` (UTC). Date portion must equal `timestamp`. | `created_at: 2026-06-19T10:30:00Z` |
| `last_accessed_at` | ISO 8601 datetime | No | Updated by agent at runtime when file is read. Absent until first agent read. | `last_accessed_at: 2026-06-19T14:00:00Z` |
| `promoted_at` | ISO 8601 datetime | No | Present only when explicitly promoted `volátil` → `perene`. **Presence overrides `class`** at runtime. | `promoted_at: 2026-06-19T12:00:00Z` |

### 1.3 Deprecation Fields (conditional — only when deprecated)

| Field | Type | Constraints |
|-------|------|-------------|
| `deprecated` | boolean | Must be `true` when deprecated. If `false`/absent, the other two must be absent. |
| `deprecated_at` | ISO 8601 datetime | **Required when `deprecated: true`.** |
| `deprecated_reason` | string | **Required when `deprecated: true`.** Should reference the superseding file path. |

### 1.4 Quarantine Fields (conditional — only when quarantined)

| Field | Type | Constraints |
|-------|------|-------------|
| `quarantined_at` | ISO 8601 datetime | Presence indicates quarantine. **Mutually exclusive with `deprecated: true`** (V-071). |
| `quarantine_reason` | string | **Required when `quarantined_at` present.** |
| `quarantine_expires_at` | ISO 8601 datetime | **Required when `quarantined_at` present.** Purge date; convention: exactly 30 days after `quarantined_at`. |

### 1.5 Legacy Retained (optional — preserved from pre-migration schema)

| Field | Type | Notes |
|-------|------|-------|
| `excrtx_type` | string | The **old** Acervo `type` (e.g. `fact`, `rule`, `workflow`, `tool`, `profile`, `lesson`, `context`). Renamed during migration to avoid collision with the OKF `type` field. No vocabulary constraint — preserves whatever value the original file had. |
| `nature` | string | Directory routing key used by `excrtx-memory-manager`. Coexists with OKF `type` — they serve different purposes (`type` = concept type; `nature` = directory routing). May be English (`context`, `knowledge`, `decisions`, `contracts`, `workflows`, `tools`, `skills`, `persona`) or Portuguese (`conhecimento`, `contexto`, `reflexoes`, `processos`, `ferramentas`, `instrucoes`). |
| `confidence` | string | Knowledge quality signal: `low`, `medium`, or `high`. |
| `sources` | list[string] | Provenance tracking — list of source URLs or references. |

### 1.6 OKF Optional (not used by Acervo by default)

| Field | Type | Notes |
|-------|------|-------|
| `resource` | string | Defined by OKF v0.1 for external resource references. The Acervo ignores it; OKF consumers may use it. Add per-file when relevant. |

---

## 2. The `type` vs `excrtx_type` Distinction

This is the single most important migration detail:

- **`type`** (OKF canonical) — the **concept type**. Vocabulary: `decision`, `memory`, `reflection`, `context`, `knowledge`, `artifact`. Derived from the file's directory path during migration (see [schema-spec.md §3.2](schema-spec.md)).
- **`excrtx_type`** (legacy retained) — the **old Acervo type**. Vocabulary: `fact`, `rule`, `workflow`, `tool`, `profile`, `lesson`, `context`, `project`, `domain`, `role`, `prompt`. Whatever value the file had before migration is preserved verbatim.

The two fields may carry the same string value (e.g. both `context`) — this is correct, because they have different semantics. **Never assume `type` and `excrtx_type` are interchangeable.** OKF consumers read `type`; the Acervo's own tooling may consult `excrtx_type` for legacy behavior.

Similarly, **`nature`** is a third orthogonal field: the directory routing key. `type` answers "what kind of knowledge is this?"; `nature` answers "which directory should this file live in?". A future ADR may consolidate `nature` into `type`, but for now they coexist.

---

## 3. Examples

### 3.1 New Volatile Knowledge

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
runtime. Hermes provides the execution layer; Exocórtex provides the identity,
methodology, and behavioral skills.
```

### 3.2 Deprecated Memory

```yaml
---
type: memory
title: Default LLM model is DeepSeek-V3
description: Previous default model, now superseded by MiniMax-M3
tags: [model, config, deepseek]
timestamp: 2026-05-01

class: volátil
created_at: 2026-05-01T09:00:00Z

deprecated: true
deprecated_at: 2026-06-19T10:30:00Z
deprecated_reason: "Superseded by memories/modelo-default-v2.md — MiniMax-M3 is now default"

nature: knowledge
confidence: high
---

Superseded by: [modelo-default-v2](../memories/modelo-default-v2.md)

DeepSeek-V3 was the default model from 2026-05-01 until 2026-06-19.
```

### 3.3 Quarantined File

```yaml
---
type: context
title: Exocortex-Dev sprint status — March 2026
description: Sprint context snapshot from March 2026, now stale
tags: [sprint, status, exocortex-dev, stale]
timestamp: 2026-03-01

class: volátil
created_at: 2026-03-01T07:00:00Z
last_accessed_at: 2026-03-15T11:20:00Z

quarantined_at: 2026-06-19T03:00:00Z
quarantine_reason: "Not accessed in 92 days (last read 2026-03-15)"
quarantine_expires_at: 2026-07-19T03:00:00Z

nature: context
---

This context snapshot is stale and has been quarantined by the syndic.
**Quarantine expires:** 2026-07-19. Promote to `perene` before expiry to preserve.
```

---

## 4. Validation Rule Summary

The validator script (`scripts/validate_frontmatter.py`) enforces 43 `ERROR` and 6 `WARN` rules (49 total). The `WARN` rules are V-004, V-022, V-025, V-026, V-072, V-075. Highlights:

| Category | Key Rules |
|----------|-----------|
| **Structural (V-001–V-004)** | File must start with `---`; closing `---` present; valid YAML; non-empty body (WARN). |
| **OKF Presence (V-010–V-014)** | `type`, `title`, `description`, `tags`, `timestamp` all required. |
| **OKF Values (V-020–V-030)** | `type` must be one of the 6 concept types; `tags` must be a YAML list; `timestamp` must be a valid `YYYY-MM-DD` date. WARN tier: `title` > 200 chars (V-022), `description` with newlines (V-025) or > 120 chars (V-026). |
| **Acervo Extension (V-040–V-046)** | `class` required (`perene`/`volátil`); `created_at` required (ISO 8601 UTC); `last_accessed_at`/`promoted_at` format-checked if present. |
| **Deprecation (V-050–V-056)** | If `deprecated: true` → `deprecated_at` + `deprecated_reason` required; if `deprecated` absent/false → the other two must NOT be present. |
| **Quarantine (V-060–V-068)** | If `quarantined_at` present → `quarantine_reason` + `quarantine_expires_at` required; expiry ≥ `quarantined_at`. |
| **Cross-Field (V-070–V-076)** | `created_at` date must equal `timestamp`; **deprecated XOR quarantined** (V-071 — never both); `promoted_at` present but `class: volátil` → WARN (V-072 — suggest updating `class` to `perene`); `confidence` outside `low`/`medium`/`high` → WARN (V-075). |

**Exit code:** `0` = pass (WARN allowed); `1` = one or more ERROR rules failed.

Full rule tables and migration derivation rules: see [schema-spec.md](schema-spec.md).

---

## 5. ISO 8601 Format Reference

| Field Type | Format | Regex | Example |
|------------|--------|-------|---------|
| Date | `YYYY-MM-DD` | `^\d{4}-\d{2}-\d{2}$` | `2026-06-19` |
| Datetime | `YYYY-MM-DDTHH:MM:SSZ` | `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$` | `2026-06-19T10:30:00Z` |

**No timezone offsets allowed** — all datetimes normalized to UTC (`Z`). The migration script converts offset-based timestamps to UTC during normalization.

---

## 6. Related Documents

- [ADR-013](ADR-013-frontmatter-schema-okf.md) — Schema decision
- [ADR-014](ADR-014-deprecation-policy.md) — Deprecation policy
- [ADR-015](ADR-015-quarantine-lifecycle.md) — Quarantine lifecycle
- [ADR-016](ADR-016-semantic-revision-on-insert.md) — Semantic revision on insert
- [ADR-017](ADR-017-okf-compatibility.md) — OKF v0.1 compatibility
- [ADR-018](ADR-018-autonomous-syndic.md) — Autonomous syndic
- [schema-spec.md](schema-spec.md) — Full detailed spec (migration derivation rules, full validation tables)
- [log-convention.md](log-convention.md) — `log.md` append-only format
- `scripts/validate_frontmatter.py` — Validator (enforces §4 rules)
- `scripts/migrate_frontmatter.py` — Migration script (one-time upgrade from legacy schema)
