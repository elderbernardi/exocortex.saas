# Telegram delivery pattern for visual artifacts

Use when the user is on Telegram and the artifact is a visual board, HTML prototype, deck preview, or multi-file package.

## Durable pattern

1. Create the artifact package under `~/.hermes/acervo/_artifacts/{artifact_id}/`.
2. Preserve source in `source/` and generated outputs in `exports/`.
3. Validate the primary exports and prepare a **delivery manifest** that lists their hashes but does not list the ZIP itself.
4. Build the ZIP even when the main deliverable is a single HTML file. Include source, primary exports, evaluations and the delivery manifest.
5. Compute the final ZIP size and SHA-256.
6. Register the ZIP in the canonical `manifest.json` outside the archive, then rerun manifest validation.
7. Deliver the ZIP via `MEDIA:/absolute/path/to/file.zip`.
8. Also deliver or identify the primary HTML/PDF/asset for direct inspection.

### Avoid checksum recursion

A ZIP cannot contain a manifest with the ZIP's own final checksum: updating that checksum changes the archive and invalidates the value. Use two layers:

- **inside the ZIP:** `manifest.delivery.json`, covering the files contained in the archive and excluding the ZIP self-record;
- **canonical artifact root:** `manifest.json`, covering the primary exports plus the completed ZIP.

Do not rebuild the ZIP after adding its checksum to the canonical manifest unless you recompute the archive and repeat the sequence.

## Why

Telegram Mobile can be unreliable for direct single-file delivery and preview. A ZIP gives the user a stable downloadable package and preserves source, export and manifest together.

## Verification

Before delivery:

- ZIP exists and size is greater than zero.
- Manifest includes the primary export and the ZIP.
- HTML or visual export was opened locally when possible.
- External publication, public links and sharing still follow Draft-First.