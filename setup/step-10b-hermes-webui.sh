#!/usr/bin/env bash
# =============================================================================
# Step 10b: Integração — Hermes WebUI (cockpit opcional)
# =============================================================================
# Provisiona o hermes-webui (nesquena/hermes-webui, licença MIT) como
# interface web do Hermes Agent. Ativação via EXOCORTEX_ENABLE_HERMES_WEBUI=1.
#
# Fonte controlada em provision/sources/sources.lock.yaml (ref pinada).
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

setup_hermes_webui() {
  if [ "${EXOCORTEX_ENABLE_HERMES_WEBUI:-0}" != "1" ]; then
    info "Hermes WebUI não ativado por default"
    info "  Para configurar: EXOCORTEX_ENABLE_HERMES_WEBUI=1 bash setup.sh"
    return 0
  fi

  if ! command -v git >/dev/null 2>&1; then
    warn "git não encontrado; Hermes WebUI não foi provisionado"
    return 0
  fi

  local installer="$SCRIPT_DIR/provision/hermes-webui/scripts/install.sh"
  if [ ! -x "$installer" ] && [ ! -f "$installer" ]; then
    warn "Instalador Hermes WebUI não encontrado: $installer"
    return 0
  fi

  info "Provisionando Hermes WebUI opcional"
  bash "$installer"

  echo ""
  warn "====================================================================="
  warn "  IMPORTANTE: O cockpit/servidor da Web UI foi instalado com sucesso."
  warn "  Ele NÃO inicia automaticamente. Para utilizá-lo, você deve rodar:"
  warn "    cd ~/.hermes/hermes-webui && ./ctl.sh start"
  warn "====================================================================="
  echo ""
}

info "Hermes WebUI (cockpit opcional)..."
setup_hermes_webui
