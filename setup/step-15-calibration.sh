#!/usr/bin/env bash
# =============================================================================
# Step 15: Calibração interativa de PDD (Opcional — --calibrate)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

if [ "${CALIBRATE_MODE:-0}" = "1" ]; then
  info "Iniciando calibração interativa cognitivo do Hermes..."
  if [ -x "$SCRIPT_DIR/scripts/calibrate-hermes.sh" ]; then
    bash "$SCRIPT_DIR/scripts/calibrate-hermes.sh"
  else
    warn "Script de calibração não encontrado: $SCRIPT_DIR/scripts/calibrate-hermes.sh"
  fi
fi
