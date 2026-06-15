#!/usr/bin/env bash
# =============================================================================
# Hermes WebUI — Smoke Test
# =============================================================================
# Verifica que o hermes-webui está instalado e funcional.
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
WEBUI_HOME="${EXOCORTEX_HERMES_WEBUI_HOME:-$HERMES_HOME/hermes-webui}"
WEBUI_PORT="${EXOCORTEX_HERMES_WEBUI_PORT:-8787}"

info "Smoke test — Hermes WebUI"
info "  WEBUI_HOME: $WEBUI_HOME"

# Check install directory
[ -d "$WEBUI_HOME" ] || fail "Diretório do WebUI não encontrado: $WEBUI_HOME"
log "Diretório presente"

# Check bootstrap.py
[ -f "$WEBUI_HOME/bootstrap.py" ] || fail "bootstrap.py ausente em $WEBUI_HOME"
log "bootstrap.py presente"

# Check ctl.sh
[ -f "$WEBUI_HOME/ctl.sh" ] || fail "ctl.sh ausente em $WEBUI_HOME"
log "ctl.sh presente"

# Check server.py
[ -f "$WEBUI_HOME/server.py" ] || fail "server.py ausente em $WEBUI_HOME"
log "server.py presente"

# Check controlled ref
if [ -d "$WEBUI_HOME/.git" ]; then
  local_ref="$(git -C "$WEBUI_HOME" rev-parse HEAD)"
  info "Ref local: $local_ref"
  log "Git checkout válido"
else
  warn "Não é um repositório git — pode ser instalação manual"
fi

# Check .env
if [ -f "$WEBUI_HOME/.env" ]; then
  log ".env presente"
else
  warn ".env ausente — usando defaults"
fi

# Optional: check if server is running
if command -v curl >/dev/null 2>&1; then
  if curl -sf "http://127.0.0.1:$WEBUI_PORT/health" >/dev/null 2>&1; then
    log "Servidor respondendo em http://127.0.0.1:$WEBUI_PORT/health"
  else
    info "Servidor não está rodando (normal se não foi iniciado)"
  fi
fi

echo
log "Smoke test concluído."
