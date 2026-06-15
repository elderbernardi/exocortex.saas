#!/usr/bin/env bash
# =============================================================================
# Step 16: Skin EXCRTX no Hermes WebUI (identidade visual)
# =============================================================================
# Provisiona a skin EXCRTX no Hermes WebUI e define tema light + skin excrtx
# como padrão. Idempotente — seguro rodar múltiplas vezes.
#
# CSS injetado em static/style.css, registrado em:
#   - static/index.html  (whitelist de skins)
#   - api/config.py      (enum do servidor)
#   - static/boot.js     (lista do skin picker)
#   - static/i18n.js     (texto de ajuda /theme em 15 idiomas)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

setup_excrtx_skin() {
  local provisioner="$SCRIPT_DIR/setup/provision/scripts/provision-excrtx-skin.py"

  if [ ! -f "$provisioner" ]; then
    warn "Provisioner não encontrado: $provisioner"
    return 0
  fi

  if [ ! -d "$HERMES_HOME/hermes-webui" ]; then
    info "Hermes WebUI não instalado — skin EXCRTX não provisionada"
    return 0
  fi

  info "Provisionando skin EXCRTX no Hermes WebUI..."
  python3 "$provisioner"
}

info "Skin EXCRTX (identidade visual)..."
setup_excrtx_skin
