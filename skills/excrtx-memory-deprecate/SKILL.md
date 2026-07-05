---
name: excrtx-memory-deprecate
description: >-
  Marks Acervo memories that are junk or wrong (were never true, or are no longer
  worth keeping) as deprecated, feeding the quarantine pipeline. Junk/wrongness ONLY:
  replaced-but-was-true content is supersession and routes through acervoctl
  apply-supersede (conflict protocol, 08 §4), never through this skill.
version: 2.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, acervo, deprecation, junk, wrongness, lifecycle]
    related_skills: [excrtx-memory-manager, excrtx-memory-quarantine, excrtx-memory-syndic]
compiled_rules: |
  - Deprecation marks junk/wrongness ONLY: content that was never true, or is no longer worth keeping. Replaced truth (price, config, status changed) is SUPERSESSION — route it through `acervoctl apply-supersede`, never through deprecation.
  - When deprecating: set deprecated: true, deprecated_at (ISO 8601 UTC), deprecated_reason (why it is wrong/junk), and status: deprecated on the file; append a DEPRECATED entry to the container's log.md.
  - Never deprecate: class: perene files, promoted_at files, raw/ sources, files already deprecated, decisions, or files in another microverso — flag those for executive review instead.
  - Conservative rule: deprecate only on clear wrongness. When in doubt, flag for the executive via the maintenance digest — do not deprecate.
---

# Memory Deprecate

Implements the **junk/wrongness half** of the Deprecation Policy (ADR-014), narrowed
by the memory-v2 conflict protocol (08 §4). `deprecated` means: **was never true, or
is no longer worth keeping** — a bad extraction, a hallucinated claim, a duplicate,
speculation with no source, an assertion the executive declares wrong.

It is **not** the path for replaced truth. In Schema v0.2, `superseded ≠ deprecated`:
when a new memory *replaces* an old one that **was true at the time** (price changed,
config changed, status moved), that is **supersession** and it is applied by the
conflict protocol in `excrtx-memory-manager` via:

```bash
python3 scripts/acervoctl.py apply-supersede --new <new-file> --old <old-file>
```

**Supersession never routes through this skill.** Genuine disputes (both sides have
standing sources, or the target is `perene`/a decision) go through
`acervoctl open-dispute` and the executive — also never through this skill.

Deprecation is **not** deletion. Deprecated files remain for audit trail, are
skipped by active retrieval, and become quarantine candidates after 180 days
(ADR-015). The executive can always reverse a deprecation.

## When to Use

Trigger this skill when a specific existing file has been **judged wrong or junk**:

- The write-path conflict protocol (`excrtx-memory-manager` WRITE, 08 §4) determined
  the old content **was never true** — not merely replaced. Example: a fact extracted
  incorrectly from a document, an entity attribute that was always wrong.
- The **executive** declares a memory wrong or worthless and asks for its removal
  from active truth.
- An **audit** (syndic, dedup sweep, doctor) surfaces junk: sourceless speculation,
  broken duplicates, collector's-fallacy leftovers with no scope.

The action runs inside the target's container only (see [Scope Rules](#scope-rules)).

## When NOT to Use

- **Supersession** — the old claim was true and got replaced by a newer state of the
  world. Use `acervoctl apply-supersede` (via the manager's conflict protocol). This
  is the single most important boundary of this skill.
- **Genuine dispute** — both claims have standing sources, or the target is
  `perene`/a decision. Use `acervoctl open-dispute`; the executive resolves.
- **`decisions/`** — Decisions are immutable once active. A wrong decision is
  superseded by a new decision (explicit executive act), never auto-deprecated.
- **`raw/`** — Source files are immutable by contract (ADR-014). Never modify,
  deprecate, or quarantine anything in `raw/`.
- **`macro/`** — Identity-layer changes are tracked in git, not in the Acervo
  lifecycle. There is no `log.md` for `macro/`.
- **Files being quarantined** — A file with `quarantined_at` set is already in
  the purge pipeline. Do not deprecate it; the syndic owns its fate.

## Procedure

Follow the 4-step protocol. Each step has a hard gate — do not skip ahead.

### Step 1 — Classify: is this actually junk/wrongness?

Before touching the target file, confirm the relationship class. Only ONE class
belongs to this skill:

| Class | Definition | Route |
|-------|------------|-------|
| **Junk / wrongness** | The claim **was never true** (bad extraction, hallucination, factual error) or is **no longer worth keeping** (sourceless speculation, unusable duplicate). | **This skill** (Step 3). |
| **Supersession** | The old claim was true; the world changed (new price, new config, new status) and a newer object replaces it. | `acervoctl apply-supersede --new --old` — STOP here, hand back to `excrtx-memory-manager`. |
| **Genuine dispute** | Two claims disagree and both have standing sources; or the target is `perene`/a decision. | `acervoctl open-dispute --a --b --title --scope` + digest item — STOP, the executive resolves. |
| **Coexist / augmentation** | Different aspects, scopes, or timeframes of the same subject. | No action; at most a `relates_to` link. STOP. |

**Conservative principle:** if you cannot classify with confidence, treat it as
ambiguous (Step 4). Never deprecate on a hunch.

### Step 2 — Immunity gates

Skip (and flag instead of deprecating) any target that is:

- `class: perene` or has `promoted_at` set (perene immunity — executive-only);
- a `decision` (immutable; wrong decisions are superseded by new decisions);
- under `raw/` or `_inbox/` (immutable evidence);
- already `deprecated: true` / `status: deprecated` (idempotency — skip silently);
- already `quarantined_at` (the syndic owns it);
- in a different microverso than the one you are operating in (domain isolation).

### Step 3 — Apply deprecation

For a confirmed junk/wrong target:

1. **Set the deprecation fields** on the file's frontmatter (see
   [Deprecation Format](#deprecation-format)) — including `status: deprecated`
   (Schema v0.2 rule V2-032: the status scalar and the deprecation trio must agree).
2. **Append a `DEPRECATED` entry to the container's `log.md`** (see
   [Deprecation Format](#deprecation-format)).
3. If multiple files are junk (e.g. a duplicate cluster), deprecate each one with
   its own `DEPRECATED` log entry.

The file stays in place; the syndic will quarantine it after 180 days (ADR-015).

### Step 4 — Handle Ambiguity

If Step 1 cannot classify the relationship with confidence:

1. **Do not deprecate.** Leave the target untouched.
2. **Flag for executive review** via the maintenance digest (one line: the two
   paths + the doubt). The executive decides: deprecate, supersede, dispute, or
   leave as-is.
3. If the trigger was a write in progress, the new file may carry a body note
   `Potential overlap with: [title](../path/to/old.md) — review needed.` so the
   doubt is visible at read time.

## Scope Rules

### Domain isolation (hard boundary)

Deprecation **never** crosses container boundaries. A wrong memory in
`micro/exocortex-ops/` does not authorize touching files in `micro/commercial/`
— they are different domains with independent truth.

| Operation target | Action scope |
|------------------|--------------|
| `micro/{slug}/` | `micro/{slug}/` only |
| `global/` | `global/` only |
| `shared/` | `shared/` only; cross-microverso wrongness is flagged (Step 4), never auto-deprecated |

### Perene immunity

Files with any of the following are **never** auto-deprecated:

- `class: perene`
- `promoted_at` is present (presence overrides `class` at runtime per
  schema-spec §1.2 — the file is treated as `perene` regardless of the `class`
  value)

If a perene file appears to be wrong or contradicted, that is a **genuine
dispute**: route it through `acervoctl open-dispute` (Step 1) or flag it (Step 4).
The executive must explicitly decide the fate of a perene file — this skill never
does it automatically.

### Idempotency

If the old file already has `deprecated: true`, skip it. Running the check twice
on the same new file must not produce duplicate deprecations or duplicate log
entries. Before writing a `DEPRECATED` entry, verify the old file does not
already have `deprecated: true`.

## Deprecation Format

### Target file — frontmatter fields

Set the deprecation trio plus the status scalar on the target file's frontmatter
(Schema v0.2, rule V2-032 — trio and status must agree):

```yaml
status: deprecated
deprecated: true
deprecated_at: 2026-07-04T10:30:00Z
deprecated_reason: "Wrong extraction — claim never held; source misread (see raw/relatorio-q2.pdf)"
```

Rules:
- `deprecated_at` — current UTC datetime, format `YYYY-MM-DDTHH:MM:SSZ`.
- `deprecated_reason` — non-empty string stating **why the content is wrong or
  junk** (and, when applicable, who judged it: conflict protocol, executive, audit).
  It is NOT a "superseded by" pointer — if you are writing a replacement path here,
  you are superseding, not deprecating: use `apply-supersede` instead.
- Do not set `superseded_by` — that field belongs exclusively to the supersession
  pipeline.
- Do not modify any other frontmatter field on the target file. Do not touch
  `last_accessed_at` — deprecation is not a read.

### Log entry — log.md

Append a `DEPRECATED` entry to the container's `log.md` (per log-convention §2):

```markdown
- DEPRECATED: <file-relative-path> — <one-line wrongness/junk reason>
```

Rules:
- `<file-relative-path>` is relative to the container root (the microverso
  directory, `global/`, or `shared/`), using forward slashes. Never absolute,
  never `./` prefix.
- One bullet per deprecation. If multiple files are deprecated, one bullet each.
- Follow the append protocol from log-convention §4: find or create today's
  `## YYYY-MM-DD` heading (chronological ascending — newest at bottom), append
  the bullet below the last bullet under that heading.
- Locate the log using the `_meta/`-first rule: if `{container}/_meta/` exists,
  the log is at `{container}/_meta/log.md`; otherwise `{container}/log.md`.
- Never edit existing log lines — append only.

## Pitfalls

- **Deprecating a supersession** — The classic error this v2 exists to kill. If
  the old claim was true and the world changed, the old file must become
  `status: superseded` with a `superseded_by` link via `apply-supersede` —
  deprecating it erases the temporal truth chain ("what did we believe in Q2"
  becomes unanswerable). If your `deprecated_reason` starts with "superseded
  by...", stop and reroute.
- **Auto-resolving a dispute** — Two sourced claims that disagree are not
  "one of them is junk". Open a `conflict` object (`open-dispute`) and let the
  executive resolve. Deprecating one side silently is a unilateral verdict.
- **False positive wrongness** — "MiniMax pricing" vs "MiniMax rate limits" share
  tags and entity but are complementary, not wrong. Always read the target file
  and classify (Step 1) before deprecating. When uncertain, flag (Step 4).
- **Cross-microverso contamination** — Acting outside the target's container
  violates domain isolation. Hard-boundary the operation to the container. See
  [Scope Rules](#scope-rules).
- **Deprecating a perene file or a decision** — Both are immune; route as
  dispute or flag for the executive. See [Scope Rules](#scope-rules).
- **Forgetting `status: deprecated`** — Setting the trio without flipping the
  status scalar violates V2-032 and leaves the file visible to status-filtered
  retrieval. Set both, atomically.
- **Forgetting to update log.md** — A deprecation without a `DEPRECATED` log
  entry is an incomplete operation. The syndic will detect the gap on its next
  scan. Always append the log entry in the same operation as the frontmatter
  update.
- **Deprecating an already-deprecated file** — Idempotency violation. Always
  check `deprecated: true` / `status: deprecated` before writing. Duplicate
  deprecations produce duplicate log entries and confuse the audit trail.
- **Modifying the file beyond deprecation fields** — Do not rewrite the body,
  do not change tags, do not update `last_accessed_at`. Only `status` and the
  deprecation trio change.

## Verification

Before declaring the deprecation complete, verify:

- [ ] The relationship was classified (Step 1) and is genuinely junk/wrongness —
      not supersession (→ `apply-supersede`), not dispute (→ `open-dispute`),
      not coexist.
- [ ] The operation stayed inside the correct container (domain isolation).
- [ ] No perene file (`class: perene` or `promoted_at` present), decision, or
      `raw/` source was deprecated.
- [ ] No already-deprecated file was re-deprecated (idempotency).
- [ ] For each deprecated file: `status: deprecated`, `deprecated: true`,
      `deprecated_at` (valid ISO 8601 UTC), and `deprecated_reason` (non-empty,
      states the wrongness — no "superseded by" pointers) are all set.
- [ ] `superseded_by` was NOT touched.
- [ ] No other frontmatter field was modified.
- [ ] The container's `log.md` has a `DEPRECATED` entry per file, using the
      exact format from [Deprecation Format](#deprecation-format).
- [ ] The log entry was appended (not inserted mid-file), under today's date
      heading, without editing any existing line.
- [ ] If ambiguity was encountered (Step 4): nothing was deprecated and the item
      was flagged for executive review in the digest.
