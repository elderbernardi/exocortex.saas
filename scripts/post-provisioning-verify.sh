#!/usr/bin/env bash
# =============================================================================
# Exocórtex — Wrapper pós-provisionamento
# =============================================================================
# Chamado pelo setup.sh ao final da instalação.
# Delega para run-provisioning-tests.sh com defaults de pós-setup.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Verificação Pós-Provisionamento             ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

exec bash "$SCRIPT_DIR/run-provisioning-tests.sh" \
  --skip-api \
  "$@"
