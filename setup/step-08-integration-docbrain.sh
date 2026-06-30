#!/usr/bin/env bash
# =============================================================================
# Step 08: Integração — DocBrain (parser engine via GitHub clone)
# =============================================================================
# Clona/atualiza o DocBrain em $EXOCORTEX_HOME/tools/docbrain e constrói
# o projeto. A ref usada é pinada em provision/sources/sources.lock.yaml
# (entrada 'docbrain') para garantir installs reprodutíveis.
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

# Resolvedor de papéis LLM (DocBrain usa o papel 'auxiliar').
source "$(dirname "${BASH_SOURCE[0]}")/lib/llm-roles.sh"

# ─── Read pinned ref from sources.lock.yaml ───────────────────────────────────

_resolve_docbrain_pin() {
  local lock_file="$SCRIPT_DIR/provision/sources/sources.lock.yaml"
  if [ ! -f "$lock_file" ]; then
    fail "sources.lock.yaml não encontrado em $lock_file — não é possível resolver ref pinada do DocBrain"
  fi

  local controlled_ref
  controlled_ref=$(python3 - "$lock_file" <<'PY'
import sys
from pathlib import Path

lock_path = Path(sys.argv[1])
text = lock_path.read_text(encoding='utf-8').splitlines()

in_docbrain = False
in_controlled = False

for line in text:
    stripped = line.strip()
    if stripped == 'docbrain:':
        in_docbrain = True
        in_controlled = False
        continue
    if in_docbrain:
        # Another top-level source key ends the docbrain block
        indent = len(line) - len(line.lstrip(' '))
        if indent == 2 and stripped.endswith(':') and stripped != 'docbrain:':
            in_docbrain = False
            continue
        if stripped == 'controlled:':
            in_controlled = True
            continue
        if in_controlled and stripped.startswith('ref:') and 'audited_from' not in stripped:
            ref = stripped.split('ref:', 1)[1].strip().strip('"').strip("'")
            print(ref)
            sys.exit(0)
PY
  )

  if [ -z "$controlled_ref" ]; then
    fail "Ref pinada do DocBrain não encontrada em $lock_file (entrada 'docbrain.controlled.ref')"
  fi

  # Enforce that the ref is a full 40-char commit SHA — never a floating branch
  if ! echo "$controlled_ref" | grep -qE '^[0-9a-f]{40}$'; then
    fail "Ref pinada do DocBrain não é um SHA-1 completo de 40 caracteres: '$controlled_ref'. Atualize sources.lock.yaml."
  fi

  echo "$controlled_ref"
}

configure_docbrain_engine() {
  local docbrain_dir="${EXOCORTEX_DOCBRAIN_DIR:-$EXOCORTEX_HOME/tools/docbrain}"
  local repo="https://github.com/ProjetoBB/docBrainBB.git"

  if ! command -v git >/dev/null 2>&1; then
    warn "git não encontrado; pulando clone do DocBrain"
    return 0
  fi

  # Resolve the pinned ref before doing anything with the repo
  local pinned_ref
  pinned_ref=$(_resolve_docbrain_pin)
  info "DocBrain ref pinada: $pinned_ref"

  mkdir -p "$(dirname "$docbrain_dir")"

  if [ ! -d "$docbrain_dir/.git" ]; then
    info "Clonando DocBrain em $docbrain_dir"
    # Clone without checking out (we will checkout the pinned ref explicitly)
    if ! git clone --no-checkout "$repo" "$docbrain_dir" >/dev/null 2>&1; then
      warn "Falha ao clonar DocBrain"
      return 0
    fi
  else
    log "Repositório DocBrain encontrado: $docbrain_dir"
    # Fetch to make the pinned ref available locally; network may be unavailable
    # in offline/airgap environments — failure is non-fatal (pinned ref may
    # already be present from a prior fetch).
    git -C "$docbrain_dir" fetch --quiet origin 2>/dev/null || \
      warn "Fetch do DocBrain falhou (offline?); usando ref já presente no clone"
  fi

  # Checkout the pinned ref — this is the reproducibility guarantee
  if ! git -C "$docbrain_dir" checkout --quiet "$pinned_ref" 2>/dev/null; then
    warn "git checkout da ref pinada falhou ($pinned_ref). Execute um fetch manual para obtê-la."
    return 0
  fi
  log "DocBrain em ref pinada: $pinned_ref"

  # ── npm install + build ──────────────────────────────────────────────────
  # npm absent: degrade gracefully (write reminder, warn, continue).
  # npm present but install/build fails: FAIL loudly — a broken build would
  # silently deploy unusable tooling, which is worse than failing early.

  if ! command -v npm >/dev/null 2>&1; then
    warn "npm não encontrado; pulando npm install/build do DocBrain"
    mkdir -p "$HERMES_HOME/reminders"
    cat > "$HERMES_HOME/reminders/docbrain-npm-missing.md" <<'REMINDER'
# DocBrain sem build (npm ausente)

O DocBrain foi clonado em ref pinada, mas o `npm` não estava disponível
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
