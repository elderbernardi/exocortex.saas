# Manifest Template

Use este template como referência para `manifest.json` de pacotes em `~/.hermes/acervo/_artifacts/{artifact_id}/`.

```json
{
  "artifact_id": "art_YYYYMMDD_HHMMSS_slug",
  "title": "Título humano",
  "microverso": "global",
  "status": "draft",
  "source_type": "markdown",
  "source_path": "source/source.md",
  "assets_dir": "assets",
  "exports": [],
  "drive_target": {
    "provider": "google_drive",
    "folder_path": "exocortex/inbox",
    "visibility": "private"
  },
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

Regras:

- `status` muda para `published` somente após receipt válido.
- `exports` precisa conter `path`, `kind`, `mime`, `sha256` e `size` para cada arquivo final.
- `drive_target.visibility` fica `private` por padrão.
- Falhas devem preencher `last_error` com erro compacto e sem segredos.
