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

# Warn if no model is configured — smoke tests will be skipped
if [ -z "${EXOCORTEX_HARNESS_MODEL:-${EXOCORTEX_DEFAULT_MODEL:-}}" ]; then
  echo -e "  \033[1;33m⚠ Nenhum modelo configurado (EXOCORTEX_DEFAULT_MODEL).\033[0m"
  echo -e "  \033[1;33m  Smoke tests serão pulados — só validação determinística vai rodar.\033[0m"
  echo -e "  \033[1;33m  Para validação completa: configure o papel 'default' (bash setup.sh) ou export EXOCORTEX_HARNESS_MODEL.\033[0m"
  echo ""
fi

exec bash "$SCRIPT_DIR/run-provisioning-tests.sh" \
  --skip-api \
  "$@"
