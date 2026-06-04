# Telegram delivery pattern for visual artifacts

Use when the user is on Telegram and the artifact is a visual board, HTML prototype, deck preview, or multi-file package.

## Durable pattern

1. Create the artifact package under `~/.hermes/acervo/_artifacts/{artifact_id}/`.
2. Preserve source in `source/` and generated outputs in `exports/`.
3. Build a ZIP export even when the main deliverable is a single HTML file.
4. Register the ZIP in `manifest.json` with size, MIME and SHA-256.
5. Deliver the ZIP via `MEDIA:/absolute/path/to/file.zip`.
6. Also include the local path to the primary HTML/PDF/asset for desktop inspection.

## Why

Telegram Mobile can be unreliable for direct single-file delivery and preview. A ZIP gives the user a stable downloadable package and preserves source, export and manifest together.

## Verification

Before delivery:

- ZIP exists and size is greater than zero.
- Manifest includes the primary export and the ZIP.
- HTML or visual export was opened locally when possible.
- External publication, public links and sharing still follow Draft-First.