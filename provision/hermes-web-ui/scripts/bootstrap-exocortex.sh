#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
load_env

if [ "$EXOCORTEX_BOOTSTRAP_RUNTIME" != "1" ]; then
  info "Bootstrap do runtime Exocórtex desativado por EXOCORTEX_BOOTSTRAP_RUNTIME=0"
  exit 0
fi

receipt="$EXOCORTEX_HERMES_HOME/.exocortex-web-ui-bootstrap.done"
if [ -f "$receipt" ] && [ "$EXOCORTEX_BOOTSTRAP_FORCE" != "1" ]; then
  info "Bootstrap do runtime já registrado em $receipt"
  exit 0
fi

info "Executando setup.sh do Exocórtex dentro do container"
compose exec -T "$EXOCORTEX_HERMES_WEB_UI_SERVICE" bash -c "set -e; export PATH=/opt/hermes/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin; export HERMES_HOME=/srv/hermes; export EXOCORTEX_HOME=/srv/exocortex; export ACERVO=/srv/exocortex/acervo; mkdir -p /srv/hermes/skills /srv/hermes/memories /srv/hermes/profiles /srv/exocortex/acervo; cd /opt/exocortex.saas; export EXOCORTEX_SKIP_HERMES_WEB_UI_SETUP_STEP=1; bash ./setup.sh ${EXOCORTEX_SETUP_FLAGS:-}"

python3 - "$receipt" <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import sys
path = Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(datetime.now(timezone.utc).isoformat() + "\n", encoding='utf-8')
PY

log "Bootstrap Exocórtex registrado em $receipt"
