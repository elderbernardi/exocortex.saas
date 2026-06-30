#!/usr/bin/env bash
# =============================================================================
# Context7 — Smoke Test
# =============================================================================
# Verifica que o Context7 MCP está registrado no Hermes e, opcionalmente,
# que uma tool call básica responde.
#
# Exit semantics:
#   0 — structural check passed (context7 listed in hermes mcp list)
#   1 — critical check failed (context7 not registered or hermes unavailable)
#
# Live tool-call check is best-effort: only runs when HARNESS_MODEL is set
# (interactive/CI mode), never hard-fails offline.
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

info "Smoke test — Context7"
info "  HERMES_HOME: $HERMES_HOME"

# ── Critical: hermes CLI ─────────────────────────────────────────────────────
if ! command -v hermes >/dev/null 2>&1; then
  fail "hermes CLI não encontrado — não foi possível verificar context7"
fi
log "hermes CLI disponível"

# ── Critical: context7 registered in hermes mcp list ────────────────────────
if hermes mcp list 2>/dev/null | grep -q "context7"; then
  log "MCP server 'context7' registrado"
else
  fail "MCP server 'context7' não encontrado em 'hermes mcp list' — rode: EXOCORTEX_ENABLE_CONTEXT7=1 bash setup.sh"
fi

# ── Optional: reminder file should NOT exist once configured ─────────────────
_reminder="$HERMES_HOME/reminders/context7-api-key.md"
if [ -f "$_reminder" ]; then
  warn "Lembrete de chave pendente encontrado: $_reminder"
  warn "  Context7 pode não ter sido configurado com API key"
  warn "  Configure: CONTEXT7_API_KEY=<key> EXOCORTEX_ENABLE_CONTEXT7=1 bash setup.sh"
else
  log "Sem lembrete de chave pendente"
fi

# ── Best-effort: live tool call via hermes (only in interactive/CI mode) ─────
if [ -n "${HARNESS_MODEL:-}" ]; then
  info "HARNESS_MODEL detectado — tentando tool call ao context7 (best-effort)..."
  _ctx7_out=""
  _ctx7_exit=0
  _ctx7_out="$(hermes run \
    --model "${HARNESS_MODEL}" \
    --tool context7 \
    --input '{"tool":"resolve-library-id","libraryName":"react"}' \
    2>&1 || true)" || _ctx7_exit=$?

  if [ "$_ctx7_exit" -eq 0 ] && echo "$_ctx7_out" | grep -qi "react\|library\|context7"; then
    log "Tool call context7 respondeu (HARNESS_MODEL mode)"
  else
    warn "Tool call context7 não respondeu ou retornou resultado inesperado"
    warn "  Isso pode ser normal em ambiente offline ou com quota esgotada"
    warn "  Saída: $(echo "$_ctx7_out" | head -3)"
    # Best-effort: WARN but do not fail
  fi
else
  info "HARNESS_MODEL não definido — pulando live tool call (estrutural OK)"
fi

echo
log "Smoke test Context7 concluído."
