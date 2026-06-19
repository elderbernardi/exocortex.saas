# ADR-017: OKF v0.1 Compatibility Strategy

**Status:** Proposed
**Date:** 2026-06-19
**Decision by:** Elder Bernardi

## Context

The Open Knowledge Format (OKF v0.1) defines a minimal, vendor-neutral standard for knowledge representation: markdown files with YAML frontmatter, where `type` is the only mandatory field, plus recommended fields `title`, `description`, `resource`, `tags`, `timestamp`. OKF is designed for interoperability — wikis written by different producers can be consumed by different agents without translation.

The Acervo Cognitivo is already structurally aligned with OKF (markdown + YAML frontmatter in a git repo). However, the current frontmatter schema does not guarantee OKF field presence, making the Acervo non-consumable by OKF-compatible tools without translation.

## Decision

### Superset Strategy

The Acervo frontmatter schema (ADR-013) is a **superset** of OKF v0.1. All OKF canonical fields are mandatory in the Acervo. Acervo extension fields are additional and do not conflict with OKF.

| OKF v0.1 Field | Acervo Status | Notes |
|----------------|---------------|-------|
| `type` | Mandatory | Acervo vocabulary is a subset of OKF's open-ended type space |
| `title` | Mandatory | Direct match |
| `description` | Mandatory | Direct match |
| `tags` | Mandatory | Direct match |
| `resource` | Optional (not in Acervo by default) | Can be added per-file for external references |
| `timestamp` | Mandatory | Maps to `created_at` with date-only granularity for OKF compatibility |

### Conformance Criteria

An Acervo file is **OKF-conformant** if:
1. It has YAML frontmatter.
2. Frontmatter contains `type`, `title`, `description`, `tags`, `timestamp`.
3. Body is valid markdown.
4. File path uses `/` as separator (standard on Linux/git).

Acervo extension fields (`class`, `created_at`, `last_accessed_at`, `promoted_at`, `deprecated`, etc.) do not affect OKF conformance — they are additional metadata that OKF consumers can ignore.

### Linking Convention

OKF uses standard markdown links for concept-to-concept relationships. The Acervo adopts this convention:

- **Supersede links:** `Supersedes: [old-title](../path/to/old.md)` in the body.
- **Cross-references:** Standard markdown links, same as today.
- **No proprietary link format.** No `[[wikilinks]]` — OKF uses standard markdown links.

### Index Files

OKF defines `index.md` as optional progressive disclosure. The Acervo already uses `index.md` per microverso. This is compatible.

OKF defines `log.md` as optional chronological history. The Acervo adopts this convention (see Task 02 for full spec).

### Future: OKF Export

A future task (not in this plan) could implement an OKF export tool that:
1. Reads an Acervo microverso.
2. Strips Acervo extension fields.
3. Outputs a clean OKF bundle.

This is not needed now — the superset strategy means Acervo files are already OKF-conformant as-is. But an export tool would be useful for sharing knowledge with external agents.

## Consequences

- **Positive:** Acervo is consumable by any OKF-compatible tool (visualizers, external agents, catalog exporters) without translation.
- **Positive:** Future interoperability with other OKF producers (e.g., ingesting an external OKF bundle into the Acervo).
- **Negative:** `timestamp` and `created_at` are technically redundant. Acceptable — `timestamp` is the OKF-compatible date-only field; `created_at` is the Acervo datetime-precision field. A future ADR may consolidate if OKF evolves to accept datetime.
- **Neutral:** `resource` field is not mandatory in the Acervo. Files that reference external resources can include it; others can omit.
