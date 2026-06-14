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
- semantic domain paths only when explicitly requested or already present in `drive_target.folder_path`

## Destination Precedence

1. Explicit destination from the executive
2. Existing `drive_target.folder_path` in the artifact
3. Default fallback: `exocortex/inbox`

Never infer Drive destination solely from the local filesystem path.

## Interdependent files

If two or more files belong together, publish them inside a dedicated subfolder under the resolved destination.

Examples:

- `exocortex/inbox/<artifact-slug>/`
- `exocortex/inbox/<artifact-slug>/assets/`

## Post-upload interaction

After publishing, always inform the executive of the exact Drive path used and ask whether they want to move the artifact elsewhere.

If they ask to move it, prefer moving the Drive file/folder to the new destination over creating a duplicate upload.

## Minimum Verification

- `manifest.json` contains non-empty `drive_target.folder_path`.
- `receipt.google_drive.json` contains `folder_id` and `folder_path`.
- `drive get <file_id>` returns `parents` matching the destination folder (not root).
