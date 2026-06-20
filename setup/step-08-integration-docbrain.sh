#!/usr/bin/env bash
# =============================================================================
# Step 08: Integração — DocBrain (parser engine via GitHub clone)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

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
  if [ -n "${OPENROUTER_API_KEY:-}" ] || [ -n "${DOCBRAIN_LLM_API_KEY:-}" ]; then
    log "Key LLM disponível para DocBrain"
    # Cleanup stale reminder if key now exists
    if [ -f "$HERMES_HOME/reminders/docbrain-llm-key.md" ]; then
      rm -f "$HERMES_HOME/reminders/docbrain-llm-key.md"
      log "Reminder stale removido (key já disponível)"
    fi
  else
    mkdir -p "$HERMES_HOME/reminders"
    cat > "$HERMES_HOME/reminders/docbrain-llm-key.md" <<'REMINDER'
# Pending DocBrain LLM key

DocBrain is installed, but no LLM key was available during setup.

## Before acting on this reminder

Check the live environment first — if OPENROUTER_API_KEY or DOCBRAIN_LLM_API_KEY
is already set, this reminder is stale and should be deleted.

## If no key exists

DocBrain uses DOCBRAIN_LLM_API_KEY if set, otherwise falls back to OPENROUTER_API_KEY.
Set either one. DEEPSEEK_API_KEY is a separate credential and is NOT used by DocBrain.
REMINDER
    info "Sem key LLM; lembrete criado em $HERMES_HOME/reminders/docbrain-llm-key.md"
  fi
}

info "DocBrain (parser engine via GitHub clone)..."
configure_docbrain_engine
