#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROVISION_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROVISION_DIR/../.." && pwd)"
ENV_FILE="${EXOCORTEX_PROVISION_ENV_FILE:-$PROVISION_DIR/env/.env}"
ENV_EXAMPLE="$PROVISION_DIR/env/.env.example"
COMPOSE_FILE="$PROVISION_DIR/docker/compose.yml"
SOURCES_LOCK_FILE="${EXOCORTEX_SOURCES_LOCK_FILE:-$REPO_ROOT/provision/sources/sources.lock.yaml}"

read_source_lock_field() {
  local source_name="$1"
  local section_name="$2"
  local field_name="$3"

  [ -f "$SOURCES_LOCK_FILE" ] || fail "sources.lock.yaml não encontrado: $SOURCES_LOCK_FILE"
  python3 - "$SOURCES_LOCK_FILE" "$source_name" "$section_name" "$field_name" <<'PY'
import sys
from pathlib import Path

lock_path, source_name, section_name, field_name = sys.argv[1:5]
lines = Path(lock_path).read_text(encoding="utf-8").splitlines()

in_sources = False
current_source = None
current_section = None

for raw in lines:
    if not raw.strip() or raw.lstrip().startswith("#"):
        continue
    indent = len(raw) - len(raw.lstrip(" "))
    stripped = raw.strip()

    if indent == 0 and stripped == "sources:":
        in_sources = True
        current_source = None
        current_section = None
        continue
    if indent == 0 and not stripped.startswith("sources:"):
        in_sources = False
        current_source = None
        current_section = None
        continue
    if not in_sources:
        continue

    if indent == 2 and stripped.endswith(":"):
        current_source = stripped[:-1]
        current_section = None
        continue
    if current_source != source_name:
        continue
    if indent == 4 and stripped.endswith(":"):
        current_section = stripped[:-1]
        continue
    if current_section != section_name or indent != 6 or ":" not in stripped:
        continue

    key, value = stripped.split(":", 1)
    if key.strip() == field_name:
        print(value.strip().strip('"').strip("'"))
        raise SystemExit(0)

raise SystemExit(f"Campo não encontrado em {lock_path}: {source_name}.{section_name}.{field_name}")
PY
}

resolve_web_ui_source_from_lock() {
  if [ -z "${EXOCORTEX_HERMES_WEB_UI_REPO_URL:-}" ]; then
    export EXOCORTEX_HERMES_WEB_UI_REPO_URL="$(read_source_lock_field hermes-web-ui upstream git)"
    log "EXOCORTEX_HERMES_WEB_UI_REPO_URL resolvido via sources.lock.yaml"
  fi

  if [ -z "${EXOCORTEX_HERMES_WEB_UI_REF:-}" ]; then
    export EXOCORTEX_HERMES_WEB_UI_REF="$(read_source_lock_field hermes-web-ui controlled ref)"
    log "EXOCORTEX_HERMES_WEB_UI_REF resolvido via sources.lock.yaml"
  fi
}

load_env() {
  if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
  fi

  export EXOCORTEX_HERMES_WEB_UI_SERVICE="${EXOCORTEX_HERMES_WEB_UI_SERVICE:-hermes-web-ui}"
  export EXOCORTEX_HERMES_HOME="${EXOCORTEX_HERMES_HOME:-$HOME/.hermes}"
  export EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"
  export EXOCORTEX_WEB_UI_HOME="${EXOCORTEX_WEB_UI_HOME:-$HOME/.hermes-web-ui}"
  export EXOCORTEX_UI_PORT="${EXOCORTEX_UI_PORT:-8648}"
  export EXOCORTEX_UI_CONTAINER_PORT="${EXOCORTEX_UI_CONTAINER_PORT:-8648}"
  export EXOCORTEX_ALLOWED_PROFILES="${EXOCORTEX_ALLOWED_PROFILES:-default,manut}"
  export EXOCORTEX_DEFAULT_PROFILE="${EXOCORTEX_DEFAULT_PROFILE:-default}"
  export EXOCORTEX_BOOTSTRAP_RUNTIME="${EXOCORTEX_BOOTSTRAP_RUNTIME:-1}"
  export EXOCORTEX_BOOTSTRAP_FORCE="${EXOCORTEX_BOOTSTRAP_FORCE:-0}"
  export EXOCORTEX_ALLOW_FLOATING_UPSTREAM_REF="${EXOCORTEX_ALLOW_FLOATING_UPSTREAM_REF:-0}"
  resolve_web_ui_source_from_lock
}

resolve_tailscale_ipv4() {
  require_cmd tailscale
  local ts_ip
  ts_ip="$(tailscale ip -4 2>/dev/null | head -n1 | tr -d '[:space:]')"
  [ -n "$ts_ip" ] || fail "Não foi possível resolver IPv4 do Tailscale para EXOCORTEX_UI_BIND_IP=tailscale-auto"
  printf '%s' "$ts_ip"
}

normalize_ui_bind_settings() {
  local requested_bind="${EXOCORTEX_UI_BIND_IP:-127.0.0.1}"
  local resolved_bind="$requested_bind"

  if [ "$requested_bind" = "tailscale-auto" ]; then
    resolved_bind="$(resolve_tailscale_ipv4)"
    export EXOCORTEX_UI_BIND_IP="$resolved_bind"
    log "EXOCORTEX_UI_BIND_IP resolvido via Tailscale: $resolved_bind"

    if [ -z "${CORS_ORIGINS:-}" ]; then
      export CORS_ORIGINS="http://${resolved_bind}:${EXOCORTEX_UI_PORT}"
      log "CORS_ORIGINS derivado automaticamente para bind Tailscale"
    fi
  fi
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Comando obrigatório ausente: $1"
}

compose() {
  normalize_ui_bind_settings
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

ensure_dirs() {
  mkdir -p "$EXOCORTEX_HERMES_HOME" "$EXOCORTEX_HOME" "$EXOCORTEX_WEB_UI_HOME"
}

random_secret() {
  python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(36))
PY
}

replace_env_value() {
  local key="$1"
  local value="$2"
  python3 - "$ENV_FILE" "$key" "$value" <<'PY'
import re, sys
path, key, value = sys.argv[1:4]
text = open(path, 'r', encoding='utf-8').read()
pattern = rf'^{re.escape(key)}=.*$'
replacement = f'{key}={value}'
text, count = re.subn(pattern, replacement, text, count=1, flags=re.M)
if count == 0:
    if text and not text.endswith('\n'):
        text += '\n'
    text += replacement + '\n'
open(path, 'w', encoding='utf-8').write(text)
PY
}

bind_env_value_from_shell() {
  local key="$1"
  local value="${!key:-}"
  local existing=""

  [ -n "$value" ] || return 0

  if grep -q "^${key}=" "$ENV_FILE"; then
    existing="$(grep "^${key}=" "$ENV_FILE" | cut -d'=' -f2- || true)"
  fi

  if [ -n "$existing" ]; then
    return 0
  fi

  replace_env_value "$key" "$value"
  log "$key vinculada ao ambiente de provisionamento"
}

ensure_env_file() {
  mkdir -p "$(dirname "$ENV_FILE")"
  if [ ! -f "$ENV_FILE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    log "Arquivo de ambiente criado em $ENV_FILE"
  fi

  if grep -q '^AUTH_JWT_SECRET=__GENERATE_ME__$' "$ENV_FILE"; then
    replace_env_value AUTH_JWT_SECRET "$(random_secret)"
    log "AUTH_JWT_SECRET gerado localmente"
  fi

  if grep -q '^EXOCORTEX_ADMIN_PASSWORD=__GENERATE_ME__$' "$ENV_FILE"; then
    replace_env_value EXOCORTEX_ADMIN_PASSWORD "$(random_secret)"
    log "EXOCORTEX_ADMIN_PASSWORD gerado localmente"
  fi

  bind_env_value_from_shell OPENROUTER_API_KEY
  bind_env_value_from_shell FIRECRAWL_API_KEY
}

validate_security_envelope() {
  local bind_ip="${EXOCORTEX_UI_BIND_IP:-127.0.0.1}"
  local cors_origins="${CORS_ORIGINS:-}"
  local upstream_ref="${EXOCORTEX_HERMES_WEB_UI_REF:-}"
  local allow_floating="${EXOCORTEX_ALLOW_FLOATING_UPSTREAM_REF:-0}"

  if [ -z "$upstream_ref" ]; then
    fail "EXOCORTEX_HERMES_WEB_UI_REF não pode ficar vazio"
  fi

  case "$upstream_ref" in
    main|master|HEAD)
      if [ "$allow_floating" != "1" ]; then
        fail "Ref flutuante '$upstream_ref' bloqueada. Use tag/commit pinado ou EXOCORTEX_ALLOW_FLOATING_UPSTREAM_REF=1 em dev consciente."
      fi
      warn "Usando ref flutuante '$upstream_ref' por override explícito"
      ;;
  esac

  if [ "$bind_ip" != "127.0.0.1" ] && [ "$bind_ip" != "::1" ] && [ -z "$cors_origins" ]; then
    fail "CORS_ORIGINS é obrigatório quando EXOCORTEX_UI_BIND_IP não é loopback"
  fi
}

wait_for_health() {
  local tries="${1:-60}"
  local host="${EXOCORTEX_UI_BIND_IP:-127.0.0.1}"
  local url="http://${host}:${EXOCORTEX_UI_PORT}/health"
  local i=1
  while [ "$i" -le "$tries" ]; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      log "UI respondeu em $url"
      return 0
    fi
    sleep 2
    i=$((i + 1))
  done
  fail "UI não respondeu em $url"
}
