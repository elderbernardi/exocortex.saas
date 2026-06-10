# Quick-Setup Guide Propagation (Google Cloud OAuth)

Goal: ensure the `gcloud_quick_setup.py` script is deployed alongside the `google-workspace` skill during reprovisioning.

## Scope

The script generates pre-configured Google Cloud Console links with auto-detected project ID,
eliminating the need for manual console navigation. Reduces setup from ~9 steps to ~3.

## Where It Lives

- **Seed/repo:** `scripts/gcloud_quick_setup.py` (exocortex.saas)
- **Hermes runtime:** `$HERMES_HOME/skills/productivity/google-workspace/scripts/gcloud_quick_setup.py`
- **Integration:** `$HERMES_HOME/skills/productivity/google-workspace/scripts/setup.py --setup-guide`

## Propagation Requirements

1. Copy `gcloud_quick_setup.py` to `$HERMES_HOME/skills/productivity/google-workspace/scripts/` during provisioning.
2. Ensure `setup.py` has a functional `--setup-guide` command.
3. Script must be standalone (works with `python gcloud_quick_setup.py` directly).

## Project Detection

Precedence order for auto-detecting the project ID:
1. Existing `client_secret.json` in `~/.hermes/` (extracts numeric prefix from client_id)
2. `gcloud config get-value project` (if gcloud CLI available)
3. `gcloud projects list --limit=1` (fallback)
4. If nothing found → instruct user to provide `--project ID`

## Post-Deploy Smoke Test

```bash
# Auto-detection (should find project)
python $HERMES_HOME/skills/productivity/google-workspace/scripts/gcloud_quick_setup.py --format json

# Via setup.py
python $HERMES_HOME/skills/productivity/google-workspace/scripts/setup.py --setup-guide text

# Text format
python $HERMES_HOME/skills/productivity/google-workspace/scripts/gcloud_quick_setup.py --format text
```

## Pitfall

The `gcloud_quick_setup.py` script depends on `_hermes_home.py` (sibling module).
If copied to another directory without `_hermes_home.py`, import fails.
Always keep together with the other `google-workspace` skill scripts.