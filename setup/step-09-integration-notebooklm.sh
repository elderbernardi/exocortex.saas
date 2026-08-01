#!/usr/bin/env bash
# NotebookLM — registro e verificação. Dependências são declaradas no manifesto
# setup/capabilities.json e nunca instaladas implicitamente por este estágio.

set -euo pipefail

if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
fi

configure_notebooklm_integration() {
  info "NotebookLM (CLI + MCP)..."

  local missing=0
  local command
  for command in nlm notebooklm-mcp hermes; do
    if ! command -v "$command" >/dev/null 2>&1; then
      warn "Capacidade ausente: $command"
      missing=1
    fi
  done
  if [ "$missing" = "1" ]; then
    warn "Instale a ferramenta isolada e rode novamente: uv tool install notebooklm-mcp-cli"
    return 1
  fi

  local nlm_version
  nlm_version="$(nlm --version 2>/dev/null | sed -n '1p')"
  log "nlm disponível: $(command -v nlm) (${nlm_version:-versão não detectada})"
  log "notebooklm-mcp disponível: $(command -v notebooklm-mcp)"

  if nlm login --check >/dev/null 2>&1; then
    log "NotebookLM: autenticação funcional"
  else
    mkdir -p "$HERMES_HOME/reminders"
    printf '%s\n' \
      '# Pending NotebookLM login' \
      '' \
      'As ferramentas estão instaladas, mas o gate de autenticação não passou.' \
      'Execute: nlm login && nlm login --check' \
      > "$HERMES_HOME/reminders/notebooklm-login.md"
    warn "NotebookLM: autenticação não comprovada; lembrete criado"
  fi

  if hermes mcp list 2>/dev/null | grep -q "notebooklm"; then
    log "MCP server 'notebooklm' já configurado"
  else
    printf 'y\n' | hermes mcp add notebooklm --command notebooklm-mcp >/dev/null
    log "MCP server 'notebooklm' registrado"
  fi

  hermes mcp test notebooklm >/dev/null
  log "MCP server 'notebooklm' conectado e com ferramentas descobertas"
}

configure_notebooklm_integration