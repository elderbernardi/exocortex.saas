#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA Provisioner — Common Utilities
# =============================================================================
# Source this file from other provisioner scripts:
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "$SCRIPT_DIR/common.sh"
# =============================================================================

set -euo pipefail

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly DIM='\033[2m'
readonly NC='\033[0m'

# Paths (resolved relative to provisioner root)
PROVISIONER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -d "$PROVISIONER_DIR/artifacts" ]; then
  ARTIFACTS_DIR="$(cd "$PROVISIONER_DIR/artifacts" && pwd)"
elif [ -d "$PROVISIONER_DIR/../artifacts" ]; then
  ARTIFACTS_DIR="$(cd "$PROVISIONER_DIR/../artifacts" && pwd)"
else
  ARTIFACTS_DIR="$PROVISIONER_DIR/artifacts"
fi
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
EXOCORTEX_SKILLS="$HERMES_HOME/skills/exocortex"

# Expected counts
readonly EXPECTED_SKILLS=15
readonly EXPECTED_ACERVO_LAYERS=4

# Logging
log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; }
step() { echo -e "\n${BOLD}▸ $1${NC}"; }

# JSON output helper (for agent consumption)
json_kv() {
  local key="$1" value="$2"
  printf '"%s": "%s"' "$key" "$value"
}

# Check if a command exists
has_command() {
  command -v "$1" &>/dev/null
}
