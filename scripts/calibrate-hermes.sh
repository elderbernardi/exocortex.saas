#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Script de Calibração Cognitiva e Alinhamento PDD
# =============================================================================
# Wrapper que delega a execução para o scripts/calibrate-hermes.py modular.
#
# Uso:
#   bash scripts/calibrate-hermes.sh [--model MODEL_ID] [--all]
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Cores e Estilos
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${CYAN}ℹ${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

# --- Check Python 3 ---
if ! command -v python3 >/dev/null 2>&1; then
  fail "Python 3 não está instalado ou não está no PATH."
fi

# --- Check PyYAML dependency ---
if ! python3 -c "import yaml" >/dev/null 2>&1; then
  warn "PyYAML não está instalado. Tentando instalar via pip..."
  if command -v pip3 >/dev/null 2>&1; then
    pip3 install PyYAML --quiet || pip install PyYAML --quiet || warn "Falha ao instalar PyYAML automaticamente. Por favor, execute: pip install PyYAML"
  elif command -v pip >/dev/null 2>&1; then
    pip install PyYAML --quiet || warn "Falha ao instalar PyYAML automaticamente. Por favor, execute: pip install PyYAML"
  else
    warn "pip não encontrado. Por favor, instale o pacote PyYAML (ex: pip install PyYAML)."
  fi
fi

# --- Executa o runner em Python ---
exec python3 "$REPO_ROOT/scripts/calibrate-hermes.py" "$@"
