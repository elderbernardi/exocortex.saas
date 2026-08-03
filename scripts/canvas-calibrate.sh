#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Canvas Calibration Script (F5 Slice A)
# =============================================================================
# Wrapper that delegates execution to scripts/canvas-calibrate.py.
#
# Usage:
#   bash scripts/canvas-calibrate.sh               # keyless eval (non-mutating)
#   bash scripts/canvas-calibrate.sh --refresh     # recompile SOUL then eval
#   # --live is Task 6 (not implemented yet)
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

# --- Executa o runner em Python ---
exec python3 "$REPO_ROOT/scripts/canvas_calibrate.py" "$@"
