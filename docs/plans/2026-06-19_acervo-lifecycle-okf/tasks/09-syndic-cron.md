# Task 09: Create Syndic Cron Job

**Status:** done
**Depends on:** Task 06 (syndic skill promoted)
**Produces:** Cron job entry in Hermes

## Context

The syndic (ADR-018) needs to run autonomously on a weekly schedule. This task creates the cron job in Hermes that triggers the syndic skill under the `manut` profile and delivers the summary report to the executive's home channel.

## Deliverable

### Cron Job Configuration

Using the Hermes cron system:

- **Schedule:** Weekly, suggested Sunday 03:00 (`0 3 * * 0` or `weekly`)
- **Profile:** `manut`
- **Skill:** `excrtx-memory-syndic`
- **Deliver:** `origin` (executive's home channel — Telegram)
- **Model:** Use the default maintenance model (lower cost model acceptable for maintenance tasks)

### Prompt for Cron Job

```
Run the Acervo Cognitivo syndic cycle. Execute the full scan → quarantine → purge → report pipeline as defined in the excrtx-memory-syndic skill. Deliver the summary report to the executive.
```

### Setup Steps

1. Verify syndic skill is promoted (verdict PASS, added to bundle, compiled).
2. Verify quarantine directory exists (Task 07).
3. Create cron job:

```bash
hermes cron add \
  --name "Acervo Syndic" \
  --schedule "0 3 * * 0" \
  --profile manut \
  --skill excrtx-memory-syndic \
  --deliver origin \
  --prompt "Run the Acervo Cognitivo syndic cycle. Execute the full scan → quarantine → purge → report pipeline as defined in the excrtx-memory-syndic skill. Deliver the summary report to the executive."
```

4. Verify cron job is listed:

```bash
hermes cron list
```

5. Run a dry-run (manual trigger) to verify the cycle works end-to-end:

```bash
hermes -p manut --skill excrtx-memory-syndic
```

### Edge Cases to Handle

- **Empty Acervo:** If no files match scan criteria, report should say "No candidates found" and exit cleanly.
- **Permission errors:** If a file can't be moved, log error in report and continue.
- **Large Acervo:** If scan takes long, the skill should handle it gracefully (stream results, don't timeout).

## Verification

- [x] Cron job created and listed in `hermes cron list` (ID: b82e9f700fe4)
- [x] Schedule is weekly (`0 3 * * 0` — Sunday 03:00)
- [ ] Profile is `manut` — N/A: `hermes cron create` CLI does not support `--profile`; per task instructions, profile-based execution skipped when unsupported
- [x] Deliver target is `origin` (executive's home channel)
- [ ] Manual dry-run produces a summary report — SKIPPED: task explicitly says "Do NOT run the syndic manually (migration in Task 08 may still be in progress)"
- [ ] Report format matches ADR-018 specification — deferred to first scheduled run
- [ ] No errors on empty scan — deferred to first scheduled run
