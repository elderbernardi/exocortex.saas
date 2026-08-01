#!/usr/bin/env bash
# =============================================================================
# Step 07: Identidade (SOUL_SEED.md → SOUL.md) + Branding (logo)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

if [ -f "$SCRIPT_DIR/SOUL_SEED.md" ]; then
  SOUL_TARGET="$HERMES_HOME/SOUL.md"
  if [ -f "$SOUL_TARGET" ] && grep -q "Você é o Exocórtex.IA" "$SOUL_TARGET"; then
    # O compile_soul.py roda depois deste step e atualiza apenas o bloco
    # compilado. A Constituição preenchida pelo onboarding fica intacta.
    log "SOUL.md Exocórtex já presente; identidade e onboarding preservados"
  else
    if [ -f "$SOUL_TARGET" ]; then
      BACKUP_DIR="$HERMES_HOME/backups/exocortex-install"
      mkdir -p "$BACKUP_DIR"
      BACKUP_PATH="$BACKUP_DIR/SOUL.before-exocortex.$(date +%Y%m%d_%H%M%S).md"
      cp "$SOUL_TARGET" "$BACKUP_PATH"
      log "Identidade Hermes anterior preservada em $BACKUP_PATH"
    fi
    cp "$SCRIPT_DIR/SOUL_SEED.md" "$SOUL_TARGET"
    log "SOUL.md Exocórtex instalado; Macroverso permanece pendente até o onboarding"
  fi
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
