#!/usr/bin/env bash
# =============================================================================
# Hermes WebUI — Install Script
# =============================================================================
# Clona e provisiona o hermes-webui (nesquena/hermes-webui) no ambiente local.
# Consome a ref controlada de provision/sources/sources.lock.yaml.
#
# Uso:
#   bash provision/hermes-webui/scripts/install.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LOCK_FILE="$REPO_ROOT/provision/sources/sources.lock.yaml"

# ─── Helpers ─────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

# ─── Environment ─────────────────────────────────────────────────────────────

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
WEBUI_HOME="${EXOCORTEX_HERMES_WEBUI_HOME:-$HERMES_HOME/hermes-webui}"
WEBUI_PORT="${EXOCORTEX_HERMES_WEBUI_PORT:-8787}"
WEBUI_HOST="${EXOCORTEX_HERMES_WEBUI_HOST:-127.0.0.1}"

# ─── Resolve ref from sources.lock.yaml ──────────────────────────────────────

resolve_webui_ref() {
  [ -f "$LOCK_FILE" ] || fail "Lock file não encontrado: $LOCK_FILE"

  local ref
  ref=$(python3 - "$LOCK_FILE" <<'PY'
import sys
from pathlib import Path

lock = Path(sys.argv[1]).read_text(encoding="utf-8")
in_webui = False
in_controlled = False

for line in lock.splitlines():
    stripped = line.strip()
    indent = len(line) - len(line.lstrip(" "))

    if indent == 2 and stripped == "hermes-webui:":
        in_webui = True
        continue
    elif indent == 2 and stripped.endswith(":") and in_webui:
        break

    if in_webui and indent == 4 and stripped == "controlled:":
        in_controlled = True
        continue
    elif in_webui and indent == 4 and stripped.endswith(":"):
        in_controlled = False
        continue

    if in_webui and in_controlled and stripped.startswith("ref:"):
        print(stripped.split(":", 1)[1].strip())
        break
PY
  )

  [ -n "$ref" ] || fail "Ref hermes-webui não encontrada em $LOCK_FILE"
  echo "$ref"
}

resolve_webui_upstream() {
  [ -f "$LOCK_FILE" ] || fail "Lock file não encontrado: $LOCK_FILE"

  local url
  url=$(python3 - "$LOCK_FILE" <<'PY'
import sys
from pathlib import Path

lock = Path(sys.argv[1]).read_text(encoding="utf-8")
in_webui = False
in_upstream = False

for line in lock.splitlines():
    stripped = line.strip()
    indent = len(line) - len(line.lstrip(" "))

    if indent == 2 and stripped == "hermes-webui:":
        in_webui = True
        continue
    elif indent == 2 and stripped.endswith(":") and in_webui:
        break

    if in_webui and indent == 4 and stripped == "upstream:":
        in_upstream = True
        continue
    elif in_webui and indent == 4 and stripped.endswith(":"):
        in_upstream = False
        continue

    if in_webui and in_upstream and stripped.startswith("git:"):
        print(stripped.split(":", 1)[1].strip())
        break
PY
  )

  [ -n "$url" ] || fail "Upstream git hermes-webui não encontrado em $LOCK_FILE"
  echo "$url"
}

resolve_webui_controlled_git() {
  [ -f "$LOCK_FILE" ] || fail "Lock file não encontrado: $LOCK_FILE"

  python3 - "$LOCK_FILE" <<'PY'
import sys
from pathlib import Path

lock = Path(sys.argv[1]).read_text(encoding="utf-8")
in_webui = False
in_controlled = False

for line in lock.splitlines():
    stripped = line.strip()
    indent = len(line) - len(line.lstrip(" "))

    if indent == 2 and stripped == "hermes-webui:":
        in_webui = True
        continue
    elif indent == 2 and stripped.endswith(":") and in_webui:
        break

    if in_webui and indent == 4 and stripped == "controlled:":
        in_controlled = True
        continue
    elif in_webui and indent == 4 and stripped.endswith(":"):
        in_controlled = False
        continue

    if in_webui and in_controlled and stripped.startswith("git:"):
        print(stripped.split(":", 1)[1].strip())
        break
PY
}

# ─── Main ────────────────────────────────────────────────────────────────────

main() {
  local upstream_url upstream_ref controlled_git clone_url

  info "Provisionando Hermes WebUI..."
  info "  HERMES_HOME:  $HERMES_HOME"
  info "  WEBUI_HOME:   $WEBUI_HOME"
  info "  WEBUI_PORT:   $WEBUI_PORT"
  info "  WEBUI_HOST:   $WEBUI_HOST"

  controlled_git="$(resolve_webui_controlled_git)"
  upstream_url="$(resolve_webui_upstream)"
  upstream_ref="$(resolve_webui_ref)"

  # Prefer the controlled fork as clone source once it is a real URL;
  # fall back to upstream while controlled.git is still a placeholder.
  case "$controlled_git" in
    http*|git@*) clone_url="$controlled_git" ;;
    *)           clone_url="$upstream_url" ;;
  esac

  info "  Upstream:     $upstream_url"
  info "  Fonte clone:  $clone_url"
  info "  Ref pinada:   $upstream_ref"

  # Validate ref format: SHA-40, master/main, or a controlled branch ref (ex.: exocortex/stable)
  if [[ ! "$upstream_ref" =~ ^([0-9a-f]{40}|[A-Za-z][A-Za-z0-9._/-]*)$ ]]; then
    fail "Ref inválida (esperado SHA-1, master/main ou branch controlada): $upstream_ref"
  fi

  # Clone or fetch
  if [ ! -d "$WEBUI_HOME/.git" ]; then
    info "Clonando hermes-webui em $WEBUI_HOME..."
    git clone "$clone_url" "$WEBUI_HOME"
    log "Clone concluído"
  else
    info "hermes-webui já presente em $WEBUI_HOME"
    info "Atualizando (fetch)..."
    git -C "$WEBUI_HOME" fetch --tags --prune origin
    log "Fetch concluído"
  fi

  # Checkout pinned ref
  info "Fazendo checkout da ref controlada..."
  git -C "$WEBUI_HOME" checkout "$upstream_ref" --quiet 2>/dev/null \
    || git -C "$WEBUI_HOME" checkout -b "controlled-$(echo "$upstream_ref" | head -c 8)" "$upstream_ref" --quiet

  # When the ref is a branch (not a pinned SHA), advance an existing clone to the
  # freshly fetched tip — plain `checkout <branch>` does not fast-forward. Refuse
  # to clobber local divergence (warn instead), so a re-provision picks up the
  # latest controlled commits without silently discarding local work.
  if git -C "$WEBUI_HOME" show-ref --verify --quiet "refs/remotes/origin/$upstream_ref"; then
    if ! git -C "$WEBUI_HOME" merge --ff-only "origin/$upstream_ref" --quiet 2>/dev/null; then
      warn "Sem fast-forward para origin/$upstream_ref (divergência local) — HEAD mantido em $(git -C "$WEBUI_HOME" rev-parse --short HEAD)"
    fi
  fi
  log "Checkout na ref controlada: $(git -C "$WEBUI_HOME" rev-parse HEAD | head -c 12)"

  # Verify bootstrap.py exists
  if [ ! -f "$WEBUI_HOME/bootstrap.py" ]; then
    fail "bootstrap.py não encontrado em $WEBUI_HOME — clone pode estar corrompido"
  fi

  # Write .env with Exocórtex defaults if not present
  if [ ! -f "$WEBUI_HOME/.env" ]; then
    info "Criando .env com defaults do Exocórtex..."
    cat > "$WEBUI_HOME/.env" <<EOF
# Gerado pelo provisioner Exocórtex em $(date -Iseconds)
HERMES_WEBUI_HOST=$WEBUI_HOST
HERMES_WEBUI_PORT=$WEBUI_PORT
HERMES_HOME=$HERMES_HOME
EOF
    log ".env criado"
  else
    info ".env já existe, preservando"
  fi

  echo
  log "Hermes WebUI provisionado com sucesso."
  info "Para iniciar:"
  info "  cd $WEBUI_HOME && ./ctl.sh start"
  info "Ou:"
  info "  cd $WEBUI_HOME && python3 bootstrap.py"
}

main "$@"
