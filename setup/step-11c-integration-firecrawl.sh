#!/usr/bin/env bash
# =============================================================================
# Step 11c: Integração — Firecrawl (scraping/crawl/extract) — modelo escalonado
# =============================================================================
# Resolve o Firecrawl em 3 tiers, na ordem:
#   Tier 1 (self-host):     EXOCORTEX_ENABLE_FIRECRAWL=1 → sobe a stack Docker
#                           local (provision/firecrawl) e aponta a base URL para
#                           o endpoint local.
#   Tier 2 (BYO endpoint):  toggle desligado, mas FIRECRAWL_BASE_URL responde
#                           a um health probe → usa o servidor existente.
#   Tier 3 (degradação):    nenhum dos dois → grava um lembrete e segue sem
#                           falhar (skills caem para fallback browser/erro).
#
# Idempotente em qualquer tier. A registração do MCP (quando disponível) é
# guardada por `hermes mcp list`, espelhando step-11-integration-context7.sh.
# =============================================================================

# Standalone support — use BASH_SOURCE so common.sh resolves correctly whether
# this file is executed directly OR sourced from another script (e.g. tests).
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
fi

# Caminho do instalador self-host (overridável em testes).
FIRECRAWL_INSTALL_SCRIPT="${FIRECRAWL_INSTALL_SCRIPT:-$SCRIPT_DIR/provision/firecrawl/scripts/install.sh}"

# ─── Health probe (tolerante: qualquer resposta HTTP conta como "no ar") ─────
# Retorna 0 se a base URL responde (2xx/3xx/4xx), 1 caso contrário.
_firecrawl_probe() {
  local base="$1"
  [ -n "$base" ] || return 1
  command -v curl >/dev/null 2>&1 || return 1
  local url="${base%/}/"
  if curl -sf --max-time 5 "$url" >/dev/null 2>&1; then
    return 0
  fi
  local code
  code="$(curl -so /dev/null --max-time 5 -w "%{http_code}" "$url" 2>/dev/null || true)"
  [ -n "$code" ] && [ "$code" != "000" ]
}

# ─── Reminder de degradação (Tier 3) ─────────────────────────────────────────
_firecrawl_write_reminder() {
  local base="$1"
  mkdir -p "$HERMES_HOME/reminders"
  cat > "$HERMES_HOME/reminders/firecrawl.md" <<EOF
# Firecrawl indisponível

O Firecrawl não foi provisionado nem encontrado neste setup.

- Self-host não ficou ativo neste setup (toggle desligado, Docker ausente ou provisionamento falhou)
- Nenhum servidor respondeu em \`FIRECRAWL_BASE_URL\` (${base:-não definida})

## Skills que degradam (fallback automático, sem erro fatal)

- \`excrtx-integrate-mcp\` — usa \`web_extract\` via Firecrawl quando disponível;
  sem ele, cai para \`browser_navigate\`/\`browser_vision\` ou \`curl\`/\`git clone\`.
- \`excrtx-source-reclameaqui\` — tenta Firecrawl MCP para contornar challenges;
  sem ele, retorna o envelope de erro estruturado (\`cloudflare_challenge\`).

## Como habilitar depois

1. Self-host (Docker):
   \`EXOCORTEX_ENABLE_FIRECRAWL=1 bash setup.sh\`
2. Apontar para um Firecrawl já existente:
   \`FIRECRAWL_BASE_URL=http://<host>:3002 bash setup.sh\`
EOF
  info "Lembrete criado: $HERMES_HOME/reminders/firecrawl.md"
}

# ─── Registro do MCP do Firecrawl (guardado + idempotente) ───────────────────
# O adapter stdio recebe o endpoint local por ambiente. O backend self-hosted
# dispensa API key, mas o adapter é uma capacidade explícita do profile full.
_firecrawl_register_mcp() {
  local base="$1"
  command -v hermes >/dev/null 2>&1 || { warn "hermes CLI não encontrado; MCP Firecrawl indisponível"; return 1; }
  command -v firecrawl-mcp >/dev/null 2>&1 || {
    warn "Capacidade ausente: firecrawl-mcp"
    warn "Instale a ferramenta isolada e rode novamente: npm install --global firecrawl-mcp@3.22.0"
    return 1
  }
  if hermes mcp list 2>/dev/null | grep -q "firecrawl"; then
    log "MCP server 'firecrawl' já configurado"
  else
    printf 'y\n' | hermes mcp add firecrawl \
      --command firecrawl-mcp \
      --env "FIRECRAWL_API_URL=${FIRECRAWL_BASE_URL}" >/dev/null
    log "MCP server 'firecrawl' registrado contra o backend local"
  fi

  hermes mcp test firecrawl >/dev/null
  log "MCP server 'firecrawl' conectado ao backend $base"
}

# ─── Orquestrador dos tiers ──────────────────────────────────────────────────
configure_firecrawl() {
  local base_url="${FIRECRAWL_BASE_URL:-http://127.0.0.1:3002}"

  # ── Tier 1: self-host via Docker ──────────────────────────────────────────
  if [ "${EXOCORTEX_ENABLE_FIRECRAWL:-0}" = "1" ]; then
    if ! command -v docker >/dev/null 2>&1; then
      warn "Firecrawl self-host solicitado, mas docker não foi encontrado — tentando endpoint existente antes de degradar"
      info "  Instale Docker e rode novamente: EXOCORTEX_ENABLE_FIRECRAWL=1 bash setup.sh"
      info "  Ou aponte para um Firecrawl existente: FIRECRAWL_BASE_URL=<url> bash setup.sh"
    elif [ ! -f "$FIRECRAWL_INSTALL_SCRIPT" ]; then
      warn "Instalador do Firecrawl não encontrado: $FIRECRAWL_INSTALL_SCRIPT — tentando endpoint existente antes de degradar"
    else
      info "Tier 1: provisionando Firecrawl self-hosted (Docker)..."
      # O instalador é idempotente (down/up guardados); falha dura aborta via
      # set -euo pipefail no próprio install.sh — aqui tratamos como não-fatal
      # para o setup global (a degradação cobre o resto).
      if FIRECRAWL_BASE_URL="$base_url" bash "$FIRECRAWL_INSTALL_SCRIPT"; then
        # Self-host = endpoint local; fixa a base URL para o restante do setup.
        export FIRECRAWL_BASE_URL="$base_url"
        log "Firecrawl self-hosted ativo em $base_url"
        _firecrawl_register_mcp "$base_url"
      else
        warn "Falha ao provisionar Firecrawl self-hosted — caindo para degradação"
        _firecrawl_write_reminder "$base_url"
      fi
      return 0
    fi
  fi

  # ── Tier 2: servidor existente (BYO endpoint) ─────────────────────────────
  if _firecrawl_probe "$base_url"; then
    log "Tier 2: usando Firecrawl existing em $base_url (health OK)"
    export FIRECRAWL_BASE_URL="$base_url"
    _firecrawl_register_mcp "$base_url"
    return 0
  fi

  # ── Tier 3: degradação graciosa ───────────────────────────────────────────
  warn "Firecrawl indisponível (self-host inativo/indisponível e $base_url não respondeu)"
  info "  Skills com dependência de Firecrawl usarão fallback (browser/erro estruturado)"
  _firecrawl_write_reminder "$base_url"
  return 0
}

# Autorun (suprimível em testes via EXOCORTEX_FIRECRAWL_SKIP_AUTORUN=1).
# `: ` no-op final garante status 0 ao ser sourced com a flag de skip ativa
# (evita que `source` retorne != 0 sob `set -e` no caller).
if [ "${EXOCORTEX_FIRECRAWL_SKIP_AUTORUN:-0}" != "1" ]; then
  info "Firecrawl (scraping/crawl/extract — modelo escalonado)..."
  configure_firecrawl
fi
:
