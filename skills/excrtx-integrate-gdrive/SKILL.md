---
name: excrtx-integrate-gdrive
description: Operate Google Drive as a working system — find, inspect, edit, clean — with hardened search, Draft-First governance, and workspace hygiene. Direct API, no Composio.
version: 1.2.0
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

Operate Google Drive as a working system, not a collection of isolated files. Covers discovery, inspection, precise editing, and workspace hygiene — all over the Hermes `google-workspace` tool surface.

## When to Use

Activate when:
- The executive needs to **find** a document, spreadsheet, deck, or folder in Drive — locate the right asset, distinguish canonical from stale duplicate
- The executive needs to **inspect** structure before editing — summarize tabs, headings, slide count, ownership, last modification
- The executive needs to **edit** a Drive asset with precision — upload, update, append, share, or delete
- The executive needs to **clean** a workspace — archive, rename, flag obsolescence, surface duplicates, consolidate scattered trackers
- An artifact needs to be exported to Drive
- `excrtx-produce-artifacts` needs a Drive destination

**Don't use for:** Local file operations without Drive involvement. OAuth setup (use `excrtx-integrate-oauth`). NotebookLM integration (use `excrtx-integrate-nlmops`). Browser-based Drive access. Read-only link sharing without API.

> Upon activation, classify the input according to the Exocórtex vector taxonomy:
> - **Execução** — uploading, searching, editing, exporting Drive assets (default for most Drive operations)
> - **Manutenção** — token refresh, folder structure audit, workspace hygiene, duplicate cleanup
> - **Evolução** — rare in Drive context: when the executive is exploring structure or deciding where files belong
> - **Ambíguo** — if unclear whether this is a find, inspect, edit, or clean task, ask before acting
>
> All output must respect anti-slop quality standards. Drive operations that produce user-facing text (summaries, reports, structured output per the Operating Model format) must pass anti-slop gate. Operations logged to the active microverso's `log.md` must follow the Acervo Cognitivo 4-layer memory model.

## Operating Model

Every Drive operation follows one workflow, three levels.

### Workflow: Find → Inspect → Edit → Clean

```
Find   → locate the right asset, distinguish canonical from stale duplicate
Inspect → summarize structure before touching anything (tabs, headings, slide count)
Edit   → use the smallest tool capable; precise, range-aware, Draft-First for externals
Clean  → archive, rename, flag obsolescence, surface duplicates, consolidate scattered trackers
```

### Three Levels of Operation

| Level | What it does | Example |
|---|---|---|
| **Discovery** | Locate, differentiate canonical vs duplicate, map structure | "Which tracker is the active one, not the 2025 copy?" |
| **Intervention** | Edit, summarize, consolidate, restructure | "Condense this spreadsheet and highlight the risk rows" |
| **Hygiene** | Archive, rename, flag obsolescence, follow-up chain | "This doc is a duplicate of the 2026 version — archive?" |

When operating, classify the current task into one of these three levels. Discovery always precedes Intervention. Intervention in a shared critical document must default to reversible operations.

### Output Format

Every completed operation reports using this structure:

```text
ASSET        → file name, type, why this is the right file
CURRENT STATE → structure summary, key problems found
ACTION       → edits made or recommended
FOLLOW-UPS   → archive/merge/duplicate cleanup/next file to update
```

### Operational Governance

1. **Never edit blindly.** Confirm the target when there is meaningful ambiguity between candidates (same name, similar modification time). A wrong-target edit in a shared document is worse than a slow confirmation.
2. **Prefer reversible operations for shared critical documents.** Upload a copy, append instead of overwrite, use trash instead of permanent delete. Only escalate to destructive when explicitly authorized.
3. **Differentiate local cleanup from structural surgery.** Fixing a typo in one cell ≠ refactoring 15 slides. Match tool power to scope. Structural changes get an explicit DRAFT even when the file is internal.

## Procedure

### Step 1 — Validate Authentication

1. Check OAuth token: `python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`
2. If expired, guide the executive through re-auth flow via `excrtx-integrate-oauth`
3. Never proceed with API calls without a validated token

### Step 2 — Search (with hardening)

Use `google_api.py drive search` from the Hermes `google-workspace` skill as the canonical search surface. Drive search is notoriously fragile. Apply this hardening sequence:

1. **Normalize query** — strip diacritics, lowercase, remove special chars
2. **Build query** — use `fullText contains '<term>'` for content, `name contains '<term>'` for filenames
3. **Add safety filter** — always include `trashed = false` in the query
4. **Paginate** — iterate all pages, never trust first-page results alone
5. **Validate results** — confirm MIME type, modification date, and owner before returning

```bash
# Canonical search tool — always use this, never raw curl
GAPI="python3 ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI drive search "name contains '<term>' and trashed = false" --max 10
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

### Search & Technical
- **Search returning stale results:** Drive API caches aggressively. If a recently uploaded file isn't found, wait 5-10s and retry with `orderBy=modifiedTime desc`.
- **MIME type mismatch:** Google Docs native formats (application/vnd.google-apps.*) cannot be downloaded directly. Use export endpoint with target MIME.
- **Shared Drive vs My Drive:** `corpora=allDrives` + `includeItemsFromAllDrives=true` + `supportsAllDrives=true` are required for shared drives. Default queries only search My Drive.
- **Silent overwrite:** Never overwrite without confirmation. Check file existence first, present options to executive.
- **Token expiry mid-operation:** Long batch operations can exceed token TTL. Validate token before each batch chunk.

### Operational Governance
- **Wrong-target edit:** Operating on a stale duplicate instead of the canonical file is the most common and most damaging Workspace failure. Always verify you have the right file before editing — check owner, modification time, and folder context.
- **Destructive edit on shared critical doc:** Overwriting a cell range in the company-wide tracker without DRAFT is irreversible and affects every stakeholder. Default to append, copy, or trash. Require explicit authorization for destructive operations.
- **Skipping inspection before editing:** Editing a spreadsheet without first reading its structure (tab names, header rows, data shape) produces malformed output. Always inspect first — even a 5-second `sheets get` on the header row prevents cascade failures.
- **Mixing tool scopes:** Using a full rewrite to fix one typo wastes tokens and risks collateral damage. Using a cell-level patch to restructure 15 slides takes 50 tool calls and misses the big picture. Match the tool to the scope.

## Verification

### Auth & Search
- [ ] `setup.py --check` returns exit 0 (OAuth token valid)
- [ ] Search query includes `trashed = false` hardening
- [ ] Shared Drive queries include `supportsAllDrives=true`
- [ ] Results paginated with `nextPageToken` (never trust first page alone)

### Draft-First & Publication
- [ ] Upload shows DRAFT to executive before API call (Draft-First)
- [ ] Destructive edits on shared docs have explicit authorization
- [ ] Uploaded file URL is registered in artifact manifest
- [ ] Drive operation logged in active microverso's `log.md`

### Operating Model
- [ ] Inspection completed before first edit (structure confirmed)
- [ ] Correct file confirmed to be canonical (not a stale duplicate)
- [ ] Tool scope matches operation scope (cell edit ≠ full rewrite)
- [ ] Output includes ASSET / CURRENT STATE / ACTION / FOLLOW-UPS
- [ ] Follow-ups explicitly listed (archive, merge, next file, hygiene actions)
