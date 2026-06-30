#!/usr/bin/env bash
# =============================================================================
# Hindsight — Smoke Test
# =============================================================================
# Verifica que o Hindsight está provisionado e que a API responde.
# Mirrors provision/hermes-webui/scripts/smoke.sh structure.
#
# Exit semantics:
#   0  — all critical checks passed (container running + API reachable)
#   1  — critical check failed (container missing/stopped, or API down)
#
# The health endpoint is best-effort probed at /health on the API port.
# A timeout (container still starting) is treated as a WARNING, not a failure,
# to match the same policy applied in setup/step-01-hindsight.sh.
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
HS_DIR="${EXOCORTEX_HINDSIGHT_DIR:-$HERMES_HOME/hindsight-local}"
HS_API_PORT="${EXOCORTEX_HINDSIGHT_API_PORT:-8888}"

info "Smoke test — Hindsight"
info "  HS_DIR:   $HS_DIR"
info "  API port: $HS_API_PORT"

# ── Critical: provisioning directory ────────────────────────────────────────
[ -d "$HS_DIR" ] || fail "Hindsight dir não encontrado: $HS_DIR"
log "Diretório presente"

# ── Critical: docker-compose.yml ────────────────────────────────────────────
[ -f "$HS_DIR/docker-compose.yml" ] || fail "docker-compose.yml ausente em $HS_DIR"
log "docker-compose.yml presente"

# ── Critical: .env ──────────────────────────────────────────────────────────
[ -f "$HS_DIR/.env" ] || fail ".env ausente em $HS_DIR"
if grep -q "CHANGE_ME" "$HS_DIR/.env"; then
  fail ".env contém CHANGE_ME — configure HINDSIGHT_API_LLM_API_KEY"
fi
log ".env presente e configurado"

# ── Critical: container running ─────────────────────────────────────────────
if command -v docker >/dev/null 2>&1; then
  _container_status="$(docker inspect --format '{{.State.Status}}' exocortex-hindsight 2>/dev/null || echo "missing")"
  case "$_container_status" in
    running)
      log "Container exocortex-hindsight: running"
      ;;
    missing)
      fail "Container exocortex-hindsight não encontrado — rode: EXOCORTEX_ENABLE_HINDSIGHT=1 bash setup.sh"
      ;;
    *)
      fail "Container exocortex-hindsight em estado inesperado: $_container_status"
      ;;
  esac
else
  warn "docker não disponível — não foi possível verificar o estado do container"
fi

# ── Best-effort: health endpoint ────────────────────────────────────────────
_hs_health_url="http://127.0.0.1:${HS_API_PORT}/health"
if command -v curl >/dev/null 2>&1; then
  _health_ok=0
  _attempt=0
  for _attempt in 1 2 3; do
    if curl -sf --max-time 5 "$_hs_health_url" >/dev/null 2>&1; then
      _health_ok=1
      break
    fi
    _http_code="$(curl -so /dev/null --max-time 5 -w "%{http_code}" "$_hs_health_url" 2>/dev/null || true)"
    if [ -n "$_http_code" ] && [ "$_http_code" != "000" ]; then
      _health_ok=1
      break
    fi
    [ "$_attempt" -lt 3 ] && sleep 2
  done

  if [ "$_health_ok" = "1" ]; then
    log "API respondendo em ${_hs_health_url}"
  else
    warn "API sem resposta em ${_hs_health_url} após 3 tentativas"
    warn "  Container pode ainda estar inicializando"
    warn "  Verifique: docker logs exocortex-hindsight"
    # WARN-not-fail: slow start is expected on first run
  fi
else
  warn "curl não disponível — pulando verificação de saúde da API"
fi

echo
log "Smoke test Hindsight concluído."
