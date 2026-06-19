---
name: excrtx-memory-quarantine
description: "Quarantine lifecycle for Acervo files — move stale or deprecated files to quarantine, purge expired items, restore within 30-day window."
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - acervo
    - quarantine
    - cleanup
    - lifecycle
    - purge
    - restore
    related_skills:
    - excrtx-memory-manager
    - excrtx-memory-deprecate
    - excrtx-memory-syndic
compiled_rules: |
  - Quarantine MOVES files to $ACERVO/.quarantine/ preserving directory structure — never copies; the file leaves its original location.
  - Quarantine is NOT active memory — search, context loading, and briefing skip .quarantine/ entirely.
  - Each quarantined file gets quarantined_at, quarantine_reason, quarantine_expires_at (= quarantined_at + exactly 30 days, UTC).
  - Files in quarantine >30 days without restore are permanently purged — irreversible, no backup, no recovery.
  - Perene files, promoted_at files, raw/ directories, and the macro/ layer are immune — never quarantine them.
  - A file cannot be simultaneously deprecated and quarantined — strip deprecation fields when quarantining a deprecated file.
  - Every quarantine, purge, and restore is dual-logged in .purge_log (global) AND the origin container's log.md.
---

# Acervo Memory Quarantine

Implements the three-phase quarantine lifecycle from **ADR-015** (`SCAN → QUARANTINE → PURGE`) plus the executive-initiated **RESTORE**. No Acervo file is ever deleted directly — every removal passes through a 30-day quarantine window first.

This skill is the *mechanics* layer. It does not decide *what* to quarantine (that is the syndic's scan, ADR-018) — it executes the move, purge, and restore operations correctly once a candidate is identified.

## Acervo Location

```
ACERVO="${HERMES_HOME:-$HOME/.hermes}/acervo"
```

All paths below are relative to `$ACERVO` unless stated otherwise. The quarantine root is `$ACERVO/.quarantine/`.

## When to Use

- The **syndic** (running under `manut`, ADR-018) identified a quarantine candidate during its scan and asks this skill to execute the move.
- The **executive** manually requests that a specific stale or superseded file be quarantined.
- A scheduled **purge sweep** needs to delete files whose 30-day quarantine window has expired.
- The **executive** requests restoration of a file still inside its 30-day quarantine window.

Typical candidate signals (identified by the scan, not by this skill):
- `class: volátil` AND `last_accessed_at` older than 90 days (stale volatile).
- `deprecated: true` AND `deprecated_at` older than 180 days (long-deprecated).

## When NOT to Use

- **Do not quarantine immune files.** `class: perene`, any file with `promoted_at` present, anything under a `raw/` directory, and anything in the `macro/` layer are permanently immune (see [Immunity Rules](#immunity-rules)). Refuse and report.
- **Do not use for consolidation.** When the scan detects multiple files covering the same scope, that is a *report* for executive review, not a quarantine action. Never auto-quarantine consolidation candidates.
- **Do not use for direct deletion.** There is no "delete" operation here. Everything routes through quarantine first. If you need a file gone, quarantine it and let the 30-day window elapse.
- **Do not quarantine a file already in `.quarantine/`.** It is already in the pipeline. Re-quarantining resets the clock and loses audit history.
- **Do not use as a deprecation substitute.** Deprecation (ADR-014) marks a file superseded but keeps it active and readable; quarantine removes it from active memory. They are different lifecycle states — and mutually exclusive in frontmatter (V-071).


All three procedures share two invariants: every file operation is a **MOVE** (never a copy), and every operation is **dual-logged** (`.purge_log` + origin `log.md`). The skeletons below are executable as written; the linked references carry the exact inputs, frontmatter snippets, path-derivation examples, and edge cases. The consolidated [Verification](#verification) section gates all three.

## Procedure: Quarantine

Move a candidate file from its active location into `.quarantine/`, preserving structure, stamping quarantine fields, and dual-logging the operation.

**Inputs:** `<original_path>` (`$ACERVO`-relative), `<reason>` (one line).

1. **Validate eligibility** (stop and report on first failure): file exists at `<original_path>`; **not immune** ([Immunity Rules](#immunity-rules)); not already under `.quarantine/`; frontmatter has no `quarantined_at`.
2. **Compute the quarantine path:** prepend `.quarantine/` and mirror the full tree (`mkdir -p` intermediate dirs). e.g. `micro/x/knowledge/a.md` → `.quarantine/micro/x/knowledge/a.md`.
3. **Move, don't copy:** `mv "$ACERVO/<original_path>" "$ACERVO/<quarantine_path>"`; assert the original path is gone (`test ! -e`).
4. **Stamp frontmatter:** add `quarantined_at` = NOW (UTC `YYYY-MM-DDTHH:MM:SSZ`), `quarantine_reason` = `<reason>`, `quarantine_expires_at` = NOW + exactly 30 days. If the file is `deprecated: true`, **strip** `deprecated`/`deprecated_at`/`deprecated_reason` first (V-071 — mutually exclusive). Leave all other fields untouched.
5. **Append to `.purge_log`:** `MOVED: <original> → <quarantine> | reason: <reason> | expires: <EXPIRES>`.
6. **Append to origin `log.md`** (`_meta/`-first rule, container-relative path): `- QUARANTINED: <container-relative-path> — <reason>`.

Full step detail, inputs, and edge cases: [references/procedure-quarantine.md](references/procedure-quarantine.md).

## Procedure: Purge

Permanently delete files whose 30-day quarantine window has elapsed. **Purge is irreversible** — no backup, no recovery. Run as a sweep over `.quarantine/`.

1. **Scan `.quarantine/`** for `.md` files (skip `.purge_log`, `README.md`). For each, read `quarantine_expires_at` and compute `NOW` (UTC). A file is a purge target only when `NOW >= quarantine_expires_at`. **Missing/unparseable expiry → do not purge**; flag for review (data-integrity error, not consent).
2. **Recover the original path** by stripping the `.quarantine/` prefix; cross-check against the `MOVED:` entry in `.purge_log` and prefer the logged value on mismatch (flag the discrepancy).
3. **Delete permanently:** `rm "$ACERVO/<quarantine_path>"`; confirm with `test ! -e`.
4. **Append to `.purge_log`:** `PURGED: <quarantine> | original: <original> | quarantined: <quarantined_at> | purged: <NOW>` (capture `<quarantined_at>` before deletion).
5. **Append to origin `log.md`:** `- PURGED: <container-relative-path> — quarantine expired (30 days)` (tail is literal).

Full step detail and the batch-timeout guidance: [references/procedure-purge.md](references/procedure-purge.md).

## Procedure: Restore

Move a quarantined file back to its original location within the 30-day window. **Restore is executive-initiated** — the syndic never restores on its own.

1. **Validate the window is open:** read `quarantine_expires_at`, compute `NOW`. If `NOW >= quarantine_expires_at` → **refuse** (file is purged or earmarked; no override). Missing/unparseable expiry → refuse and flag.
2. **Compute the original path** by stripping the `.quarantine/` prefix (cross-check the `MOVED:` entry); `mkdir -p` the original location if needed.
3. **Move back, don't copy:** `mv "$ACERVO/<quarantine_path>" "$ACERVO/<original_path>"`; verify the file is gone from `.quarantine/`.
4. **Strip the quarantine fields** (`quarantined_at`, `quarantine_reason`, `quarantine_expires_at`). The file returns to active memory in its prior state. Do **not** reintroduce deprecation fields stripped at quarantine time — re-deprecation is a separate action.
5. **Append to `.purge_log`:** `RESTORED: <quarantine> → <original> | restored: <NOW>`.
6. **Append to origin `log.md`:** `- RESTORED: <container-relative-path> — restored from quarantine by executive` (tail is literal).

Full step detail: [references/procedure-restore.md](references/procedure-restore.md).

## Quarantine Directory Structure

```
$ACERVO/.quarantine/
├── README.md              # explains the directory (not a memory file)
├── .purge_log             # global append-only audit log of every move/purge/restore
├── micro/
│   ├── exocortex-dev/
│   │   └── knowledge/
│   │       └── old-model-config.md
│   └── exocortex-ops/
│       └── context/
│           └── port-numbers-v1.md
├── global/
│   └── tools/
│       └── deprecated-api.md
└── shared/
    └── cross-refs/
        └── stale-bridge.md
```

Properties:
- The structure under `.quarantine/` **mirrors** the `$ACERVO` tree. A file's original location is always recoverable by stripping the `.quarantine/` prefix.
- `.quarantine/` is **not part of active memory.** Search, context loading, briefing, and the `excrtx-memory-manager` READ/SEARCH operations skip it entirely. A quarantined file is invisible to normal agent operation.
- `.purge_log` is the single global audit trail. It is append-only.
- `README.md` is a human note, not indexed knowledge.

## Immunity Rules

The following are **never** quarantined. The quarantine procedure must refuse them and report the immunity reason.

| Immunity | How to check | Why |
|----------|--------------|-----|
| `class: perene` | frontmatter `class == "perene"` | Perene files are durable governance — never auto-deprecated or removed. |
| `promoted_at` present | frontmatter has a `promoted_at` field (any value) | `promoted_at` overrides `class` at runtime (V-072) — the file is treated as `perene` even if `class` still reads `volátil`. Promotion is an explicit executive act protecting the file. |
| `raw/` directory | path contains a `raw/` segment | Raw sources are immutable by contract — never modified, never removed. |
| `macro/` layer | path starts with `macro/` | The Macroverso is identity — always permanent, tracked in git, never quarantined. |

**Check order:** `promoted_at` → `class` → path segments (`raw/`, `macro/`). Check `promoted_at` *before* `class`, because a `volátil` file with `promoted_at` is immune despite its `class` value.

## Logging Convention

Every operation writes to **two** logs. Omitting either breaks the audit trail.

### `.purge_log` (global)

Location: `$ACERVO/.quarantine/.purge_log`. Append-only. Paths are `$ACERVO`-relative. One line per event:

| Event | Format |
|-------|--------|
| Quarantine | `MOVED: <original> → <quarantine> \| reason: <reason> \| expires: <expires>` |
| Purge | `PURGED: <quarantine> \| original: <original> \| quarantined: <quarantined_at> \| purged: <NOW>` |
| Restore | `RESTORED: <quarantine> → <original> \| restored: <NOW>` |

### `log.md` (per origin container)

Location resolved with the **`_meta/`-first rule**:
- For `micro/{slug}/` files: `micro/{slug}/_meta/log.md` if `_meta/` exists, else `micro/{slug}/log.md`.
- For `global/` files: `global/_meta/log.md` if `global/_meta/` exists, else `global/log.md`.
- For `shared/` files: `shared/_meta/log.md` if `shared/_meta/` exists, else `shared/log.md`.
- `macro/` has **no** `log.md` — and is immune anyway.

Always check for `_meta/` first; never assume. Paths in entries are **container-relative** (e.g. `knowledge/old-model-config.md`), forward slashes, no `./`. Entries are single bullets, appended under today's `## YYYY-MM-DD` heading, chronological ascending (newest at bottom), append-only — never edit existing lines.

| Entry type | Exact format |
|------------|--------------|
| `QUARANTINED` | `- QUARANTINED: <container-relative-path> — <reason>` |
| `PURGED` | `- PURGED: <container-relative-path> — quarantine expired (30 days)` |
| `RESTORED` | `- RESTORED: <container-relative-path> — restored from quarantine by executive` |

The `PURGED` and `RESTORED` tails are **literal** strings — they are the only reasons those entry types are written.

## Pitfalls

- **Copying instead of moving.** Quarantine is a MOVE — the file leaves its original location. A copy leaves a stale duplicate in active memory, defeating the purpose. After `mv`, assert the original path no longer exists.
- **Flattening the directory structure.** Dumping every quarantined file into `.quarantine/` root destroys the ability to reconstruct the original path. Always mirror the full tree: `micro/exocortex-dev/knowledge/x.md` → `.quarantine/micro/exocortex-dev/knowledge/x.md`.
- **Forgetting `.purge_log`.** The global audit log is the only place that records the original→quarantine mapping for files from *any* microverso. Without it, purge and restore cannot reliably reconstruct original paths. Always append the `MOVED:`/`PURGED:`/`RESTORED:` line.
- **Forgetting the origin `log.md`.** The per-container log is the human-facing history. A quarantine with no `log.md` entry is a silent disappearance. Always resolve the log via the `_meta/`-first rule and append.
- **Purging without checking the restore window.** A file must be purged only when `NOW >= quarantine_expires_at`. Purging early destroys a file the executive could still have restored. Always read `quarantine_expires_at` from frontmatter and compare against current UTC time.
- **Quarantining a perene / promoted file.** Immunity is hard. A `volátil` file with `promoted_at` looks like a normal volatile — but `promoted_at` makes it immune. Check `promoted_at` *before* `class`.
- **Leaving `deprecated: true` on a quarantined file.** V-071 forbids simultaneous deprecation and quarantine. A long-deprecated candidate must have its deprecation fields stripped when quarantined, or the file fails schema validation.
- **Restoring deprecation on restore.** Restore returns a file to *active* memory. Re-introducing `deprecated` fields that were stripped at quarantine time would silently re-deprecate a file the executive just rescued. If it should be deprecated again, run the deprecation skill separately.
- **Re-quarantining a quarantined file.** Resetting `quarantined_at` discards the original expiry and audit trail. If a file is already in `.quarantine/`, do not quarantine it again.
- **Missing/`NULL` expiry as a purge signal.** A quarantined file without `quarantine_expires_at` is a data-integrity error, not consent to purge. Flag it for review; never purge on the absence of the field.
- **Using quarantine for consolidation.** Multiple overlapping files are a *report* for the executive, not an auto-quarantine action. Consolidation candidates are never quarantined without an explicit executive decision.
- **Manual frontmatter edits creating phantom quarantines.** A file with `quarantined_at` stamped but still sitting in its original directory (e.g. someone hand-edited the frontmatter without moving it) will be double-counted — the purge sweep sees the expiry but the file is not actually under `.quarantine/`. Always verify the file is physically in `.quarantine/` before purging; do not trust the frontmatter alone.
- **Large Acervo purge timeouts.** A purge sweep over 200+ quarantined files may exceed the scan timeout (frontmatter read per file adds up). Process in batches — e.g. 50 files per sweep — and resume from the last processed path. Log each batch separately in `.purge_log` so partial progress is auditable.

## Verification

After any quarantine, purge, or restore operation, confirm **all** of the following before considering the task complete:

- [ ] **Quarantine:** original path empty; quarantine path holds the file with content intact; frontmatter has the three `quarantine_*` fields with `quarantine_expires_at` = `quarantined_at` + 30 days; deprecation fields stripped (if applicable); `MOVED:` line in `.purge_log`; `QUARANTINED:` entry in origin `log.md`.
- [ ] **Purge:** expired file deleted from `.quarantine/`; no non-expired file touched; `PURGED:` line in `.purge_log` (with original path + both timestamps); `PURGED:` entry in origin `log.md` with literal tail.
- [ ] **Restore:** file back at original path; gone from `.quarantine/`; no `quarantine_*` fields in frontmatter; `RESTORED:` line in `.purge_log`; `RESTORED:` entry in origin `log.md` with literal tail.
- [ ] **Immunity honored:** no `perene`, `promoted_at`, `raw/`, or `macro/` file was quarantined.
- [ ] **Structure preserved:** the `.quarantine/` subtree mirrors the `$ACERVO` tree — original paths are reconstructable by stripping the `.quarantine/` prefix.
- [ ] **Dual logging:** every operation appears in *both* `.purge_log` and the origin container's `log.md`.

Run the skill judge to confirm structural compliance:

```bash
python3 scripts/skill_judge.py --skill excrtx-memory-quarantine --d1-only
```
