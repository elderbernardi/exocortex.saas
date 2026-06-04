# Multichannel intake contract and rollout

Durable lessons from the first end-to-end implementation of the Exocórtex intake path.

## Canonical separation

Use this layer order:

1. input channel
2. `_inbox`
3. semantic acervo
4. `_artifacts`
5. publish

The inbox is operational staging, not semantic knowledge. Do not ingest directly into `micro/` or any semantic directory before triage.

## Channel contract

Channels do not decide workflow. Each channel should only emit a local `IntakeEnvelope` with enough metadata for downstream routing.

Suggested envelope fields:

- `channel`
- `source_type`
- `source_ref`
- `captured_at`
- `sender`
- `title`
- `mime_type`
- `original_filename`
- `local_path`
- `text_fallback`
- `notes`

The server-side intake layer decides extraction, triage, promotion, and publication.

## Preservation rule

Always preserve the untouched payload under:

`~/.hermes/acervo/_inbox/{intake_id}/original/`

Derived text, OCR, previews, and analysis belong under `derived/`. Never overwrite the original artifact.

## Promotion rule

Promotion from `_inbox` to semantic acervo requires explicit triage metadata:

- target microverso
- functional directory
- Nature
- title
- rationale

Without those fields, keep the item in inbox state.

## Canonical workspace shape

`~/.hermes/acervo/_inbox/{intake_id}/`
- `manifest.json`
- `routing.json`
- `log.json`
- `original/`
- `derived/`

Recommended id pattern:

`int_YYYYMMDD_HHMMSS_slug`

## Current implementation baseline

The first canonical tool lives at:

`~/.hermes/acervo/global/tools/intake_ingest.py`

Subcommands:

- `ingest`
- `analyze`
- `show`
- `promote`

Supported extraction baseline:

- text-like files directly
- PDF via `pypdf` with `pdftotext` fallback
- images via OCR
- ZIP via inventory
- audio/video via metadata probe
- links as lightweight snapshots

## Architecture constraint

For productized surfaces, preserve the official boundary:

`USER -> GUI -> SERVER -> HERMES`

Do not let a channel-specific adapter redefine the cognitive workflow. Telegram, web GUI, email, or webhook should all converge into the same intake contract.

## Rollout order

Prefer this order:

1. canonical local intake tool
2. server/API wrapper around `IntakeEnvelope`
3. GUI dropzone or upload surface
4. channel adapters like Telegram

This keeps channel work thin and preserves one routing brain.

## Reproducibility expectations

When this capability changes, update all four surfaces together:

- project docs/ADR
- project setup/bundle
- acervo contract/tool
- `hermes-setup` microverso decisions/workflows

A change is not complete if the implementation exists but the replication path is missing.
