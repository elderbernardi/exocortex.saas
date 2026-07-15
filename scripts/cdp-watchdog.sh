#!/usr/bin/env bash
# =============================================================================
# CDP Watchdog — Health check + auto-restart do Chromium CDP
# =============================================================================
# Verifica se o endpoint CDP em 127.0.0.1:9222 responde.
# Se não responder, mata processos stale e recria o Chromium CDP.
#
# Usado pelo cron:  cdp-watchdog  (a cada 5 min, no_agent)
# =============================================================================

CDP_URL="${CDP_URL:-http://127.0.0.1:9222}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVE_PY="/tmp/bu/serve_cdp.py"
LOCKFILE="/tmp/bu/cdp-watchdog.lock"

# ── Guard: não executa se outro watchdog está rodando ────────────────────────
exec 200>"$LOCKFILE"
if ! flock -n 200; then
  echo "[$(date -Iseconds)] watchdog já está rodando (lock $LOCKFILE)" >&2
  exit 0
fi

# ── Health check ────────────────────────────────────────────────────────────
if curl -sf --max-time 5 "$CDP_URL/json/version" >/dev/null 2>&1; then
  # CDP está vivo — nada a fazer
  exit 0
fi

echo "[$(date -Iseconds)] CDP não respondeu. Reciclando..." >&2

# ── Kill stale CDP processes ────────────────────────────────────────────────
pkill -f 'serve_cdp.py' 2>/dev/null || true
sleep 2

# ── Garantir que o script existe ────────────────────────────────────────────
mkdir -p /tmp/bu
if [ ! -f "$SERVE_PY" ]; then
  cat > "$SERVE_PY" <<'PY'
from playwright.sync_api import sync_playwright
import time
p = sync_playwright().start()
b = p.chromium.launch(
    headless=True,
    args=['--no-sandbox','--disable-dev-shm-usage',
          '--remote-debugging-port=9222','--remote-debugging-address=127.0.0.1'],
)
print('CDP ready on :9222', flush=True)
while True:
    time.sleep(60)
PY
fi

# ── Relaunch CDP ────────────────────────────────────────────────────────────
nohup uvx --from playwright python3 "$SERVE_PY" >/tmp/bu/cdp.log 2>&1 &
CDP_PID=$!
echo "[$(date -Iseconds)] CDP relançado com PID=$CDP_PID" >&2

# ── Wait for readiness ──────────────────────────────────────────────────────
for i in $(seq 1 12); do
  sleep 5
  if curl -sf --max-time 5 "$CDP_URL/json/version" >/dev/null 2>&1; then
    echo "[$(date -Iseconds)] CDP pronto após ${i} tentativas" >&2
    exit 0
  fi
  echo "[$(date -Iseconds)] aguardando CDP... ($i/12)" >&2
done

echo "[$(date -Iseconds)] CDP não subiu após 60s" >&2
exit 1
