#!/usr/bin/env bash
# =============================================================================
# Step 11: Integração — Context7 (documentação de tech stacks via MCP)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

configure_context7_mcp() {
  # Toggle gate: proceed when EXOCORTEX_ENABLE_CONTEXT7=1 OR CONTEXT7_API_KEY is
  # set (back-compat: key-based installs keep working without the flag).
  if [ "${EXOCORTEX_ENABLE_CONTEXT7:-0}" != "1" ] && [ -z "${CONTEXT7_API_KEY:-}" ]; then
    info "Context7 não ativado (EXOCORTEX_ENABLE_CONTEXT7 != 1 e CONTEXT7_API_KEY não definida)"
    info "  Para configurar: EXOCORTEX_ENABLE_CONTEXT7=1 bash setup.sh"
    return 0
  fi

  if ! command -v hermes >/dev/null 2>&1; then
    warn "hermes CLI não encontrado; pulando context7 MCP"
    return 0
  fi
  if hermes mcp list 2>/dev/null | grep -q "context7"; then
    log "MCP server 'context7' já configurado"
    return 0
  fi
  if [ -z "${CONTEXT7_API_KEY:-}" ]; then
    mkdir -p "$HERMES_HOME/reminders"
    cat > "$HERMES_HOME/reminders/context7-api-key.md" <<'EOF'
# Pending Context7 API Key

Context7 MCP não foi configurado porque CONTEXT7_API_KEY não estava definida.
Context7 fornece documentação atualizada de tech stacks (Next.js, React, etc.).

Para configurar:
1. Obtenha uma API key em https://context7.com
2. Execute: CONTEXT7_API_KEY=<key> bash setup.sh
   ou configure manualmente: hermes mcp add context7 --command "npx -y @context7/mcp" --env CONTEXT7_API_KEY=<key>
EOF
    info "CONTEXT7_API_KEY não definida; lembrete criado"
    info "  Context7 pode ser adicionado depois: hermes mcp add context7 --command 'npx -y @context7/mcp'"
    return 0
  fi
  printf 'y\n' | hermes mcp add context7 \
    --command "npx -y @context7/mcp" \
    --env "CONTEXT7_API_KEY=${CONTEXT7_API_KEY}" \
    >/dev/null 2>&1 && \
    log "MCP server 'context7' adicionado (documentação de tech stacks)" || \
    warn "Falha ao adicionar MCP server 'context7'"
}

info "Context7 (documentação de tech stacks via MCP)..."
configure_context7_mcp
