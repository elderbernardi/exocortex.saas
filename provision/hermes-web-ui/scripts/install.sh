#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"

require_cmd docker
require_cmd curl
require_cmd python3
load_env
ensure_env_file
load_env
validate_security_envelope
ensure_dirs

info "Subindo Hermes Web UI opinado do Exocórtex"
bash "$SCRIPT_DIR/bootstrap-admin.sh"
bash "$SCRIPT_DIR/bootstrap-profiles.sh"
compose up -d --build
wait_for_health 90

bash "$SCRIPT_DIR/bootstrap-exocortex.sh"
bash "$SCRIPT_DIR/smoke.sh"

echo ""
log "Provisionamento concluído"
info "UI:                http://127.0.0.1:${EXOCORTEX_UI_PORT}"
info "Usuário admin:     ${EXOCORTEX_ADMIN_USERNAME:-admin}"
info "Segredos em:       $ENV_FILE"
info "Hermes runtime:    ${EXOCORTEX_HERMES_HOME}"
info "Exocortex home:    ${EXOCORTEX_HOME}"
info "Web UI state:      ${EXOCORTEX_WEB_UI_HOME}"
