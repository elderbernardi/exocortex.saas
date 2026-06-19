## Procedure: Purge

Permanently delete files whose 30-day quarantine window has elapsed. **Purge is irreversible.** Run as a sweep over `.quarantine/`.

1. **Scan `.quarantine/` for expired items.** For each `.md` file under `$ACERVO/.quarantine/`:
   - Read its frontmatter `quarantine_expires_at`.
   - Compute `NOW` = current UTC datetime.
   - If `NOW >= quarantine_expires_at`, the file is **expired** and is a purge target.
   - If `quarantine_expires_at` is missing or unparseable, **do not purge** — flag for review (a quarantined file must always have the field; its absence is a data-integrity problem, not a purge signal).

2. **For each expired file, recover the original path.** The original path is reconstructable by stripping the `.quarantine/` prefix from the file's location:
   ```
   .quarantine/micro/exocortex-dev/knowledge/old-model-config.md
     → original_path = micro/exocortex-dev/knowledge/old-model-config.md
   ```
   (If a `.purge_log` `MOVED:` entry exists for this file, cross-check the recorded `<original_path>` matches; prefer the logged value on discrepancy and flag the mismatch.)

3. **Delete the file permanently:**
   ```bash
   rm "$ACERVO/.quarantine/<restored-relative-path>"
   ```
   No backup, no trash, no recovery. Confirm deletion with `test ! -e`.

4. **Append to `.purge_log`:**
   ```
   PURGED: <quarantine_path> | original: <original_path> | quarantined: <quarantined_at> | purged: <NOW>
   ```
   `<quarantined_at>` comes from the deleted file's frontmatter (captured before deletion). `<NOW>` is the purge timestamp.

5. **Append to the origin container's `log.md`** (resolved from `<original_path>` via the [logging convention](#logging-convention)):
   ```
   - PURGED: <container-relative-path> — quarantine expired (30 days)
   ```
   The tail `quarantine expired (30 days)` is literal — purge is logged only for this reason.

### Purge — Verification

- [ ] Every expired file is gone from `.quarantine/`.
- [ ] No non-expired file was touched.
- [ ] Each purge has a `PURGED:` line in `.purge_log` with original path and both timestamps.
- [ ] Each origin `log.md` has a `PURGED:` entry with the literal tail.
