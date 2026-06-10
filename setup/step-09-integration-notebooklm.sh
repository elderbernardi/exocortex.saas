#!/usr/bin/env bash
# =============================================================================
# Step 09: Integração — NotebookLM (CLI + MCP)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

# ─── Helpers ─────────────────────────────────────────────────────────────────

# Ensure uv is available. Tries: existing PATH → pip install → curl installer.
_ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    log "uv disponível: $(command -v uv)"
    return 0
  fi

  # Try pip install first (lightweight, same Python env)
  if python3 -m pip install --quiet uv 2>/dev/null; then
    if command -v uv >/dev/null 2>&1; then
      log "uv instalado via pip: $(command -v uv)"
      return 0
    fi
  fi

  # Fallback: curl installer (canonical, but requires network + shell)
  if command -v curl >/dev/null 2>&1; then
    info "Instalando uv via curl installer..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; then
      # Ensure ~/.local/bin is in PATH for this session
      export PATH="$HOME/.local/bin:$PATH"
      if command -v uv >/dev/null 2>&1; then
        log "uv instalado via curl: $(command -v uv)"
        return 0
      fi
    fi
  fi

  warn "Não foi possível instalar uv. nlm será instalado via pip se necessário."
  return 1
}

# Install or upgrade nlm CLI. Prefers uv tool install; falls back to pip.
_install_nlm() {
  if command -v uv >/dev/null 2>&1; then
    info "Instalando/atualizando nlm via uv tool install notebooklm-mcp-cli"
    if uv tool install notebooklm-mcp-cli --force 2>/dev/null; then
      log "nlm instalado/atualizado via uv"
      return 0
    fi
    warn "uv tool install falhou, tentando pip..."
  fi

  if python3 -m pip install --upgrade --quiet notebooklm-mcp-cli 2>/dev/null; then
    log "nlm instalado/atualizado via pip"
    return 0
  fi

  warn "Falha ao instalar notebooklm-mcp-cli"
  return 1
}

# Check nlm version meets minimum. Returns 0 if OK, 1 if outdated/missing.
_check_nlm_version() {
  local min_version="0.7.0"
  local current

  if ! command -v nlm >/dev/null 2>&1; then
    return 1
  fi

  current=$(nlm --version 2>/dev/null | grep -oP '[\d]+\.[\d]+\.[\d]+' | head -1)
  if [ -z "$current" ]; then
    warn "Não foi possível detectar versão do nlm"
    return 1
  fi

  # Simple semver comparison: compare major.minor.patch numerically
  local IFS=.
  local cur_parts=($current) min_parts=($min_version)
  for i in 0 1 2; do
    if [ "${cur_parts[$i]:-0}" -gt "${min_parts[$i]:-0}" ]; then
      log "nlm $current >= $min_version ✓"
      return 0
    elif [ "${cur_parts[$i]:-0}" -lt "${min_parts[$i]:-0}" ]; then
      warn "nlm $current está desatualizado (mínimo recomendado: $min_version)"
      return 1
    fi
  done
  log "nlm $current >= $min_version ✓"
  return 0
}

# ─── Main ─────────────────────────────────────────────────────────────────────

configure_notebooklm_integration() {
  info "NotebookLM (CLI + MCP)..."

  # 1. Ensure uv (preferred) or pip fallback for package management
  _ensure_uv || true

  # 2. Install/upgrade nlm if missing or outdated
  if ! _check_nlm_version; then
    _install_nlm || {
      warn "nlm CLI não pôde ser instalado. NotebookLM indisponível."
      return 0
    }
    # Re-check version after install
    _check_nlm_version || warn "nlm instalado mas versão pode ser insuficiente"
  fi

  log "nlm CLI disponível: $(command -v nlm) ($(nlm --version 2>/dev/null | head -1))"

  # 3. Auth check
  if nlm login --check >/dev/null 2>&1; then
    log "nlm autenticado"
  else
    mkdir -p "$HERMES_HOME/reminders"
    cat > "$HERMES_HOME/reminders/notebooklm-login.md" <<'EOF'
# Pending NotebookLM login
nlm CLI instalado mas autenticação não está ativa.
No terminal: nlm login && nlm login --check
EOF
    warn "nlm sem auth ativa; lembrete criado em $HERMES_HOME/reminders/notebooklm-login.md"
  fi

  # 4. MCP server registration
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

configure_notebooklm_integration
