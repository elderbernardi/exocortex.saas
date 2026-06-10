#!/usr/bin/env bash
# =============================================================================
# Step 05: Copiar profiles e bundles
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

info "Instalando profiles..."

if [ -d "$PROFILES_SRC" ]; then
  cp -r "$PROFILES_SRC"/* "$PROFILES_DST/" 2>/dev/null || true
  log "Profiles: $(ls -1d "$PROFILES_DST"/*/ 2>/dev/null | wc -l) profiles"
fi

info "Instalando bundles..."

if [ -d "$BUNDLES_SRC" ]; then
  cp -r "$BUNDLES_SRC"/* "$BUNDLES_DST/" 2>/dev/null || true
  log "Bundle copiado"
fi
