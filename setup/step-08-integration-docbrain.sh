#!/usr/bin/env bash
# =============================================================================
# Step 08: Integração — DocBrain (parser engine via GitHub clone)
# =============================================================================
# Clona/atualiza o DocBrain em $EXOCORTEX_HOME/tools/docbrain e constrói
# o projeto. DocBrain rastreia o branch main de
# https://github.com/elderbernardi/docbrain — veja provision/sources/sources.lock.yaml
# (entrada 'docbrain', allow_upstream_main: true) para o registro informativo.
#
# Decisão de produto: reproducibilidade foi trocada por continuidade de entrega
# — o branch main é sempre o mais recente. Registrado no contrato exocortex→docbrain.
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

# Resolvedor de papéis LLM (DocBrain usa o papel 'auxiliar').
source "$(dirname "${BASH_SOURCE[0]}")/lib/llm-roles.sh"

configure_docbrain_engine() {
  local docbrain_dir="${EXOCORTEX_DOCBRAIN_DIR:-$EXOCORTEX_HOME/tools/docbrain}"
  local repo="https://github.com/elderbernardi/docbrain"
  local branch="main"

  if ! command -v git >/dev/null 2>&1; then
    warn "git não encontrado; pulando clone do DocBrain"
    return 0
  fi

  mkdir -p "$(dirname "$docbrain_dir")"

  if [ ! -d "$docbrain_dir/.git" ]; then
    info "Clonando DocBrain (branch $branch) em $docbrain_dir"
    if ! git clone --branch "$branch" "$repo" "$docbrain_dir" >/dev/null 2>&1; then
      warn "Falha ao clonar DocBrain"
      return 0
    fi
  else
    log "Repositório DocBrain encontrado: $docbrain_dir — atualizando para origin/$branch"
    # Fetch latest from origin/main; offline failure is non-fatal.
    if git -C "$docbrain_dir" fetch --quiet origin "$branch" 2>/dev/null; then
      # Fast-forward to origin/main — hard reset so even a dirty tree becomes clean.
      git -C "$docbrain_dir" checkout --quiet "$branch" 2>/dev/null || true
      git -C "$docbrain_dir" reset --hard "origin/$branch" --quiet 2>/dev/null || \
        warn "Não foi possível avançar para origin/$branch (offline?); usando o checkout existente"
    else
      warn "Fetch do DocBrain falhou (offline?); usando checkout existente"
    fi
  fi
  log "DocBrain em $(git -C "$docbrain_dir" rev-parse --short HEAD 2>/dev/null || echo 'desconhecido') (origin/$branch)"

  # ── npm install + build ──────────────────────────────────────────────────
  # npm absent: degrade gracefully (write reminder, warn, continue).
  # npm present but install/build fails: FAIL loudly — a broken build would
  # silently deploy unusable tooling, which is worse than failing early.

  if ! command -v npm >/dev/null 2>&1; then
    warn "npm não encontrado; pulando npm install/build do DocBrain"
    mkdir -p "$HERMES_HOME/reminders"
    cat > "$HERMES_HOME/reminders/docbrain-npm-missing.md" <<'REMINDER'
# DocBrain sem build (npm ausente)

O DocBrain foi clonado (branch main), mas o `npm` não estava disponível
no momento do setup, então `npm install` e `npm run build` foram pulados.

Para completar a instalação:
  1. Instale o Node.js/npm (node 18+ recomendado)
  2. Execute: bash setup.sh  (o step-08 tentará novamente)
REMINDER
    return 0
  fi

  info "Executando npm install em $docbrain_dir"
  if ! (cd "$docbrain_dir" && npm install 2>&1); then
    fail "npm install falhou para o DocBrain em $docbrain_dir — verifique os erros acima e corrija antes de continuar"
  fi

  info "Executando npm run build em $docbrain_dir"
  if ! (cd "$docbrain_dir" && npm run build 2>&1); then
    fail "npm run build falhou para o DocBrain em $docbrain_dir — verifique os erros acima e corrija antes de continuar"
  fi

  log "DocBrain dependências/build verificados"

  # Ponte: papel 'auxiliar' → contrato do DocBrain (DOCBRAIN_LLM_*). O papel aux
  # herda 'default' quando não configurado separadamente (resolvedor central).
  exocortex_resolve_role aux
  if [ "$ROLE_USABLE" = "1" ]; then
    cat > "$docbrain_dir/.env" <<ENVFILE
# Gerado pelo Exocórtex (step-08) a partir do papel LLM 'auxiliar'.
# Fonte de verdade: EXOCORTEX_AUX_* (ou EXOCORTEX_DEFAULT_* herdado) no .env.local.
DOCBRAIN_LLM_API_KEY="$ROLE_API_KEY"
DOCBRAIN_LLM_MODEL="$ROLE_MODEL"
DOCBRAIN_LLM_BASE_URL="$ROLE_CHAT_URL"
ENVFILE
    # chmod failure is non-fatal: .env file may be on a filesystem that does not
    # support POSIX permissions (e.g. FAT, certain network mounts).
    chmod 600 "$docbrain_dir/.env" 2>/dev/null || true
    log "DocBrain LLM configurado via papel 'auxiliar' (provider=$ROLE_PROVIDER model=$ROLE_MODEL)"
    if [ -f "$HERMES_HOME/reminders/docbrain-llm-key.md" ]; then
      rm -f "$HERMES_HOME/reminders/docbrain-llm-key.md"
      log "Reminder stale removido (papel auxiliar já configurado)"
    fi
  else
    mkdir -p "$HERMES_HOME/reminders"
    cat > "$HERMES_HOME/reminders/docbrain-llm-key.md" <<'REMINDER'
# DocBrain sem LLM (papel 'auxiliar' não configurado)

DocBrain foi instalado, mas o papel LLM 'auxiliar' não estava utilizável no setup.

## Antes de agir neste lembrete

Confira o ambiente — se EXOCORTEX_AUX_* (ou o EXOCORTEX_DEFAULT_* herdado) já
estiver configurado, este lembrete é obsoleto e pode ser apagado.

## Como configurar

O DocBrain usa o papel 'auxiliar' do Exocórtex. Configure EXOCORTEX_AUX_API_KEY
(+ PROVIDER/MODEL) no .env.local — ou deixe vazio para herdar o papel 'default'.
Rode: bash setup.sh   (o step-08 regenera $docbrain_dir/.env automaticamente).
REMINDER
    info "Papel 'auxiliar' indisponível; lembrete criado em $HERMES_HOME/reminders/docbrain-llm-key.md"
  fi
}

info "DocBrain (parser engine via GitHub clone)..."
configure_docbrain_engine
