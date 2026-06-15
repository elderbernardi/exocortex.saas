---
name: excrtx-integrate-gdrive
description: Configure and operate Google Drive via direct API (no Composio), with focus on search robustness and validation.
version: 1.1.0
category: excrtx
platforms:
- linux
author: Exocortex
metadata:
  hermes:
    tags:
    - exocortex
    - integration
    - gdrive
    - api
    related_skills:
    - excrtx-integrate-oauth
    - excrtx-produce-artifacts
    calibration:
    - feature_id: EX-25
      calibration_prompt: 'Você opera Google Drive via API direta com hardening: filtro ''trashed = false'', paginação com
        nextPageToken, campos expandidos (id, name, mimeType, modifiedTime, webViewLink), suporte a --raw-query.'
      test_prompt: Busque no meu Drive todos os documentos que mencionam 'relatório trimestral' e me liste os 5 mais recentes.
      acceptance_criteria: '1. O agente usa a API do Drive (não Composio) para buscar

        2. A query inclui filtro ''trashed = false''

        3. Resultados incluem campos expandidos (nome, mimeType, data de modificação, link)

        4. Se houver mais de uma página de resultados, usa nextPageToken para paginar'
      remediation_tip: 'FALHA: Busca no Drive sem hardening. As regras exigem: 1) Sempre filtrar ''trashed = false'', 2) Usar
        paginação com nextPageToken para não perder resultados, 3) Expandir campos retornados. Use o driver em $HERMES_HOME/skills/productivity/google-workspace/scripts/google_api.py.'
---
# Google Drive Integration

Direct Google Drive API integration without Composio, focusing on search robustness and validation.

## When to Use

Activate when:
- The executive requests file upload, search, or management on Google Drive
- An artifact needs to be exported to Drive
- `excrtx-produce-artifacts` needs a Drive destination

**Don't use for:** Local file operations without Drive involvement. OAuth setup (use `excrtx-integrate-oauth`). NotebookLM integration (use `excrtx-integrate-nlmops`). Browser-based Drive access. Read-only link sharing without API.

> Upon activation, classify the input as **Execução** (uploading, searching, exporting) or **Manutenção** (token refresh, folder structure setup) for proper logging.

## Procedure

### Step 1 — Validate Authentication

1. Check OAuth token: `python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`
2. If expired, guide the executive through re-auth flow via `excrtx-integrate-oauth`
3. Never proceed with API calls without a validated token

### Step 2 — Search (with hardening)

Drive search is notoriously fragile. Apply this hardening sequence:

1. **Normalize query** — strip diacritics, lowercase, remove special chars
2. **Build query** — use `fullText contains '<term>'` for content, `name contains '<term>'` for filenames
3. **Add safety filter** — always include `trashed = false` in the query
4. **Paginate** — iterate all pages, never trust first-page results alone
5. **Validate results** — confirm MIME type, modification date, and owner before returning

```python
# Example hardened search query
query = f"name contains '{normalized_term}' and trashed = false"
```

### Step 3 — Upload (Draft-First)

All uploads are external actions — apply Draft-First protocol:

1. Present DRAFT to the executive: target folder, filename, MIME type
2. Await confirmation before proceeding
3. Resolve target folder:
   - Search by name first (`name = '<folder>' and mimeType = 'application/vnd.google-apps.folder' and trashed = false`)
   - If not found, prompt executive: "Folder '<name>' not found. Create it?"
   - Never create folders silently without confirmation
4. Check for existing file with same name (avoid duplicates)
5. Upload with correct MIME type
6. Return shareable link and log in microverso's `log.md`

**Error handling:** If upload fails (network timeout, quota exceeded, auth error), retry once after 5s. If retry fails, save the file locally in `~/.hermes/acervo/_artifacts/{artifact_id}/exports/` and report the failure to the executive with the local path as fallback.

### Step 4 — Artifact Export

When `excrtx-produce-artifacts` requests Drive export:

1. Generate artifact locally
2. Upload to the microverso's designated Drive folder (Step 3)
3. Register Drive URL in artifact manifest
4. Classify operation as Vetor `exec` (producing output)

## Pitfalls

- **Search returning stale results:** Drive API caches aggressively. If a recently uploaded file isn't found, wait 5-10s and retry with `orderBy=modifiedTime desc`.
- **MIME type mismatch:** Google Docs native formats (application/vnd.google-apps.*) cannot be downloaded directly. Use export endpoint with target MIME.
- **Shared Drive vs My Drive:** `corpora=allDrives` + `includeItemsFromAllDrives=true` + `supportsAllDrives=true` are required for shared drives. Default queries only search My Drive.
- **Silent overwrite:** Never overwrite without confirmation. Check file existence first, present options to executive.
- **Token expiry mid-operation:** Long batch operations can exceed token TTL. Validate token before each batch chunk.

## Verification

- [ ] `setup.py --check` returns exit 0 (OAuth token valid)
- [ ] Search query includes `trashed = false` hardening
- [ ] Upload shows DRAFT to executive before API call (Draft-First)
- [ ] Uploaded file URL is registered in artifact manifest
- [ ] Drive operation logged in active microverso's `log.md`
- [ ] Shared Drive queries include `supportsAllDrives=true`
