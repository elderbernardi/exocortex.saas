# Google Drive Upload via API — Functional Pattern

Use this via `execute_code` when publishing artifacts to Google Drive.
The skill's original `artifact_publish.py` does **not** exist — this is the canonical replacement.

## Pre-conditions

- OAuth token at `~/.hermes/google_token.json` (verified with `setup.py --check`)
- `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2` installed
- Artifact directory created with exports in place

## Script

```python
import json, sys
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
TOKEN_PATH = HERMES_HOME / "google_token.json"

# ── Adjust these per-artifact ──
ARTIFACT_DIR = HERMES_HOME / "acervo" / "_artifacts" / "items" / "{artifact_id}"
HTML_PATH = ARTIFACT_DIR / "exports" / "{filename}.html"
DRIVE_FOLDER = ["exocortex", "inbox"]  # split path into parts
DRIVE_FILENAME = "{descriptive-name}.html"
DRIVE_MIME = "text/html"
DRIVE_DESC = "{description}"
# ─────────────────────────────────

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
service = build("drive", "v3", credentials=creds)

def find_or_create_path(service, path_parts):
    """Walk/create folder path, return final folder ID."""
    parent_id = "root"
    for part in path_parts:
        q = f"name = '{part}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed = false"
        results = service.files().list(q=q, fields="files(id,name)", pageSize=5).execute()
        files = results.get("files", [])
        if files:
            parent_id = files[0]["id"]
        else:
            folder_meta = {
                "name": part,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id]
            }
            folder = service.files().create(body=folder_meta, fields="id").execute()
            parent_id = folder["id"]
            print(f"  CREATED folder '{part}': {parent_id}")
    return parent_id

print(f"Resolving Drive destination: {'/'.join(DRIVE_FOLDER)}")
folder_id = find_or_create_path(service, DRIVE_FOLDER)
print(f"  folder_id: {folder_id}")

file_metadata = {
    "name": DRIVE_FILENAME,
    "parents": [folder_id],
    "description": DRIVE_DESC
}
media = MediaFileUpload(str(HTML_PATH), mimetype=DRIVE_MIME, resumable=True)
uploaded = service.files().create(
    body=file_metadata,
    media_body=media,
    fields="id, name, webViewLink, size, md5Checksum"
).execute()

print(f"\nUPLOAD OK:")
print(json.dumps(uploaded, indent=2))
```

## Return values

The upload returns a dict with:
- `id` — Drive file ID (use in receipt)
- `name` — confirmed filename
- `webViewLink` — human-viewable link
- `size` — bytes
- `md5Checksum` — MD5 hash for verification

## After upload

1. Write `manifest.json` with `status: "published"`, SHA-256, and `drive_target`
2. Write `receipts/receipt.google_drive.json` with `folder_id`, `drive_file_id`, `web_view_link`, SHA-256, `md5`, `size`
3. Report to executive: filename, Drive path, web link

## Session reference

Session 2026-06-16: HTML README render → `art_20260616_readme_release` published to `exocortex/inbox`.
