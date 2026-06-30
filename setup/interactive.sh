#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Setup: Interactive Prompts Library
# =============================================================================
# Biblioteca de funções para prompts interativos estilo npm-init.
# Permite confirmar ou alterar valores de variáveis de ambiente,
# API keys, paths e flags antes da instalação.
#
# Uso:
#   source setup/interactive.sh
#
# Requer: common.sh já carregado (para cores e helpers)
# Ref: ADR-012-interactive-setup.md
# =============================================================================

# Guard: evita re-source
if [ "${_EXOCORTEX_INTERACTIVE_LOADED:-}" = "1" ]; then
  return 0 2>/dev/null || true
fi
_EXOCORTEX_INTERACTIVE_LOADED=1

# ─── Configuration ──────────────────────────────────────────────────────────

INTERACTIVE_MODE="${INTERACTIVE_MODE:-1}"
ENV_LOCAL_FILE="${ENV_LOCAL_FILE:-$SCRIPT_DIR/.env.local}"
STEP_BY_STEP_MODE="${STEP_BY_STEP_MODE:-0}"

# ─── .env.local persistence ────────────────────────────────────────────────

# Load .env.local if exists (values don't override already-set env vars)
load_env_local() {
  if [ -f "$ENV_LOCAL_FILE" ]; then
    while IFS='=' read -r key value; do
      # Skip comments and empty lines
      [[ "$key" =~ ^[[:space:]]*# ]] && continue
      [[ -z "$key" ]] && continue
      # Trim whitespace
      key=$(echo "$key" | xargs)
      value=$(echo "$value" | xargs)
      # Remove surrounding quotes
      value="${value#\"}"
      value="${value%\"}"
      value="${value#\'}"
      value="${value%\'}"
      # Only set if not already defined in environment
      if [ -z "${!key:-}" ]; then
        export "$key=$value"
      fi
    done < "$ENV_LOCAL_FILE"
  fi
}

# Save a key=value pair to .env.local (creates or updates)
save_to_env_local() {
  local key="$1" value="$2"

  # Create file with secure permissions if it doesn't exist
  if [ ! -f "$ENV_LOCAL_FILE" ]; then
    cat > "$ENV_LOCAL_FILE" <<'HEADER'
# =============================================================================
# Exocórtex.IA — Configuração Local (gerada pelo setup interativo)
# =============================================================================
# Este arquivo é gerado automaticamente e NÃO deve ser commitado.
# Valores aqui sobrescrevem defaults quando .env.local é carregado.
# =============================================================================
HEADER
    chmod 600 "$ENV_LOCAL_FILE"
  fi

  # Update existing key or append
  if grep -q "^${key}=" "$ENV_LOCAL_FILE" 2>/dev/null; then
    # Use sed to replace the line (handles special chars in value)
    local escaped_value
    escaped_value=$(printf '%s' "$value" | sed 's/[&/\]/\\&/g')
    sed -i "s|^${key}=.*|${key}=\"${escaped_value}\"|" "$ENV_LOCAL_FILE"
  else
    echo "${key}=\"${value}\"" >> "$ENV_LOCAL_FILE"
  fi
}

# ─── Masking ────────────────────────────────────────────────────────────────

# Mask a sensitive value for display: sk-or-v1-600a...356f
mask_value() {
  local value="$1"
  if [ -z "$value" ]; then
    echo "(vazio)"
    return
  fi
  local len=${#value}
  if [ $len -le 8 ]; then
    echo "****"
  elif [ $len -le 16 ]; then
    echo "${value:0:4}...${value: -4}"
  else
    echo "${value:0:6}...${value: -4}"
  fi
}

# Check if a variable name looks like a secret
is_secret_var() {
  local name="$1"
  echo "$name" | grep -qiE "key|token|secret|password|credential"
}

# Warn (never block) when a secret value looks malformed — whitespace usually
# means a partial paste; a very short value usually means a truncated key.
validate_secret_format() {
  local var_name="$1" value="$2"
  [ -z "$value" ] && return 0
  if printf '%s' "$value" | grep -q '[[:space:]]'; then
    warn "$var_name contém espaço ou quebra de linha — possível cópia parcial. Revise a chave antes de prosseguir."
    return 0
  fi
  if [ "${#value}" -lt 12 ]; then
    warn "$var_name parece curta demais para uma credencial completa. Confirme se colou a chave inteira."
  fi
}

# ─── Prompt Functions ──────────────────────────────────────────────────────

# prompt_value VAR_NAME DEFAULT DESCRIPTION
# Shows current value, allows user to confirm (Enter) or type a new value.
# In non-interactive mode (--yes), accepts the default silently.
prompt_value() {
  local var_name="$1"
  local default_value="$2"
  local description="$3"

  local current_value="${!var_name:-$default_value}"

  if [ "$INTERACTIVE_MODE" != "1" ]; then
    # Non-interactive: use current/default silently
    export "$var_name=$current_value"
    return 0
  fi

  local display_value="$current_value"
  if [ -z "$display_value" ]; then
    display_value="${DIM}(vazio)${NC}"
  fi

  echo -en "  ${CYAN}$description${NC}\n"
  echo -en "  ${var_name} ${DIM}[$display_value]${NC}: "
  read -r user_input

  if [ -n "$user_input" ]; then
    export "$var_name=$user_input"
    save_to_env_local "$var_name" "$user_input"
  else
    export "$var_name=$current_value"
    if [ -n "$current_value" ]; then
      save_to_env_local "$var_name" "$current_value"
    fi
  fi
}

# prompt_secret VAR_NAME DEFAULT DESCRIPTION
# Same as prompt_value but masks the current value in display.
prompt_secret() {
  local var_name="$1"
  local default_value="$2"
  local description="$3"

  local current_value="${!var_name:-$default_value}"

  if [ "$INTERACTIVE_MODE" != "1" ]; then
    export "$var_name=$current_value"
    return 0
  fi

  local display_value
  if [ -n "$current_value" ]; then
    display_value=$(mask_value "$current_value")
  else
    display_value="${DIM}(vazio)${NC}"
  fi

  echo -en "  ${CYAN}$description${NC}\n"
  echo -en "  ${var_name} ${DIM}[$display_value]${NC}: "
  read -r user_input

  if [ -n "$user_input" ]; then
    export "$var_name=$user_input"
    save_to_env_local "$var_name" "$user_input"
  else
    export "$var_name=$current_value"
    if [ -n "$current_value" ]; then
      save_to_env_local "$var_name" "$current_value"
    fi
  fi

  validate_secret_format "$var_name" "${!var_name:-}"
}

# prompt_flag VAR_NAME DEFAULT DESCRIPTION
# Boolean prompt: y/N or Y/n depending on default.
prompt_flag() {
  local var_name="$1"
  local default_value="$2"  # "0" or "1"
  local description="$3"

  local current_value="${!var_name:-$default_value}"

  if [ "$INTERACTIVE_MODE" != "1" ]; then
    export "$var_name=$current_value"
    return 0
  fi

  local hint
  if [ "$current_value" = "1" ]; then
    hint="[S/n]"
  else
    hint="[s/N]"
  fi

  echo -en "  ${CYAN}$description${NC} ${DIM}$hint${NC}: "
  read -r user_input

  case "${user_input,,}" in
    s|y|sim|yes|1)
      export "$var_name=1"
      save_to_env_local "$var_name" "1"
      ;;
    n|nao|no|0)
      export "$var_name=0"
      save_to_env_local "$var_name" "0"
      ;;
    "")
      export "$var_name=$current_value"
      save_to_env_local "$var_name" "$current_value"
      ;;
    *)
      warn "Valor inválido: '$user_input'. Usando default: $current_value"
      export "$var_name=$current_value"
      ;;
  esac
}

# confirm_proceed MESSAGE
# Returns 0 if user confirms, 1 if not.
# In non-interactive mode, always returns 0.
confirm_proceed() {
  local message="${1:-Prosseguir com a instalação?}"

  if [ "$INTERACTIVE_MODE" != "1" ]; then
    return 0
  fi

  echo ""
  echo -en "  ${BOLD}$message${NC} ${DIM}[s/N]${NC}: "
  if ! read -r user_input; then
    return 130
  fi

  case "${user_input,,}" in
    s|y|sim|yes) return 0 ;;
    *) return 1 ;;
  esac
}

pause_step_by_step() {
  local message="${1:-Pressione Enter para continuar.}"

  if [ "$INTERACTIVE_MODE" != "1" ] || [ "${STEP_BY_STEP_MODE:-0}" != "1" ]; then
    return 0
  fi

  echo -en "  ${DIM}$message${NC}"
  read -r _step_ack || return 130
}

# Lista os providers do catálogo (setup/providers.json) com seus modelos default.
list_llm_providers() {
  local providers_file="$SCRIPT_DIR/setup/providers.json"
  [ -f "$providers_file" ] || providers_file="$SCRIPT_DIR/providers.json"
  if command -v python3 >/dev/null 2>&1 && [ -f "$providers_file" ]; then
    python3 - "$providers_file" <<'PY' 2>/dev/null || true
import json, sys
try:
    data = json.load(open(sys.argv[1])).get("providers", {})
    for pid, p in data.items():
        vis = " (visão)" if p.get("vision") else ""
        print(f"    - {pid}{vis} → modelo default: {p.get('default_model','')}")
except Exception:
    pass
PY
  fi
}

show_api_key_guidance() {
  echo -e "  ${DIM}Origem dos valores:${NC} shell atual → .env.local → defaults do setup"
  echo ""
  echo -e "  ${BOLD}Provedores LLM em 3 papéis${NC} — cada papel é provider + modelo + chave (+ base URL opcional):"
  echo -e "    ${BOLD}default${NC}  — sempre usado quando nenhum outro papel foi informado. ${DIM}(obrigatório)${NC}"
  echo -e "    ${BOLD}vision${NC}   — modelo com visão. ${DIM}Vazio = herda o default campo a campo.${NC}"
  echo -e "    ${BOLD}auxiliar${NC} — modelo para softwares externos (DocBrain, Hindsight). ${DIM}Vazio = herda o default.${NC}"
  echo ""
  echo -e "  ${DIM}base URL vazia = derivada do provider. Providers conhecidos:${NC}"
  list_llm_providers
  echo ""
}

# prompt_llm_role ROLE_PREFIX ROLE_DESC [REQUIRED]
# Prompts provider/model/api_key/base_url para um papel. ROLE_PREFIX ∈ DEFAULT|VISION|AUX.
prompt_llm_role() {
  local prefix="$1" desc="$2" required="${3:-0}"
  local inherit_hint=""
  [ "$required" != "1" ] && inherit_hint=" ${DIM}(Enter em branco = herda o default)${NC}"

  echo -e "  ${BOLD}» Papel ${desc}${NC}${inherit_hint}"
  prompt_value  "EXOCORTEX_${prefix}_PROVIDER" "$(eval echo "\${EXOCORTEX_${prefix}_PROVIDER:-}")" "Provider (ex.: openrouter, deepseek, openai, gemini, xai)"
  prompt_value  "EXOCORTEX_${prefix}_MODEL"    "$(eval echo "\${EXOCORTEX_${prefix}_MODEL:-}")"    "Modelo (ex.: deepseek-v4-pro). Vazio usa o default do provider"
  prompt_secret "EXOCORTEX_${prefix}_API_KEY"  "$(eval echo "\${EXOCORTEX_${prefix}_API_KEY:-}")"  "Chave de API do provider"
  prompt_value  "EXOCORTEX_${prefix}_BASE_URL" "$(eval echo "\${EXOCORTEX_${prefix}_BASE_URL:-}")" "Base URL (vazio = derivada do catálogo do provider)"
  echo ""
}

# ─── Display Functions ─────────────────────────────────────────────────────

# show_config_table
# Displays all current configuration values in a formatted table.
show_config_table() {
  echo ""
  echo -e "${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}║   Configuração Atual                                     ║${NC}"
  echo -e "${BOLD}╠═══════════════════════════════════════════════════════════╣${NC}"

  _show_row() {
    local name="$1" value="$2" status="$3"
    local display_val="$value"

    if is_secret_var "$name" && [ -n "$value" ]; then
      display_val=$(mask_value "$value")
    fi

    if [ -z "$value" ]; then
      display_val="(não definido)"
      status="${YELLOW}○${NC}"
    elif [ "$status" = "ok" ]; then
      status="${GREEN}●${NC}"
    else
      status="${CYAN}●${NC}"
    fi

    printf "  %b  %-35s %s\n" "$status" "$name" "$display_val"
  }

  echo -e "${BOLD}║ Paths${NC}"
  _show_row "HERMES_HOME"     "${HERMES_HOME:-}"     "ok"
  _show_row "EXOCORTEX_HOME"  "${EXOCORTEX_HOME:-}"  "ok"
  _show_row "ACERVO"          "${ACERVO:-}"           "ok"

  echo -e "${BOLD}║ Provedores LLM (3 papéis)${NC}"
  _show_row "EXOCORTEX_DEFAULT_PROVIDER" "${EXOCORTEX_DEFAULT_PROVIDER:-}" "ok"
  _show_row "EXOCORTEX_DEFAULT_MODEL"    "${EXOCORTEX_DEFAULT_MODEL:-}"    "ok"
  _show_row "EXOCORTEX_DEFAULT_API_KEY"  "${EXOCORTEX_DEFAULT_API_KEY:-}"  "ok"
  _show_row "EXOCORTEX_VISION_PROVIDER"  "${EXOCORTEX_VISION_PROVIDER:-}"  "ok"
  _show_row "EXOCORTEX_VISION_MODEL"     "${EXOCORTEX_VISION_MODEL:-}"     "ok"
  _show_row "EXOCORTEX_VISION_API_KEY"   "${EXOCORTEX_VISION_API_KEY:-}"   "ok"
  _show_row "EXOCORTEX_AUX_PROVIDER"     "${EXOCORTEX_AUX_PROVIDER:-}"     "ok"
  _show_row "EXOCORTEX_AUX_MODEL"        "${EXOCORTEX_AUX_MODEL:-}"        "ok"
  _show_row "EXOCORTEX_AUX_API_KEY"      "${EXOCORTEX_AUX_API_KEY:-}"      "ok"

  echo -e "${BOLD}║ Serviços (não-LLM)${NC}"
  _show_row "TELEGRAM_BOT_TOKEN"     "${TELEGRAM_BOT_TOKEN:-}"     "ok"
  _show_row "CONTEXT7_API_KEY"       "${CONTEXT7_API_KEY:-}"       "ok"
  _show_row "FIRECRAWL_API_KEY"      "${FIRECRAWL_API_KEY:-}"      "ok"
  _show_row "FIRECRAWL_BASE_URL"     "${FIRECRAWL_BASE_URL:-http://127.0.0.1:3002}" "ok"
  _show_row "HINDSIGHT_API_KEY"      "${HINDSIGHT_API_KEY:-}"      "ok"

  echo -e "${BOLD}║ Features (flags)${NC}"
  _show_row "EXOCORTEX_ENABLE_HINDSIGHT"   "${EXOCORTEX_ENABLE_HINDSIGHT:-0}"     "ok"
  _show_row "EXOCORTEX_ENABLE_HERMES_WEBUI" "${EXOCORTEX_ENABLE_HERMES_WEBUI:-0}" "ok"
  _show_row "EXOCORTEX_ENABLE_CONTEXT7"    "${EXOCORTEX_ENABLE_CONTEXT7:-0}"      "ok"
  _show_row "IMBROKE_MODE"                  "${IMBROKE_MODE:-0}"                   "ok"
  _show_row "CALIBRATE_MODE"                "${CALIBRATE_MODE:-0}"                "ok"

  echo -e "${BOLD}║ Paths Opcionais${NC}"
  _show_row "EXOCORTEX_DOCBRAIN_DIR"       "${EXOCORTEX_DOCBRAIN_DIR:-}"       "ok"
  _show_row "EXOCORTEX_HERMES_WEBUI_HOME"  "${EXOCORTEX_HERMES_WEBUI_HOME:-}" "ok"
  _show_row "EXOCORTEX_HERMES_WEBUI_PORT"  "${EXOCORTEX_HERMES_WEBUI_PORT:-}" "ok"
  _show_row "EXOCORTEX_HERMES_WEBUI_HOST"  "${EXOCORTEX_HERMES_WEBUI_HOST:-}" "ok"

  echo -e "${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
  echo ""
}

# ─── Interactive Init Flow ─────────────────────────────────────────────────

# run_interactive_init
# Main interactive configuration flow. Prompts for each setting group.
run_interactive_init() {
  echo ""
  if [ "${STEP_BY_STEP_MODE:-0}" = "1" ]; then
    echo -e "${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║   Configuração Guiada (passo a passo)                    ║${NC}"
    echo -e "${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo -e "${DIM}Cada bloco para e explica o que está sendo conferido.${NC}"
  else
    echo -e "${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║   Configuração Interativa (Enter = aceitar default)      ║${NC}"
    echo -e "${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
  fi
  echo ""

  # ─── Paths ──────────────────────────────────────────────────────────
  echo -e "${BOLD}─── Paths ───${NC}"
  pause_step_by_step "Revise os paths base. Enter para continuar: " || return 130
  prompt_value "HERMES_HOME"    "${HERMES_HOME:-$HOME/.hermes}"     "Diretório do runtime Hermes"
  prompt_value "EXOCORTEX_HOME" "${EXOCORTEX_HOME:-$HOME/exocortex}" "Diretório do workspace Exocórtex"
  echo ""

  # Recalculate derived paths
  ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"
  export ACERVO

  # ─── Provedores LLM (3 papéis) ─────────────────────────────────────
  echo -e "${BOLD}─── Provedores LLM (3 papéis) ───${NC}"
  pause_step_by_step "Agora vamos configurar os provedores LLM (default/vision/auxiliar). Enter para continuar: " || return 130
  show_api_key_guidance
  prompt_llm_role "DEFAULT" "default (sempre usado)"            1
  prompt_llm_role "VISION"  "vision (modelo com visão)"         0
  prompt_llm_role "AUX"     "auxiliar (DocBrain / Hindsight)"   0

  # ─── Serviços (não-LLM) ────────────────────────────────────────────
  echo -e "${BOLD}─── Serviços (não-LLM) ───${NC}"
  pause_step_by_step "Por fim, as chaves de serviços (Telegram, Firecrawl, Context7). Enter para continuar: " || return 130
  prompt_secret "TELEGRAM_BOT_TOKEN"   "${TELEGRAM_BOT_TOKEN:-}"   "Token do Telegram Bot (@BotFather)"
  prompt_secret "CONTEXT7_API_KEY"     "${CONTEXT7_API_KEY:-}"     "Chave Context7 (docs tech stacks, opcional)"
  prompt_secret "FIRECRAWL_API_KEY"    "${FIRECRAWL_API_KEY:-}"    "Chave Firecrawl (crawling/extract, opcional)"
  prompt_value  "FIRECRAWL_BASE_URL"   "${FIRECRAWL_BASE_URL:-http://127.0.0.1:3002}" "Endpoint Firecrawl (default local: 127.0.0.1:3002)"
  prompt_secret "HINDSIGHT_API_KEY"    "${HINDSIGHT_API_KEY:-}"    "Chave Hindsight cloud (opcional)"
  echo ""

  # ─── Features ──────────────────────────────────────────────────────
  echo -e "${BOLD}─── Features Opcionais ───${NC}"
  pause_step_by_step "Por fim, revise as features opcionais. Enter para continuar: " || return 130
  prompt_flag "EXOCORTEX_ENABLE_HINDSIGHT"    "${EXOCORTEX_ENABLE_HINDSIGHT:-1}"    "Ativar Hindsight (memória Docker local)?"
  prompt_flag "EXOCORTEX_ENABLE_HERMES_WEBUI" "${EXOCORTEX_ENABLE_HERMES_WEBUI:-0}" "Ativar Hermes WebUI (cockpit web)?"
  prompt_flag "EXOCORTEX_ENABLE_CONTEXT7"     "${EXOCORTEX_ENABLE_CONTEXT7:-0}"     "Ativar Context7 (docs de tech stacks via MCP)?"
  echo ""

  # ─── Paths opcionais (só se features ativadas) ─────────────────────
  if [ "${EXOCORTEX_ENABLE_HERMES_WEBUI:-0}" = "1" ]; then
    echo -e "${BOLD}─── Hermes WebUI ───${NC}"
    prompt_value "EXOCORTEX_HERMES_WEBUI_HOME" "${EXOCORTEX_HERMES_WEBUI_HOME:-$HERMES_HOME/hermes-webui}" "Diretório do WebUI"
    prompt_value "EXOCORTEX_HERMES_WEBUI_PORT" "${EXOCORTEX_HERMES_WEBUI_PORT:-8787}" "Porta do WebUI"
    prompt_value "EXOCORTEX_HERMES_WEBUI_HOST" "${EXOCORTEX_HERMES_WEBUI_HOST:-127.0.0.1}" "Bind address do WebUI"
    echo ""
  fi

  # Re-export derived paths after possible changes
  ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"
  SKILLS_SRC="$SCRIPT_DIR/skills"
  SKILLS_DST="$HERMES_HOME/skills/excrtx"
  PROFILES_SRC="$SCRIPT_DIR/profiles"
  PROFILES_DST="$HERMES_HOME/profiles"
  BUNDLES_SRC="$SCRIPT_DIR/skill-bundles"
  BUNDLES_DST="$HERMES_HOME/skill-bundles"
  ACERVO_SRC="$SCRIPT_DIR/acervo"

  export HERMES_HOME EXOCORTEX_HOME ACERVO SCRIPT_DIR
  export IMBROKE_MODE CALIBRATE_MODE STEP_BY_STEP_MODE FIRECRAWL_BASE_URL
  export SKILLS_SRC SKILLS_DST PROFILES_SRC PROFILES_DST BUNDLES_SRC BUNDLES_DST ACERVO_SRC
}
