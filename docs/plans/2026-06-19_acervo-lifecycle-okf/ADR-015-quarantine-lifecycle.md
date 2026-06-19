# ADR-015: Quarantine Lifecycle — Safe Cleanup with Purge Window

**Status:** Proposed
**Date:** 2026-06-19
**Decision by:** Elder Bernardi

## Context

The Acervo grows monotonically. Deprecated files, stale configurations, and superseded memories accumulate without cleanup. Direct deletion is unsafe — a file may be needed later. A safety window between "candidate for removal" and "permanent deletion" is required.

## Decision

### Three-Phase Lifecycle

```
SCAN → QUARANTINE → PURGE
```

No file is ever deleted directly. Every file passes through quarantine first.

### Phase 1: Scan (Autonomous)

The syndic agent (see ADR-018) scans the Acervo for quarantine candidates:

| Candidate Type | Condition |
|----------------|-----------|
| Stale volatile | `class: volátil` AND `last_accessed_at` > 90 days ago |
| Long-deprecated | `deprecated: true` AND `deprecated_at` > 180 days ago |
| Consolidation candidates | Multiple files covering same scope (heuristic — flag for executive review, not auto-quarantine) |

**Excluded from scan:** `class: perene` files, `promoted_at` files, `raw/` directories, `macro/` layer (identity — always permanent).

### Phase 2: Quarantine (Autonomous)

Files identified in scan are **moved** (not copied) to `$ACERVO/.quarantine/`:

```
$ACERVO/.quarantine/
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
└── .purge_log
```

**Quarantine properties:**
- **Not part of active memory.** The agent does not retrieve quarantined files in normal operations. Search, context loading, and briefing skip `.quarantine/` entirely.
- Each file retains its frontmatter and gains: `quarantined_at`, `quarantine_reason`, `quarantine_expires_at` (30 days from `quarantined_at`).
- The original `log.md` of the microverso records: `QUARANTINED: <path> — <reason>`.
- The `.purge_log` records: `MOVED: <original_path> → <quarantine_path> | reason: <reason> | expires: <date>`.

### Phase 3: Purge (Autonomous)

After 30 days in quarantine without restore:
- The file is **permanently deleted** from `.quarantine/`.
- The `.purge_log` records: `PURGED: <quarantine_path> | original: <original_path> | quarantined: <date> | purged: <date>`.
- The `log.md` of the origin microverso records: `PURGED: <path> — quarantine expired (30 days)`.

**Purge is irreversible.** After 30 days, the file is gone. No backup, no recovery.

### Restore (Executive-Initiated)

The executive can restore a quarantined file at any time within the 30-day window:
- File is moved back to its original location.
- Quarantine fields (`quarantined_at`, `quarantine_reason`, `quarantine_expires_at`) are removed.
- The `log.md` records: `RESTORED: <path> — restored from quarantine by executive`.
- The `.purge_log` records: `RESTORED: <quarantine_path> → <original_path> | restored: <date>`.

### Consolidation Candidates (Semi-Autonomous)

When the scan detects multiple files covering the same scope (heuristic overlap), these are **not** auto-quarantined. Instead:
- A report is generated listing the candidates.
- The report is delivered to the executive (via cron job output or manual trigger).
- The executive decides which to keep, which to deprecate, and which to quarantine.

## Consequences

- **Positive:** Safe cleanup — 30-day window prevents accidental knowledge loss.
- **Positive:** Autonomous — no executive approval needed for quarantine or purge (only for consolidation).
- **Positive:** Full audit trail — `.purge_log` and `log.md` record every movement.
- **Negative:** 30-day window is a balance. Too short → risk of losing needed knowledge. Too long → quarantine grows. Adjustable via parameter.
- **Risk:** Consolidation heuristic may produce false positives. Mitigation: never auto-quarantine consolidation candidates; always defer to executive.
