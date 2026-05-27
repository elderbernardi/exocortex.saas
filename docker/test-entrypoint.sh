#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Test Entrypoint for Docker
# =============================================================================
# Este script roda DENTRO do container Docker para preparar o ambiente de teste.
# Ele simula um Hermes limpo recebendo a configuração PDD v2.
#
# Fluxo:
#   1. Copiar credenciais do host (read-only mount → writable HERMES_HOME)
#   2. Executar setup.sh do PDD v2 (popula skills no HERMES_HOME limpo)
#   3. Verificar estado
#   4. Abrir shell interativo para testes manuais
# =============================================================================

set -euo pipefail

HERMES_HOME="${HERMES_HOME:-/opt/data}"
WORKSPACE="${WORKSPACE:-/workspace}"
SECRETS_DIR="/opt/secrets"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Exocórtex.IA — PDD v2 Test Environment     ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# =============================================================================
# Step 1: Bootstrap HERMES_HOME
# =============================================================================
info "HERMES_HOME: $HERMES_HOME"
info "WORKSPACE:   $WORKSPACE"

# Copiar credenciais
if [ -f "$SECRETS_DIR/.env" ]; then
  cp "$SECRETS_DIR/.env" "$HERMES_HOME/.env"
  log "Credenciais copiadas: .env"
else
  warn ".env não encontrado em $SECRETS_DIR"
fi

if [ -f "$SECRETS_DIR/auth.json" ]; then
  cp "$SECRETS_DIR/auth.json" "$HERMES_HOME/auth.json"
  log "Credenciais copiadas: auth.json"
else
  warn "auth.json não encontrado em $SECRETS_DIR"
fi

if [ -f "$SECRETS_DIR/config.yaml" ]; then
  cp "$SECRETS_DIR/config.yaml" "$HERMES_HOME/config.yaml"
  log "Config copiada: config.yaml"
else
  warn "config.yaml não encontrado em $SECRETS_DIR"
fi

# Copiar arquivos de identidade (SOUL.md, MEMORY.md)
if [ -f "$WORKSPACE/SOUL.md" ]; then
  cp "$WORKSPACE/SOUL.md" "$HERMES_HOME/SOUL.md"
  log "Identidade copiada: SOUL.md (Exocórtex persona)"
else
  warn "SOUL.md não encontrado em $WORKSPACE"
fi

if [ -f "$WORKSPACE/MEMORY.md" ]; then
  cp "$WORKSPACE/MEMORY.md" "$HERMES_HOME/memories/MEMORY.md"
  log "Memória copiada: MEMORY.md"
else
  warn "MEMORY.md não encontrado em $WORKSPACE"
fi

# =============================================================================
# Step 2: Executar setup.sh PDD v2 (P0 Foundation)
# =============================================================================
echo ""
info "Executando P0 Foundation (setup.sh)..."
echo ""

cd "$WORKSPACE"

# Criar estrutura base do acervo
mkdir -p "$HERMES_HOME/skills/exocortex"
mkdir -p "$HERMES_HOME/acervo"/{macro,global,micro/_template,shared/cross-refs}
mkdir -p "$HERMES_HOME/profiles"
mkdir -p "$HERMES_HOME/skill-bundles"

# Copiar skills do repositório para o HERMES_HOME limpo
SKILLS_SRC="$WORKSPACE/.hermes/skills/exocortex"
SKILLS_DST="$HERMES_HOME/skills/exocortex"

if [ -d "$SKILLS_SRC" ]; then
  for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name=$(basename "$skill_dir")
    if [ -d "$skill_dir" ]; then
      mkdir -p "$SKILLS_DST/$skill_name"
      cp -r "$skill_dir"* "$SKILLS_DST/$skill_name/" 2>/dev/null || true
      log "Skill copiada: $skill_name"
    fi
  done
else
  warn "Skills source não encontrado: $SKILLS_SRC"
fi

# Copiar acervo
ACERVO_SRC="$WORKSPACE/.hermes/acervo"
ACERVO_DST="$HERMES_HOME/acervo"
if [ -d "$ACERVO_SRC" ]; then
  cp -r "$ACERVO_SRC"/* "$ACERVO_DST/" 2>/dev/null || true
  log "Acervo copiado: $(find "$ACERVO_DST" -type f 2>/dev/null | wc -l) arquivos"
fi

# Copiar profiles
PROFILES_SRC="$WORKSPACE/.hermes/profiles"
PROFILES_DST="$HERMES_HOME/profiles"
if [ -d "$PROFILES_SRC" ]; then
  cp -r "$PROFILES_SRC"/* "$PROFILES_DST/" 2>/dev/null || true
  log "Profiles copiados"
fi

# Copiar bundle
BUNDLES_SRC="$WORKSPACE/.hermes/skill-bundles"
BUNDLES_DST="$HERMES_HOME/skill-bundles"
if [ -d "$BUNDLES_SRC" ]; then
  cp -r "$BUNDLES_SRC"/* "$BUNDLES_DST/" 2>/dev/null || true
  log "Bundles copiados"
fi

# =============================================================================
# Step 3: Verificação
# =============================================================================
echo ""
info "=== VERIFICAÇÃO ==="
echo ""

echo "Skills instaladas:"
ls "$SKILLS_DST/" 2>/dev/null | while read -r s; do echo "  ✓ $s"; done
SKILL_COUNT=$(ls -1d "$SKILLS_DST"/*/ 2>/dev/null | wc -l)
echo "  Total: $SKILL_COUNT"
echo ""

echo "Acervo (4 camadas):"
for layer in macro global micro shared; do
  count=$(find "$ACERVO_DST/$layer" -type f 2>/dev/null | wc -l)
  echo "  $layer/: $count arquivos"
done
echo ""

echo "Profiles:"
ls "$PROFILES_DST/" 2>/dev/null | while read -r p; do echo "  ✓ $p"; done
echo ""

echo "Bundles:"
ls "$BUNDLES_DST/" 2>/dev/null | while read -r b; do echo "  ✓ $b"; done
echo ""

# Verificar hermes CLI
if command -v hermes > /dev/null 2>&1; then
  log "hermes CLI: $(hermes --version 2>/dev/null | head -1)"
else
  warn "hermes CLI não encontrado no PATH"
fi

# =============================================================================
# Step 4: Shell interativo
# =============================================================================
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Ambiente pronto. Entrando em shell.         ║"
echo "║                                               ║"
echo "║   Comandos úteis:                             ║"
echo "║     hermes skills list                        ║"
echo "║     hermes chat                               ║"
echo "║     hermes chat --skills exocortex-self-test  ║"
echo "║                                               ║"
echo "║   Para sair: exit                             ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

cd "$WORKSPACE"
exec /bin/bash
