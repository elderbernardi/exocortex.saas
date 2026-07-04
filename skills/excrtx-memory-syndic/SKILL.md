---
name: excrtx-memory-syndic
description: "Autonomous Acervo cleanup agent — scans for stale/deprecated files, quarantines eligible items, purges expired quarantines, reports consolidation candidates. Runs under manut profile."
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, acervo, syndic, cleanup, maintenance, autonomous]
    related_skills: [excrtx-memory-quarantine, excrtx-memory-deprecate, excrtx-memory-manager]
compiled_rules: |
  - Syndic operates autonomously under manut profile — no Draft-First for quarantine or purge operations (ADR-018).
  - The 30-day quarantine window is the safety net, not executive pre-approval — report after the cycle, not before.
  - Scan criteria: volátil files with last_accessed_at >90 days, deprecated files with deprecated_at >180 days, consolidation candidates (flagged, never auto-quarantined).
  - Perene files, promoted_at files, raw/ directories, and the macro/ layer are immune — never scanned for quarantine.
  - Purge files in .quarantine/ whose quarantine_expires_at has passed (30 days without restore).
  - Consolidation candidates are reported to the executive only — the syndic never quarantines them.
  - Delegates actual file moves, purges, and restores to excrtx-memory-quarantine — the syndic decides WHAT, the quarantine skill executes HOW.
  - Every cycle produces a summary report delivered to the executive's home channel.
  - All operations are dual-logged in .purge_log (global) and the origin container's log.md by the quarantine skill.
  - Idempotent: running the cycle twice in the same day produces no duplicate quarantines — a file already carrying quarantined_at is skipped.
  - Fail safe: if a file cannot be moved (permissions, missing path), log the error and continue the cycle — never abort on a single failure.
---

# Acervo Memory Syndic

Autonomous maintenance agent for the Acervo Cognitivo. Orchestrates the full
cleanup lifecycle from **ADR-018**: `SCAN → QUARANTINE → PURGE → REPORT`. Runs
under the `manut` profile, triggered by a weekly cron job or manual invocation.

The syndic is the **orchestrator** — it decides *what* to act on. The
**mechanics** (move files, update frontmatter, dual-log) are delegated to
`excrtx-memory-quarantine`. This separation ensures the quarantine skill's
invariants (immunity checks, 30-day window, dual logging) are always honored
regardless of who triggers the operation.
(fonte canônica dos thresholds: `global/contracts/memory-lifecycle-constants.md`)

## Acervo Location

```
ACERVO="${ACERVO:-${EXOCORTEX_HOME:-$HOME/exocortex}/acervo}"
[ -d "$ACERVO" ] || ACERVO="${HERMES_HOME:-$HOME/.hermes}/acervo"
```

All paths below are relative to `$ACERVO` unless stated otherwise.

## When to Use

Trigger the syndic cycle when any of the following hold:

- **Cron trigger (automatic).** Weekly schedule (suggested: Sunday 03:00 UTC)
  under the `manut` profile. Runs the full cycle without human intervention.
- **Manual invocation.** The executive says "clean the acervo", "run syndic",
  "run maintenance cycle", or similar. Executes the same full cycle on demand.
- **Post-insertion hook (event-driven).** After `excrtx-memory-deprecate`
  flags a file as deprecated during a WRITE, the syndic's next scheduled cycle
  will evaluate it for quarantine (after the 180-day deprecation window).

The syndic is **not** triggered per-file. It is a batch sweep over the entire
Acervo. Per-file quarantine (e.g., executive manually quarantining a specific
stale file) goes through `excrtx-memory-quarantine` directly.

## When NOT to Use

- **Do not use for semantic revision.** Detecting contradictions between a new
  file and existing ones is the job of `excrtx-memory-deprecate` (ADR-016). The
  syndic consumes the *result* of deprecation (long-deprecated files become
  quarantine candidates after 180 days), but does not perform deprecation itself.
- **Do not use for manual file operations.** If the executive asks to quarantine,
  restore, or purge a *specific* file, invoke `excrtx-memory-quarantine`
  directly. The syndic is a batch orchestrator, not a single-file tool.
- **Do not use for consolidation merges.** The syndic *detects* consolidation
  candidates and *reports* them. The actual decision to merge, deprecate, or
  quarantine overlapping files is an executive act. Never auto-action
  consolidation candidates.
- **Do not use outside the `manut` profile.** The syndic's Draft-First exemption
  (ADR-018) is scoped to the maintenance profile. Running it under `exec` or
  `evol` would bypass the profile separation that governs autonomous authority.
- **Do not use to modify file content.** The syndic moves files and updates
  lifecycle frontmatter (via the quarantine skill). It never edits the
  semantic content of a memory, decision, or context file.

## Procedure: Full Cycle

The syndic cycle is a six-step pipeline. Each step feeds the next. The cycle
is **idempotent** — running it twice in the same day produces no duplicate
quarantines or purges.

### Step 1 — Scan All Containers

Walk the Acervo tree and collect every `.md` file with frontmatter:

```
$ACERVO/micro/*/    (all microversos)
$ACERVO/global/
$ACERVO/shared/
```

**Exclude from the walk** (never enter these directories):

- `$ACERVO/.quarantine/` — already in the purge pipeline.
- `$ACERVO/macro/` — identity layer, always permanent, no `log.md`.
- Any `raw/` directory at any depth — immutable sources.
- `_meta/`, `_inbox/`, `_artifacts/`, `_tasks/`, `_routines/`, `_automations/` — structural/transient, not memory files.

For each `.md` file found, read its frontmatter and proceed to Step 2.

**Count** the total files scanned for the report (`Scanned: N files across M microversos`). `M` is the number of microverso directories under `micro/` that contributed at least one scanned file.

### Step 2 — Apply Immunity Filter

For each file from Step 1, check the [Immunity Rules](#immunity-rules). Immune
files are **skipped entirely** — they are not quarantine candidates and are
not counted in the quarantine total. They are still counted in the scanned
total.

### Step 3 — Evaluate Scan Criteria

For each non-immune file, evaluate the [Scan Criteria](#scan-criteria). Classify
each file as one of:

| Classification | Action |
|----------------|--------|
| **Stale volatile** | Quarantine candidate → Step 4 |
| **Long-deprecated** | Quarantine candidate → Step 4 |
| **Consolidation candidate** | Report only → Step 5 (no quarantine) |
| **None of the above** | Skip — file is healthy |

**Idempotency check:** before adding a file to the quarantine list, verify its
frontmatter does not already contain `quarantined_at`. If it does, the file was
already quarantined in a prior cycle (or by a manual operation) — skip it. This
prevents duplicate quarantines on repeated runs. (In practice, files already in
`.quarantine/` are excluded by the Step 1 walk — this check is a belt-and-suspenders guard for files that may have been quarantined in-place by a manual frontmatter edit.)

### Step 4 — Quarantine Eligible Files

For each file classified as stale-volatile or long-deprecated in Step 3:

1. **Delegate to `excrtx-memory-quarantine`** with:
   - `<original_path>` — the `$ACERVO`-relative path (e.g. `micro/exocortex-dev/knowledge/old-model-config.md`).
   - `<reason>` — a one-line reason string:
     - Stale volatile: `"Not accessed in N days (last read YYYY-MM-DD)"`
     - Long-deprecated: `"Long-deprecated (deprecated_at YYYY-MM-DD), quarantine window opened"`

2. **The quarantine skill** handles the actual move, frontmatter update
   (`quarantined_at`, `quarantine_reason`, `quarantine_expires_at`), and
   dual-logging (`.purge_log` + origin `log.md`). The syndic does not
   duplicate these operations.

3. **Fail-safe on error:** if the quarantine skill reports a failure (file
   not found, permission denied, immune-file refusal, already-quarantined),
   **log the error to the cycle report** under an `Errors:` section and
   **continue** to the next candidate. Never abort the cycle on a single
   failure.

**Count** the successfully quarantined files for the report.

### Step 5 — Purge Expired Quarantine Items

Scan `$ACERVO/.quarantine/` for files whose 30-day window has elapsed:

1. For each `.md` file under `.quarantine/` (excluding `.purge_log` and
   `README.md`), read its frontmatter `quarantine_expires_at`.
2. Compute `NOW` = current UTC datetime.
3. If `NOW >= quarantine_expires_at`, the file is **expired** — a purge target.
4. If `quarantine_expires_at` is missing or unparseable, **do not purge** —
   flag for review (data-integrity issue, not a purge signal).
5. **Delegate the purge to `excrtx-memory-quarantine`** (Purge procedure).
   The quarantine skill handles deletion, `.purge_log` appending, and origin
   `log.md` appending.

**Fail-safe on error:** if a purge fails, log the error and continue to the
next expired file.

**Count** the successfully purged files for the report.

### Step 6 — Detect Consolidation Candidates

This step is **detection only** — no files are moved, quarantined, or modified.

1. Within each container (microverso, `global/`, `shared/`), group active
   (non-quarantined, non-deprecated) `.md` files by **tag overlap**: files
   sharing 2+ tags are candidates.
2. For each group, check **title similarity** and **entity matching** (same
   model name, tool name, port number, config key mentioned in bodies).
3. If a group has 2+ files covering the same scope (heuristic — same subject
   entity, overlapping claims), flag it as a consolidation candidate.
4. Record the group in the cycle report (container path, file count, shared
   topic). Do NOT quarantine, do NOT deprecate, do NOT merge.

The executive reviews the report and decides which files to keep, deprecate,
or quarantine. The syndic's job ends at reporting.

### Step 7 — Generate Summary Report

After all steps complete, generate the [Summary Report](#report-format) and
deliver it to the executive's home channel. The report is the **only output**
of the cycle visible to the executive — it is a notification, not a permission
request.

**Delivery mechanism:** the cron job's stdout (or the manual invocation's
response) is the report. Under cron, this is routed to the executive's home
channel per the [Cron Configuration](#cron-configuration) section.

## Scan Criteria

Three candidate types (priority: stale-volatile → long-deprecated →
consolidation). See [references/scan-criteria.md](references/scan-criteria.md)
for full field-level tables, reason strings, and edge cases.

- **Stale volatile:** `class: volátil`, `last_accessed_at` >90 days,
  `promoted_at` absent, `quarantined_at` absent, `deprecated` not `true`.
  Reason: `"Not accessed in N days (last read YYYY-MM-DD)"`. If
  `last_accessed_at` is absent, fall back to `created_at`; if both absent,
  skip and flag for review.
- **Long-deprecated:** `deprecated: true`, `deprecated_at` >180 days,
  `quarantined_at` absent. Reason: `"Long-deprecated (deprecated_at
  YYYY-MM-DD), quarantine window opened"`. The quarantine skill strips
  deprecated fields (V-071) — the reason string preserves history.
- **Consolidation candidates:** 2+ files in the same container sharing 2+
  tags, with similar titles or matching key entities. **Report only — never
  auto-quarantined.** The executive decides.

## Immunity Rules

The following are **never** quarantined (excluded at Step 2 before scan
criteria). See [references/scan-criteria.md](references/scan-criteria.md) for
the full table with rationale.

- `class: perene` — durable governance (ADR-014).
- `promoted_at` present — overrides `class` at runtime (V-072); check
  **before** `class`.
- `raw/` directory — immutable sources (ADR-014).
- `macro/` layer — identity, always permanent.

Even if a perene or promoted file is `deprecated: true`, it remains immune —
flag it in the report, do not quarantine.

## Report Format

Every cycle produces exactly one summary report (ADR-018). The report is
localized to **PT-BR** — the executive's working language. File paths inside
the report stay in their original filesystem form (English ASCII,
`$ACERVO`-relative); only the human-readable labels are translated.

See [references/report-format.md](references/report-format.md) for the full
template, field semantics, error section format, zero-action report, and cron
configuration details (schedule, Hermes cron setup, manual invocation,
silent-failure detection).

Skeleton (PT-BR labels, English paths):

```
[RELATÓRIO DO SÍNDICO] YYYY-MM-DD
====================================
Escaneados: N arquivos em N microversos
Quarentenados: N arquivos
Purgados: N arquivos
Candidatos a consolidação: N (flagged for review)
Ocupação da quarentena: N arquivos
Próxima janela de purga: YYYY-MM-DD
```

## Pitfalls

- **Scanning `macro/` or `raw/`.** Both are immune by contract — `macro/` is
  identity (permanent, git-tracked, no `log.md`), `raw/` is immutable sources.
  Exclude both from the Step 1 walk.
- **Quarantining a `perene` or `promoted_at` file.** A `volátil` file with
  `promoted_at` looks normal but is immune. Check `promoted_at` *before*
  `class`. Even a perene file that is somehow `deprecated: true` remains
  immune — flag it, do not quarantine.
- **Purging without checking the restore window.** Purge only when
  `NOW >= quarantine_expires_at`. Never purge a file with missing or
  unparseable `quarantine_expires_at` — that is a data-integrity error, not
  consent to purge.
- **Forgetting to log.** The quarantine skill handles dual-logging
  (`.purge_log` + origin `log.md`). The syndic must not duplicate these
  entries but should verify they were written.
- **Auto-quarantining consolidation candidates.** Consolidation candidates are
  *reported*, never *actioned*. Auto-quarantining would silently remove files
  the executive may want to keep or merge.
- **Aborting on first error.** Log the error and continue. The fail-safe is
  per-file, not per-cycle. Aborting leaves stale files in active memory and
  breaks the weekly cadence.
- **Running under the wrong profile.** The Draft-First exemption (ADR-018) is
  scoped to `manut`. Always run under `manut`.
- **Duplicate quarantines on repeated runs.** The Step 1 walk excludes
  `.quarantine/`, and the Step 3 idempotency check skips files already
  carrying `quarantined_at`.
- **Forgetting the report on a zero-action cycle.** The zero-action report is
  the confirmation that the syndic ran. Suppressing it creates the same
  silent-failure signal as a cron crash.

## Verification

After every syndic cycle, confirm **all** of the following before considering
the cycle complete:

- [ ] **Scan coverage:** the walk covered all `micro/*/`, `global/`, and
      `shared/` directories. `macro/`, `raw/`, `.quarantine/`, and
      structural directories (`_meta/`, `_inbox/`, etc.) were excluded.
- [ ] **Immunity honored:** no `perene`, `promoted_at`, `raw/`, or `macro/`
      file was quarantined. The immunity filter checked `promoted_at` before
      `class`.
- [ ] **Scan criteria correct:** stale-volatile files had `last_accessed_at`
      >90 days; long-deprecated files had `deprecated_at` >180 days. Edge
      cases (missing `last_accessed_at`) were handled by fallback or flagged.
- [ ] **Quarantine delegated:** each quarantine was executed by
      `excrtx-memory-quarantine`, not by the syndic directly. The quarantine
      skill's verification checklist passed for each file.
- [ ] **Purge window checked:** each purged file had `quarantine_expires_at`
      in the past. No file with missing/unparseable expiry was purged.
- [ ] **Consolidation reported, not actioned:** consolidation candidates
      appear in the report only. No consolidation candidate was quarantined,
      deprecated, or merged.
- [ ] **Dual logging:** every quarantine and purge operation has entries in
      both `.purge_log` (global) and the origin container's `log.md`.
- [ ] **Idempotency:** no file was quarantined twice. Files already carrying
      `quarantined_at` were skipped.
- [ ] **Fail-safe:** if any file failed to quarantine or purge, the error was
      logged in the report's `Errors:` section and the cycle continued.
- [ ] **Report generated:** the summary report was produced and delivered to
      the executive's home channel. If the cycle had zero actions, the
      zero-action report was still produced.
- [ ] **Quarantine occupancy:** the report's `Quarantine occupancy` count
      matches the actual file count in `.quarantine/` at end of cycle.

Run the skill judge to confirm structural compliance:

```bash
python3 scripts/skill_judge.py --skill excrtx-memory-syndic --d1-only
```
