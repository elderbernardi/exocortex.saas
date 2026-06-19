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

# Validação de frontmatter OKF v0.1 no Acervo instalado (não-bloqueante)
if [ -f "$SCRIPT_DIR/scripts/validate_frontmatter.py" ] && [ -d "$ACERVO" ]; then
  info "Validando frontmatter OKF v0.1 no Acervo..."
  if python3 "$SCRIPT_DIR/scripts/validate_frontmatter.py" --dir "$ACERVO" 2>&1; then
    log "Frontmatter do Acervo: válido."
  else
    warn "Frontmatter do Acervo tem arquivos não-conformes com o schema OKF v0.1."
    warn "Execute manualmente para ver detalhes: python3 scripts/validate_frontmatter.py --dir \$ACERVO --report"
    warn "Para migrar arquivos legados: python3 scripts/migrate_frontmatter.py --dir \$ACERVO"
  fi
else
  warn "validate_frontmatter.py ou \$ACERVO não encontrado — validação de frontmatter pulada."
fi
