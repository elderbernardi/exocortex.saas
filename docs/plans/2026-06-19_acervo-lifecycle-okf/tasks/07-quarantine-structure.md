# Task 07: Build Quarantine Directory Structure

**Status:** pending
**Depends on:** ADR-015
**Produces:** `$ACERVO/.quarantine/` directory + `.purge_log`

## Context

The quarantine directory (ADR-015) must exist before the quarantine skill (Task 05) and syndic skill (Task 06) can operate. This is a simple setup task — create the directory, initialize the purge log, and document the structure.

## Deliverable

### 1. Create Directory

```bash
mkdir -p "$ACERVO/.quarantine"
```

### 2. Initialize Purge Log

Create `$ACERVO/.quarantine/.purge_log`:

```markdown
# Quarantine Purge Log

This file is append-only. Every quarantine, purge, and restore operation is logged here.
Do not edit existing entries.

## Format

MOVED: <original_path> → <quarantine_path> | reason: <reason> | expires: <date>
PURGED: <quarantine_path> | original: <original_path> | quarantined: <date> | purged: <date>
RESTORED: <quarantine_path> → <original_path> | restored: <date>

---

(No operations yet)
```

### 3. Document Structure

Create `$ACERVO/.quarantine/README.md`:

```markdown
# Quarantine Zone

This directory holds files removed from active Acervo memory pending permanent deletion.

## Rules

- Files here are NOT part of active memory. Agents do not retrieve them.
- Each file has a 30-day window from `quarantined_at`.
- After 30 days without restore, files are permanently deleted.
- Restore is available to the executive at any time within the window.

## Structure

Files preserve their original Acervo path:
  micro/{slug}/knowledge/old-file.md → .quarantine/micro/{slug}/knowledge/old-file.md

## Logs

- `.purge_log` — append-only log of all operations.
```

### 4. Add to .gitignore (if applicable)

If the Acervo is in a git repo, consider whether `.quarantine/` should be tracked. Recommendation: track the directory structure (`.gitkeep`) but not the quarantined files themselves (they're transient).

## Verification

- [ ] `$ACERVO/.quarantine/` directory exists
- [ ] `.purge_log` initialized with format documentation
- [ ] `README.md` exists in quarantine directory
- [ ] Directory is outside active memory tree (not under `micro/`, `global/`, `shared/`, `macro/`)
