#!/usr/bin/env bash
# =============================================================================
# Step 07: Identidade (SOUL_SEED.md → SOUL.md) + Branding (logo)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

if [ -f "$SCRIPT_DIR/SOUL_SEED.md" ]; then
  cp "$SCRIPT_DIR/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"
  log "SOUL.md instalado (de SOUL_SEED.md)"
fi

# ─── Branding: logo ASCII + script ───────────────────────────────────────
BRANDING_SRC="$ACERVO/global/branding"
BRANDING_DST="$HERMES_HOME"

if [ -f "$BRANDING_SRC/exocortex-ascii-logo.txt" ]; then
  cp "$BRANDING_SRC/exocortex-ascii-logo.txt" "$BRANDING_DST/exocortex-ascii-logo.txt"
  log "Logo ASCII instalada em HERMES_HOME"
else
  warn "Logo ASCII não encontrada em $BRANDING_SRC"
fi

if [ -f "$BRANDING_SRC/exocortex-logo.sh" ]; then
  cp "$BRANDING_SRC/exocortex-logo.sh" "$BRANDING_DST/exocortex-logo.sh"
  chmod +x "$BRANDING_DST/exocortex-logo.sh"
  log "Logo script instalado em HERMES_HOME (executável)"
else
  warn "Logo script não encontrado em $BRANDING_SRC"
fi
