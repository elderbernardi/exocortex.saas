#!/usr/bin/env bash
# Exocórtex.IA — bootstrap v2 sobre Hermes Agent existente

set -euo pipefail

REPO_URL="${EXOCORTEX_REPO_URL:-https://github.com/elderbernardi/exocortex.saas.git}"
VERSION="${VERSION:-main}"
INSTALLER_DIR="${EXOCORTEX_INSTALLER_DIR:-$HOME/.exocortex-installer}"
SETUP_ARGS=()

print_help() {
  cat <<'EOF'
Uso: bash install.sh [opções]

Pré-condição: Hermes Agent já instalado e configurado.

Opções:
  --profile core|full          core = harness; full = integrações + serviços self-hosted
  --yes, -y                    aplica sem confirmação
  --plan                       mostra plano e preflight, sem alterar o runtime
  --verify-only                verifica uma instalação existente
  --step-by-step               confirma cada estágio
  --skip-acceptance            pula os 3 cenários vivos do contrato cognitivo
  --allow-degraded-services    permite full sem todos os serviços saudáveis
  --model ID                   modelo opcional só para a aceitação; default = Hermes atual
  -h, --help                   mostra esta ajuda

O instalador não instala Hermes, não instala pacotes do sistema e não roda o
catálogo completo de dogfood. Após obter o checkout, o manifesto de capacidades
detecta o SO e apresenta correções nativas. Relatórios ficam em
$HERMES_HOME/exocortex-install/runs/<timestamp>/.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) print_help; exit 0 ;;
    --profile)
      option="$1"
      shift
      [ $# -gt 0 ] || { echo "$option requer valor" >&2; exit 2; }
      [ "$1" = "core" ] || [ "$1" = "full" ] || { echo "--profile aceita core ou full" >&2; exit 2; }
      SETUP_ARGS+=("$option" "$1")
      ;;
    --model)
      option="$1"
      shift
      [ $# -gt 0 ] || { echo "$option requer valor" >&2; exit 2; }
      SETUP_ARGS+=("$option" "$1")
      ;;
    --allow-degraded-services)
      SETUP_ARGS+=("$1")
      ;;
    --yes|-y|--plan|--verify-only|--step-by-step|--skip-acceptance)
      SETUP_ARGS+=("$1")
      ;;
    --calibrate)
      # Compatibilidade: a aceitação contratual mínima já é o default.
      ;;
    *) echo "Flag não suportada: $1" >&2; exit 2 ;;
  esac
  shift
done

for command in hermes python3 git rsync; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "✗ Pré-requisito ausente: $command" >&2
    if [ "$command" = "hermes" ]; then
      echo "  Instale e configure Hermes antes do Exocórtex:" >&2
      echo "  https://hermes-agent.nousresearch.com/docs/" >&2
    fi
    exit 2
  }
done

hermes config check >/dev/null || {
  echo "✗ Hermes existe, mas 'hermes config check' falhou." >&2
  exit 2
}

echo "Exocórtex installer v2"
echo "  Hermes:  $(hermes --version 2>/dev/null | sed -n '1p')"
echo "  Fonte:   $REPO_URL @ $VERSION"
echo "  Runtime: ${HERMES_HOME:-$HOME/.hermes}"

parent_dir="$(dirname "$INSTALLER_DIR")"
mkdir -p "$parent_dir"
staging="$(mktemp -d "${INSTALLER_DIR}.staging.XXXXXX")"
if ! git clone --quiet --depth 1 --branch "$VERSION" "$REPO_URL" "$staging/repo"; then
  echo "✗ Não foi possível obter $REPO_URL @ $VERSION" >&2
  echo "  Staging preservado para diagnóstico: $staging" >&2
  exit 3
fi

if [ -e "$INSTALLER_DIR" ]; then
  backup="${INSTALLER_DIR}.previous.$(date +%Y%m%d_%H%M%S)"
  mv "$INSTALLER_DIR" "$backup"
  echo "  Instalador anterior: $backup"
fi
mv "$staging/repo" "$INSTALLER_DIR"
rmdir "$staging"

exec bash "$INSTALLER_DIR/setup.sh" "${SETUP_ARGS[@]}"