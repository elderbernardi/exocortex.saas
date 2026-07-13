#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Bootstrap Installer
# =============================================================================
# Instala Hermes Agent (se necessário) e o Exocórtex.IA com um comando:
#
#   curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh | bash
#
# Com Telegram:
#   TELEGRAM_BOT_TOKEN="seu_token" curl -fsSL ... | bash
#
# Versão específica:
#   VERSION=v1.0.0-rc2 curl -fsSL ... | bash
#
# Ref: https://github.com/elderbernardi/exocortex.saas
# =============================================================================

set -euo pipefail

# ─── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
HERMES='\033[1;38;5;229m'
BOLD='\033[1m'
NC='\033[0m'
log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

has_setup_flag() {
  local expected="$1"
  local flag
  for flag in "${SETUP_FLAGS[@]}"; do
    if [ "$flag" = "$expected" ]; then
      return 0
    fi
  done
  return 1
}

mask_secret() {
  local value="$1"
  if [ -z "$value" ]; then
    echo "(vazio)"
    return
  fi

  local len=${#value}
  if [ "$len" -le 8 ]; then
    echo "****"
  elif [ "$len" -le 16 ]; then
    echo "${value:0:4}...${value: -4}"
  else
    echo "${value:0:6}...${value: -4}"
  fi
}

sanitize_text() {
  local text="$1"
  local secret_name secret_value masked_value
  for secret_name in EXOCORTEX_DEFAULT_API_KEY EXOCORTEX_VISION_API_KEY EXOCORTEX_AUX_API_KEY TELEGRAM_BOT_TOKEN CONTEXT7_API_KEY FIRECRAWL_API_KEY HINDSIGHT_API_KEY OPENROUTER_API_KEY DEEPSEEK_API_KEY DOCBRAIN_LLM_API_KEY; do
    secret_value="${!secret_name:-}"
    if [ -n "$secret_value" ]; then
      masked_value=$(mask_secret "$secret_value")
      text="${text//$secret_value/$masked_value}"
    fi
  done
  printf '%s' "$text"
}

print_sanitized_tail() {
  local file="$1"
  local max_lines="${2:-18}"

  if [ ! -s "$file" ]; then
    info "O comando falhou sem stderr capturado."
    return
  fi

  local -a lines=()
  mapfile -t lines < "$file"

  local total=${#lines[@]}
  local start=0
  if [ "$total" -gt "$max_lines" ]; then
    start=$((total - max_lines))
  fi

  local i
  for ((i=start; i<total; i++)); do
    printf '      %s\n' "$(sanitize_text "${lines[$i]}")"
  done
}

run_command_with_context() {
  local stage="$1"
  local hint="$2"
  shift 2

  local log_file
  log_file=$(mktemp)

  if "$@" >"$log_file" 2>&1; then
    rm -f "$log_file"
    return 0
  else
    local exit_code=$?
    echo ''
    warn "Falha na etapa: $stage (exit $exit_code)"
    if [ -n "$hint" ]; then
      info "$hint"
    fi
    info "Comando: $(sanitize_text "$*")"
    info "Últimas linhas úteis:"
    print_sanitized_tail "$log_file"
    rm -f "$log_file"
    return "$exit_code"
  fi
}

run_shell_with_context() {
  local stage="$1"
  local hint="$2"
  local command="$3"
  local log_file
  log_file=$(mktemp)

  if bash -o pipefail -c "$command" >"$log_file" 2>&1; then
    rm -f "$log_file"
    return 0
  else
    local exit_code=$?
    echo ''
    warn "Falha na etapa: $stage (exit $exit_code)"
    if [ -n "$hint" ]; then
      info "$hint"
    fi
    info "Comando: $(sanitize_text "$command")"
    info "Últimas linhas úteis:"
    print_sanitized_tail "$log_file"
    rm -f "$log_file"
    return "$exit_code"
  fi
}

show_stage() {
  local number="$1"
  local title="$2"
  echo ''
  echo -e "${BOLD}→ Etapa ${number}: ${title}${NC}"
}

show_mode_narrative() {
  if has_setup_flag "--yes" || has_setup_flag "-y"; then
    info "Modo headless (--yes): sem prompts; vou narrar o progresso, persistir os valores atuais e seguir direto para o setup."
    return
  fi

  if has_setup_flag "--step-by-step" || has_setup_flag "--guided"; then
    info "Modo guiado (--step-by-step): depois do bootstrap, o setup vai parar em cada bloco para revisão explícita."
    return
  fi

  info "Modo padrão: vou narrar cada etapa, mostrar o que foi detectado sem expor segredos e abrir o setup com confirmação final antes do provisionamento completo."
}

print_env_preflight_row() {
  local name="$1"
  local description="$2"
  local value="${!name:-}"
  local display="(ausente)"

  if [ -n "$value" ]; then
    display=$(mask_secret "$value")
  fi

  printf '  - %-22s %s — %s\n' "$name" "$display" "$description"
}

warn_if_secret_suspicious() {
  local name="$1"
  local hint="$2"
  local value="${!name:-}"

  if [ -z "$value" ]; then
    return
  fi

  if printf '%s' "$value" | grep -q '[[:space:]]'; then
    warn "$name contém espaço ou quebra de linha. Isso costuma indicar cópia parcial ou colagem com caracteres extras. $hint"
    return
  fi

  if [ ${#value} -lt 12 ]; then
    warn "$name parece curta demais para uma credencial completa. $hint"
  fi
}

show_env_preflight() {
  local firecrawl_url="${FIRECRAWL_BASE_URL:-http://127.0.0.1:3002}"

  show_stage "3/7" "Preflight do bootstrap Hermes"
  show_mode_narrative
  info "Paths-alvo desta instalação:"
  printf '  - HERMES_HOME          %s\n' "$HERMES_HOME"
  printf '  - EXOCORTEX_HOME       %s\n' "$EXOCORTEX_HOME"
  printf '  - INSTALLER_DIR        %s\n' "$INSTALLER_DIR"
  echo ''
  info "Env vars detectadas antes do Hermes (mascaradas quando sensíveis):"
  info "  Provedores LLM (3 papéis — default obrigatório; vision/aux herdam default):"
  print_env_preflight_row "EXOCORTEX_DEFAULT_PROVIDER" "provider do papel default"
  print_env_preflight_row "EXOCORTEX_DEFAULT_MODEL" "modelo do papel default"
  print_env_preflight_row "EXOCORTEX_DEFAULT_API_KEY" "chave do papel default (obrigatória)"
  print_env_preflight_row "EXOCORTEX_VISION_API_KEY" "chave do papel vision (opcional)"
  print_env_preflight_row "EXOCORTEX_AUX_API_KEY" "chave do papel auxiliar — DocBrain/Hindsight (opcional)"
  info "  Serviços (não-LLM):"
  print_env_preflight_row "TELEGRAM_BOT_TOKEN" "gateway Telegram opcional"
  print_env_preflight_row "FIRECRAWL_API_KEY" "crawling/extract opcional"
  print_env_preflight_row "CONTEXT7_API_KEY" "docs técnicos opcionais"
  printf '  - %-26s %s — endpoint esperado para Firecrawl local\n' "FIRECRAWL_BASE_URL" "$firecrawl_url"
  echo ''

  warn_if_secret_suspicious "EXOCORTEX_DEFAULT_API_KEY" "Se a chave veio por copy/paste, revise antes do setup."
  warn_if_secret_suspicious "TELEGRAM_BOT_TOKEN" "Tokens do BotFather normalmente têm formato numérico + dois pontos + segredo."

  if [ -z "${EXOCORTEX_DEFAULT_API_KEY:-}" ]; then
    warn "Papel LLM 'default' não detectado (EXOCORTEX_DEFAULT_API_KEY). O setup vai migrar chaves legadas e/ou perguntar. Sem ele, o reasoning remoto sobe sem rota pronta."
  fi

  if [ -z "${FIRECRAWL_API_KEY:-}" ]; then
    info "Firecrawl é opcional. Se você subir uma instância local, o default esperado aqui é $firecrawl_url."
  fi
}

# ─── Configuration ───────────────────────────────────────────────────────────
REPO_URL="${EXOCORTEX_REPO_URL:-https://github.com/elderbernardi/exocortex.saas.git}"
REPO_API="${EXOCORTEX_REPO_API:-https://api.github.com/repos/elderbernardi/exocortex.saas}"
HERMES_INSTALLER="${EXOCORTEX_HERMES_INSTALLER:-https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh}"
INSTALLER_DIR="${EXOCORTEX_INSTALLER_DIR:-$HOME/.exocortex-installer}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"
SETUP_FLAGS=()

print_help() {
  cat <<EOF
Uso: bash install.sh [opções]

Opções:
  --yes, -y         Executa setup sem prompts
  --step-by-step    Força revisão guiada de paths, env vars e API keys
  --init-only       Salva configuração e não executa os steps
  --skip-env-check  Pula validação de pré-requisitos do setup
  --imbroke         Ativa contingência OpenRouter free
  --calibrate       Executa calibração cognitiva ao final
  -h, --help        Mostra esta ajuda

Exemplos:
  curl -fsSL <url>/install.sh | bash
  curl -fsSL <url>/install.sh | bash -s -- --step-by-step
  curl -fsSL <url>/install.sh | TELEGRAM_BOT_TOKEN="..." bash -s -- --yes
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --yes|-y|--step-by-step|--guided|--init-only|--skip-env-check|--imbroke|--calibrate)
      SETUP_FLAGS+=("$1")
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
    *)
      fail "Flag não suportada: $1"
      ;;
  esac
  shift
done

run_setup_script() {
  local requires_tty=1
  local flag
  for flag in "${SETUP_FLAGS[@]}"; do
    case "$flag" in
      --yes|-y)
        requires_tty=0
        ;;
    esac
  done

  if [ "$requires_tty" -eq 0 ]; then
    HERMES_HOME="$HERMES_HOME" \
    EXOCORTEX_HOME="$EXOCORTEX_HOME" \
    TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}" \
    bash setup.sh "${SETUP_FLAGS[@]}"
    return $?
  fi

  if [ -t 0 ]; then
    HERMES_HOME="$HERMES_HOME" \
    EXOCORTEX_HOME="$EXOCORTEX_HOME" \
    TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}" \
    bash setup.sh "${SETUP_FLAGS[@]}"
    return $?
  fi

  if [ -r /dev/tty ]; then
    info "stdin do bootstrap não é interativo; conectando prompts ao terminal atual (/dev/tty)..."
    HERMES_HOME="$HERMES_HOME" \
    EXOCORTEX_HOME="$EXOCORTEX_HOME" \
    TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}" \
    bash setup.sh "${SETUP_FLAGS[@]}" < /dev/tty
    return $?
  fi

  fail "Setup interativo requer um terminal. Reexecute em um TTY ou rode manualmente: HERMES_HOME=\"$HERMES_HOME\" EXOCORTEX_HOME=\"$EXOCORTEX_HOME\" bash $INSTALLER_DIR/setup.sh --yes"
}

# ─── Banner ──────────────────────────────────────────────────────────────────
echo ''
echo -e "${CYAN}    ███████╗██╗  ██╗ ██████╗██████╗ ████████╗██╗  ██╗   ██╗ █████╗ ${NC}"
echo -e "${CYAN}    ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗╚══██╔══╝╚██╗██╔╝   ██║██╔══██╗${NC}"
echo -e "${CYAN}    █████╗   ╚███╔╝ ██║     ██████╔╝   ██║    ╚███╔╝    ██║███████║${NC}"
echo -e "${CYAN}    ██╔══╝   ██╔██╗ ██║     ██╔══██╗   ██║    ██╔██╗    ██║██╔══██║${NC}"
echo -e "${CYAN}    ███████╗██╔╝ ██╗╚██████╗██║  ██║   ██║   ██╔╝ ██╗   ██║██║  ██║${NC}"
echo -e "${CYAN}    ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝╚═╝  ╚═╝${NC}"
echo ''
echo -e "                   ${CYAN}c o g n i ç ã o   e s t e n d i d a${NC}"
echo -e "                  ${HERMES}◆  Hermes Agent  ◆${NC}"
echo -e "                         ${BOLD}Instalador${NC}"
echo ''

# ─── Step 1: Detect OS ──────────────────────────────────────────────────────
show_mode_narrative
show_stage "1/7" "Detectando sistema operacional"
OS="$(uname -s)"
case "$OS" in
  Linux*)  OS_NAME="Linux" ;;
  Darwin*) OS_NAME="macOS" ;;
  *)       fail "Sistema operacional não suportado: $OS" ;;
esac
info "Sistema: $OS_NAME ($(uname -m))"

# ─── Step 2: Check and install dependencies ─────────────────────────────────
show_stage "2/7" "Verificando dependências locais"
info "Verificando dependências..."

# Detect package manager
PKG_MGR=""
if command -v apt-get >/dev/null 2>&1; then
  PKG_MGR="apt"
elif command -v brew >/dev/null 2>&1; then
  PKG_MGR="brew"
elif command -v dnf >/dev/null 2>&1; then
  PKG_MGR="dnf"
elif command -v pacman >/dev/null 2>&1; then
  PKG_MGR="pacman"
fi

# sudo helper: use sudo only if not root
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  fi
fi

install_packages() {
  local pkgs=("$@")
  if [ ${#pkgs[@]} -eq 0 ]; then return 0; fi

  info "Dependências ausentes: ${pkgs[*]}"
  info "Gerenciador detectado: ${PKG_MGR:-desconhecido}"
  case "$PKG_MGR" in
    apt)
      run_command_with_context "Instalação de dependências" "Falha ao preparar dependências com apt. Se o erro persistir, execute os comandos manualmente e rode o instalador de novo." $SUDO apt-get update -qq || return $?
      run_command_with_context "Instalação de dependências" "Falha ao instalar dependências com apt. Verifique permissões sudo, lock do apt ou conectividade." $SUDO apt-get install -y -qq "${pkgs[@]}" || return $?
      ;;
    brew)
      run_command_with_context "Instalação de dependências" "Falha ao instalar dependências com Homebrew. Revise o stderr sanitizado abaixo." brew install "${pkgs[@]}" || return $?
      ;;
    dnf)
      run_command_with_context "Instalação de dependências" "Falha ao instalar dependências com dnf. Revise o stderr sanitizado abaixo." $SUDO dnf install -y -q "${pkgs[@]}" || return $?
      ;;
    pacman)
      run_command_with_context "Instalação de dependências" "Falha ao instalar dependências com pacman. Revise o stderr sanitizado abaixo." $SUDO pacman -S --noconfirm "${pkgs[@]}" || return $?
      ;;
    *)
      fail "Gerenciador de pacotes não detectado. Instale manualmente: ${pkgs[*]}"
      ;;
  esac
}

# Check core deps
MISSING_DEPS=()
for cmd in git curl rsync; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    MISSING_DEPS+=("$cmd")
  fi
done

# Check Python 3
PYTHON_PKGS=()
if ! command -v python3 >/dev/null 2>&1; then
  case "$PKG_MGR" in
    apt) PYTHON_PKGS=(python3 python3-pip python3-venv) ;;
    brew) PYTHON_PKGS=(python@3.11) ;;
    dnf) PYTHON_PKGS=(python3 python3-pip) ;;
    pacman) PYTHON_PKGS=(python python-pip) ;;
  esac
fi

# Install if anything is missing
if [ ${#MISSING_DEPS[@]} -gt 0 ] || [ ${#PYTHON_PKGS[@]} -gt 0 ]; then
  ALL_PKGS=("${MISSING_DEPS[@]}" "${PYTHON_PKGS[@]}")
  install_packages "${ALL_PKGS[@]}"

  # Verify after install
  for cmd in git curl rsync python3; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      fail "$cmd não encontrado após instalação. Instale manualmente."
    fi
  done
fi

log "Dependências OK (git, curl, rsync, python3)"

# ─── Step 3: Install Hermes (if not present) ────────────────────────────────
show_env_preflight

show_stage "4/7" "Instalando ou validando Hermes"
if command -v hermes >/dev/null 2>&1; then
  HERMES_VERSION=$(hermes --version 2>/dev/null | sed -n '1p')
  log "Hermes já instalado: $HERMES_VERSION"
  info "Binário detectado em: $(command -v hermes)"
else
  echo ''
  info "Hermes Agent não encontrado. Instalando..."
  info "Fonte: github.com/NousResearch/hermes-agent"
  info "Instalador remoto: $HERMES_INSTALLER"
  echo ''

  if run_shell_with_context "Bootstrap Hermes" "Falha ao executar o instalador do Hermes. Revise URL, conectividade e permissões de escrita em ~/.local/bin." "curl -fsSL \"$HERMES_INSTALLER\" | bash"; then
    # Reload PATH (Hermes installer adds to ~/.local/bin)
    export PATH="$HOME/.local/bin:$PATH"
    info "Validando 'hermes' no PATH após o bootstrap..."

    if command -v hermes >/dev/null 2>&1; then
      HERMES_VERSION=$(hermes --version 2>/dev/null | sed -n '1p')
      log "Hermes instalado: $HERMES_VERSION"
    else
      fail "Hermes instalado mas 'hermes' não encontrado no PATH.
  Adicione ao PATH: export PATH=\"\$HOME/.local/bin:\$PATH\"
  E re-execute este instalador."
    fi
  else
    fail "Falha ao instalar Hermes. Contexto acima; URL do instalador: $HERMES_INSTALLER"
  fi
fi

# ─── Step 4: Resolve version ────────────────────────────────────────────────
show_stage "5/7" "Resolvendo versão do Exocórtex"
if [ -n "${VERSION:-}" ]; then
  INSTALL_VERSION="$VERSION"
  info "Versão solicitada: $INSTALL_VERSION"
else
  info "Consultando versão mais recente..."

  # Try GitHub API for latest tag
  if command -v jq >/dev/null 2>&1; then
    INSTALL_VERSION=$(curl -fsSL "${REPO_API}/tags" 2>/dev/null | jq -r '.[0].name // empty' 2>/dev/null || true)
  else
    # Fallback without jq: parse JSON with grep/sed
    INSTALL_VERSION=$(curl -fsSL "${REPO_API}/tags" 2>/dev/null | grep -m1 '"name"' | sed 's/.*"name": *"\([^"]*\)".*/\1/' || true)
  fi

  if [ -z "$INSTALL_VERSION" ]; then
    warn "Não foi possível determinar a tag mais recente. Usando 'release-candidate'."
    INSTALL_VERSION="release-candidate"
  fi

  info "Versão: $INSTALL_VERSION"
fi

# ─── Step 5: Download/update installer ───────────────────────────────────────
show_stage "6/7" "Baixando ou atualizando o instalador Exocórtex"
info "Diretório do instalador: $INSTALLER_DIR"

VERSION_FILE="$INSTALLER_DIR/.exocortex-version"
NEEDS_DOWNLOAD=true

if [ -d "$INSTALLER_DIR/.git" ]; then
  CURRENT_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "unknown")
  if [ "$CURRENT_VERSION" = "$INSTALL_VERSION" ]; then
    info "Versão $INSTALL_VERSION já baixada. Re-executando setup..."
    NEEDS_DOWNLOAD=false
  else
    info "Atualizando de $CURRENT_VERSION para $INSTALL_VERSION..."
    rm -rf "$INSTALLER_DIR"
  fi
fi

if $NEEDS_DOWNLOAD; then
  info "Baixando Exocórtex.IA ($INSTALL_VERSION)..."

  if run_command_with_context "Clone do Exocórtex" "Falha ao clonar a versão solicitada. Vou tentar um fallback sem --branch." git clone --depth 1 --branch "$INSTALL_VERSION" "$REPO_URL" "$INSTALLER_DIR"; then
    echo "$INSTALL_VERSION" > "$VERSION_FILE"
    log "Download completo"
  else
    # Fallback: try without --branch (might be a commit hash or branch name issue)
    if run_command_with_context "Clone do Exocórtex (fallback)" "Falha ao clonar o repositório mesmo sem fixar a branch/tag. Revise URL, tag e conectividade." git clone --depth 1 "$REPO_URL" "$INSTALLER_DIR"; then
      cd "$INSTALLER_DIR"
      run_command_with_context "Fetch da tag solicitada" "Não consegui buscar a tag pedida; se ela não existir, sigo com o checkout disponível." git fetch --depth 1 origin "refs/tags/$INSTALL_VERSION:refs/tags/$INSTALL_VERSION" || true
      if run_command_with_context "Checkout da versão solicitada" "Tag ou branch não encontrada localmente; vou manter a revisão padrão do clone fallback." git checkout "$INSTALL_VERSION"; then
        :
      else
        warn "Tag $INSTALL_VERSION não encontrada; usando a revisão padrão do clone fallback."
      fi
      echo "$INSTALL_VERSION" > "$VERSION_FILE"
      log "Download completo (fallback)"
    else
      fail "Falha ao clonar repositório. Verifique sua conexão:
  URL: $REPO_URL
  Tag: $INSTALL_VERSION"
    fi
  fi
fi

# ─── Step 6: Run setup.sh ───────────────────────────────────────────────────
show_stage "7/7" "Executando setup do Exocórtex"
info "Executando setup (revisão final + provisionamento)."

cd "$INSTALLER_DIR"

# Locate setup.sh — could be at root (release-candidate) or in plans/pdd_v2/artifacts/
if [ -f "setup.sh" ]; then
  SETUP_PATH="."
elif [ -f "plans/pdd_v2/artifacts/setup.sh" ]; then
  SETUP_PATH="plans/pdd_v2/artifacts"
else
  fail "setup.sh não encontrado no instalador. Versão corrompida?"
fi

cd "$SETUP_PATH"

if run_setup_script; then
  :
else
  setup_exit=$?
  case "$setup_exit" in
    130)
      warn "Instalação interrompida antes do provisionamento completo."
      info "Nenhum banner de sucesso será exibido para setup cancelado/interrompido."
      exit 130
      ;;
    *)
      fail "Setup falhou (exit $setup_exit). Revise a saída acima."
      ;;
  esac
fi

# ─── Step 7: Success banner ─────────────────────────────────────────────────
echo ''
echo -e "${GREEN}    ███████╗██╗  ██╗ ██████╗██████╗ ████████╗██╗  ██╗   ██╗ █████╗ ${NC}"
echo -e "${GREEN}    ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗╚══██╔══╝╚██╗██╔╝   ██║██╔══██╗${NC}"
echo -e "${GREEN}    █████╗   ╚███╔╝ ██║     ██████╔╝   ██║    ╚███╔╝    ██║███████║${NC}"
echo -e "${GREEN}    ██╔══╝   ██╔██╗ ██║     ██╔══██╗   ██║    ██╔██╗    ██║██╔══██║${NC}"
echo -e "${GREEN}    ███████╗██╔╝ ██╗╚██████╗██║  ██║   ██║   ██╔╝ ██╗   ██║██║  ██║${NC}"
echo -e "${GREEN}    ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝╚═╝  ╚═╝${NC}"
echo ''
echo -e "  ${BOLD}${GREEN}✅ Exocórtex.IA instalado com sucesso!${NC}"
echo ''
echo -e "  Versão:    ${CYAN}$INSTALL_VERSION${NC}"
echo -e "  Hermes:    ${CYAN}$(hermes --version 2>/dev/null | sed -n '1p' || echo 'ver PATH')${NC}"
echo -e "  Skills:    ${CYAN}$(find "$HERMES_HOME/skills/excrtx" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')${NC}"
echo -e "  Runtime:   ${CYAN}$HERMES_HOME${NC}"
echo -e "  Workspace: ${CYAN}$EXOCORTEX_HOME${NC}"
echo -e "  Installer: ${CYAN}$INSTALLER_DIR${NC}"
echo ''
echo -e "  ${BOLD}Próximos passos:${NC}"
echo -e "    ${GREEN}hermes${NC}                          # iniciar sessão interativa"
echo -e "    ${GREEN}hermes -p manut${NC}                 # modo manutenção"
echo -e "    ${GREEN}hermes -p chat${NC}                  # modo chat (sem harness)"
echo ''

# Telegram status
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  echo -e "    ${GREEN}✓${NC} Telegram configurado"
else
  echo -e "    ${YELLOW}Telegram:${NC} Para configurar, re-execute com:"
  echo -e "    ${CYAN}TELEGRAM_BOT_TOKEN=\"seu_token\" bash $INSTALLER_DIR/install.sh${NC}"
fi

# Google status
if [ -f "$HERMES_HOME/reminders/google-credentials.md" ]; then
  echo -e "    ${YELLOW}Google:${NC}   gcloud auth application-default login"
fi

echo ''
echo -e "  ${BOLD}Re-run / atualizar:${NC}"
echo -e "    ${CYAN}bash $INSTALLER_DIR/install.sh${NC}"
echo -e "    ${CYAN}VERSION=<tag> bash $INSTALLER_DIR/install.sh${NC}"
echo ''
