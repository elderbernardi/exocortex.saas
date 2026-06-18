#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Setup: Common Library
# =============================================================================
# Variáveis de ambiente, cores e funções utilitárias compartilhadas por todos
# os step scripts. Pode ser carregado de duas formas:
#
#   1. Via orquestrador:  source setup/common.sh "$@"
#   2. Via standalone:    source "$(dirname "$0")/common.sh"
#
# =============================================================================

# Guard: evita re-source
if [ "${_EXOCORTEX_COMMON_LOADED:-}" = "1" ]; then
  return 0 2>/dev/null || true
fi
_EXOCORTEX_COMMON_LOADED=1

set -euo pipefail

# ─── SCRIPT_DIR (resolved first, needed for .env.local path) ────────────────

if [ -n "${_EXOCORTEX_SCRIPT_DIR:-}" ]; then
  SCRIPT_DIR="$_EXOCORTEX_SCRIPT_DIR"
else
  # Quando sourced diretamente, assume que common.sh está em setup/ e o pai é a raiz
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

# ─── .env.local auto-load ──────────────────────────────────────────────────
# Carrega valores de .env.local ANTES dos defaults, para que o arquivo
# possa definir HERMES_HOME, EXOCORTEX_HOME, etc.
# Variáveis já definidas no shell NÃO são sobrescritas.

_load_env_local_early() {
  local env_file="$SCRIPT_DIR/.env.local"
  if [ -f "$env_file" ]; then
    while IFS='=' read -r key value; do
      [[ "$key" =~ ^[[:space:]]*# ]] && continue
      [[ -z "$key" ]] && continue
      key=$(echo "$key" | xargs)
      value=$(echo "$value" | xargs)
      value="${value#\"}"; value="${value%\"}"
      value="${value#\'}"; value="${value%\'}"
      if [ -z "${!key:-}" ]; then
        export "$key=$value"
      fi
    done < "$env_file"
  fi
}

_load_env_local_early

# ─── Environment ─────────────────────────────────────────────────────────────

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"
ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"

IMBROKE_MODE="${IMBROKE_MODE:-0}"
CALIBRATE_MODE="${CALIBRATE_MODE:-0}"
INTERACTIVE_MODE="${INTERACTIVE_MODE:-1}"
INIT_ONLY="${INIT_ONLY:-0}"
SKIP_ENV_CHECK="${SKIP_ENV_CHECK:-0}"
STEP_BY_STEP_MODE="${STEP_BY_STEP_MODE:-0}"

# ─── Parse Flags (quando chamado com "$@") ────────────────────────────────────

_parse_setup_flags() {
  for arg in "$@"; do
    case "$arg" in
      --imbroke)
        IMBROKE_MODE=1
        ;;
      --calibrate)
        CALIBRATE_MODE=1
        ;;
      --yes|-y)
        INTERACTIVE_MODE=0
        ;;
      --init-only)
        INIT_ONLY=1
        ;;
      --skip-env-check)
        SKIP_ENV_CHECK=1
        ;;
      --step-by-step|--guided)
        STEP_BY_STEP_MODE=1
        ;;
      -h|--help)
        echo "Uso: bash setup.sh [--yes] [--init-only] [--skip-env-check] [--step-by-step] [--imbroke] [--calibrate]"
        echo ""
        echo "  --yes            Aceita todos os defaults sem prompts (CI/CD)"
        echo "  --init-only      Apenas configuração, sem executar steps"
        echo "  --skip-env-check Pula validação de pré-requisitos"
        echo "  --step-by-step   Força revisão guiada de paths, env vars e API keys"
        echo "  --imbroke        Ativa modo de contingência OpenRouter free"
        echo "  --calibrate      Executa calibração cognitiva interativa pós-instalação"
        exit 0
        ;;
      *)
        fail "Flag não suportada: $arg"
        ;;
    esac
  done
}

# Parse flags se argumentos foram passados
if [ $# -gt 0 ]; then
  _parse_setup_flags "$@"
fi

# ─── Colors ──────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ─── Logging ─────────────────────────────────────────────────────────────────

log() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

# ─── Derived Paths ───────────────────────────────────────────────────────────

SKILLS_SRC="$SCRIPT_DIR/skills"
SKILLS_DST="$HERMES_HOME/skills/excrtx"

PROFILES_SRC="$SCRIPT_DIR/profiles"
PROFILES_DST="$HERMES_HOME/profiles"

BUNDLES_SRC="$SCRIPT_DIR/skill-bundles"
BUNDLES_DST="$HERMES_HOME/skill-bundles"

ACERVO_SRC="$SCRIPT_DIR/acervo"

# ─── Export ──────────────────────────────────────────────────────────────────

export HERMES_HOME EXOCORTEX_HOME ACERVO SCRIPT_DIR
export IMBROKE_MODE CALIBRATE_MODE INTERACTIVE_MODE INIT_ONLY SKIP_ENV_CHECK STEP_BY_STEP_MODE
export SKILLS_SRC SKILLS_DST PROFILES_SRC PROFILES_DST BUNDLES_SRC BUNDLES_DST ACERVO_SRC
