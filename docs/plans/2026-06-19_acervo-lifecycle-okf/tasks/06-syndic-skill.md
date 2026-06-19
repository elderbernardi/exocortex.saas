# Task 06: Write `excrtx-memory-syndic` Skill

**Status:** pending
**Depends on:** Task 04 (deprecate skill), Task 05 (quarantine skill), ADR-018
**Produces:** `skills/excrtx-memory-syndic/SKILL.md`
**Judge required:** Yes — must reach verdict `PASS` before promotion

## Context

The syndic is the autonomous maintenance agent (ADR-018). It orchestrates the full cleanup cycle: scan → quarantine → purge → report. It runs under the `manut` profile, triggered by cron or manual invocation. It calls `excrtx-memory-quarantine` for the actual file operations.

## Skill Specification

### Frontmatter Requirements

```yaml
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
  - Syndic operates autonomously under manut profile — no Draft-First for quarantine/purge.
  - Scan criteria: volátil files not accessed >90 days, deprecated files >180 days, consolidation candidates (flagged, not auto-quarantined).
  - Perene files, promoted_at files, raw/ and macro/ are immune — never scanned for quarantine.
  - Purge files in quarantine >30 days without restore.
  - Every cycle produces a summary report delivered to executive's home channel.
  - Consolidation candidates are reported, not actioned — executive decides.
  - All operations logged in .purge_log and origin microverso log.md.
---
```

### Required Body Sections

1. **`## When to Use`** — cron trigger (weekly), manual trigger ("clean the acervo", "run syndic"), post-insertion hook.
2. **`## When NOT to Use`** — don't use for semantic revision (that's `excrtx-memory-deprecate`); don't use for manual file operations (that's `excrtx-memory-quarantine`).
3. **`## Procedure: Full Cycle`** — the complete scan → quarantine → purge → report pipeline.
   - Step 1: Scan all microversos for candidates.
   - Step 2: Filter out immune files (perene, promoted, raw, macro).
   - Step 3: Quarantine eligible files (call `excrtx-memory-quarantine`).
   - Step 4: Purge expired quarantine items (call `excrtx-memory-quarantine`).
   - Step 5: Detect consolidation candidates (heuristic, generate report).
   - Step 6: Generate summary report.
4. **`## Scan Criteria`** — detailed conditions for each candidate type (stale volatile, long-deprecated, consolidation).
5. **`## Immunity Rules`** — what cannot be quarantined and why.
6. **`## Report Format`** — the exact format of the summary report delivered to the executive.
7. **`## Cron Configuration`** — how to set up the weekly cron job (schedule, profile, deliver).
8. **`## Pitfalls`** — scanning macro/, quarantining perene files, purging without checking restore window, silent cron failure, forgetting to log.
9. **`## Verification`** — checklist: scan covered all microversos, immune files excluded, quarantine operations logged, purge checked restore window, report generated.

### Key Behavioral Rules

- **Autonomous.** No Draft-First for quarantine/purge. The 30-day window is the safety net.
- **Report, don't ask.** The summary is delivered after the cycle, not before. The executive intervenes via restore, not pre-approval.
- **Consolidation = report only.** Never auto-quarantine consolidation candidates.
- **Idempotent.** Running the cycle twice in the same day should not produce duplicate quarantines.
- **Fail safe.** If a file can't be moved (permissions, missing), log the error and continue. Don't abort the cycle.

### Report Format

```
[SYNDIC REPORT] 2026-06-22
============================
Scanned: 127 files across 10 microversos
Quarantined: 3 files
  - micro/exocortex-dev/knowledge/old-model-config.md (stale: 95 days)
  - micro/exocortex-ops/context/port-numbers-v1.md (stale: 102 days)
  - micro/exocortex-dev/knowledge/deprecated-api.md (deprecated: 185 days)
Purged: 1 file
  - micro/exocortex-ops/knowledge/old-pricing.md (quarantine expired)
Consolidation candidates: 2 (flagged for review)
  - micro/exocortex-dev/knowledge/ — 3 files about model defaults
  - micro/exocortex-ops/context/ — 2 files about port configuration
Quarantine occupancy: 4 files
Next purge window: 2026-07-22
```

## Skill Judgment Pipeline

```bash
# D1 structural check
python3 scripts/skill_judge.py --skill excrtx-memory-syndic --d1-only

# Full judge
python3 scripts/skill_judge.py --skill excrtx-memory-syndic
```

Must reach `PASS` before promotion.

### Integration Test

1. Set up a test acervo with:
   - 1 stale volatile file (last_accessed_at 100 days ago)
   - 1 long-deprecated file (deprecated_at 200 days ago)
   - 1 perene file (should be immune)
   - 1 expired quarantine item (quarantined_at 35 days ago)
2. Run syndic cycle.
3. Verify: stale file quarantined, deprecated file quarantined, perene file untouched, expired item purged, report generated.

## Verification

- [ ] SKILL.md exists at `skills/excrtx-memory-syndic/SKILL.md`
- [ ] D1 structural check passes
- [ ] Full judge verdict = `PASS`
- [ ] Integration test: stale volatile quarantined
- [ ] Integration test: long-deprecated quarantined
- [ ] Integration test: perene file immune
- [ ] Integration test: expired quarantine purged
- [ ] Integration test: report generated with correct format
- [ ] Skill added to bundle
- [ ] `compile_soul.py` run
