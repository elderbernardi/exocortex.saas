#!/usr/bin/env bash
# =============================================================================
# Step 08: Integração — DocBrain (parser engine via GitHub clone)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

# Resolvedor de papéis LLM (DocBrain usa o papel 'auxiliar').
source "$(dirname "${BASH_SOURCE[0]}")/lib/llm-roles.sh"

configure_docbrain_engine() {
  local docbrain_dir="${EXOCORTEX_DOCBRAIN_DIR:-$EXOCORTEX_HOME/tools/docbrain}"
  local repo="https://github.com/ProjetoBB/docBrainBB.git"
  if ! command -v git >/dev/null 2>&1; then
    warn "git não encontrado; pulando clone do DocBrain"
    return 0
  fi
  if ! command -v npm >/dev/null 2>&1; then
    warn "npm não encontrado; pulando setup do DocBrain"
    return 0
  fi
  mkdir -p "$(dirname "$docbrain_dir")"
  if [ ! -d "$docbrain_dir/.git" ]; then
    info "Clonando DocBrain em $docbrain_dir"
    git clone "$repo" "$docbrain_dir" >/dev/null 2>&1 || {
      warn "Falha ao clonar DocBrain"
      return 0
    }
  else
    log "Repositório DocBrain encontrado: $docbrain_dir"
  fi
  (cd "$docbrain_dir" && git pull --ff-only origin main >/dev/null 2>&1 || true && npm install >/dev/null 2>&1 || true && npm run build >/dev/null 2>&1 || true)
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
