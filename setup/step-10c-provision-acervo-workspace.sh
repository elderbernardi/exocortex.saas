#!/usr/bin/env bash
# =============================================================================
# Step 10c: Provisiona Space "Acervo Cognitivo" no Hermes WebUI
# =============================================================================
# Usa $ACERVO (canônico, common.sh:58) como path do space.
# Idempotente — não duplica entradas existentes.
# Não-bloqueante: se a WebUI não está instalada, o step segue normalmente.
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

provision_acervo_workspace() {
  local provisioner="$SCRIPT_DIR/setup/provision/scripts/provision-acervo-workspace.py"

  if [ ! -f "$provisioner" ]; then
    warn "Provisioner não encontrado: $provisioner"
    return 0
  fi

  if [ ! -d "$HERMES_HOME/hermes-webui" ]; then
    info "Hermes WebUI não instalado — Space Acervo não provisionado"
    return 0
  fi

  info "Provisionando Space 'Acervo Cognitivo' no Hermes WebUI..."
  info "  ACERVO=${ACERVO:-$EXOCORTEX_HOME/acervo}"
  python3 "$provisioner"
}

info "Space Acervo Cognitivo no Hermes WebUI..."
provision_acervo_workspace
