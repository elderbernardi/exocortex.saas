#!/usr/bin/env bash
# =============================================================================
#  ╔═══════════════════════════════════════════════════════════════╗
#  ║              Exocórtex.IA — Installer v2.0.0                 ║
#  ║                                                               ║
#  ║  curl -fsSL https://exocortex.sh | bash                       ║
#  ║  ── ou ──                                                     ║
#  ║  bash <(curl -fsSL https://raw.githubusercontent.com/         ║
#  ║    elderbernardi/exocortex.saas/main/install-exocortex.sh)    ║
#  ╚═══════════════════════════════════════════════════════════════╝
# =============================================================================
set -euo pipefail

# ─── Config ─────────────────────────────────────────────────────────────────
REPO="elderbernardi/exocortex.saas"
BRANCH="main"
TARBALL_URL="https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz"
PROVISIONER_REL="plans/pdd_v2/provisioner"

if [ -d "$PWD/$PROVISIONER_REL" ]; then
  INSTALL_DIR="$PWD/$PROVISIONER_REL"
  LOCAL_REPO=true
else
  INSTALL_DIR="${EXOCORTEX_DIR:-$PWD/.exocortex-provisioner}"
  LOCAL_REPO=false
fi

# ─── Colors ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; }
step() { echo -e "\n${BOLD}▸ $1${NC}"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }

# ─── Banner ─────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  ╔═══════════════════════════════════════╗${NC}"
echo -e "${BOLD}  ║${NC}   ${CYAN}Exocórtex.IA${NC} — Provisioner v2.0.0   ${BOLD}║${NC}"
echo -e "${BOLD}  ╚═══════════════════════════════════════╝${NC}"
echo ""

# ─── Step 1: Check prerequisites ───────────────────────────────────────────
step "Verificando pré-requisitos..."

MISSING=()
command -v curl &>/dev/null || MISSING+=("curl")
command -v tar  &>/dev/null || MISSING+=("tar")

if [ ${#MISSING[@]} -gt 0 ]; then
  fail "Faltam dependências: ${MISSING[*]}"
  echo "  Instale com: sudo apt install ${MISSING[*]}"
  exit 1
fi
log "curl e tar disponíveis"

# Check Python
if command -v python3 &>/dev/null; then
  PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
  log "Python $PY_VERSION"
else
  warn "Python 3 não encontrado — necessário para o Hermes Agent"
fi

# ─── Step 2: Detect agent CLI ──────────────────────────────────────────────
step "Detectando agente CLI..."

AGENT_CMD=""
AGENT_NAME=""

# Priority order: hermes > codex > gemini > claude > aider
if command -v hermes &>/dev/null; then
  AGENT_CMD="hermes"
  AGENT_NAME="Hermes Agent"
  HERMES_VERSION=$(hermes --version 2>/dev/null | head -1 | grep -oP 'v[\d.]+' || echo "unknown")
  log "Hermes Agent ($HERMES_VERSION) detectado"
elif command -v codex &>/dev/null; then
  AGENT_CMD="codex"
  AGENT_NAME="Codex CLI"
  log "Codex CLI detectado"
elif command -v gemini &>/dev/null; then
  AGENT_CMD="gemini"
  AGENT_NAME="Gemini CLI"
  log "Gemini CLI detectado"
elif command -v claude &>/dev/null; then
  AGENT_CMD="claude"
  AGENT_NAME="Claude CLI"
  log "Claude CLI detectado"
elif command -v aider &>/dev/null; then
  AGENT_CMD="aider"
  AGENT_NAME="Aider"
  log "Aider detectado"
else
  warn "Nenhum agente CLI detectado"
  info "Instale um agente CLI compatível:"
  info "  • Hermes Agent: uv tool install hermes-agent  (ou pipx install hermes-agent)"
  info "  • Codex CLI:    npm install -g @openai/codex"
  info "  • Gemini CLI:   npm install -g @google/gemini-cli"
  info "  • Claude CLI:   npm install -g @anthropic-ai/claude-code"
  echo ""
  info "Após instalar, execute este script novamente."
  info "Ou use manualmente: veja instruções ao final."
  AGENT_CMD=""
fi

# ─── Step 3: Setup provisioner ──────────────────────────────────────────

if [ "$LOCAL_REPO" = true ]; then
  step "Usando repositório local em $INSTALL_DIR..."
  log "Provisioner encontrado localmente"
else
  step "Baixando Exocórtex Provisioner de github.com/$REPO..."

  TMPDIR=$(mktemp -d)
  trap "rm -rf $TMPDIR" EXIT

  echo -e "  ${DIM}$TARBALL_URL${NC}"
  curl -fsSL "$TARBALL_URL" -o "$TMPDIR/repo.tar.gz"
  log "Download completo"

  step "Extraindo provisioner..."

  tar xzf "$TMPDIR/repo.tar.gz" -C "$TMPDIR"
  EXTRACTED=$(find "$TMPDIR" -maxdepth 1 -type d -name "exocortex*" | head -1)

  if [ -z "$EXTRACTED" ]; then
    fail "Falha ao extrair — estrutura inesperada"
    exit 1
  fi

  rm -rf "$INSTALL_DIR"
  mkdir -p "$INSTALL_DIR"

  cp -r "$EXTRACTED/$PROVISIONER_REL/"* "$INSTALL_DIR/"
  cp -r "$EXTRACTED/plans/pdd_v2/artifacts" "$INSTALL_DIR/artifacts"
  mkdir -p "$INSTALL_DIR/phases"
  cp "$EXTRACTED/plans/pdd_v2/phases/"P*.md "$INSTALL_DIR/phases/" 2>/dev/null || true
  cp "$EXTRACTED/plans/pdd_v2/PLAYBOOK.yaml" "$INSTALL_DIR/" 2>/dev/null || true

  log "Provisioner instalado em $INSTALL_DIR"
fi

chmod +x "$INSTALL_DIR/lib/"*.sh "$INSTALL_DIR/docker/entrypoint.sh" 2>/dev/null || true

# ─── Step 5: Verify integrity ─────────────────────────────────────────────
step "Verificando integridade..."

if bash "$INSTALL_DIR/lib/verify.sh" --pre-provision 2>&1 | tail -1 | grep -q "passed"; then
  log "Golden image íntegra"
else
  warn "Verificação parcial — alguns checks falharam"
  bash "$INSTALL_DIR/lib/verify.sh" --pre-provision 2>&1
fi

PROMPT_COUNT=$(find "$INSTALL_DIR/prompts" -name "P*.md" -type f | wc -l)
log "$PROMPT_COUNT prompts PDD prontos"

# ─── Step 6: Launch agent ──────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  ┌─────────────────────────────────────────┐${NC}"
echo -e "${BOLD}  │${NC}  ${GREEN}✅ Provisioner pronto!${NC}                    ${BOLD}│${NC}"
echo -e "${BOLD}  │${NC}                                           ${BOLD}│${NC}"
echo -e "${BOLD}  │${NC}  📦 $PROMPT_COUNT prompts  •  15 skills  •  2 profiles ${BOLD}│${NC}"
echo -e "${BOLD}  │${NC}  📍 ${DIM}$INSTALL_DIR${NC}       ${BOLD}│${NC}"
echo -e "${BOLD}  └─────────────────────────────────────────┘${NC}"
echo ""

# Build the instruction for the agent
AGENT_INSTRUCTION="Leia o arquivo RUNBOOK.md em $INSTALL_DIR/RUNBOOK.md e siga todas as instruções sequencialmente para instalar e configurar o Exocórtex.IA. Este é um provisioner conversacional: execute cada fase, faça apenas as perguntas indicadas, e reporte o progresso ao usuário."

if [ -n "$AGENT_CMD" ]; then
  step "Iniciando $AGENT_NAME..."
  echo ""
  info "O agente vai ler o RUNBOOK e guiar a instalação."
  info "Responda às perguntas quando solicitado."
  echo ""

  case "$AGENT_CMD" in
    hermes)
      # Hermes: pass RUNBOOK content as context + instruction
      echo -e "${DIM}  → hermes chat com contexto do RUNBOOK${NC}"
      echo ""
      cd "$INSTALL_DIR" && exec hermes chat -q "$AGENT_INSTRUCTION"
      ;;
    codex)
      # Codex: use CODEX_BOOTSTRAP.md as the prompt, --cd for workspace
      BOOTSTRAP="$INSTALL_DIR/CODEX_BOOTSTRAP.md"
      if [ ! -f "$BOOTSTRAP" ]; then
        fail "CODEX_BOOTSTRAP.md não encontrado em $INSTALL_DIR"
        exit 1
      fi
      echo -e "${DIM}  → codex com bootstrap prompt${NC}"
      echo ""
      exec codex --cd "$INSTALL_DIR" "$(cat "$BOOTSTRAP")"
      ;;
    gemini)
      # Gemini CLI: pass as prompt
      echo -e "${DIM}  → gemini com instruções do RUNBOOK${NC}"
      echo ""
      exec gemini -p "$AGENT_INSTRUCTION"
      ;;
    claude)
      # Claude CLI: pass as prompt with file context
      echo -e "${DIM}  → claude com instruções do RUNBOOK${NC}"
      echo ""
      exec claude -p "$AGENT_INSTRUCTION" --add-file "$INSTALL_DIR/RUNBOOK.md"
      ;;
    aider)
      # Aider: open with RUNBOOK context
      echo -e "${DIM}  → aider com RUNBOOK como contexto${NC}"
      echo ""
      exec aider --read "$INSTALL_DIR/RUNBOOK.md" --message "$AGENT_INSTRUCTION"
      ;;
  esac
else
  # No agent CLI — show manual instructions
  step "Modo manual"
  echo ""
  info "Nenhum agente CLI detectado. Para prosseguir, escolha uma opção:"
  echo ""
  echo -e "  ${BOLD}Opção 1: Instale um agente e re-execute${NC}"
  echo "  curl -fsSL https://raw.githubusercontent.com/$REPO/$BRANCH/install-exocortex.sh | bash"
  echo ""
  echo -e "  ${BOLD}Opção 2: Use manualmente com qualquer agente${NC}"
  echo "  Cole a seguinte instrução no seu agente (ChatGPT, Claude, etc.):"
  echo ""
  echo -e "  ${CYAN}───────────────────────────────────────${NC}"
  echo "  Leia o RUNBOOK.md e siga as instruções para instalar o Exocórtex.IA."
  echo "  O arquivo está em: $INSTALL_DIR/RUNBOOK.md"
  echo -e "  ${CYAN}───────────────────────────────────────${NC}"
  echo ""
  echo -e "  ${BOLD}Opção 3: Provisione apenas a golden image (sem PDD)${NC}"
  echo "  bash $INSTALL_DIR/artifacts/setup.sh"
  echo ""
fi
