# Setup Propagation Checklist (Google Drive Hardening)

Goal: ensure that `drive search` hardening is not lost during reprovisioning.

## Minimum Propagation Scope

Apply the idempotent `patch_google_drive_search` function to:
- Project setup (`.../exocortex.saas/setup.sh`)
- Canonical Hermes setup (`~/.hermes/setup.sh`)
- Artifacts seed setup (`.../plans/pdd_v2/artifacts/setup.sh`)

## Function Requirements

1. Detects already hardened state (doesn't reapply).
2. If `google_api.py` doesn't exist, emits warning and doesn't break setup.
3. Replaces the `drive_search` block with a version that has:
   - Textual query escaping (`'`, `\\`)
   - `trashed = false` in non-raw mode
   - Pagination via `nextPageToken`
   - `--max >= 1` validation

## Post-Setup Smoke Test

1. Auth:
`python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`

2. Accent search:
`python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py drive search "relatório" --max 3`

3. Apostrophe search:
`python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py drive search "O'Reilly" --max 2`

4. Setup syntax:
`bash -n <target-setup.sh>`

## Pitfall

Applying hardening only to the runtime file (`google_api.py`) and forgetting setup causes silent regression on the next clean machine/profile.
