#!/usr/bin/env bash
# =============================================================================
# Firecrawl — Smoke Test
# =============================================================================
# Verifica que o Firecrawl self-hosted está provisionado e que a API responde,
# incluindo uma requisição mínima de scrape. Mirrors a estrutura de
# provision/hindsight/scripts/smoke.sh.
#
# Exit semantics:
#   0 — checks críticos passaram (artefatos presentes + API alcançável)
#   1 — falha crítica (runtime ausente, container parado, ou API down)
#
# A requisição de scrape é best-effort: uma falha de scrape (rede do alvo, etc.)
# após a API responder é WARN, não fail — espelha a política do step-01-hindsight.
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
FC_DIR="${EXOCORTEX_FIRECRAWL_DIR:-$HERMES_HOME/firecrawl}"
FC_BASE_URL="${FIRECRAWL_BASE_URL:-http://127.0.0.1:3002}"

_docker_status() {
  local name="$1"
  if docker inspect --format '{{.State.Status}}' "$name" 2>/dev/null; then
    return 0
  fi
  if command -v sg >/dev/null 2>&1 && getent group docker >/dev/null 2>&1; then
    if sg docker -c "docker inspect --format '{{.State.Status}}' '$name'" 2>/dev/null; then
      return 0
    fi
  fi
  if command -v sudo >/dev/null 2>&1; then
    if sudo -n docker inspect --format '{{.State.Status}}' "$name" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

info "Smoke test — Firecrawl"
info "  FC_DIR:   $FC_DIR"
info "  Base URL: $FC_BASE_URL"

# ── Critical: runtime directory ─────────────────────────────────────────────
[ -d "$FC_DIR" ] || fail "Firecrawl dir não encontrado: $FC_DIR — rode: EXOCORTEX_ENABLE_FIRECRAWL=1 bash setup.sh"
log "Diretório presente"

# ── Critical: docker-compose.yml ────────────────────────────────────────────
[ -f "$FC_DIR/docker-compose.yml" ] || fail "docker-compose.yml ausente em $FC_DIR"
log "docker-compose.yml presente"

# ── Critical: API container running ─────────────────────────────────────────
if command -v docker >/dev/null 2>&1; then
  _container_status="$(_docker_status exocortex-firecrawl-api 2>/dev/null | tr -d '\r\n' || echo "missing")"
  case "$_container_status" in
    running)
      log "Container exocortex-firecrawl-api: running"
      ;;
    missing)
      fail "Container exocortex-firecrawl-api não encontrado — rode: EXOCORTEX_ENABLE_FIRECRAWL=1 bash setup.sh"
      ;;
    *)
      fail "Container exocortex-firecrawl-api em estado inesperado: $_container_status"
      ;;
  esac
else
  warn "docker não disponível — não foi possível verificar o estado do container"
fi

# ── Critical: API reachable ─────────────────────────────────────────────────
_health_url="${FC_BASE_URL%/}/"
if command -v curl >/dev/null 2>&1; then
  _api_ok=0
  _attempt=0
  for _attempt in 1 2 3; do
    if curl -sf --max-time 5 "$_health_url" >/dev/null 2>&1; then
      _api_ok=1
      break
    fi
    _http_code="$(curl -so /dev/null --max-time 5 -w "%{http_code}" "$_health_url" 2>/dev/null || true)"
    if [ -n "$_http_code" ] && [ "$_http_code" != "000" ]; then
      _api_ok=1
      break
    fi
    [ "$_attempt" -lt 3 ] && sleep 2
  done

  if [ "$_api_ok" = "1" ]; then
    log "API respondendo em ${_health_url}"
  else
    fail "API sem resposta em ${_health_url} após 3 tentativas — verifique: docker logs exocortex-firecrawl-api"
  fi

  # ── Best-effort: minimal scrape request ──────────────────────────────────
  # Self-hosted dispensa API key. Sucesso = HTTP 2xx; falha de scrape após a
  # API responder é WARN (rede do alvo pode estar indisponível no ambiente).
  _scrape_url="${FC_BASE_URL%/}/v1/scrape"
  _scrape_code="$(curl -so /dev/null --max-time 30 -w "%{http_code}" \
    -X POST "$_scrape_url" \
    -H 'Content-Type: application/json' \
    -d '{"url":"https://example.com","formats":["markdown"]}' 2>/dev/null || true)"
  case "$_scrape_code" in
    2*)
      log "Scrape de fumaça OK (POST /v1/scrape → HTTP $_scrape_code)"
      ;;
    "" | 000)
      warn "Scrape de fumaça sem resposta (POST /v1/scrape) — API pode estar inicializando workers"
      ;;
    *)
      warn "Scrape de fumaça retornou HTTP $_scrape_code (POST /v1/scrape) — provável bloqueio de rede do alvo; API está no ar"
      ;;
  esac
else
  warn "curl não disponível — pulando verificação de saúde da API"
fi

echo
log "Smoke test Firecrawl concluído."
