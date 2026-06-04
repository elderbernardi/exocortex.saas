# Remote draft editing sync

Session-derived architecture note for Exocórtex running Hermes on a remote server while the user edits drafts in familiar tools.

## Core pattern

Do not sync the whole Acervo with Drive. Treat each editable draft as an artifact lifecycle:

1. Exocórtex creates the local canonical source under `_artifacts/{artifact_id}/source/`.
2. Exocórtex publishes a private editable surface, preferably Google Docs for text drafts.
3. The user edits the document in the familiar surface.
4. Exocórtex imports only that artifact on demand or via watcher.
5. Exocórtex computes a diff against the local canonical source.
6. Exocórtex asks for acceptance before promoting the human-edited version to canonical source.
7. Exocórtex updates manifest/receipt/state after acceptance.

## Separation rule

Keep cognitive content separate from operational sync metadata.

Recommended MVP layout:

```text
~/.hermes/acervo/_artifacts/{artifact_id}/
├── source/
│   ├── source.md
│   └── revisions/
├── exports/
├── assets/
├── manifest.json
├── receipt.google_drive.json
└── _ops/
    ├── sync.json
    ├── locks.json
    ├── events.log
    └── diffs/
```

`_ops/` is operational. It must not enter normal context, must not be treated as knowledge, and must not be promoted into a microverso. Load it only for tasks like sync, import, conflict resolution, Drive debugging, or audit.

Longer-term SaaS shape: move operational sync metadata to a registry such as `~/.hermes/acervo/_ops/artifact_registry.sqlite`, exposing computed summaries to the agent instead of raw JSON.

## Google Docs MVP

Use Google Docs as editing surface, not as the global source of truth.

Minimal commands/capabilities to implement:

- `artifact_edit publish-doc`: create private Google Doc from local source.
- `artifact_edit import-doc`: export current Doc text, save revision, compute diff.
- `artifact_edit accept`: promote imported revision to `source/source.md` after approval.

Initial sync may be manual: user says “importar alterações”. Webhooks are a UX improvement, not a requirement for coherence.

## Version binding

Every external editable surface needs a binding between:

- `artifact_id`
- local source path
- local source hash
- provider
- Drive file ID / Google Doc ID
- remote modified time or revision ID
- last imported revision
- lifecycle state
- merge policy

## Lifecycle states

Use explicit state names:

- `draft_local`
- `sent_for_editing`
- `human_editing`
- `remote_changed`
- `imported_pending_review`
- `accepted_canonical`
- `published`
- `archived`

## Merge policies

- `manual_review`: default. Show diff and ask before promoting.
- `safe_overwrite`: only for simple artifacts where the user explicitly accepts remote as source.
- `section_merge`: for anchored or named-range documents.
- `append_notes`: import only a user-notes block.

## Conflict rules

1. If local changed after export and remote also changed, mark conflict.
2. If remote removed anchors, fall back to manual review.
3. If Exocórtex needs to regenerate while the user edits, create a separate suggestion section instead of overwriting human edits.
4. If a published document changes, open a new revision cycle instead of mutating the old published receipt.

## Tooling notes

Google Drive `changes.watch` and `changes.list` can later detect remote changes, but notifications only signal that changes exist. The sync worker must fetch the change feed and filter by registered artifact IDs.

Google Docs named ranges/placeholders support controlled section replacement. Use them for structured documents such as ofícios, atas, planos and recurring institutional reports.

Operational Transformation/CRDT details should usually stay abstract. For Google Docs, delegate concurrent editing semantics to Google; do not build OT yourself for the MVP.
