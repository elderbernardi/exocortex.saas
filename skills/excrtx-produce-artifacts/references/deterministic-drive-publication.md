# Deterministic Drive publication

## When to use
Use this reference when a publication flow is ambiguously choosing between `exocortex/inbox`, semantic Drive paths, and local filesystem-relative paths.

## Durable rule
Drive destination resolution must be deterministic and must **not** infer target folders from the local filesystem path.

Precedence:
1. explicit destination provided by the executive
2. existing `manifest.drive_target.folder_path`
3. fallback to `exocortex/inbox`

## Packaging rule
If the publication contains more than one interdependent file, publish the set into a dedicated subfolder under the resolved base destination.

Examples:
- single file, no explicit destination -> `exocortex/inbox`
- multiple related files, no explicit destination -> `exocortex/inbox/<artifact-slug>`
- explicit destination `exocortex/gabinete/2026/oficios` -> publish there, even if the local files live under another microverso

## Implementation touchpoints validated in session
- `acervo/global/tools/harness/init_artifact_package.py`
  - manifest should be born with:
    - `drive_target.provider = google_drive`
    - `drive_target.folder_path = exocortex/inbox`
    - `drive_target.visibility = private`
- `acervo/global/tools/artifact_publish.py`
  - central resolver for Drive target selection
  - publication command should create folders deterministically in Drive
  - write `receipts/receipt.google_drive.json`
  - support post-publication move operation in Drive
- `setup/step-04-install-acervo.sh`
  - install global tools from `acervo/global/tools/*.py`, not only `harness/*.py`

## Post-publication UX rule
After upload, always report:
- exact Drive folder path
- folder/file IDs when available
- link when available

Then ask:
- `Você deseja mover para outro lugar?`

If the executive chooses another destination, prefer a Drive move over re-upload when possible.

## Verification recipe
Minimum verification before claiming the rule is enforced:
1. `py_compile` the publisher and manifest-init scripts
2. run unit coverage for precedence and subfolder behavior
3. run a local `init` flow and inspect the generated `manifest.json`
4. only then perform a real Drive upload if approved

## Pitfall
If HERMES/Acervo setup copies only `acervo/global/tools/harness/*`, the publication entrypoint may exist in the repo but never reach the active runtime. Verify installer coverage when adding top-level tools.
