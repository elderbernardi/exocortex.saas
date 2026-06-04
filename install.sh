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
BOLD='\033[1m'
NC='\033[0m'

log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

# ─── Configuration ───────────────────────────────────────────────────────────
REPO_URL="https://github.com/elderbernardi/exocortex.saas.git"
REPO_API="https://api.github.com/repos/elderbernardi/exocortex.saas"
HERMES_INSTALLER="https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh"
INSTALLER_DIR="${EXOCORTEX_INSTALLER_DIR:-$HOME/.exocortex-installer}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"

# ─── Banner ──────────────────────────────────────────────────────────────────
echo ''
echo -e "${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║${NC}   ${CYAN}Exocórtex.IA${NC} — Instalador                              ${BOLD}║${NC}"
echo -e "${BOLD}║${NC}   Exoesqueleto para o pensamento                          ${BOLD}║${NC}"
echo -e "${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ''

# ─── Step 1: Detect OS ──────────────────────────────────────────────────────
OS="$(uname -s)"
case "$OS" in
  Linux*)  OS_NAME="Linux" ;;
  Darwin*) OS_NAME="macOS" ;;
  *)       fail "Sistema operacional não suportado: $OS" ;;
esac
info "Sistema: $OS_NAME ($(uname -m))"

# ─── Step 2: Check and install dependencies ─────────────────────────────────
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

  info "Instalando: ${pkgs[*]}..."
  case "$PKG_MGR" in
    apt)
      $SUDO apt-get update -qq >/dev/null 2>&1
      $SUDO apt-get install -y -qq "${pkgs[@]}" >/dev/null 2>&1
      ;;
    brew)
      brew install "${pkgs[@]}" >/dev/null 2>&1
      ;;
    dnf)
      $SUDO dnf install -y -q "${pkgs[@]}" >/dev/null 2>&1
      ;;
    pacman)
      $SUDO pacman -S --noconfirm "${pkgs[@]}" >/dev/null 2>&1
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
if command -v hermes >/dev/null 2>&1; then
  HERMES_VERSION=$(hermes --version 2>/dev/null | head -1)
  log "Hermes já instalado: $HERMES_VERSION"
else
  echo ''
  info "Hermes Agent não encontrado. Instalando..."
  info "Fonte: github.com/NousResearch/hermes-agent"
  echo ''

  if curl -fsSL "$HERMES_INSTALLER" | bash; then
    # Reload PATH (Hermes installer adds to ~/.local/bin)
    export PATH="$HOME/.local/bin:$PATH"

    if command -v hermes >/dev/null 2>&1; then
      HERMES_VERSION=$(hermes --version 2>/dev/null | head -1)
      log "Hermes instalado: $HERMES_VERSION"
    else
      fail "Hermes instalado mas 'hermes' não encontrado no PATH.
  Adicione ao PATH: export PATH=\"\$HOME/.local/bin:\$PATH\"
  E re-execute este instalador."
    fi
  else
    fail "Falha ao instalar Hermes. Verifique sua conexão e tente novamente."
  fi
fi

# ─── Step 4: Resolve version ────────────────────────────────────────────────
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
echo ''
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

  if git clone --depth 1 --branch "$INSTALL_VERSION" "$REPO_URL" "$INSTALLER_DIR" 2>/dev/null; then
    echo "$INSTALL_VERSION" > "$VERSION_FILE"
    log "Download completo"
  else
    # Fallback: try without --branch (might be a commit hash or branch name issue)
    if git clone --depth 1 "$REPO_URL" "$INSTALLER_DIR" 2>/dev/null; then
      cd "$INSTALLER_DIR"
      git fetch --depth 1 origin "refs/tags/$INSTALL_VERSION:refs/tags/$INSTALL_VERSION" 2>/dev/null || true
      git checkout "$INSTALL_VERSION" 2>/dev/null || warn "Tag $INSTALL_VERSION não encontrada; usando main"
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
echo ''
info "Executando setup..."
echo ''

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

HERMES_HOME="$HERMES_HOME" \
EXOCORTEX_HOME="$EXOCORTEX_HOME" \
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}" \
bash setup.sh

# ─── Step 7: Success banner ─────────────────────────────────────────────────
echo ''
echo -e "${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║${NC}   ${GREEN}✅ Exocórtex.IA instalado com sucesso!${NC}                  ${BOLD}║${NC}"
echo -e "${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ''
echo -e "  Versão:    ${CYAN}$INSTALL_VERSION${NC}"
echo -e "  Hermes:    ${CYAN}$(hermes --version 2>/dev/null | head -1 || echo 'ver PATH')${NC}"
echo -e "  Skills:    ${CYAN}$(find "$HERMES_HOME/skills/exocortex" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')${NC}"
echo -e "  Runtime:   ${CYAN}$HERMES_HOME${NC}"
echo -e "  Workspace: ${CYAN}$EXOCORTEX_HOME${NC}"
echo -e "  Installer: ${CYAN}$INSTALLER_DIR${NC}"
echo ''
echo -e "  ${BOLD}Próximos passos:${NC}"
echo -e "    ${GREEN}hermes${NC}                          # iniciar sessão interativa"
echo -e "    ${GREEN}hermes -p manut${NC}                 # modo manutenção"
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
