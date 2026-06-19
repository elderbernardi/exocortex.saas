## Procedure: Restore

Move a quarantined file back to its original location within the 30-day window. **Restore is executive-initiated** — the syndic never restores on its own.

**Inputs:** `<quarantine_path>` (or the original path; the file is located under `.quarantine/`).

1. **Validate the restore window is still open:**
   - Read the file's frontmatter `quarantine_expires_at`.
   - Compute `NOW` = current UTC datetime.
   - If `NOW >= quarantine_expires_at` → **refuse**: *"Quarantine window has expired. The file has been (or will be) purged. Restore is no longer possible."* After expiry, the file is gone or earmarked for deletion — there is no override.
   - If `quarantine_expires_at` is missing/unparseable → refuse and flag for review.

2. **Compute the original path** by stripping the `.quarantine/` prefix (cross-check against the `MOVED:` entry in `.purge_log`):
   ```
   .quarantine/micro/exocortex-dev/knowledge/old-model-config.md
     → micro/exocortex-dev/knowledge/old-model-config.md
   ```
   Create intermediate directories at the original location if needed (`mkdir -p`).

3. **Move the file back** (MOVE, not copy):
   ```bash
   mv "$ACERVO/<quarantine_path>" "$ACERVO/<original_path>"
   ```
   Verify the file no longer exists under `.quarantine/`.

4. **Strip the quarantine fields** from the restored file's frontmatter — remove `quarantined_at`, `quarantine_reason`, `quarantine_expires_at`. The file returns to active memory in its prior lifecycle state (typically `class: volátil`). Do **not** reintroduce deprecation fields that were stripped at quarantine time — restore brings the file back to *active*; if it should be deprecated again, that is a separate deprecation action.

5. **Append to `.purge_log`:**
   ```
   RESTORED: <quarantine_path> → <original_path> | restored: <NOW>
   ```

6. **Append to the origin container's `log.md`:**
   ```
   - RESTORED: <container-relative-path> — restored from quarantine by executive
   ```
   The tail is literal — restoration is an executive act.

### Restore — Verification

- [ ] File is back at `<original_path>` with content intact.
- [ ] File is gone from `.quarantine/`.
- [ ] Frontmatter has no `quarantined_*` fields.
- [ ] `.purge_log` has a `RESTORED:` line.
- [ ] Origin `log.md` has a `RESTORED:` entry with the literal tail.
