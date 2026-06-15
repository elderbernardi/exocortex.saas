#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Validação Completa de Environment
# =============================================================================
# Verifica TODOS os pré-requisitos do sistema antes do setup:
#   - Binários obrigatórios, recomendados e opcionais
#   - Versões mínimas (bash, python3, hermes, node)
#   - Módulos Python (yaml, google-auth-oauthlib, pptx)
#   - Conectividade de rede (GitHub, PyPI, astral.sh)
#   - Variáveis de ambiente e API keys
#
# Uso:
#   bash scripts/validate-environment.sh           # relatório visual
#   bash scripts/validate-environment.sh --json    # saída JSON
#   bash scripts/validate-environment.sh --install # tenta instalar faltantes
#
# Exit codes:
#   0 = Tudo OK
#   1 = Faltam dependências obrigatórias
#   2 = Faltam dependências recomendadas (mas pode prosseguir)
#
# Ref: ADR-012-interactive-setup.md
# =============================================================================

set -uo pipefail

# ─── Configuração ───────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ─── Parse flags ─────────────────────────────────────────────────────────────

OUTPUT_JSON=false
TRY_INSTALL=false
QUIET=false

for arg in "$@"; do
  case "$arg" in
    --json) OUTPUT_JSON=true ;;
    --install) TRY_INSTALL=true ;;
    --quiet|-q) QUIET=true ;;
    --help|-h)
      echo "Uso: bash $0 [--json] [--install] [--quiet]"
      echo ""
      echo "  --json     Saída em formato JSON"
      echo "  --install  Tenta instalar dependências faltantes"
      echo "  --quiet    Suprime output visual (apenas exit code)"
      exit 0
      ;;
    *) echo "Flag desconhecida: $arg"; exit 1 ;;
  esac
done

# JSON mode implies quiet (no visual output mixed with JSON)
if $OUTPUT_JSON; then
  QUIET=true
fi

# ─── Colors ──────────────────────────────────────────────────────────────────

if [ -t 1 ] && ! $QUIET; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  CYAN='\033[0;36m'
  BOLD='\033[1m'
  DIM='\033[2m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' CYAN='' BOLD='' DIM='' NC=''
fi

# ─── Estado global ──────────────────────────────────────────────────────────

declare -a RESULTS_JSON=()
FAIL_COUNT=0
WARN_COUNT=0
PASS_COUNT=0

# ─── Helpers ─────────────────────────────────────────────────────────────────

_log() { $QUIET || echo -e "$1"; }

record_result() {
  local name="$1" category="$2" status="$3" detail="$4" suggestion="${5:-}"
  case "$status" in
    OK)   PASS_COUNT=$((PASS_COUNT + 1)); _log "  ${GREEN}✅${NC} ${name} ${DIM}${detail}${NC}" ;;
    WARN) WARN_COUNT=$((WARN_COUNT + 1)); _log "  ${YELLOW}⚠${NC}  ${name} ${DIM}${detail}${NC}" ;;
    FAIL) FAIL_COUNT=$((FAIL_COUNT + 1)); _log "  ${RED}❌${NC} ${name} ${DIM}${detail}${NC}" ;;
    INFO) _log "  ${CYAN}ℹ${NC}  ${name} ${DIM}${detail}${NC}" ;;
    SKIP) _log "  ${DIM}⏭  ${name} ${detail}${NC}" ;;
  esac

  if [ -n "$suggestion" ] && [ "$status" != "OK" ] && [ "$status" != "INFO" ] && [ "$status" != "SKIP" ]; then
    _log "     ${DIM}→ $suggestion${NC}"
  fi

  # JSON accumulator
  local json_entry
  json_entry=$(printf '{"name":"%s","category":"%s","status":"%s","detail":"%s","suggestion":"%s"}' \
    "$name" "$category" "$status" "$detail" "$suggestion")
  RESULTS_JSON+=("$json_entry")
}

# Detect package manager
detect_pkg_manager() {
  if command -v apt-get >/dev/null 2>&1; then echo "apt"
  elif command -v brew >/dev/null 2>&1; then echo "brew"
  elif command -v dnf >/dev/null 2>&1; then echo "dnf"
  elif command -v pacman >/dev/null 2>&1; then echo "pacman"
  else echo "unknown"
  fi
}

PKG_MGR="$(detect_pkg_manager)"

# Suggest install command for a package
suggest_install() {
  local pkg="$1"
  case "$PKG_MGR" in
    apt) echo "sudo apt-get install -y $pkg" ;;
    brew) echo "brew install $pkg" ;;
    dnf) echo "sudo dnf install -y $pkg" ;;
    pacman) echo "sudo pacman -S --noconfirm $pkg" ;;
    *) echo "Instale manualmente: $pkg" ;;
  esac
}

# Try to install a package
try_install() {
  local pkg="$1"
  if ! $TRY_INSTALL; then return 1; fi

  local sudo_cmd=""
  if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
    sudo_cmd="sudo"
  fi

  _log "     ${CYAN}→ Instalando $pkg...${NC}"
  case "$PKG_MGR" in
    apt) $sudo_cmd apt-get update -qq >/dev/null 2>&1 && $sudo_cmd apt-get install -y -qq "$pkg" >/dev/null 2>&1 ;;
    brew) brew install "$pkg" >/dev/null 2>&1 ;;
    dnf) $sudo_cmd dnf install -y -q "$pkg" >/dev/null 2>&1 ;;
    pacman) $sudo_cmd pacman -S --noconfirm "$pkg" >/dev/null 2>&1 ;;
    *) return 1 ;;
  esac
}

# Compare versions: returns 0 if $1 >= $2
version_gte() {
  local a b
  a=$(echo "$1" | tr '.' ' ')
  b=$(echo "$2" | tr '.' ' ')
  set -- $a; local a1="${1:-0}" a2="${2:-0}" a3="${3:-0}"
  set -- $b; local b1="${1:-0}" b2="${2:-0}" b3="${3:-0}"

  if [ "$a1" -gt "$b1" ] 2>/dev/null; then return 0; fi
  if [ "$a1" -lt "$b1" ] 2>/dev/null; then return 1; fi
  if [ "$a2" -gt "$b2" ] 2>/dev/null; then return 0; fi
  if [ "$a2" -lt "$b2" ] 2>/dev/null; then return 1; fi
  if [ "$a3" -ge "$b3" ] 2>/dev/null; then return 0; fi
  return 1
}

# ─── Check Functions ────────────────────────────────────────────────────────

check_binary() {
  local name="$1" criticality="$2" pkg_name="${3:-$1}" min_version="${4:-}" auto_installed="${5:-false}"

  if command -v "$name" >/dev/null 2>&1; then
    local version_str=""
    if [ -n "$min_version" ]; then
      case "$name" in
        bash) version_str="${BASH_VERSION%%(*}" ; version_str="${BASH_VERSINFO[0]}.${BASH_VERSINFO[1]}.${BASH_VERSINFO[2]}" ;;
        python3) version_str=$(python3 --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1) ;;
        hermes) version_str=$(hermes --version 2>/dev/null | grep -oP '\d{4}\.\d+\.\d+' | head -1) ;;
        node) version_str=$(node --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1) ;;
        npm) version_str=$(npm --version 2>/dev/null | head -1) ;;
        docker) version_str=$(docker --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1) ;;
        git) version_str=$(git --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1) ;;
      esac

      if [ -n "$version_str" ]; then
        if version_gte "$version_str" "$min_version"; then
          record_result "$name" "binary" "OK" "$version_str (≥$min_version)"
        else
          record_result "$name" "binary" "FAIL" "$version_str (requer ≥$min_version)" "$(suggest_install "$pkg_name")"
          return 1
        fi
      else
        record_result "$name" "binary" "OK" "presente (versão não detectada)"
      fi
    else
      record_result "$name" "binary" "OK" "$(command -v "$name")"
    fi
    return 0
  fi

  # Not found
  if [ "$auto_installed" = "true" ]; then
    record_result "$name" "binary" "SKIP" "ausente (será instalado automaticamente pelo setup)"
    return 0
  fi

  case "$criticality" in
    required)
      if $TRY_INSTALL && try_install "$pkg_name"; then
        if command -v "$name" >/dev/null 2>&1; then
          record_result "$name" "binary" "OK" "instalado agora"
          return 0
        fi
      fi
      record_result "$name" "binary" "FAIL" "não encontrado (OBRIGATÓRIO)" "$(suggest_install "$pkg_name")"
      return 1
      ;;
    recommended)
      if $TRY_INSTALL && try_install "$pkg_name"; then
        if command -v "$name" >/dev/null 2>&1; then
          record_result "$name" "binary" "OK" "instalado agora"
          return 0
        fi
      fi
      record_result "$name" "binary" "WARN" "não encontrado (recomendado)" "$(suggest_install "$pkg_name")"
      return 1
      ;;
    optional)
      record_result "$name" "binary" "INFO" "não encontrado (opcional)" "$(suggest_install "$pkg_name")"
      return 0
      ;;
  esac
}

check_python_module() {
  local module="$1" import_name="$2" criticality="$3" pip_name="${4:-$module}" auto_installed="${5:-false}"

  if ! command -v python3 >/dev/null 2>&1; then
    record_result "py:$module" "python" "FAIL" "python3 não disponível"
    return 1
  fi

  if python3 -c "import $import_name" 2>/dev/null; then
    local version=""
    version=$(python3 -c "import $import_name; print(getattr($import_name, '__version__', 'ok'))" 2>/dev/null || echo "ok")
    record_result "py:$module" "python" "OK" "$version"
    return 0
  fi

  if [ "$auto_installed" = "true" ]; then
    record_result "py:$module" "python" "SKIP" "ausente (será instalado automaticamente pelo setup)"
    return 0
  fi

  case "$criticality" in
    required)
      record_result "py:$module" "python" "FAIL" "não encontrado (OBRIGATÓRIO)" "pip3 install $pip_name"
      return 1
      ;;
    recommended)
      record_result "py:$module" "python" "WARN" "não encontrado (recomendado)" "pip3 install $pip_name"
      return 1
      ;;
    optional)
      record_result "py:$module" "python" "INFO" "não encontrado (opcional)" "pip3 install $pip_name"
      return 0
      ;;
  esac
}

check_connectivity() {
  local name="$1" url="$2"

  if ! command -v curl >/dev/null 2>&1; then
    record_result "net:$name" "network" "WARN" "curl não disponível para teste"
    return 1
  fi

  if curl -fsS --connect-timeout 5 --max-time 10 "$url" >/dev/null 2>&1; then
    record_result "net:$name" "network" "OK" "$url"
  else
    record_result "net:$name" "network" "WARN" "não acessível ($url)" "Verifique conexão de rede ou proxy"
  fi
}

check_env_var() {
  local name="$1" criticality="$2" description="$3"

  local value="${!name:-}"
  if [ -n "$value" ]; then
    # Mask sensitive values
    local display="$value"
    if echo "$name" | grep -qiE "key|token|secret|password"; then
      if [ ${#value} -gt 12 ]; then
        display="${value:0:6}...${value: -4}"
      else
        display="***"
      fi
    fi
    record_result "$name" "env" "OK" "$display"
    return 0
  fi

  case "$criticality" in
    required)
      record_result "$name" "env" "FAIL" "não definida ($description)" "export $name=<valor>"
      return 1
      ;;
    recommended)
      record_result "$name" "env" "WARN" "não definida ($description)" "export $name=<valor>"
      return 1
      ;;
    optional)
      record_result "$name" "env" "INFO" "não definida ($description)"
      return 0
      ;;
  esac
}

# ─── Main Checks ────────────────────────────────────────────────────────────

run_all_checks() {
  _log ""
  _log "${BOLD}╔═══════════════════════════════════════════════════════╗${NC}"
  _log "${BOLD}║   Exocórtex.IA — Validação de Environment           ║${NC}"
  _log "${BOLD}╚═══════════════════════════════════════════════════════╝${NC}"
  _log ""
  _log "  Package manager: ${CYAN}${PKG_MGR}${NC}"
  _log "  Modo instalação: ${CYAN}$($TRY_INSTALL && echo "ativo (--install)" || echo "desabilitado")${NC}"
  _log ""

  # ─── Binários ──────────────────────────────────────────────────────────
  _log "${BOLD}─── Binários do Sistema ───${NC}"

  # Python pkg names vary by distro
  local python_pkg="python3"
  local python_pip_pkg="python3-pip"
  case "$PKG_MGR" in
    brew) python_pkg="python@3.11" ; python_pip_pkg="" ;;
    pacman) python_pkg="python" ; python_pip_pkg="python-pip" ;;
  esac

  check_binary "bash"    "required"    "bash"     "4.0"
  check_binary "python3" "required"    "$python_pkg" "3.10"
  check_binary "git"     "required"    "git"
  check_binary "curl"    "required"    "curl"
  check_binary "rsync"   "required"    "rsync"
  check_binary "hermes"  "required"    "hermes"   "2026.4.8"
  check_binary "npm"     "recommended" "npm"
  check_binary "node"    "recommended" "nodejs"   "18.0.0"
  check_binary "pip3"    "recommended" "$python_pip_pkg"
  check_binary "jq"      "optional"   "jq"
  check_binary "docker"  "optional"   "docker.io"
  check_binary "wget"    "optional"   "wget"

  # Auto-installed by setup steps (don't flag as missing)
  check_binary "gcloud"  "optional"   "google-cloud-sdk"  ""  "true"
  check_binary "uv"      "optional"   "uv"                ""  "true"
  check_binary "nlm"     "optional"   "notebooklm-mcp-cli" "" "true"

  _log ""

  # ─── Módulos Python ───────────────────────────────────────────────────
  _log "${BOLD}─── Módulos Python ───${NC}"

  check_python_module "PyYAML"                "yaml"                    "required"    "PyYAML"
  check_python_module "google-auth-oauthlib"  "google_auth_oauthlib"    "optional"    "google-auth-oauthlib"  "true"
  check_python_module "google-api-python-client" "googleapiclient"      "optional"    "google-api-python-client" "true"
  check_python_module "google-auth-httplib2"  "google_auth_httplib2"    "optional"    "google-auth-httplib2"  "true"
  check_python_module "python-pptx"           "pptx"                    "optional"    "python-pptx"

  _log ""

  # ─── Conectividade ────────────────────────────────────────────────────
  _log "${BOLD}─── Conectividade de Rede ───${NC}"

  check_connectivity "GitHub"   "https://github.com"
  check_connectivity "PyPI"     "https://pypi.org/simple/"
  check_connectivity "astral.sh" "https://astral.sh"

  _log ""

  # ─── Variáveis de Ambiente ────────────────────────────────────────────
  _log "${BOLD}─── Variáveis de Ambiente ───${NC}"

  check_env_var "HERMES_HOME"          "optional"    "Diretório Hermes (default: ~/.hermes)"
  check_env_var "EXOCORTEX_HOME"       "optional"    "Diretório Exocórtex (default: ~/exocortex)"
  check_env_var "OPENROUTER_API_KEY"   "recommended" "Chave OpenRouter (LLM routing)"
  check_env_var "TELEGRAM_BOT_TOKEN"   "recommended" "Token Telegram Bot"
  check_env_var "CONTEXT7_API_KEY"     "optional"    "Chave Context7 (docs tech stacks)"
  check_env_var "FIRECRAWL_API_KEY"    "optional"    "Chave Firecrawl (crawling/extract)"
  check_env_var "DOCBRAIN_LLM_API_KEY" "optional"    "Override LLM key para DocBrain"
  check_env_var "HINDSIGHT_API_KEY"    "optional"    "Chave Hindsight cloud"
  check_env_var "DEEPSEEK_API_KEY"     "optional"    "Chave DeepSeek (fallback Hindsight)"
  check_env_var "GOOGLE_APPLICATION_CREDENTIALS" "optional" "Path para service account JSON"

  _log ""

  # ─── Paths do projeto ────────────────────────────────────────────────
  _log "${BOLD}─── Paths do Projeto ───${NC}"

  local hermes_home="${HERMES_HOME:-$HOME/.hermes}"
  local exocortex_home="${EXOCORTEX_HOME:-$HOME/exocortex}"

  if [ -d "$hermes_home" ]; then
    record_result "HERMES_HOME" "path" "OK" "$hermes_home"
  else
    record_result "HERMES_HOME" "path" "INFO" "$hermes_home (será criado pelo setup)"
  fi

  if [ -d "$hermes_home/skills" ]; then
    record_result "HERMES_HOME/skills" "path" "OK" "diretório de skills presente"
  else
    record_result "HERMES_HOME/skills" "path" "INFO" "ausente (será criado pelo setup)"
  fi

  if [ -d "$hermes_home/memories" ]; then
    record_result "HERMES_HOME/memories" "path" "OK" "diretório de memórias presente"
  else
    record_result "HERMES_HOME/memories" "path" "INFO" "ausente (será criado pelo setup)"
  fi

  if [ -d "$exocortex_home" ]; then
    record_result "EXOCORTEX_HOME" "path" "OK" "$exocortex_home"
  else
    record_result "EXOCORTEX_HOME" "path" "INFO" "$exocortex_home (será criado pelo setup)"
  fi

  _log ""
}

# ─── JSON Output ─────────────────────────────────────────────────────────────

emit_json() {
  echo "{"
  echo "  \"timestamp\": \"$(date -Iseconds)\","
  echo "  \"package_manager\": \"$PKG_MGR\","
  echo "  \"summary\": {"
  echo "    \"pass\": $PASS_COUNT,"
  echo "    \"warn\": $WARN_COUNT,"
  echo "    \"fail\": $FAIL_COUNT"
  echo "  },"
  echo "  \"results\": ["
  local first=true
  for entry in "${RESULTS_JSON[@]}"; do
    if $first; then first=false; else echo ","; fi
    echo -n "    $entry"
  done
  echo ""
  echo "  ]"
  echo "}"
}

# ─── Summary ────────────────────────────────────────────────────────────────

print_summary() {
  _log "${BOLD}═══ Resumo ═══${NC}"
  _log "  ${GREEN}✅ Pass: $PASS_COUNT${NC}  |  ${YELLOW}⚠ Warn: $WARN_COUNT${NC}  |  ${RED}❌ Fail: $FAIL_COUNT${NC}"
  _log ""

  if [ $FAIL_COUNT -gt 0 ]; then
    _log "${RED}${BOLD}⛔ Existem $FAIL_COUNT dependência(s) obrigatória(s) faltando.${NC}"
    _log "${RED}   O setup pode falhar. Corrija os itens ❌ acima antes de prosseguir.${NC}"
    if ! $TRY_INSTALL; then
      _log ""
      _log "  ${DIM}Dica: execute com --install para tentar instalar automaticamente:${NC}"
      _log "  ${CYAN}bash scripts/validate-environment.sh --install${NC}"
    fi
  elif [ $WARN_COUNT -gt 0 ]; then
    _log "${YELLOW}⚠ Existem $WARN_COUNT dependência(s) recomendada(s) faltando.${NC}"
    _log "${YELLOW}  O setup pode prosseguir, mas algumas features serão limitadas.${NC}"
  else
    _log "${GREEN}✅ Todos os pré-requisitos atendidos. Pronto para o setup.${NC}"
  fi
  _log ""
}

# ─── Main ────────────────────────────────────────────────────────────────────

run_all_checks

if $OUTPUT_JSON; then
  emit_json
else
  print_summary
fi

# Exit code
if [ $FAIL_COUNT -gt 0 ]; then
  exit 1
elif [ $WARN_COUNT -gt 0 ]; then
  exit 2
else
  exit 0
fi
