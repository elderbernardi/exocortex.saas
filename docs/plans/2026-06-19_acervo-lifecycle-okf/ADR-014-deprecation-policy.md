# ADR-014: Deprecation Policy for Transient Knowledge

**Status:** Proposed
**Date:** 2026-06-19
**Decision by:** Elder Bernardi

## Context

The Acervo stores both permanent decisions ("we chose PostgreSQL as the database") and transient state ("the default model is DeepSeek-V3"). Today, both coexist without distinction. When transient state changes, the old version remains active and the agent may retrieve it instead of the current truth.

## Decision

### Binary Classification

Every file in the Acervo is classified via the `class` frontmatter field:

| Class | Description | Examples | Lifecycle |
|-------|-------------|----------|-----------|
| **perene** | Permanent truth — decisions, architecture, identity, reflections, explicitly promoted artifacts | "ADR-006: Custom Skill vs MCP", "Executive values: honesty, quality" | Never auto-deprecated. Never quarantined. |
| **volátil** | Transient state — configurations, prices, model defaults, port numbers, versions | "Default model is M3", "Web UI port is 8787", "Minimax pricing: $0.10/M tokens" | Candidate for deprecation when superseded. Candidate for quarantine when stale. |

### Promotion Override

Any file with `promoted_at` set is **always perene**, regardless of `class` value. This allows the executive to explicitly promote a volatile fact to permanent status (e.g., "this configuration is now a architectural decision").

### Deprecation Trigger: Semantic Revision on Insert

When a new memory is inserted into the Acervo (see ADR-016 for full protocol), the agent must:

1. **Detect overlap** — search for existing memories covering the same scope/entity.
2. **Compare truth** — if the new memory contradicts the existing one, the existing one is deprecated.
3. **Mark deprecation** — set `deprecated: true`, `deprecated_at`, `deprecated_reason` on the old file.
4. **Link** — add a markdown link in the new file body: `Superseded: [old-memory](../path/to/old.md)`

### Deprecation ≠ Deletion

Deprecated files remain in the Acervo for audit trail. They are:
- **Ignored** by active retrieval (search skips `deprecated: true` files unless explicitly requested).
- **Candidates for quarantine** after 180 days in deprecated state (see ADR-015).
- **Never deleted** without going through the quarantine pipeline.

### What Cannot Be Auto-Deprecated

- Files with `class: perene` — only the executive can deprecate these.
- Files with `promoted_at` set — promoted artifacts are immutable to auto-deprecation.
- Files in `raw/` directories — sources are immutable by contract.

## Consequences

- **Positive:** Contradictory knowledge is resolved at insert time, not at retrieval time. The agent always retrieves current truth.
- **Positive:** Audit trail preserved — deprecated files show what was believed before and why it changed.
- **Negative:** Insertion becomes a two-step operation (write new + deprecate old). Slight overhead.
- **Risk:** Semantic overlap detection is heuristic, not deterministic. False positives (deprecating something that isn't actually contradicted) are possible. Mitigation: the agent should be conservative — only deprecate when the contradiction is clear, not when it's ambiguous.
