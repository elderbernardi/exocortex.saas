#!/usr/bin/env bash
# =============================================================================
# Step 07: Identidade (SOUL_SEED.md → SOUL.md)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

if [ -f "$SCRIPT_DIR/SOUL_SEED.md" ]; then
  cp "$SCRIPT_DIR/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"
  log "SOUL.md instalado (de SOUL_SEED.md)"
fi
