#!/usr/bin/env bash
# =============================================================================
# Firecrawl — Install Script (Tier 1: self-hosted via Docker)
# =============================================================================
# Sobe a stack self-hosted do Firecrawl (api + playwright + redis + postgres + rabbitmq)
# a partir do docker-compose.yml vendorizado em provision/firecrawl/, e aguarda
# a API responder. Idempotente (safe re-run: down/up guardados, .env preservado).
#
# Uso:
#   bash provision/firecrawl/scripts/install.sh
#
# Variáveis de ambiente:
#   HERMES_HOME            Default: ~/.hermes
#   FIRECRAWL_BASE_URL     Default: http://127.0.0.1:3002 (deriva a porta do host)
#   EXOCORTEX_FIRECRAWL_DIR  Diretório de runtime. Default: $HERMES_HOME/firecrawl
#   FIRECRAWL_BULL_AUTH_KEY  Segredo do painel de filas. Default: gerado/preservado
#   OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME  Opcional (AI features)
#
# Saída:
#   0 — stack no ar (ou subindo); a checagem de saúde é WARN-not-fail
#   1 — falha dura (compose ausente, docker compose up falhou)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROVISION_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_SRC="$PROVISION_DIR/docker-compose.yml"

# ─── Helpers ─────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

# ─── Environment ─────────────────────────────────────────────────────────────

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
FC_DIR="${EXOCORTEX_FIRECRAWL_DIR:-$HERMES_HOME/firecrawl}"
FC_BASE_URL="${FIRECRAWL_BASE_URL:-http://127.0.0.1:3002}"

# Durable setup log (installer-safety rule: logs under $HERMES_HOME/logs/setup/).
LOG_DIR="$HERMES_HOME/logs/setup"
mkdir -p "$LOG_DIR"
FC_LOG="$LOG_DIR/firecrawl-install.log"

# Derive host port from FIRECRAWL_BASE_URL (strip scheme + host + path).
_derive_port() {
  local url="$1" port
  # http://127.0.0.1:3002  → 3002 ; default 3002 when no explicit port
  port="$(printf '%s' "$url" | sed -E 's#^[a-zA-Z]+://##; s#/.*$##; s#^[^:]*:?##')"
  if [[ "$port" =~ ^[0-9]+$ ]]; then
    printf '%s' "$port"
  else
    printf '3002'
  fi
}
FC_PORT="$(_derive_port "$FC_BASE_URL")"

# ─── Preconditions ───────────────────────────────────────────────────────────

[ -f "$COMPOSE_SRC" ] || fail "docker-compose.yml não encontrado: $COMPOSE_SRC"

if ! command -v docker >/dev/null 2>&1; then
  fail "docker não encontrado — instale Docker e rode novamente"
fi
if ! docker compose version >/dev/null 2>&1; then
  fail "'docker compose' (v2) não disponível — atualize o Docker"
fi

info "Provisionando Firecrawl (self-hosted)..."
info "  HERMES_HOME:  $HERMES_HOME"
info "  FC_DIR:       $FC_DIR"
info "  Host port:    $FC_PORT (de FIRECRAWL_BASE_URL=$FC_BASE_URL)"
info "  Log:          $FC_LOG"

# ─── Runtime directory + compose copy ────────────────────────────────────────
# Copiamos o compose vendorizado para um diretório de runtime sob HERMES_HOME,
# para que o .env (com segredos) viva fora da árvore versionada do repo.

mkdir -p "$FC_DIR"
cp "$COMPOSE_SRC" "$FC_DIR/docker-compose.yml"
log "docker-compose.yml copiado para runtime"

# ─── .env (idempotente: preserva existente, gera segredos só na 1ª vez) ──────

FC_ENV="$FC_DIR/.env"
if [ ! -f "$FC_ENV" ]; then
  # Segredo do painel de filas — preferimos o passado por env; senão geramos.
  local_bull_key="${FIRECRAWL_BULL_AUTH_KEY:-}"
  if [ -z "$local_bull_key" ]; then
    if command -v openssl >/dev/null 2>&1; then
      local_bull_key="$(openssl rand -hex 16)"
    else
      local_bull_key="exocortex-$(date +%s)"
    fi
  fi
  {
    echo "# Gerado pelo provisioner Exocórtex em $(date -Iseconds)"
    echo "# Self-hosted: a API NÃO exige Firecrawl API key (auth bypass)."
    echo "PORT=${FC_PORT}"
    echo "INTERNAL_PORT=3002"
    echo "HOST=0.0.0.0"
    echo "USE_DB_AUTHENTICATION=false"
    echo "BULL_AUTH_KEY=${local_bull_key}"
    echo "# Credenciais Postgres (mantenha consistentes entre api e nuq-postgres):"
    echo "POSTGRES_USER=postgres"
    echo "POSTGRES_PASSWORD=postgres"
    echo "POSTGRES_DB=postgres"
    echo "# AI features (opcional) — preenchidas a partir do ambiente, se houver:"
    echo "OPENAI_API_KEY=${OPENAI_API_KEY:-}"
    echo "OPENAI_BASE_URL=${OPENAI_BASE_URL:-}"
    echo "MODEL_NAME=${MODEL_NAME:-}"
    echo "MODEL_EMBEDDING_NAME=${MODEL_EMBEDDING_NAME:-}"
  } > "$FC_ENV"
  chmod 600 "$FC_ENV"
  log ".env criado em $FC_ENV (porta=$FC_PORT)"
else
  info ".env já existe, preservando: $FC_ENV"
  # Mantém a porta do .env alinhada com FIRECRAWL_BASE_URL atual.
  if grep -q '^PORT=' "$FC_ENV"; then
    sed -i "s/^PORT=.*/PORT=${FC_PORT}/" "$FC_ENV"
  else
    echo "PORT=${FC_PORT}" >> "$FC_ENV"
  fi
fi

# ─── Pull + up (idempotente) ─────────────────────────────────────────────────
# `docker compose up -d` é idempotente: recria apenas containers cuja config
# mudou; no-op quando já estão no ar com a mesma definição.

# pull failure is non-fatal: imagens podem já estar em cache (offline/airgap).
( cd "$FC_DIR" && docker compose pull >>"$FC_LOG" 2>&1 ) || \
  warn "docker compose pull falhou (seguindo com imagens em cache, se houver) — ver $FC_LOG"

info "Subindo a stack (docker compose up -d)..."
if ! ( cd "$FC_DIR" && docker compose up -d >>"$FC_LOG" 2>&1 ); then
  warn "docker compose up -d falhou — ver $FC_LOG"
  fail "Não foi possível subir a stack do Firecrawl"
fi
log "Stack Firecrawl no ar (API host: :${FC_PORT})"

# ─── Health poll (WARN-not-fail: cold start da API é lento) ──────────────────

_health_url="http://127.0.0.1:${FC_PORT}/"
_health_ok=0
if command -v curl >/dev/null 2>&1; then
  info "Aguardando a API responder em ${_health_url} ..."
  _attempt=0
  for _attempt in $(seq 1 12); do
    if curl -sf --max-time 5 "$_health_url" >/dev/null 2>&1; then
      _health_ok=1
      break
    fi
    # Qualquer resposta HTTP (2xx/3xx/4xx) já indica que a API subiu.
    _http_code="$(curl -so /dev/null --max-time 5 -w "%{http_code}" "$_health_url" 2>/dev/null || true)"
    if [ -n "$_http_code" ] && [ "$_http_code" != "000" ]; then
      _health_ok=1
      break
    fi
    [ "$_attempt" -lt 12 ] && sleep 5
  done
  if [ "$_health_ok" = "1" ]; then
    log "Firecrawl health check: API respondendo em ${_health_url}"
  else
    warn "Firecrawl health check: sem resposta em ${_health_url} após 12 tentativas"
    warn "  A API pode ainda estar inicializando (primeiro boot baixa browsers)."
    warn "  Verifique: docker logs exocortex-firecrawl-api"
  fi
else
  warn "curl não disponível — pulando verificação de saúde da API"
fi

echo
log "Firecrawl provisionado."
info "  API:          ${FC_BASE_URL}"
info "  Painel filas: ${FC_BASE_URL%/}/admin/<BULL_AUTH_KEY>/queues"
info "  Parar:        cd $FC_DIR && docker compose down"
