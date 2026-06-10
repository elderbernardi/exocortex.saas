---
name: excrtx-integrate-gdrive
description: Configure and operate Google Drive via direct API (no Composio), with focus on search robustness and validation.
version: 1.0.0
author: Exocortex
metadata:
  hermes:
    tags: [exocortex, integration, gdrive, api]
---

# Google Drive Integration

Direct Google Drive API integration without Composio, focusing on search robustness and validation.

## Trigger

Activate when:
- The executive requests file upload, search, or management on Google Drive
- An artifact needs to be exported to Drive
- `excrtx-produce-artifacts` needs a Drive destination

## Procedure

### 1. Authentication

Use the OAuth token managed by `excrtx-integrate-oauth`. If not configured, guide the executive through setup.

### 2. Search

Drive search is notoriously fragile. Apply hardening:

1. **Normalize query** — strip diacritics, lowercase, remove special chars
2. **Use `fullText contains`** for content search, `name contains` for filenames
3. **Paginate** — never trust first-page results alone
4. **Validate results** — confirm MIME type, modification date, owner

See: `references/drive-search-hardening.md`

### 3. Upload

1. Resolve target folder (create if missing)
2. Check for existing file with same name (avoid duplicates)
3. Upload with correct MIME type
4. Return shareable link

### 4. Artifact Export

When `excrtx-produce-artifacts` requests Drive export:

1. Generate artifact locally
2. Upload to the microverso's designated Drive folder
3. Register Drive URL in artifact manifest

## Rules

- Never upload without confirming target folder with the executive
- Never overwrite existing files silently — ask first
- Always validate OAuth token before operations
- Log all Drive operations in the active microverso's log

## Verification

- [ ] OAuth token validated before API calls
- [ ] Search results verified (MIME, date, owner)
- [ ] Duplicate check before upload
- [ ] Drive URL registered in manifest after upload
