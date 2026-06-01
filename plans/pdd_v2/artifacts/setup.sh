#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — PDD v2 Setup Script (Semente)
# =============================================================================
# Script de reprodução: provisiona um Hermes limpo com configuração Exocórtex v2.
#
# Uso:
#   HERMES_HOME=/path/to/hermes bash setup.sh
#
# Requer:
#   - HERMES_HOME definido (diretório do Hermes alvo)
#   - Este script rodado a partir do diretório plans/pdd_v2/artifacts/
# =============================================================================

set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

patch_google_drive_search() {
  local gapi="$HERMES_HOME/skills/productivity/google-workspace/scripts/google_api.py"

  if [ ! -f "$gapi" ]; then
    warn "google_api.py não encontrado em $gapi (patch Drive não aplicado)"
    return 0
  fi

  local patch_status
  patch_status=$(python3 - "$gapi" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

if "trashed = false" in text and "nextPageToken, files(" in text:
    print("ALREADY")
    raise SystemExit(0)

pattern = r"def drive_search\(args\):\n(?:.*\n)*?\n\ndef drive_get\(args\):"
replacement = '''def drive_search(args):
    if args.max < 1:
        print("ERROR: --max must be >= 1", file=sys.stderr)
        sys.exit(1)

    if args.raw_query:
        query = args.query
    else:
        # Escape single quotes in Drive query literals and ignore trashed items by default.
        escaped = args.query.replace("\\", "\\\\").replace("'", "\\'")
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

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Exocórtex.IA — PDD v2 Setup                ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

info "HERMES_HOME: $HERMES_HOME"
info "ARTIFACTS:   $SCRIPT_DIR"

# =============================================================================
# Step 1: Criar estrutura base
# =============================================================================
info "Criando estrutura base..."

mkdir -p "$HERMES_HOME/skills/exocortex"
mkdir -p "$HERMES_HOME/acervo"/{macro/assets,global,micro/_template,shared/cross-refs}
mkdir -p "$HERMES_HOME/profiles"
mkdir -p "$HERMES_HOME/skill-bundles"
mkdir -p "$HERMES_HOME/memories"

log "Estrutura de diretórios criada"

# =============================================================================
# Step 2: Copiar skills
# =============================================================================
info "Instalando skills..."

SKILLS_SRC="$SCRIPT_DIR/skills"
SKILLS_DST="$HERMES_HOME/skills/exocortex"

if [ -d "$SKILLS_SRC" ]; then
  for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name=$(basename "$skill_dir")
    if [ -d "$skill_dir" ]; then
      mkdir -p "$SKILLS_DST/$skill_name"
      cp -r "$skill_dir"* "$SKILLS_DST/$skill_name/" 2>/dev/null || true
      log "Skill: $skill_name"
    fi
  done
else
  fail "Skills source não encontrado: $SKILLS_SRC"
fi

# =============================================================================
# Step 3: Copiar acervo
# =============================================================================
info "Instalando acervo..."

ACERVO_SRC="$SCRIPT_DIR/acervo"
ACERVO_DST="$HERMES_HOME/acervo"

if [ -d "$ACERVO_SRC" ]; then
  cp -r "$ACERVO_SRC"/* "$ACERVO_DST/" 2>/dev/null || true
  log "Acervo: $(find "$ACERVO_DST" -type f 2>/dev/null | wc -l) arquivos"
else
  fail "Acervo source não encontrado: $ACERVO_SRC"
fi

# =============================================================================
# Step 4: Copiar profiles
# =============================================================================
info "Instalando profiles..."

PROFILES_SRC="$SCRIPT_DIR/profiles"
PROFILES_DST="$HERMES_HOME/profiles"

if [ -d "$PROFILES_SRC" ]; then
  cp -r "$PROFILES_SRC"/* "$PROFILES_DST/" 2>/dev/null || true
  log "Profiles: $(ls -1d "$PROFILES_DST"/*/ 2>/dev/null | wc -l) profiles"
fi

# =============================================================================
# Step 5: Copiar bundle
# =============================================================================
info "Instalando bundles..."

BUNDLES_SRC="$SCRIPT_DIR/skill-bundles"
BUNDLES_DST="$HERMES_HOME/skill-bundles"

if [ -d "$BUNDLES_SRC" ]; then
  cp -r "$BUNDLES_SRC"/* "$BUNDLES_DST/" 2>/dev/null || true
  log "Bundle copiado"
fi

# =============================================================================
# Step 5.1: Hardening Drive Search no google-workspace
# =============================================================================
info "Aplicando hardening de Google Drive search..."
patch_google_drive_search

# =============================================================================
# Step 6: Identidade (SOUL_SEED)
# =============================================================================
if [ -f "$SCRIPT_DIR/SOUL_SEED.md" ]; then
  cp "$SCRIPT_DIR/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"
  log "SOUL.md instalado (de SOUL_SEED.md)"
fi

# =============================================================================
# Step 7: Verificação
# =============================================================================
echo ""
info "=== VERIFICAÇÃO ==="
echo ""

echo "Skills instaladas:"
SKILL_COUNT=0
for d in "$SKILLS_DST"/*/; do
  [ -d "$d" ] && echo "  ✓ $(basename "$d")" && SKILL_COUNT=$((SKILL_COUNT + 1))
done
echo "  Total: $SKILL_COUNT"
echo ""

echo "Acervo (4 camadas):"
for layer in macro global micro shared; do
  count=$(find "$ACERVO_DST/$layer" -type f 2>/dev/null | wc -l)
  echo "  $layer/: $count arquivos"
done
echo ""

echo "Profiles:"
ls "$PROFILES_DST/" 2>/dev/null | while read -r p; do echo "  ✓ $p"; done
echo ""

echo "Bundles:"
ls "$BUNDLES_DST/" 2>/dev/null | while read -r b; do echo "  ✓ $b"; done
echo ""

# Verificar hermes CLI
if command -v hermes > /dev/null 2>&1; then
  log "hermes CLI: $(hermes --version 2>/dev/null | head -1)"
else
  warn "hermes CLI não encontrado no PATH"
fi

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Setup PDD v2 completo.                     ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
