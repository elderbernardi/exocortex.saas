# Provisioning idempotency — step-04 acervo rsync + step-05 profiles

## Summary

The acervo and profiles provisioning steps (step-04 and step-05) did not preserve user customizations when re-run. This caused existing SOUL.md files and custom profile/bundle copies to be overwritten during re-provisioning, breaking idempotency.

## Root cause

- **step-04** (`setup/step-04-install-acervo.sh`): The main `copy_acervo_seed()` function used `rsync -a` without `--ignore-existing`, overwriting user-edited files like the SOUL.md onboarding constitution.
- **step-05** (`setup/step-05-install-profiles.sh`): Both `cp -r` calls (profiles and bundles) clobbered existing files, overwriting manual customizations.

Note: `step-07-install-identity.sh` was already idempotent (guards SOUL.md with a separate preserve logic); steps 04 and 05 are the residual fix.

## Solution

- **step-04**: Add `--ignore-existing` flag to the main rsync invocation in `copy_acervo_seed()`. (Editorial and ops seeds already used this flag; the main seed was the outlier.)
- **step-05**: Change both `cp -r` calls to `cp -rn` (no-clobber mode) to skip existing files.

Result: Re-running provisioning preserves user edits to SOUL.md and custom profiles/bundles while still adding new seed files and profiles.

## Testing

3 tests added to `tests/test_provisioning_idempotency.py`:
- `test_step04_source_has_ignore_existing` — verify step-04 has `--ignore-existing` in source
- `test_step04_preserves_user_macro_soul` — functional: rsync with flag preserves existing SOUL.md, adds new seed files
- `test_step05_source_no_clobber` — verify step-05 uses `cp -rn` in source

All passing post-fix.

## Related

- Installer v2 (step-07) already guards SOUL — this completes the idempotency surface.
- Umbrella change record: C0-provisioning-idempotency (SOLO, exocortex-only, no contract surface).

---

**Note:** Issue creation via `gh issue create` is owner-gated. This draft is ready for promotion to a GitHub issue.
