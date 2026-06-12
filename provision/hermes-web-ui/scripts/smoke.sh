#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
load_env
require_cmd curl
require_cmd python3

wait_for_health 30

[ -f "$EXOCORTEX_HERMES_HOME/SOUL.md" ] || fail "SOUL.md não encontrado em $EXOCORTEX_HERMES_HOME"
[ -f "$EXOCORTEX_HERMES_HOME/profiles/manut/profile.yaml" ] || fail "Profile manut ausente em $EXOCORTEX_HERMES_HOME/profiles/manut/profile.yaml"
[ -f "$EXOCORTEX_WEB_UI_HOME/config.json" ] || fail "config.json da UI ausente em $EXOCORTEX_WEB_UI_HOME"
[ -f "$EXOCORTEX_WEB_UI_HOME/hermes-web-ui.db" ] || fail "DB da UI ausente em $EXOCORTEX_WEB_UI_HOME/hermes-web-ui.db"

health_json="$(curl -fsS "http://127.0.0.1:${EXOCORTEX_UI_PORT}/health")"
python3 - "$EXOCORTEX_WEB_UI_HOME/hermes-web-ui.db" "$health_json" <<'PY'
import json
import sqlite3
import sys

db_path, health_json = sys.argv[1:3]
conn = sqlite3.connect(db_path)
cur = conn.cursor()
user = cur.execute("SELECT username, role, status FROM users ORDER BY id ASC LIMIT 1").fetchone()
profiles = cur.execute("SELECT profile_name, is_default FROM user_profiles ORDER BY is_default DESC, profile_name ASC").fetchall()
summary = {
    'health': json.loads(health_json),
    'admin_user': user,
    'profiles': profiles,
}
print(json.dumps(summary, ensure_ascii=False))
conn.close()
PY

log "Smoke suite passou"
