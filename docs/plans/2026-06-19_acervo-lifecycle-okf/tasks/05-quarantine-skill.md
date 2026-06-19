# Task 05: Write `excrtx-memory-quarantine` Skill

**Status:** pending
**Depends on:** Task 01 (schema spec), ADR-015
**Produces:** `skills/excrtx-memory-quarantine/SKILL.md`
**Judge required:** Yes — must reach verdict `PASS` before promotion

## Context

This skill implements the quarantine mechanics (ADR-015). It provides the operations: move to quarantine, purge expired items, restore from quarantine. It is called by the syndic (Task 06) for autonomous cleanup, and can be called directly by the executive for manual operations.

## Skill Specification

### Frontmatter Requirements

```yaml
---
name: excrtx-memory-quarantine
description: "Quarantine lifecycle for Acervo files — move stale or deprecated files to quarantine, purge expired items, restore within 30-day window."
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, acervo, quarantine, cleanup, lifecycle]
    related_skills: [excrtx-memory-manager, excrtx-memory-deprecate, excrtx-memory-syndic]
compiled_rules: |
  - Quarantine moves files to $ACERVO/.quarantine/ preserving directory structure.
  - Quarantine is NOT part of active memory — agent does not retrieve quarantined files.
  - Each quarantined file gets: quarantined_at, quarantine_reason, quarantine_expires_at (30 days from quarantined_at).
  - Files in quarantine >30 days without restore are permanently deleted.
  - Perene files and promoted_at files are immune to quarantine.
  - raw/ and macro/ directories are immune to quarantine.
  - Every quarantine/purge/restore operation is logged in .purge_log and the origin microverso's log.md.
---
```

### Required Body Sections

1. **`## When to Use`** — called by syndic for autonomous cleanup; called by executive for manual quarantine/restore.
2. **`## When NOT to Use`** — don't quarantine perene/promoted/raw/macro files; don't use for consolidation (that's a report, not an action).
3. **`## Procedure: Quarantine`** — step-by-step: validate candidate is eligible → create quarantine path preserving structure → move file → add quarantine fields to frontmatter → update .purge_log → update log.md.
4. **`## Procedure: Purge`** — step-by-step: scan .quarantine/ for expired items → delete file → update .purge_log → update origin log.md.
5. **`## Procedure: Restore`** — step-by-step: validate within 30-day window → move file back to original path → strip quarantine fields from frontmatter → update .purge_log → update log.md.
6. **`## Quarantine Directory Structure`** — document the `$ACERVO/.quarantine/` layout.
7. **`## Immunity Rules`** — perene, promoted_at, raw/, macro/ are immune. How to check.
8. **`## Pitfalls`** — moving without preserving structure, forgetting .purge_log, purging without checking restore window, quarantining perene files.
9. **`## Verification`** — checklist: file moved correctly, frontmatter updated, both logs updated, quarantine directory structure preserved.

### Key Behavioral Rules

- **Move, not copy.** The file leaves its original location. No duplicates.
- **Preserve directory structure.** `micro/exocortex-dev/knowledge/old.md` → `.quarantine/micro/exocortex-dev/knowledge/old.md`.
- **30-day window is hard.** After 30 days, purge is irreversible. No exceptions.
- **Dual logging.** Every operation in both `.purge_log` (global) and `log.md` (per-microverso).
- **Frontmatter updates.** Quarantine fields added on quarantine, stripped on restore.

## Skill Judgment Pipeline

```bash
# D1 structural check
python3 scripts/skill_judge.py --skill excrtx-memory-quarantine --d1-only

# Full judge
python3 scripts/skill_judge.py --skill excrtx-memory-quarantine
```

Must reach `PASS` before promotion.

### Integration Test

1. Create a test volatile file with `last_accessed_at` 100 days ago.
2. Run quarantine operation.
3. Verify: file moved to `.quarantine/`, frontmatter has quarantine fields, `.purge_log` updated, `log.md` updated.
4. Run restore.
5. Verify: file back in original location, quarantine fields stripped, both logs updated.
6. Create a perene file, attempt quarantine — should be refused.

## Verification

- [ ] SKILL.md exists at `skills/excrtx-memory-quarantine/SKILL.md`
- [ ] D1 structural check passes
- [ ] Full judge verdict = `PASS`
- [ ] Integration test: quarantine moves file correctly
- [ ] Integration test: restore works within 30-day window
- [ ] Integration test: perene file refused
- [ ] Integration test: purge deletes expired file
- [ ] Skill added to bundle
- [ ] `compile_soul.py` run
