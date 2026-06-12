#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
load_env

backup_dir="${1:-$PROVISION_DIR/backups}"
stamp="$(date +%Y%m%d-%H%M%S)"
out="$backup_dir/exocortex-hermes-ui-$stamp.tgz"
mkdir -p "$backup_dir"

tar -czf "$out" \
  -C "$(dirname "$EXOCORTEX_HERMES_HOME")" "$(basename "$EXOCORTEX_HERMES_HOME")" \
  -C "$(dirname "$EXOCORTEX_HOME")" "$(basename "$EXOCORTEX_HOME")" \
  -C "$(dirname "$EXOCORTEX_WEB_UI_HOME")" "$(basename "$EXOCORTEX_WEB_UI_HOME")"

log "Backup gerado em $out"
