#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Candidate-Release Setup Script (Camada 1 + 2)
# =============================================================================
# Provisiona infraestrutura (Camada 1) e identidade (Camada 2) do Exocórtex
# sobre Hermes Agent, seguindo ADR-010 (layered deployment).
#
# Uso:
#   HERMES_HOME=/path/to/hermes EXOCORTEX_HOME=~/exocortex bash setup.sh
#   HERMES_HOME=/path/to/hermes EXOCORTEX_HOME=~/exocortex bash setup.sh --imbroke
#   HERMES_HOME=/path/to/hermes EXOCORTEX_HOME=~/exocortex bash setup.sh --calibrate
#
# Flags:
#   --imbroke   Ativa explicitamente o modo de contingência OpenRouter free
#   --calibrate Executa o alinhamento de calibração cognitivo interativo do Hermes pós-instalação
#
# Requer:
#   - HERMES_HOME definido (runtime do Hermes)
#   - EXOCORTEX_HOME definido (workspace cognitivo, default: ~/exocortex)
#
# Ref: docs/ADR/ADR-010-layered-deployment.md
#      micro/hermes-setup/decisions/hermes-runtime-cwd-exocortex-home.md
# =============================================================================

SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Passa SCRIPT_DIR para common.sh saber onde está a raiz do projeto
export _EXOCORTEX_SCRIPT_DIR="$SETUP_DIR"

source "$SETUP_DIR/setup/common.sh" "$@"

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Exocórtex.IA — Candidate-Release Setup     ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

info "HERMES_HOME:    $HERMES_HOME"
info "EXOCORTEX_HOME: $EXOCORTEX_HOME"
info "ACERVO:         $ACERVO"
info "ARTIFACTS:      $SCRIPT_DIR"

# =============================================================================
# Steps modulares — cada arquivo é independente e pode ser executado standalone
# =============================================================================

source "$SETUP_DIR/setup/step-01-hindsight.sh"
source "$SETUP_DIR/setup/step-02-create-structure.sh"
source "$SETUP_DIR/setup/step-03-install-skills.sh"
source "$SETUP_DIR/setup/step-04-install-acervo.sh"
source "$SETUP_DIR/setup/step-05-install-profiles.sh"
source "$SETUP_DIR/setup/step-06-hardening.sh"
source "$SETUP_DIR/setup/step-07-install-identity.sh"
source "$SETUP_DIR/setup/step-08-integration-docbrain.sh"
source "$SETUP_DIR/setup/step-09-integration-notebooklm.sh"
source "$SETUP_DIR/setup/step-10-integration-browser.sh"
source "$SETUP_DIR/setup/step-11-integration-context7.sh"
source "$SETUP_DIR/setup/step-12-verify-keys.sh"
source "$SETUP_DIR/setup/step-13-final-verification.sh"
source "$SETUP_DIR/setup/step-14-post-provisioning.sh"
source "$SETUP_DIR/setup/step-15-calibration.sh"
