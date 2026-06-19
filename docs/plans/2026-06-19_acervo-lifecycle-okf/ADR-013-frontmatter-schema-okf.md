# ADR-013: Frontmatter Schema with OKF v0.1 Alignment

**Status:** Proposed
**Date:** 2026-06-19
**Decision by:** Elder Bernardi

## Context

The Acervo Cognitivo uses YAML frontmatter on markdown files, but the schema is inconsistent across microversos. Some files have `title`, `created`, `nature`, `type`, `tags`, `confidence`. Others omit fields or use different names. There is no mandatory field set, no lifecycle metadata, and no compatibility with external knowledge formats.

The Open Knowledge Format (OKF v0.1), published by Google Cloud on 2026-06-12, defines a minimal standard: markdown files with YAML frontmatter where `type` is the only mandatory field, plus recommended fields `title`, `description`, `resource`, `tags`, `timestamp`. OKF is designed for agent-to-agent knowledge sharing without translation.

## Decision

Adopt a two-tier frontmatter schema: **OKF Canonical** (mandatory, interoperable) + **Acervo Extension** (lifecycle governance).

### Tier 1: OKF Canonical Fields (mandatory on every file)

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Concept type. Acervo vocabulary: `decision`, `memory`, `reflection`, `context`, `knowledge`, `artifact` |
| `title` | string | Human-readable title |
| `description` | string | One-line summary |
| `tags` | list[string] | Taxonomy tags |
| `timestamp` | ISO 8601 date | Creation date (maps to `created_at`) |

### Tier 2: Acervo Extension Fields (lifecycle governance)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `class` | `perene` \| `volátil` | Yes | Governs lifecycle. Perene = never auto-deprecated. Volátil = deprecation candidate. |
| `created_at` | ISO 8601 datetime | Yes | Creation timestamp (equals `timestamp` but with time granularity) |
| `last_accessed_at` | ISO 8601 datetime | No | Updated by agent at runtime when file is read |
| `promoted_at` | ISO 8601 datetime | No | When explicitly promoted to perene. Presence = always perene regardless of `class`. |

### Tier 3: Deprecation Fields (conditional — present only when deprecated)

| Field | Type | Description |
|-------|------|-------------|
| `deprecated` | boolean | Must be `true` when deprecated |
| `deprecated_at` | ISO 8601 datetime | When deprecated |
| `deprecated_reason` | string | Why (e.g., "superseded by memories/modelo-default-v2.md") |

### Tier 4: Quarantine Fields (conditional — present only when quarantined)

| Field | Type | Description |
|-------|------|-------------|
| `quarantined_at` | ISO 8601 datetime | When moved to quarantine |
| `quarantine_reason` | string | Why (e.g., "not accessed in 92 days") |
| `quarantine_expires_at` | ISO 8601 datetime | 30 days from `quarantined_at` — purge date |

### Legacy Field Migration

Existing fields map to the new schema:

| Old Field | New Field | Notes |
|-----------|-----------|-------|
| `type` (e.g., `type: fact`) | `excrtx_type` | **Collision!** OKF `type` is the concept type. Old `type` renamed to `excrtx_type` to preserve data without collision. |
| `nature` | (retained, not deprecated) | Still used by `excrtx-memory-manager` for directory routing. Coexists with `type`. |
| `confidence` | (retained, optional) | Still useful for knowledge quality signaling. |
| `updated` | `last_accessed_at` | Renamed for precision. Old `updated` semantically meant "last modified", not "last accessed". New field is "last read by agent". |
| `sources` | (retained, optional) | Provenance tracking. |

### Example: Complete Frontmatter

```yaml
---
# OKF Canonical (mandatory)
type: memory
title: Default LLM model is MiniMax-M3
description: Current default model for Exocórtex operations
tags: [model, config, minimax]
timestamp: 2026-06-19
# Acervo Extension (lifecycle)
class: volátil
created_at: 2026-06-19T10:30:00Z
last_accessed_at: 2026-06-19T14:00:00Z
# Legacy (retained)
nature: knowledge
confidence: high
---
```

### Example: Deprecated Memory

```yaml
---
type: memory
title: Default LLM model is DeepSeek-V3
description: Previous default model, now superseded
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
```

## Consequences

- **Positive:** Frontmatter is now interoperable with any OKF-compatible tool. Lifecycle is queryable via YAML. Deprecation is explicit, not implicit.
- **Negative:** All existing files require migration (adding `type`, `timestamp`, `class`, `created_at`). This is a one-time cost.
- **Neutral:** `nature` coexists with `type`. They serve different purposes: `type` is the OKF concept type; `nature` is the Acervo directory routing key. Future ADR may consolidate.
