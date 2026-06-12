#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
load_env
require_cmd python3

config_path="$EXOCORTEX_WEB_UI_HOME/config.json"
receipt_path="$EXOCORTEX_WEB_UI_HOME/exocortex-bootstrap.json"
profiles_csv="${EXOCORTEX_ALLOWED_PROFILES:-default,manut}"
default_profile="${EXOCORTEX_DEFAULT_PROFILE:-default}"
autostart_enabled="${EXOCORTEX_GATEWAY_AUTOSTART_ENABLED:-1}"

mkdir -p "$EXOCORTEX_WEB_UI_HOME"
python3 - "$config_path" "$receipt_path" "$profiles_csv" "$default_profile" "$autostart_enabled" <<'PY'
import json
import sys
import time
from pathlib import Path

_, config_path, receipt_path, profiles_csv, default_profile, enabled_raw = sys.argv
profiles = [p.strip() for p in profiles_csv.split(',') if p.strip()]
enabled = enabled_raw == '1'
config_file = Path(config_path)
receipt_file = Path(receipt_path)
config_file.parent.mkdir(parents=True, exist_ok=True)

current = {}
if config_file.exists():
    try:
        current = json.loads(config_file.read_text(encoding='utf-8'))
    except Exception:
        current = {}

current['gatewayAutoStart'] = {
    'enabled': enabled,
    'include': profiles,
    'exclude': [],
}
current['defaultProfile'] = default_profile
config_file.write_text(json.dumps(current, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

receipt = {
    'updated_at_ms': int(time.time() * 1000),
    'profiles': profiles,
    'default_profile': default_profile,
    'gateway_autostart_enabled': enabled,
}
receipt_file.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(receipt, ensure_ascii=False))
PY

log "Config da UI alinhada aos perfis do Exocórtex"
