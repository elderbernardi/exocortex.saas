#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Resolvedor de papéis LLM (shell)
# =============================================================================
# Wrapper fino sobre o resolvedor canônico em Python (scripts/lib/llm_roles.py).
# Toda a herança (vision/aux → default) e o catálogo de providers vivem no
# módulo Python; este arquivo só captura o resultado em variáveis de shell.
#
# Uso:
#   source setup/lib/llm-roles.sh
#   exocortex_resolve_role default   # popula ROLE_PROVIDER/MODEL/API_KEY/...
#   echo "$ROLE_MODEL"
#
#   exocortex_ping_role aux          # teste real (1 chamada) ao endpoint do papel
#
# Variáveis exportadas por exocortex_resolve_role:
#   ROLE_PROVIDER ROLE_MODEL ROLE_API_KEY ROLE_BASE_URL ROLE_CHAT_URL
#   ROLE_STYLE ROLE_VISION ROLE_USABLE
# =============================================================================

if [ "${_EXOCORTEX_LLM_ROLES_LOADED:-}" = "1" ]; then
  return 0 2>/dev/null || true
fi
_EXOCORTEX_LLM_ROLES_LOADED=1

# Localiza o módulo Python relativo a este arquivo (setup/lib/ -> scripts/lib/).
_LLM_ROLES_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_LLM_ROLES_PY="$_LLM_ROLES_LIB_DIR/../../scripts/lib/llm_roles.py"

# exocortex_resolve_role <default|vision|aux|auxiliar>
# Popula ROLE_* no escopo atual. Retorna 0 sempre que conseguiu resolver
# (mesmo papel inutilizável — cheque $ROLE_USABLE).
exocortex_resolve_role() {
  local role="${1:-default}"
  ROLE_PROVIDER="" ROLE_MODEL="" ROLE_API_KEY="" ROLE_BASE_URL=""
  ROLE_CHAT_URL="" ROLE_STYLE="openai" ROLE_VISION="0" ROLE_USABLE="0"

  if ! command -v python3 >/dev/null 2>&1; then
    # Fallback degradado: lê só o ambiente do próprio papel, sem herança.
    local up
    up="$(printf '%s' "$role" | tr '[:lower:]' '[:upper:]')"
    [ "$up" = "AUXILIAR" ] && up="AUX"
    eval "ROLE_PROVIDER=\"\${EXOCORTEX_${up}_PROVIDER:-}\""
    eval "ROLE_MODEL=\"\${EXOCORTEX_${up}_MODEL:-}\""
    eval "ROLE_API_KEY=\"\${EXOCORTEX_${up}_API_KEY:-}\""
    eval "ROLE_BASE_URL=\"\${EXOCORTEX_${up}_BASE_URL:-}\""
    [ -n "$ROLE_BASE_URL" ] && ROLE_CHAT_URL="${ROLE_BASE_URL%/}/chat/completions"
    [ -n "$ROLE_API_KEY" ] && [ -n "$ROLE_MODEL" ] && [ -n "$ROLE_CHAT_URL" ] && ROLE_USABLE="1"
    return 0
  fi

  local out
  if ! out="$(python3 "$_LLM_ROLES_PY" "$role" --export-shell 2>/dev/null)"; then
    return 1
  fi
  eval "$out"
  return 0
}

# exocortex_ping_role <role>
# Faz 1 chamada barata ao endpoint de chat do papel para validar
# chave+modelo+endpoint. Retorna 0 se HTTP 2xx, 1 caso contrário.
# Imprime nada; o chamador formata a mensagem. Requer curl.
exocortex_ping_role() {
  local role="${1:-default}"
  exocortex_resolve_role "$role"
  if [ "$ROLE_USABLE" != "1" ]; then
    PING_STATUS="unconfigured"
    return 1
  fi
  if ! command -v curl >/dev/null 2>&1; then
    PING_STATUS="no-curl"
    return 1
  fi

  local payload http_code
  payload="$(printf '{"model":%s,"max_tokens":1,"messages":[{"role":"user","content":"ping"}]}' \
    "$(printf '%s' "$ROLE_MODEL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')")"

  # `-w %{http_code}` já imprime "000" em falha de conexão; nada de `|| echo`
  # (geraria duplicação tipo "000000").
  http_code="$(curl -sS -o /dev/null -w '%{http_code}' \
    --max-time 30 \
    -X POST "$ROLE_CHAT_URL" \
    -H "Authorization: Bearer $ROLE_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload" 2>/dev/null)"

  PING_STATUS="${http_code:-000}"
  case "$http_code" in
    2*) return 0 ;;
    *)  return 1 ;;
  esac
}
