#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
load_env

archive="${1:-}"
[ -n "$archive" ] || fail "Uso: bash restore.sh /caminho/backup.tgz"
[ -f "$archive" ] || fail "Arquivo não encontrado: $archive"
require_cmd rsync

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
mkdir -p "$EXOCORTEX_HERMES_HOME" "$EXOCORTEX_HOME" "$EXOCORTEX_WEB_UI_HOME"
tar -xzf "$archive" -C "$tmpdir"
rsync -a "$tmpdir/$(basename "$EXOCORTEX_HERMES_HOME")/" "$EXOCORTEX_HERMES_HOME/"
rsync -a "$tmpdir/$(basename "$EXOCORTEX_HOME")/" "$EXOCORTEX_HOME/"
rsync -a "$tmpdir/$(basename "$EXOCORTEX_WEB_UI_HOME")/" "$EXOCORTEX_WEB_UI_HOME/"

log "Restore concluído a partir de $archive"
