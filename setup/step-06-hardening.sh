#!/usr/bin/env bash
# =============================================================================
# Step 06: Hardening (Drive search + email baseline + MCP baseline)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

patch_google_drive_search() {
  local gapi="$HERMES_HOME/skills/productivity/google-workspace/scripts/google_api.py"

  if [ ! -f "$gapi" ]; then
    warn "google_api.py não encontrado em $gapi (patch Drive não aplicado)"
    return 0
  fi

  local patch_status
  patch_status=$(python3 - "$gapi" <<'PY'
import py_compile
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

pattern = r"def drive_search\(args\):\n(?:.*\n)*?\n\ndef drive_get\(args\):"
replacement = r'''def drive_search(args):
    if args.max < 1:
        print("ERROR: --max must be >= 1", file=sys.stderr)
        sys.exit(1)

    if args.raw_query:
        query = args.query
    else:
        # Escape single quotes in Drive query literals and ignore trashed items by default.
        escaped = args.query.replace('\\\\', '\\\\\\\\').replace("'", "\\\\'")
        query = f"fullText contains '{escaped}' and trashed = false"

    fields = "nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)"
    page_size = min(args.max, 1000)
    files = []
    page_token = None

    if _gws_binary():
        while len(files) < args.max:
            params = {
                "q": query,
                "pageSize": min(page_size, args.max - len(files)),
                "fields": fields,
            }
            if page_token:
                params["pageToken"] = page_token
            results = _run_gws(["drive", "files", "list"], params=params)
            files.extend(results.get("files", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break
        print(json.dumps(files[: args.max], indent=2, ensure_ascii=False))
        return

    service = build_service("drive", "v3")
    while len(files) < args.max:
        results = service.files().list(
            q=query,
            pageSize=min(page_size, args.max - len(files)),
            fields=fields,
            pageToken=page_token,
        ).execute()
        files.extend(results.get("files", []))
        page_token = results.get("nextPageToken")
        if not page_token:
            break
    print(json.dumps(files[: args.max], indent=2, ensure_ascii=False))


def drive_get(args):'''

new_text, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
if count != 1:
    print("SKIP")
    raise SystemExit(0)

if new_text == text:
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError:
        print("SKIP")
        raise SystemExit(0)
    else:
        print("ALREADY")
        raise SystemExit(0)

path.write_text(new_text, encoding="utf-8")
print("PATCHED")
PY
)

  case "$patch_status" in
    ALREADY) log "Google Drive search hardening já presente" ;;
    PATCHED) log "Google Drive search hardening aplicado" ;;
    *) warn "Falha ao aplicar patch de Drive (bloco não encontrado)" ;;
  esac
}

enforce_email_baseline() {
  local himalaya_skill="$HERMES_HOME/skills/email/himalaya"
  local hymalaia_skill="$HERMES_HOME/skills/email/hymalaia"

  if [ -d "$himalaya_skill" ]; then
    rm -rf "$himalaya_skill"
    log "Email baseline: skill 'himalaya' removida; padrão é 'productivity/google-workspace'"
  elif [ -d "$hymalaia_skill" ]; then
    rm -rf "$hymalaia_skill"
    log "Email baseline: skill 'hymalaia' removida; padrão é 'productivity/google-workspace'"
  else
    log "Email baseline OK: skill 'himalaya/hymalaia' ausente; padrão é 'productivity/google-workspace'"
  fi
}

enforce_mcp_baseline() {
  if ! command -v hermes >/dev/null 2>&1; then
    warn "hermes CLI não encontrado; pulando baseline MCP"
    return 0
  fi
  if hermes mcp list 2>/dev/null | grep -q "composio"; then
    if printf 'y\n' | hermes mcp remove composio >/dev/null 2>&1; then
      log "MCP baseline: 'composio' removido"
    else
      warn "Falha ao remover MCP server 'composio'"
    fi
  else
    log "MCP baseline OK: 'composio' já ausente"
  fi
}

info "Aplicando hardening de Google Drive search..."
patch_google_drive_search

info "Aplicando baseline de email: Google Workspace como padrão..."
enforce_email_baseline

info "Aplicando baseline MCP: removendo composio..."
enforce_mcp_baseline
