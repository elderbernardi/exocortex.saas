# Drive Path Governance for Final Artifact Publishing

Consolidated session context:

- Direct upload with `google_api.py drive upload` can fall to Drive root when `--parent` is not resolved.
- For final Exocórtex artifacts, the correct flow is `artifact_publish.py` with manifest + receipt.

## Durable Operational Rule

1. Resolve `drive_target.folder_path` before upload.
2. Ensure explicit parent in final upload.
3. Consider Drive root upload as a governance failure.
4. Fix with republication to correct folder and record receipt.

## Path Convention

Use lowercase paths for consistency:

- `exocortex/inbox` (fallback)
- `exocortex/microverso/<domain>/...` when the microverso is clear

## Minimum Verification

- `manifest.json` contains non-empty `drive_target.folder_path`.
- `receipt.google_drive.json` contains `folder_id` and `folder_path`.
- `drive get <file_id>` returns `parents` matching the destination folder (not root).
