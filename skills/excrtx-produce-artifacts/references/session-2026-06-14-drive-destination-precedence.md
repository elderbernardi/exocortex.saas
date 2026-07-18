# Session 2026-06-14 — Drive destination precedence and post-upload move policy

## Durable learning

The harness had an ambiguity between two valid publication behaviors:

1. save to `exocortex/inbox`
2. infer a semantic destination such as `exocortex/ensino/{year}/{discipline}/{type}` from task context or filesystem path

That ambiguity caused inconsistent behavior across similar sessions.

## Decision

Drive destination must follow this precedence:

1. explicit destination stated by the executive
2. existing `drive_target.folder_path` already carried by the artifact/manifest
3. default fallback: `exocortex/inbox`

## Hard rule

Do **not** infer the Drive destination from the local filesystem path alone.

A local path like `/home/user/ensino/...` may inform context, but it does not authorize silent publication to `exocortex/ensino/...`.

## Multi-file artifacts

If there are multiple interdependent files, publish them inside a dedicated subfolder under the resolved destination.

Examples:

- `exocortex/inbox/<artifact-slug>/`
- `exocortex/inbox/<artifact-slug>/assets/`
- `exocortex/ensino/2026/<disciplina>/<artifact-slug>/`

This keeps related files together and makes later moves safer.

## User-facing closing step

After every private Drive upload:

1. state the exact Drive path used
2. state the folder or file IDs when relevant
3. ask: `Você deseja mover para outro lugar?`
4. if the executive says yes, prefer moving the existing Drive file/folder to the new parent instead of re-uploading duplicates

## Why this matters

The executive wants Inbox to be the operational default and semantic organization to remain an explicit decision, not an agent inference.
