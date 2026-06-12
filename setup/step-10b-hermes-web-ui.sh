#!/usr/bin/env bash
# =============================================================================
# Step 10b: Integração — Hermes Web UI (cockpit opcional)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

setup_hermes_web_ui() {
  if [ "${EXOCORTEX_SKIP_HERMES_WEB_UI_SETUP_STEP:-0}" = "1" ]; then
    info "Hermes Web UI: step pulado para evitar recursão durante bootstrap interno"
    return 0
  fi

  if [ "${EXOCORTEX_ENABLE_HERMES_WEB_UI:-0}" != "1" ]; then
    info "Hermes Web UI não ativado por default"
    info "  Para configurar: EXOCORTEX_ENABLE_HERMES_WEB_UI=1 bash setup.sh"
    return 0
  fi

  if ! command -v docker >/dev/null 2>&1; then
    warn "docker não encontrado; Hermes Web UI não foi provisionado"
    return 0
  fi

  local installer="$SCRIPT_DIR/provision/hermes-web-ui/scripts/install.sh"
  if [ ! -x "$installer" ] && [ ! -f "$installer" ]; then
    warn "Instalador Hermes Web UI não encontrado: $installer"
    return 0
  fi

  info "Provisionando Hermes Web UI opcional"
  bash "$installer"
}

info "Hermes Web UI (cockpit opcional)..."
setup_hermes_web_ui
