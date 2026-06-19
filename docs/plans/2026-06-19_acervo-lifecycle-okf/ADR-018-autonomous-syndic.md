# ADR-018: Autonomous Syndic — Self-Governing Acervo Cleanup

**Status:** Proposed
**Date:** 2026-06-19
**Decision by:** Elder Bernardi

## Context

The Acervo needs periodic cleanup (quarantine of stale files, purging of expired quarantine items, detection of consolidation candidates). Requiring executive approval for every quarantine/purge operation creates a bottleneck — the executive would need to review dozens of files per cycle, defeating the purpose of autonomous maintenance.

The Exocórtex has a maintenance profile (`manut`) designed for housekeeping. The Draft-First protocol (EX-08) requires approval for external actions, but quarantine and purge are **internal operations** — they move files within the local filesystem, not to external destinations.

## Decision

### Syndic Role

The **syndic** is the autonomous maintenance agent that operates the Acervo cleanup lifecycle. It runs under the `manut` profile and has full authority to:

1. **Scan** the Acervo for quarantine candidates (ADR-015, Phase 1).
2. **Quarantine** files that meet the criteria (ADR-015, Phase 2).
3. **Purge** files whose quarantine window has expired (ADR-015, Phase 3).
4. **Report** consolidation candidates to the executive (ADR-015, semi-autonomous).

### What the Syndic Cannot Do

- **Cannot quarantine `perene` files** — permanent knowledge is immune.
- **Cannot quarantine `promoted_at` files** — promoted artifacts are immune.
- **Cannot quarantine `raw/` or `macro/`** — sources and identity are immutable.
- **Cannot auto-quarantine consolidation candidates** — these require executive decision.
- **Cannot delete files outside `.quarantine/`** — purge only happens inside quarantine.
- **Cannot modify file content** — only move files and update frontmatter quarantine fields.

### Draft-First Exemption

The syndic is **exempt from Draft-First** for quarantine and purge operations. Rationale:

- These are **internal filesystem operations** (move, delete local files), not external actions.
- The quarantine window (30 days) is the safety net, not executive approval.
- The executive's intervention mechanism is **restore**, not pre-approval.

The syndic **is subject to Draft-First** for:
- Consolidation recommendations (these are proposals, not actions).
- Any operation that sends data outside the local filesystem.

### Trigger Mechanisms

| Trigger | Type | Action |
|---------|------|--------|
| Cron job (weekly) | Automatic | Full scan → quarantine → purge cycle |
| Manual invocation | On-demand | Executive says "clean the acervo" or "run syndic" |
| Post-insertion hook | Event-driven | After semantic revision deprecates a file, log it for next syndic cycle |

### Cron Configuration

```
Schedule: weekly (suggested: Sunday 03:00)
Profile: manut
Skill: excrtx-memory-syndic
Output: delivered to executive's home channel (summary report)
```

The cron output is a **summary report**, not a permission request. Format:

```
[SYNDIC REPORT] 2026-06-22
Scanned: 127 files across 10 microversos
Quarantined: 3 files (2 stale volatile, 1 long-deprecated)
Purged: 1 file (quarantine expired: memories/old-port-config.md)
Consolidation candidates: 2 (flagged for review)
Quarantine occupancy: 4 files (next purge window: 2026-07-22)
```

### Logging

Every syndic action is recorded in:
1. **`.purge_log`** — append-only log of all quarantine/purge/restore operations.
2. **`log.md`** of each affected microverso — human-readable per-domain audit trail.

## Consequences

- **Positive:** Acervo self-maintains without executive bottleneck.
- **Positive:** Full audit trail — every action logged in two places.
- **Positive:** Safety net via 30-day quarantine window + restore mechanism.
- **Negative:** Risk of quarantining something the executive wanted. Mitigation: 30-day window + restore + `perene` immunity.
- **Risk:** Cron job failure (silent). Mitigation: cron output delivered to home channel; if no report appears, executive knows syndic didn't run.
