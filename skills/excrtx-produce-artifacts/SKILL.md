---
name: excrtx-produce-artifacts
description: Create, organize, export, and publish final Exocórtex artifacts in the user's workspace, maintaining reproducibility
  in the Acervo.
version: 1.0.1
category: excrtx
platforms:
- linux
author: Exocórtex
license: MIT
gate:
  require_quality_gate: true
  max_context_tokens: 2000
metadata:
  hermes:
    tags:
    - exocortex
    - artifacts
    - drive
    - acervo
    - publishing
    - reproducibility
    related_skills:
    - excrtx-memory-manager
    - google-workspace
    - excrtx-govern-draftfirst
    - excrtx-quality-antislop
    calibration:
    - feature_id: EX-22
      calibration_prompt: Você cria, organiza e publica artefatos finais. Mantém reprodutibilidade em $ACERVO/_artifacts/items/
        com views indexadas por microverso, tarefa, status e tipo. Separa artefatos em andamento de prontos para publicação.
      test_prompt: Acabei de finalizar um relatório de auditoria para o cliente 'Construtora Alfa'. Organize isso como artefato
        pronto para publicação.
      acceptance_criteria: '1. O agente persiste em $ACERVO/_artifacts/items/ com manifest YAML

        2. O manifest contém: title, microverso, type=report, status=ready, created

        3. Views indexadas (by_microverso, by_type, by_status) são mencionadas ou atualizadas

        4. Se microverso ''construtora-alfa'' não existe, pergunta antes de criar'
      remediation_tip: 'FALHA: Artefato não persistido com manifest. A skill exige que todo artefato tenha manifest YAML em
        _artifacts/items/<id>/manifest.yaml com campos obrigatórios (title, microverso, type, status, created). Não salve
        arquivos soltos — o manifest é a fonte de verdade. Atualize as views em by_type/ e by_status/.'
---
# Personal Artifact Workspace

Use this skill when the user asks for creation, organization, export, or delivery of final artifacts: documents, PDFs, HTML, spreadsheets, images, slides, ZIP packages, or reports.

Also use when the user asks to design, replicate, or audit the artifact publishing harness in another Exocórtex-Hermes.

Before executing, load when applicable:

- `excrtx-memory-manager`, to respect Acervo ontology and cascade.
- `productivity/google-workspace`, for Google Drive operations.
- `excrtx-govern-draftfirst`, if there's sharing, sending, external publication, or permission change.
- `excrtx-quality-designsys` and `excrtx-quality-taste`, if the artifact has a visual component.
- `excrtx-quality-antislop`, if the artifact has final prose.

## Principle

Drive is a publishing tool and can serve as a private human editing surface. The Acervo is the cognitive source and reproducible registry.

Don't sync the entire Acervo with Drive. Publish final exports via a controlled operational package and write local receipts. For editable drafts, sync only the linked artifact, never the Acervo tree.

Operational sync metadata is not cognitive content. Store sync state in `_ops/` inside the artifact package or in a central operational registry. Directories/files `_ops/`, `events.log`, `diffs/`, `locks.json`, and `sync.json` don't enter normal context and should only be read for explicit sync, import, conflict, or audit tasks.

When the user needs to edit drafts with Hermes/Exocórtex running on a remote server, treat Drive/Docs as an editable surface per artifact, not as Acervo sync. The correct cycle is: canonical local source → private external document → versioned import → diff/review → explicit promotion of accepted revision. See `references/remote-draft-editing-sync.md`.

## Operational Model

Harness model v0.4:

- Inbox is separate from artifacts: raw input goes to `~/.hermes/acervo/_inbox/` and a task/canvas determines the material's destination.
- Final artifacts are centralized in `~/.hermes/acervo/_artifacts/items/{artifact_id}/` (Model 2).
- Microversos and tasks point to artifacts via metadata; path is not the canonical source of the relationship.
- `friendly_name`/`publication_names` control filenames seen by the user; `artifact_id`/`canonical_slug` remain stable.
- When an artifact becomes `ready` or approved, ask the user if they want to publish.
- Before `ready`, apply Quality Gate; when Canvas/manifest requires it, run Persona Evaluation and record assessments in `evaluations/`.

```text
~/.hermes/acervo/_artifacts/items/{artifact_id}/
├── source/
│   ├── source.md
│   ├── metadata.yaml
│   └── revisions/          # snapshots imported from editable surfaces
├── assets/
│   ├── images/
│   ├── data/
│   ├── logos/
│   ├── fonts/
│   ├── raw/
│   └── generated/
├── exports/
│   ├── *.pdf
│   ├── *.html
│   ├── *.docx
│   ├── *.xlsx
│   └── *.zip
├── evaluations/
│   ├── critico.md
│   ├── professor.md
│   ├── cientista.md
│   ├── auditor.md
│   └── editor.md
├── diffs/                  # human revision diffs when external sync exists
├── sync.json               # optional link to Google Docs/Drive/external editor
├── manifest.json
└── receipts/
    └── receipt.google_drive.json
```

Compatibility: old packages at `~/.hermes/acervo/_artifacts/{artifact_id}/` remain readable, but new creations should prefer `items/{artifact_id}/`.

## Source Rule

Markdown is the default source for documents, plans, official letters, reports, scripts, and educational materials.

Accepted exceptions:

- Spreadsheets: `.xlsx`, `.csv`, `.json`, or generator script.
- Images: `.svg`, `.png`, `.html`, `.excalidraw`, or visual prompt.
- Presentations: `.md` Marp or `.pptx`.
- Received PDFs: original PDF as source, text extraction in `source/`.
- Live collaborative documents: Drive as external source; Acervo stores link and manifest.

## Standard Procedure

1. Classify the artifact: document, spreadsheet, image, presentation, HTML, ZIP, report, or code.
2. If it's versionable code, use GitHub as primary destination. If for human consumption, use Drive.
3. Resolve microverso, discipline/project/context, and human-facing destination folder.
4. Create package at `~/.hermes/acervo/_artifacts/items/{artifact_id}/`.
5. Write the source in `source/`.
6. Copy necessary assets to `assets/` with relative paths.
7. Export final formats to `exports/`.
8. Validate exports before publishing: file exists, size greater than zero, consistent MIME, and SHA-256 hash recorded.
9. Apply the Unified Quality Gate (`excrtx-quality-gate`): all final prose in the artifact must pass the anti-slop gate (`excrtx-quality-antislop`); all visual components must pass the taste gate (`excrtx-quality-taste`). Gate failures must be fixed by the executor itself before delivering.
9.1. When Canvas/manifest requires evaluation, generate assessments in `evaluations/` with relevant personas, including Scientist for factual/methodological claims and Professor for educational materials.
10. Generate or update `manifest.json` with hash, MIME, size, source, exports, and destination.
11. Publish exports to the user's private Drive via configured provider.
11.1. Resolve the destination folder before upload (`drive_target.folder_path`) and require explicit parent; root upload is invalid for final artifacts.
12. Write `receipt.{provider}.json` with IDs, links, and status.
13. Deliver to the user the Drive link and local package path.
14. If the artifact has cognitive value, create a semantic page in the microverso pointing to the artifact_id.

## Manifest and Receipt

The manifest is the local source of traceability. The receipt is the proof of publication.

Minimum manifest fields:

```json
{
  "artifact_id": "art_YYYYMMDD_HHMMSS_slug",
  "title": "Human Title",
  "microverso": "ensino",
  "status": "draft|ready|published|failed",
  "source_type": "markdown|xlsx|image|mixed|external",
  "source_path": "source/source.md",
  "assets_dir": "assets",
  "exports": [
    {
      "path": "exports/file.pdf",
      "kind": "pdf",
      "mime": "application/pdf",
      "sha256": "...",
      "size": 12345
    }
  ],
  "drive_target": {
    "provider": "google_drive",
    "folder_path": "exocortex/inbox",
    "visibility": "private"
  }
}
```

Minimum receipt fields:

```json
{
  "provider": "google_drive",
  "published_at": "ISO-8601",
  "folder_path": "exocortex/inbox",
  "folder_id": "...",
  "files": [
    {
      "export_path": "exports/file.pdf",
      "drive_file_id": "...",
      "web_view_link": "https://drive.google.com/...",
      "mime": "application/pdf",
      "visibility": "private",
      "sha256": "...",
      "size": 12345
    }
  ]
}
```

## Telegram Delivery Pattern

When the current surface is Telegram and the artifact is a visual board, HTML prototype, deck preview, or multi-file deliverable, create a ZIP export even if the primary deliverable is a single file. Register the ZIP in `manifest.json`, deliver it with `MEDIA:/absolute/path/to/file.zip`, and include the local path to the primary export. See `references/telegram-zip-visual-artifacts.md`.

## Initial Provider: Local Google Drive

Prefer Hermes local OAuth, via skill `productivity/google-workspace`, before using Composio.

Use Composio only when local OAuth doesn't exist, when the user explicitly requests it, or when the target environment requires that connector.

Pre-check:

```bash
python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
```

Initial publisher:

```bash
python ~/.hermes/acervo/global/tools/artifact_publish.py init \
  --title "Title" \
  --microverso ensino \
  --source-md /path/to/source.md \
  --drive-path "exocortex/ensino/2026/aulas"

python ~/.hermes/acervo/global/tools/artifact_publish.py publish \
  --artifact-dir ~/.hermes/acervo/_artifacts/{artifact_id}
```

## Destination Policies

Default destination when context is missing:

```text
exocortex/inbox
```

Recommended patterns:

```text
exocortex/ensino/{year}/{discipline}/{type}
exocortex/gabinete/{year}/{type}
exocortex/dev/{year}/artefatos/{project}
```

Don't ask for the folder if the intent is clear. Use Inbox when ambiguity doesn't change the delivery value.

### Deterministic destination precedence

Resolve Drive destination in this exact order:

1. If the executive explicitly says where to save, use that exact Drive path.
2. If the artifact or manifest already has a non-empty `drive_target.folder_path`, use it.
3. If the executive did not specify a destination, default to `exocortex/inbox`.
4. Do **not** infer the Drive path from the local filesystem path alone.
5. Semantic paths like `exocortex/ensino/{year}/{discipline}/{type}` are opt-in publication destinations, not silent defaults.

This removes ambiguity between Inbox and semantic publication folders: absent explicit direction, the harness defaults to Inbox.

### Interdependent multi-file artifacts

When there is more than one file and the files depend on each other, store them in a dedicated subfolder under the resolved Drive destination instead of scattering them side by side.

Examples:

```text
exocortex/inbox/<artifact-slug>/
exocortex/ensino/2026/<disciplina>/<artifact-slug>/
```

The goal is to preserve adjacency, reduce orphan files, and make later moves safer.

## Draft-First

Private upload to the user's own Drive counts as personal delivery when the user requested the artifact.

Requires Draft-First:

- Creating a public link;
- Sharing with class, third parties, domain, or organization;
- Sending via email/message;
- Publishing to site, GitHub release, or shared document;
- Converting to collaborative document when this changes format/semantics.

### Delivery Pattern — Gmail with Drive Links

In Exocórtex, email uses `productivity/google-workspace` as the operational standard. Don't route email through `himalaya`/`hymalaia` skill in the Exocórtex setup, even when it exists in the Hermes catalog.

When the executive asks for Drive upload and email send:

1. Publish final files to Drive within the `exocortex/...` structure;
2. If the executive did not specify a destination, use `exocortex/inbox`;
3. Use semantic folders like `exocortex/ensino/{year}/...` only when the executive explicitly asked for that destination or when the artifact already carries that `drive_target.folder_path`;
4. Create missing intermediate folders explicitly and record the final `folder_id`;
5. Write `receipt.google_drive.json` with `folder_id`, `drive_file_id`, links, MIME, SHA-256, and sizes;
6. After upload, tell the executive exactly where the artifact was saved and ask: `Você deseja mover para outro lugar?`;
7. If the executive asks to move it, move the Drive file/folder to the new parent instead of uploading a duplicate when feasible;
8. Compose the email with verified Drive links;
9. Present the email as DRAFT and wait for explicit approval before sending;
10. If the available Gmail backend doesn't support attachments in the current wrapper, don't improvise workarounds: keep sending with verified Drive links and record this in the receipt.

This pattern separates two action classes: private upload to the user's own Drive is artifact execution; email sending is external communication and remains under Draft-First.

Session detail: `references/session-2026-06-01-nugai-html-drive-email.md`.

## GitHub vs Drive

When the request is for an institutional, office, printing, or final delivery artifact from Exocórtex:
- Prioritize skills from the `exocortex` domain before resorting to generic or other-domain workflows.
- Use skills from other domains only as specific technical support, not as the main track.
- If there's institutional prose, also apply `excrtx-quality-antislop` and the local writing rule without gender-neutral language.
- If the artifact is for print, generate at least HTML and PDF; create a ZIP of the complete package when this improves transport, review, or reuse.
- Visually validate the exported HTML before closing the task.

## GitHub vs Drive

Use GitHub when the artifact is versionable code, PR, branch, commit, or technical release.

Use Drive when the artifact is for human consumption: PDF, spreadsheet, official letter, report, educational material, presentation, image, exported HTML, or final ZIP.

For `excrtx-produce-slides`, Drive is the default private publication destination. Vercel or public URL are optional advanced targets requiring explicit Draft-First; don't use Vercel creation/login as default path for regular users.

Hybrid case: code on GitHub; final artifacts on Drive; manifests in the Acervo.

## Durable Troubleshooting

### Valid OAuth but Drive API Disabled

Symptom: `setup.py --check` returns authenticated, but upload/search fails with `HttpError 403` stating Google Drive API hasn't been used or is disabled in the project.

Fix:

1. Enable Google Drive API in the Google Cloud project of the OAuth used by Hermes.
2. Wait for propagation.
3. Re-execute publish.

Record the failure in `receipt.google_drive.failed.json` and mark `manifest.status = failed`. Don't turn this into a negative rule about Drive or OAuth.

## Common Pitfalls

1. Syncing the entire Acervo with Drive. This mixes cognitive memory with delivery surface.
2. Publishing source/assets by default. Deliver final exports; send complete package only when it makes sense.
3. Creating public link automatically. Private upload is personal delivery; sharing requires approval.
4. Confusing valid OAuth with enabled API. The token can renew and the Drive API can still fail with 403.
5. Using Composio as default. For personal Exocórtex, prefer auditable local OAuth.
6. Leaving artifact without receipt. A link without receipt is not reproducible.
7. Generating PDF/HTML without source. Always preserve the source or document why the final format is the canonical source.
8. Ignoring assets. Copy necessary assets to the package with relative paths.
9. Final upload without resolved parent (Drive root). Every final publication needs `drive_target.folder_path` and receipt with `folder_id`.
10. Treating Vercel as default path for premium HTML decks. For regular users, final export goes to private Drive; public URL/deploy is an exception with Draft-First.

## Verification Checklist

- [ ] Skill `excrtx-produce-artifacts` loaded before creating/publishing artifact.
- [ ] Package created at `~/.hermes/acervo/_artifacts/items/{artifact_id}` for new artifacts.
- [ ] Source preserved in `source/` or exception recorded in manifest.
- [ ] Necessary assets copied to `assets/`.
- [ ] Final exports generated in `exports/`.
- [ ] On Telegram, final ZIP created and registered in manifest when artifact is visual, HTML, deck, or multi-file package.
- [ ] Hash, MIME, and size recorded in manifest.
- [ ] Quality Gate applied before `ready`.
- [ ] Persona evaluation recorded in `evaluations/` when Canvas/manifest requires it.
- [ ] If artifact is `ready`/approved, ask executive if they want to publish, except when they already explicitly requested publication in the same turn.
- [ ] Private upload done to configured Drive, with explicit parent.
- [ ] Receipt written to `receipts/receipt.google_drive.json` with `drive_file_id`, `webViewLink`, `folder_id`, SHA-256, and size.
- [ ] `manifest.json` updated to `published` when private upload confirmed.
- [ ] Failures recorded in `receipts/receipt.google_drive.failed.json`.
- [ ] External sharing/public link blocked until explicit approval.
- [ ] If cognitive value exists, semantic page created in microverso or link registered in `_meta/`.

## Reproducibility

Supporting details:

- `references/remote-draft-editing-sync.md` — pattern for human draft editing when Hermes runs on remote server: Google Docs as surface, artifact package as source, `_ops/` outside context, and import with diff/acceptance.
- `references/session-2026-05-30-mvp.md` — initial MVP design and decisions.
- `references/replication-checklist.md` — checklist to port capability to another Exocórtex-Hermes.
- `references/pdd-v2-doc-alignment.md` — how to align PDD v2, provisioner, and microverso when evolving this capability.
- `references/drive-path-governance.md` — explicit parent rule, `exocortex/inbox` fallback, and correction of improper root upload.
- `references/telegram-zip-visual-artifacts.md` — ZIP delivery pattern on Telegram for visual/HTML artifacts with manifest.
- `references/frontend-slides-artifact-track.md` — package, Drive, and Draft-First policy for premium HTML presentations generated by `excrtx-produce-slides`.
- `references/marp-frontend-slides-artifact-tracks.md` — policy for combining Marp as slide production line and Frontend Slides as premium visual artifact renderer.
- `references/remote-draft-editing-sync.md` — pattern for human draft editing when Hermes/Exocórtex runs on remote server: Google Docs/Drive as editable surface per artifact, `sync.json`, versioned import, diff, and explicit promotion of accepted revision.

Every replicable implementation must contain:

- Contract in `global/contracts/excrtx-produce-artifacts.md`;
- Equivalent tool or provider;
- `_artifacts/` area;
- Manifests and receipts;
- Rule of Drive as publication, not sync;
- Draft-First policy for sharing;
- Provider setup documentation.

## References

- `references/session-2026-05-30-mvp.md` — initial MVP design and decisions.
- `references/replication-checklist.md` — portability checklist for another Exocórtex-Hermes.
- `references/pdd-v2-doc-alignment.md` — documentary alignment between PDD v2, provisioner, and microverso.
- `templates/manifest-template.md` — annotated `manifest.json` template.

## When to Use

Activate when working with this skill's domain. See procedure for details.

**Don't use for:** Unrelated domains or when a more specialized skill exists.

## Procedure

Follow the steps and rules defined in this skill's body sections above.
