#!/usr/bin/env bash
# Exocórtex.IA — wrapper do instalador v2

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMAND="apply"
PROFILE="${EXOCORTEX_INSTALL_PROFILE:-full}"
COMMON_ARGS=()
APPLY_ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --yes|-y) APPLY_ARGS+=("--yes") ;;
    --step-by-step|--guided) APPLY_ARGS+=("--review-each") ;;
    --init-only|--plan) COMMAND="plan" ;;
    --verify-only|--verify) COMMAND="verify" ;;
    --skip-acceptance) APPLY_ARGS+=("--acceptance" "skip") ;;
    --allow-degraded-services) COMMON_ARGS+=("--allow-degraded-services") ;;
    --profile)
      shift
      [ $# -gt 0 ] || { echo "--profile requer core ou full" >&2; exit 2; }
      PROFILE="$1"
      ;;
    --model)
      shift
      [ $# -gt 0 ] || { echo "--model requer um identificador" >&2; exit 2; }
      APPLY_ARGS+=("--model" "$1")
      ;;
    --calibrate)
      # Compatibilidade: aceitação contratual já roda por default.
      ;;
    -h|--help)
      python3 "$ROOT/scripts/exocortex_install.py" apply --help
      exit 0
      ;;
    *) echo "Flag não suportada: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ "$COMMAND" = "apply" ]; then
  exec python3 "$ROOT/scripts/exocortex_install.py" apply \
    --profile "$PROFILE" "${COMMON_ARGS[@]}" "${APPLY_ARGS[@]}"
fi

exec python3 "$ROOT/scripts/exocortex_install.py" "$COMMAND" \
  --profile "$PROFILE" "${COMMON_ARGS[@]}"