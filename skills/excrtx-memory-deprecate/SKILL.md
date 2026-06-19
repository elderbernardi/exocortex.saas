---
name: excrtx-memory-deprecate
description: >-
  Semantic revision on insert — detects contradictions between a new Acervo memory
  and existing ones in the same microverso, deprecates superseded volatile files
  automatically, and flags ambiguous overlaps for executive review. Called by
  excrtx-memory-manager during WRITE, before the new file is committed to disk.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, acervo, deprecation, semantic-revision, lifecycle]
    related_skills: [excrtx-memory-manager, excrtx-memory-quarantine, excrtx-memory-syndic]
compiled_rules: |
  - On every new file creation in knowledge/, context/, contracts/, tools/ natures, run a semantic revision check before the WRITE commits.
  - Search the target container (microverso, global/, or shared/) for overlapping files using tag overlap (2+ shared tags), title similarity, and entity matching.
  - If a direct contradiction is found: deprecate the old file by setting deprecated: true, deprecated_at (ISO 8601 UTC), deprecated_reason (references the superseding file). Add a "Supersedes:" markdown link in the new file body.
  - If overlap is partial and the new file replaces the old's claim: deprecate the old. If the new file adds to the old: both coexist, do not deprecate.
  - If overlap is complementary (different aspect of same entity): both coexist, do not deprecate.
  - If the relationship is ambiguous: do NOT deprecate. Write the new file with a "Potential overlap with:" note and flag for executive review.
  - Never deprecate files with class: perene or with promoted_at set — these are immune to auto-deprecation.
  - Never deprecate across microverso boundaries — domain isolation is a hard boundary.
  - Never deprecate files already marked deprecated: true — idempotent; skip.
  - Log every deprecation in the owning container's log.md as a DEPRECATED entry per the log-convention.
  - Conservative detection: only deprecate on clear, direct contradictions. When in doubt, flag — do not deprecate.
---

# Memory Deprecate

Implements the **Semantic Revision on Insert** protocol (ADR-016) and the
**Deprecation Policy** (ADR-014). This skill is invoked by `excrtx-memory-manager`
during the `WRITE` operation, after the Domain Filter and before the new file is
committed to disk. Its purpose: detect whether the incoming file contradicts an
existing file in the same container, and if so, deprecate the predecessor —
keeping the Acervo self-correcting at insert time rather than at retrieval time.

Deprecation is **not** deletion. Deprecated files remain for audit trail, are
skipped by active retrieval, and become quarantine candidates after 180 days
(ADR-015). The executive can always reverse a deprecation by promoting the file
to `perene`.

## When to Use

Trigger this skill when **all** of the following hold:

- `excrtx-memory-manager` is performing a `WRITE` that creates a **new file**
  (not appending to an existing one).
- The new file's nature is one of: `knowledge/`, `context/`, `contracts/`,
  `tools/`. These are the natures where truth can be contradicted and superseded.
- The new file's `class` is `volátil` (or will default to `volátil` per
  schema-spec §3.3). `perene` files are new truth by definition and do not
  trigger deprecation of predecessors.

The check runs inside the write target's container only (see [Scope Rules](#scope-rules)).

## When NOT to Use

Do **not** trigger semantic revision for writes to:

- **`decisions/`** — Decisions are append-only. A new ADR may supersede an old
  one, but that is an explicit executive act, not an auto-deprecation. New
  decisions get their own ADR number and reference the prior one in prose.
- **`reflections/`** — Reflections are subjective. Two reflections on the same
  topic are complementary perspectives, never contradictions.
- **`raw/`** — Source files are immutable by contract (ADR-014). Never modify,
  deprecate, or quarantine anything in `raw/`.
- **`macro/`** — Identity-layer changes are tracked in git, not in the Acervo
  lifecycle. There is no `log.md` for `macro/`.
- **Appends to an existing file** — Semantic revision only applies to **new file
  creation**. Editing an existing file is an `UPDATED` log entry, not a
  deprecation event.
- **Files being quarantined** — A file with `quarantined_at` set is already in
  the purge pipeline. Do not deprecate it; the syndic owns its fate.

## Procedure

Follow the 4-step protocol from ADR-016. Each step has a hard gate — do not
skip ahead.

### Step 1 — Detect Overlap

Search the target container (per [Scope Rules](#scope-rules)) for existing files
that cover the same scope. Use three signals; any one is sufficient to flag a
candidate:

| Signal | Threshold | How to check |
|--------|-----------|--------------|
| **Tags overlap** | 2+ tags shared with the new file | Read `index.md` of the container; compare `tags` arrays. |
| **Title similarity** | Semantically similar titles (same subject/entity) | Scan titles in `index.md`; read candidate if title is ambiguous. |
| **Entity matching** | Same key entity mentioned (model name, tool name, port number, config key) | Grep the container for entity tokens extracted from the new file's body. |

Skip any candidate that is already `deprecated: true` — it is already superseded
and not a live conflict. Skip any candidate with `class: perene` or `promoted_at`
set — perene files are immune (see [Scope Rules](#scope-rules)).

If no candidates are found → the new file is original. Proceed to commit. No
deprecation, no log entry beyond the standard `CREATED` entry (which
`excrtx-memory-manager` writes).

### Step 2 — Compare Truth

For each overlap candidate, read the file and compare its truth claims against
the new file. Classify the relationship:

| Relationship | Definition | Action |
|--------------|------------|--------|
| **Direct contradiction** | New and old make mutually exclusive claims about the same fact (e.g., "model is M3" vs "model is DeepSeek-V3"). | Deprecate the old file (Step 3). |
| **Partial overlap — replacement** | New is a subset or superset of old, and the new claim replaces the old's claim (e.g., "default model is M3 with 128k context" supersedes "default model is M3"). | Deprecate the old file (Step 3). |
| **Partial overlap — augmentation** | New adds detail to old without invalidating it (e.g., old says "port is 8787", new says "port is 8787, configurable via env var"). | Both coexist. Do not deprecate. |
| **Complementary** | New covers a different aspect of the same entity (e.g., old: pricing; new: rate limits). | Both coexist. Do not deprecate. |

**Conservative principle:** if you cannot classify the relationship with
confidence, treat it as ambiguous (Step 4). Do not deprecate on a hunch.

### Step 3 — Deprecate Predecessor

When Step 2 identifies a direct contradiction or replacement overlap:

1. **Set deprecation fields on the old file** (see [Deprecation Format](#deprecation-format)).
2. **Add a `Supersedes:` link in the new file body** (see [Deprecation Format](#deprecation-format)).
3. **Append a `DEPRECATED` entry to the container's `log.md`** (see
   [Deprecation Format](#deprecation-format)).
4. The standard `CREATED` entry for the new file is written by
   `excrtx-memory-manager` as part of the WRITE operation — this skill does not
   duplicate it.

If multiple candidates are contradicted, deprecate each one following the same
format. Each gets its own `DEPRECATED` log entry and its own `Supersedes:` link
in the new file (one line per superseded file).

### Step 4 — Handle Ambiguity

If Step 2 cannot classify the relationship with confidence:

1. **Do not deprecate** the old file. Leave it untouched.
2. **Add a note to the new file body:**
   ```markdown
   Potential overlap with: [old-file-title](../path/to/old.md) — review needed.
   ```
3. **Append to `log.md`** — write the `CREATED` entry for the new file WITH the
   ambiguity note appended, as a single combined line:
   ```markdown
   - CREATED: <new-file-path> (volátil) — potential overlap with <old-file-path>, not auto-deprecated
   ```
   **Ownership handoff (ambiguity path only):** when this skill is invoked by
   `excrtx-memory-manager` during a WRITE and reaches Step 4, this skill owns
   the `CREATED` log entry and writes it directly. `excrtx-memory-manager` must
   NOT write a separate `CREATED` entry in this case — a single combined write
   avoids two entries for the same new file. This handoff is specific to the
   ambiguity path; on the non-ambiguous paths (Steps 1 and 3) the standard
   `CREATED` entry continues to be owned by `excrtx-memory-manager` as noted in
   those steps.
4. **Flag for executive review.** The ambiguity is surfaced in the next
   briefing or maintenance cycle. The executive decides: deprecate, merge, or
   leave both.

## Scope Rules

### Domain isolation (hard boundary)

Semantic revision **never** crosses container boundaries. A memory about model
defaults in `micro/exocortex-ops/` does not deprecate a memory about model
defaults in `micro/commercial/` — they are different domains with independent
truth.

### Search scope per write target

| Write target | Search scope |
|--------------|--------------|
| `micro/{slug}/` | `micro/{slug}/` only |
| `global/` | `global/` only |
| `shared/` | `shared/` + both referenced microversos (if the shared file names them) |

Cross-microverso conflicts in `shared/` are flagged as ambiguity (Step 4), never
auto-deprecated — the executive must resolve cross-domain contradictions.

### Perene immunity

Files with any of the following are **never** auto-deprecated:

- `class: perene`
- `promoted_at` is present (presence overrides `class` at runtime per
  schema-spec §1.2 — the file is treated as `perene` regardless of the `class`
  value)

If a perene file appears to be contradicted by a new volatile file, treat it as
**ambiguous** (Step 4). The executive must explicitly decide whether to
deprecate a perene file — this skill never does it automatically.

### Idempotency

If the old file already has `deprecated: true`, skip it. Running the check twice
on the same new file must not produce duplicate deprecations or duplicate log
entries. Before writing a `DEPRECATED` entry, verify the old file does not
already have `deprecated: true`.

## Deprecation Format

### Old file — frontmatter fields

Set exactly three fields on the old file's frontmatter (per schema-spec §1.3):

```yaml
deprecated: true
deprecated_at: 2026-06-19T10:30:00Z
deprecated_reason: "Superseded by knowledge/modelo-default-v2.md — MiniMax-M3 is now default"
```

Rules:
- `deprecated_at` — current UTC datetime, format `YYYY-MM-DDTHH:MM:SSZ`.
- `deprecated_reason` — non-empty string. Must reference the superseding file's
  relative path (from the container root) and a one-line explanation.
- Do not modify any other frontmatter field on the old file. Do not touch
  `last_accessed_at` — deprecation is not a read.

### New file — body link

Add a single line at the top of the new file's body (after frontmatter, before
any other content):

```markdown
Supersedes: [old-file-title](../path/to/old.md)
```

If multiple files are superseded, add one line per file:

```markdown
Supersedes:
- [old-file-1-title](../path/to/old1.md)
- [old-file-2-title](../path/to/old2.md)
```

The link path is relative from the new file's location to the old file's
location. Use forward slashes. The link text is the old file's `title`
frontmatter value.

### Log entry — log.md

Append a `DEPRECATED` entry to the container's `log.md` (per log-convention §2):

```markdown
- DEPRECATED: <old-file-relative-path> — superseded by <new-file-relative-path>
```

Rules:
- `<old-file-relative-path>` and `<new-file-relative-path>` are relative to the
  container root (the microverso directory, `global/`, or `shared/`), using
  forward slashes. Never absolute, never `./` prefix.
- One bullet per deprecation. If multiple files are deprecated, one bullet each.
- Follow the append protocol from log-convention §4: find or create today's
  `## YYYY-MM-DD` heading (chronological ascending — newest at bottom), append
  the bullet below the last bullet under that heading.
- Locate the log using the `_meta/`-first rule: if `{container}/_meta/` exists,
  the log is at `{container}/_meta/log.md`; otherwise `{container}/log.md`.
- Never edit existing log lines — append only.

## Pitfalls

- **False positive deprecation** — The overlap heuristics (tags, title, entity)
  are fuzzy. A file about "MiniMax pricing" and a file about "MiniMax rate
  limits" share tags and entity but are complementary, not contradictory. Always
  read the candidate file and classify the relationship (Step 2) before
  deprecating. When uncertain, flag (Step 4) — do not deprecate.
- **Cross-microverso contamination** — Searching outside the write target's
  container violates domain isolation. Hard-boundary the search to the
  container. See [Scope Rules](#scope-rules) for domain isolation details.
- **Deprecating a perene file** — Perene files are immune; treat contradictions
  as ambiguity (Step 4). See [Scope Rules](#scope-rules) for perene immunity
  details.
- **Forgetting to update log.md** — A deprecation without a `DEPRECATED` log
  entry is an incomplete operation. The syndic will detect the gap on its next
  scan. Always append the log entry in the same operation as the frontmatter
  update.
- **Forgetting the Supersedes link** — The new file must reference what it
  supersedes. Without the link, the audit trail is broken — a reader of the new
  file cannot find the predecessor.
- **Deprecating an already-deprecated file** — Idempotency violation. Always
  check `deprecated: true` on the candidate before writing. Duplicate
  deprecations produce duplicate log entries and confuse the audit trail.
- **Modifying the old file beyond deprecation fields** — Do not rewrite the old
  file's body, do not change its tags, do not update `last_accessed_at`. Only
  the three deprecation fields are added.
- **Treating augmentation as contradiction** — "Port is 8787" (old) and "Port is
  8787, configurable via PORT env var" (new) is augmentation, not contradiction.
  Both coexist. Deprecating the old file here loses the original concise
  statement for no reason.

## Verification

Before declaring the semantic revision complete, verify:

- [ ] Overlap search was performed in the correct container (domain isolation
      respected — no cross-microverso search).
- [ ] Every overlap candidate was read and its relationship classified (direct
      contradiction, replacement, augmentation, complementary, or ambiguous).
- [ ] No perene file (`class: perene` or `promoted_at` present) was deprecated.
- [ ] No already-deprecated file (`deprecated: true`) was re-deprecated.
- [ ] For each deprecated file: `deprecated: true`, `deprecated_at` (valid ISO
      8601 UTC), and `deprecated_reason` (non-empty, references superseding
      file) are all set on the old file's frontmatter.
- [ ] No other frontmatter field on the old file was modified.
- [ ] The new file body contains a `Supersedes:` link (or links) pointing to
      each deprecated file.
- [ ] The container's `log.md` has a `DEPRECATED` entry for each deprecated
      file, using the exact format from [Deprecation Format](#deprecation-format).
- [ ] The log entry was appended (not inserted mid-file), under today's date
      heading, without editing any existing line.
- [ ] If ambiguity was encountered (Step 4): the new file has a "Potential
      overlap with:" note, and the ambiguity is flagged for executive review.
- [ ] No `DEPRECATED` entry was written for a relationship classified as
      augmentation or complementary — those coexist.
