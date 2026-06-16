#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Candidate-Release Setup Script (Camada 1 + 2)
# =============================================================================
# Provisiona infraestrutura (Camada 1) e identidade (Camada 2) do Exocórtex
# sobre Hermes Agent, seguindo ADR-010 (layered deployment).
#
# Uso:
#   bash setup.sh                  # modo interativo (npm-init style)
#   bash setup.sh --yes            # aceita todos defaults (CI/CD)
#   bash setup.sh --init-only      # apenas configuração, sem executar steps
#   bash setup.sh --skip-env-check # pula validação de pré-requisitos
#   bash setup.sh --imbroke        # ativa contingência OpenRouter free
#   bash setup.sh --calibrate      # calibração cognitiva pós-instalação
#
# Flags:
#   --yes            Aceita todos os defaults sem prompts (modo CI/CD)
#   --init-only      Para após confirmação, não executa steps
#   --skip-env-check Pula validação de pré-requisitos do sistema
#   --imbroke        Ativa explicitamente o modo de contingência OpenRouter free
#   --calibrate      Executa calibração cognitiva interativa pós-instalação
#
# Imbroke activation is implemented in setup/step-12-verify-keys.sh via
# configure_openrouter_free_router and guarded by: if [ "$IMBROKE_MODE" = "1" ]
#
# Requer:
#   - HERMES_HOME definido (runtime do Hermes)
#   - EXOCORTEX_HOME definido (workspace cognitivo, default: ~/exocortex)
#
# Ref: docs/ADR/ADR-010-layered-deployment.md
#      docs/ADR/ADR-012-interactive-setup.md
# =============================================================================

SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Passa SCRIPT_DIR para common.sh saber onde está a raiz do projeto
export _EXOCORTEX_SCRIPT_DIR="$SETUP_DIR"

source "$SETUP_DIR/setup/common.sh" "$@"

# Load interactive library
source "$SETUP_DIR/setup/interactive.sh"

# Load .env.local values (if exists, won't override env vars already set)
load_env_local

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Exocórtex.IA — Candidate-Release Setup     ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# =============================================================================
# ESTÁGIO 1 — Validação de Environment (pré-requisitos do sistema)
# =============================================================================

if [ "${SKIP_ENV_CHECK:-0}" != "1" ]; then
  info "═══ Estágio 1/3: Validação de pré-requisitos ═══"
  echo ""

  if bash "$SETUP_DIR/scripts/validate-environment.sh"; then
    log "Todos os pré-requisitos atendidos."
  else
    env_exit=$?
    if [ $env_exit -eq 1 ]; then
      # Obrigatórios faltando
      echo ""
      warn "Existem dependências obrigatórias faltando."
      echo ""

      if [ "$INTERACTIVE_MODE" = "1" ]; then
        echo -en "  ${BOLD}Escolha:${NC} [i]nstalar faltantes | [c]ontinuar mesmo assim | [a]bortar: "
        read -r env_choice
        case "${env_choice,,}" in
          i|instalar|install)
            info "Tentando instalar dependências faltantes..."
            bash "$SETUP_DIR/scripts/validate-environment.sh" --install
            if [ $? -eq 1 ]; then
              fail "Ainda existem dependências obrigatórias faltando após tentativa de instalação."
            fi
            ;;
          c|continuar|continue)
            warn "Continuando sem todas as dependências — algumas features podem falhar."
            ;;
          a|abortar|abort|*)
            fail "Setup abortado pelo usuário. Corrija as dependências e tente novamente."
            ;;
        esac
      else
        fail "Dependências obrigatórias faltando. Execute com --skip-env-check para ignorar."
      fi
    else
      # Apenas recomendados faltando (exit=2)
      warn "Algumas dependências recomendadas estão faltando (features limitadas)."
    fi
  fi
  echo ""
else
  info "Validação de pré-requisitos pulada (--skip-env-check)"
  echo ""
fi

# =============================================================================
# ESTÁGIO 2 — Configuração Interativa (npm-init style)
# =============================================================================

info "═══ Estágio 2/3: Configuração ═══"

# Show current state before interactive prompts
show_config_table

if [ "$INTERACTIVE_MODE" = "1" ]; then
  echo -en "  ${BOLD}Deseja editar as configurações acima?${NC} ${DIM}[s/N]${NC}: "
  read -r edit_choice
  case "${edit_choice,,}" in
    s|y|sim|yes)
      run_interactive_init
      ;;
    *)
      info "Mantendo configurações atuais."
      # Still save current values to .env.local for next run
      save_to_env_local "HERMES_HOME" "$HERMES_HOME"
      save_to_env_local "EXOCORTEX_HOME" "$EXOCORTEX_HOME"
      ;;
  esac
else
  info "Modo não-interativo (--yes): usando valores atuais."
  # Save current values for next run
  save_to_env_local "HERMES_HOME" "$HERMES_HOME"
  save_to_env_local "EXOCORTEX_HOME" "$EXOCORTEX_HOME"
fi

echo ""

# =============================================================================
# ESTÁGIO 3 — Preview Final + Confirmação
# =============================================================================

info "═══ Estágio 3/3: Confirmação ═══"

show_config_table

info "HERMES_HOME:    $HERMES_HOME"
info "EXOCORTEX_HOME: $EXOCORTEX_HOME"
info "ACERVO:         $ACERVO"
info "ARTIFACTS:      $SCRIPT_DIR"

if [ "${INIT_ONLY:-0}" = "1" ]; then
  echo ""
  log "Modo --init-only: configuração salva em .env.local. Setup não executado."
  info "Para executar a instalação: bash setup.sh --yes"
  exit 0
fi

if ! confirm_proceed "Confirma instalação com as configurações acima?"; then
  echo ""
  warn "Setup cancelado pelo usuário."
  info "As configurações foram salvas em .env.local para a próxima execução."
  exit 0
fi

echo ""
info "Iniciando instalação..."
echo ""

# =============================================================================
# ESTÁGIO 4 — Execução dos Steps (inalterado)
# =============================================================================
# Steps modulares — cada arquivo é independente e pode ser executado standalone
# =============================================================================

source "$SETUP_DIR/setup/step-00-hermes-compat.sh"
source "$SETUP_DIR/setup/step-01-hindsight.sh"
source "$SETUP_DIR/setup/step-02-create-structure.sh"
source "$SETUP_DIR/setup/step-03-install-skills.sh"
source "$SETUP_DIR/setup/step-04-install-acervo.sh"
source "$SETUP_DIR/setup/step-05-install-profiles.sh"

# Compile behavioral rules into SOUL_SEED.md
info "Compiling behavioral rules into SOUL..."
python3 "$SETUP_DIR/scripts/compile_soul.py" --skills-dir "$HERMES_HOME/skills/excrtx" --soul "$HERMES_HOME/SOUL.md" 2>&1 || warn "compile_soul.py failed — SOUL.md may be stale"

source "$SETUP_DIR/setup/step-06-hardening.sh"
source "$SETUP_DIR/setup/step-06b-google-auth.sh"
source "$SETUP_DIR/setup/step-07-install-identity.sh"
source "$SETUP_DIR/setup/step-08-integration-docbrain.sh"
source "$SETUP_DIR/setup/step-09-integration-notebooklm.sh"
source "$SETUP_DIR/setup/step-10-integration-browser.sh"
source "$SETUP_DIR/setup/step-10b-hermes-webui.sh"
source "$SETUP_DIR/setup/step-10c-provision-acervo-workspace.sh"
source "$SETUP_DIR/setup/step-11-integration-context7.sh"
source "$SETUP_DIR/setup/step-12-verify-keys.sh"
source "$SETUP_DIR/setup/step-13-final-verification.sh"
source "$SETUP_DIR/setup/step-14-post-provisioning.sh"
source "$SETUP_DIR/setup/step-15-calibration.sh"
source "$SETUP_DIR/setup/step-16-install-excrtx-skin.sh"
source "$SETUP_DIR/setup/step-17-maintenance-crons.sh"
