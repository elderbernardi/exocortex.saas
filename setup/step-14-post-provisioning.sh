#!/usr/bin/env bash
# =============================================================================
# Step 14: Verificação pós-provisionamento
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

info "Iniciando verificação pós-provisionamento..."
if [ -x "$SCRIPT_DIR/scripts/post-provisioning-verify.sh" ]; then
  bash "$SCRIPT_DIR/scripts/post-provisioning-verify.sh" || \
    warn "Verificação pós-provisionamento reportou falhas (veja relatório no Acervo)"
else
  warn "Script de verificação não encontrado: $SCRIPT_DIR/scripts/post-provisioning-verify.sh"
fi
