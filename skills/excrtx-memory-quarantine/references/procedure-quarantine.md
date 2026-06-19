## Procedure: Quarantine

Move a candidate file from its active location into `.quarantine/`, preserving structure, stamping quarantine fields, and dual-logging the operation.

**Inputs:** `<original_path>` (relative to `$ACERVO`, e.g. `micro/exocortex-dev/knowledge/old-model-config.md`), `<reason>` (one-line, e.g. "Not accessed in 92 days (last read 2026-03-15)").

1. **Validate the candidate is eligible** (stop and report on first failure):
   - File exists at `<original_path>`.
   - File is **not immune** — run the [Immunity Rules](#immunity-rules) check. If immune, refuse: *"File is immune to quarantine (<reason>): perene / promoted_at / raw/ / macro/."*
   - File is **not already in `.quarantine/`** (path does not start with `.quarantine/`).
   - File is **not already quarantined** — its frontmatter must not already contain `quarantined_at`.

2. **Compute the quarantine path** by prepending `.quarantine/` and preserving the full relative structure:
   ```
   micro/exocortex-dev/knowledge/old-model-config.md
     → .quarantine/micro/exocortex-dev/knowledge/old-model-config.md
   global/tools/deprecated-api.md
     → .quarantine/global/tools/deprecated-api.md
   ```
   Create intermediate directories under `.quarantine/` as needed (`mkdir -p`).

3. **Move the file** (MOVE, not copy):
   ```bash
   mv "$ACERVO/<original_path>" "$ACERVO/<quarantine_path>"
   ```
   After this step the file **must not** exist at `<original_path>`. Verify with `test ! -e "$ACERVO/<original_path>"`.

4. **Update the frontmatter** of the moved file:
   - Compute `NOW` = current UTC datetime, format `YYYY-MM-DDTHH:MM:SSZ`.
   - Compute `EXPIRES` = `NOW` + exactly 30 days (same time-of-day, UTC). Format `YYYY-MM-DDTHH:MM:SSZ`.
   - **If the file currently has `deprecated: true`** (long-deprecated candidate): strip the deprecation fields first — remove `deprecated`, `deprecated_at`, `deprecated_reason`. A file cannot be simultaneously deprecated and quarantined (V-071). The quarantine *supersedes* the deprecation; the `<reason>` captures the history (e.g. "Long-deprecated (deprecated_at 2025-12-01), quarantine window opened").
   - Add the three quarantine fields:
     ```yaml
     quarantined_at: <NOW>
     quarantine_reason: "<reason>"
     quarantine_expires_at: <EXPIRES>
     ```
   - Leave all other frontmatter (OKF canonical, `class`, `created_at`, `last_accessed_at`, legacy fields) untouched.

5. **Append to `.purge_log`** (global, at `$ACERVO/.quarantine/.purge_log`):
   ```
   MOVED: <original_path> → <quarantine_path> | reason: <reason> | expires: <EXPIRES>
   ```
   Paths here are `$ACERVO`-relative so the global log can trace any microverso. Create the file if absent.

6. **Append to the origin container's `log.md`** (per the [log convention](#logging-convention)):
   ```
   - QUARANTINED: <container-relative-path> — <reason>
   ```
   `<container-relative-path>` is relative to the owning container (e.g. `knowledge/old-model-config.md` for a `micro/exocortex-dev/` file), forward slashes, no `./` prefix.

### Quarantine — Verification

- [ ] File no longer exists at `<original_path>`.
- [ ] File exists at `<quarantine_path>` with original content intact.
- [ ] Frontmatter has `quarantined_at`, `quarantine_reason`, `quarantine_expires_at`; `quarantine_expires_at` = `quarantined_at` + 30 days.
- [ ] No `deprecated`/`deprecated_at`/`deprecated_reason` fields remain (if it was a deprecated candidate).
- [ ] `.purge_log` has a `MOVED:` line for this file.
- [ ] Origin `log.md` has a `QUARANTINED:` entry under today's date.
