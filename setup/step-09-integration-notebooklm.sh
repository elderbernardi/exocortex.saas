#!/usr/bin/env bash
# =============================================================================
# Step 09: Integração — NotebookLM (CLI + MCP)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

configure_notebooklm_integration() {
  if ! command -v nlm >/dev/null 2>&1; then
    if command -v uv >/dev/null 2>&1; then
      info "Instalando nlm via uv tool install notebooklm-mcp-cli"
      uv tool install notebooklm-mcp-cli >/dev/null 2>&1 || {
        warn "Falha ao instalar notebooklm-mcp-cli via uv"
        return 0
      }
    else
      warn "nlm CLI não encontrado. Instale com: uv tool install notebooklm-mcp-cli"
      return 0
    fi
  fi
  log "nlm CLI disponível: $(command -v nlm)"
  if nlm login --check >/dev/null 2>&1; then
    log "nlm autenticado"
  else
    mkdir -p "$HERMES_HOME/reminders"
    cat > "$HERMES_HOME/reminders/notebooklm-login.md" <<'EOF'
# Pending NotebookLM login
nlm CLI instalado mas autenticação não está ativa.
No terminal: nlm login && nlm login --check
EOF
    warn "nlm sem auth ativa; lembrete criado"
  fi
  if command -v hermes >/dev/null 2>&1 && command -v notebooklm-mcp >/dev/null 2>&1; then
    if hermes mcp list 2>/dev/null | grep -q "notebooklm"; then
      log "MCP server 'notebooklm' já configurado"
    else
      printf 'y\n' | hermes mcp add notebooklm --command notebooklm-mcp >/dev/null 2>&1 && \
        log "MCP server 'notebooklm' adicionado" || \
        warn "Falha ao adicionar MCP server 'notebooklm'"
    fi
  fi
}

info "NotebookLM (CLI + MCP)..."
configure_notebooklm_integration
