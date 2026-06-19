# ADR-016: Semantic Revision on Insert

**Status:** Proposed
**Date:** 2026-06-19
**Decision by:** Elder Bernardi

## Context

When a new memory is inserted into the Acervo, it may contradict an existing memory. Today, both coexist without signaling. The agent may retrieve the wrong version — the old, contradicted truth instead of the new, current truth.

## Decision

### Protocol: Semantic Revision on Insert

Every `WRITE` operation to the Acervo that creates a new file (not appending to existing) must trigger a **semantic revision check** before the write completes.

### Step 1: Detect Overlap

The agent searches the target microverso (and `global/` if applicable) for existing files that cover the same scope. Scope is determined by:

- **Tags overlap** — files sharing 2+ tags with the new content.
- **Title similarity** — files with semantically similar titles.
- **Entity matching** — files mentioning the same key entities (model names, tool names, port numbers, etc.).

Search mechanics: read `index.md` of the target microverso, scan titles and tags, read candidate files if needed.

### Step 2: Compare Truth

If overlap is detected, the agent reads the overlapping file(s) and compares the truth claims:

- **Direct contradiction** — new says "model is M3", old says "model is DeepSeek-V3" → deprecate old.
- **Partial overlap** — new is a subset or superset of old → depends on context. If new replaces old's claim, deprecate old. If new adds to old, don't deprecate.
- **Complementary** — new covers different aspect of same entity → don't deprecate. Both coexist.

### Step 3: Deprecate Predecessor

If direct contradiction is found:

1. Set on the old file:
   ```yaml
   deprecated: true
   deprecated_at: <now>
   deprecated_reason: "Superseded by <new-file-path> — <one-line why>"
   ```

2. Add to the new file body:
   ```markdown
   Supersedes: [old-memory-title](../path/to/old.md)
   ```

3. Log in `log.md`:
   ```markdown
   - DEPRECATED: <old-file-path> — superseded by <new-file-path>
   - CREATED: <new-file-path> (volátil)
   ```

### Step 4: Handle Ambiguity

If the agent cannot determine with confidence whether the new memory contradicts the old (ambiguous overlap):

- **Do not deprecate.** Write the new file with a note: `Potential overlap with: [old-file](../path/to/old.md) — review needed.`
- Log: `- CREATED: <new-file-path> (volátil) — potential overlap with <old-file-path>, not auto-deprecated`
- Flag for executive review in the next briefing or maintenance cycle.

### Scope of Search

| Write Target | Search Scope |
|--------------|--------------|
| `micro/{slug}/` | `micro/{slug}/` only (domain isolation) |
| `global/` | `global/` only |
| `shared/` | `shared/` + both referenced microversos |

Cross-microverso semantic conflicts are **not** checked — domain isolation is a hard boundary. A memory about model defaults in `exocortex-ops` does not deprecate a memory about model defaults in `commercial` — they are different domains.

### What Triggers Semantic Revision

- New file creation in `knowledge/`, `context/`, `contracts/`, `tools/` natures.
- **Not triggered for:** `decisions/` (decisions are append-only — new decisions may supersede old ones, but that's an explicit ADR, not an auto-deprecation), `reflections/` (reflections are subjective and don't contradict), `raw/` (immutable sources).

### Integration Point

This protocol is implemented in the `excrtx-memory-deprecate` skill, which is called by `excrtx-memory-manager` during the `WRITE` operation, after the Domain Filter and before the file is committed to disk.

## Consequences

- **Positive:** Contradictions are resolved at insert time. The Acervo self-corrects.
- **Positive:** Ambiguity is surfaced, not hidden. The executive can review flagged overlaps.
- **Negative:** Insertion latency increases (search + compare). Acceptable trade-off for knowledge integrity.
- **Risk:** False positive deprecations. Mitigation: conservative detection — only deprecate on clear, direct contradictions. Ambiguity → flag, don't deprecate.
