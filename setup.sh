#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Setup Reproduzível
# =============================================================================
# Este script reproduz TODA a configuração do Hermes para o Exocórtex.IA.
# Executar em um Hermes limpo para recriar o ambiente completo.
#
# Pré-requisitos:
#   - hermes-agent instalado e funcional (`hermes doctor` OK)
#   - OPENROUTER_API_KEY configurado em ~/.hermes/.env
#   - Python 3.11+ com pip
#   - uv (para browser-use CLI)
#
# Uso:
#   chmod +x setup.sh && ./setup.sh
#
# Log: Cada ação é registrada em plans/pdd/logs/setup_replay.log
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
HERMES_DIR="$HOME/.hermes"
SKILLS_DIR="$HERMES_DIR/skills"
LOG_FILE="$PROJECT_DIR/plans/pdd/logs/setup_replay.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
  local msg="[$(date -Iseconds)] $1"
  echo -e "${GREEN}✓${NC} $msg"
  echo "$msg" >> "$LOG_FILE"
}

warn() {
  local msg="[$(date -Iseconds)] WARN: $1"
  echo -e "${YELLOW}⚠${NC} $msg"
  echo "$msg" >> "$LOG_FILE"
}

fail() {
  local msg="[$(date -Iseconds)] FAIL: $1"
  echo -e "${RED}✗${NC} $msg"
  echo "$msg" >> "$LOG_FILE"
  exit 1
}

check_prereq() {
  command -v "$1" > /dev/null 2>&1 || fail "Pré-requisito ausente: $1"
}

mkdir -p "$(dirname "$LOG_FILE")"
echo "# Setup Replay Log — $(date -Iseconds)" > "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║   Exocórtex.IA — Setup Reproduzível       ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# =============================================================================
# FASE 0: Pré-requisitos
# =============================================================================
log "Verificando pré-requisitos..."
check_prereq hermes
check_prereq python3
check_prereq pip
log "Pré-requisitos OK"

# =============================================================================
# FASE P1: Skills de Identidade
# =============================================================================
log "--- FASE P1: Identity ---"

# P1.1: Skills locais (exocortex category)
LOCAL_SKILLS=(
  "exocortex-self-test"
  "exocortex-prompt-log"
  "stop-slop"
  "taste-skill"
  "exocortex-design-system"
)

for skill in "${LOCAL_SKILLS[@]}"; do
  SKILL_SRC="$PROJECT_DIR/.hermes/skills/exocortex/$skill"
  SKILL_DST="$SKILLS_DIR/exocortex/$skill"
  
  if [ -d "$SKILL_DST" ]; then
    log "Skill já instalada: $skill"
  elif [ -d "$SKILL_SRC" ]; then
    mkdir -p "$SKILL_DST"
    cp -r "$SKILL_SRC"/* "$SKILL_DST/"
    log "Skill instalada (local): $skill"
  else
    warn "Skill source não encontrada: $SKILL_SRC — será criada via PDD prompt"
  fi
done

# =============================================================================
# FASE P2: Skills de Memória
# =============================================================================
log "--- FASE P2: Memory ---"

P2_SKILLS=(
  "acervo-manager"
  "exocortex-new-microverso"
)

for skill in "${P2_SKILLS[@]}"; do
  SKILL_SRC="$PROJECT_DIR/.hermes/skills/exocortex/$skill"
  SKILL_DST="$SKILLS_DIR/exocortex/$skill"
  
  if [ -d "$SKILL_DST" ]; then
    log "Skill já instalada: $skill"
  elif [ -d "$SKILL_SRC" ]; then
    mkdir -p "$SKILL_DST"
    cp -r "$SKILL_SRC"/* "$SKILL_DST/"
    log "Skill instalada (local): $skill"
  else
    warn "Skill source não encontrada: $SKILL_SRC — será criada via PDD prompt"
  fi
done

# P2.2: Acervo (4-layer knowledge base)
ACERVO_SRC="$PROJECT_DIR/.hermes/acervo"
ACERVO_DST="$HERMES_DIR/acervo"
if [ -d "$ACERVO_DST" ] && [ "$(find "$ACERVO_DST" -type f | wc -l)" -gt 5 ]; then
  log "Acervo já populado: $(find "$ACERVO_DST" -type f | wc -l) arquivos"
else
  if [ -d "$ACERVO_SRC" ]; then
    mkdir -p "$ACERVO_DST"
    cp -r "$ACERVO_SRC"/* "$ACERVO_DST/"
    log "Acervo instalado: macro/ global/ micro/_template/ shared/ ($(find "$ACERVO_DST" -type f | wc -l) arquivos)"
  else
    warn "Acervo source não encontrada em $ACERVO_SRC"
  fi
fi

# =============================================================================
# FASE P3: Skills de Tools + Pesquisa
# =============================================================================
log "--- FASE P3: Tools & Research ---"

# P3.1: DuckDuckGo Search (Skills Hub oficial)
if hermes skills list 2>/dev/null | grep -q "duckduckgo-search"; then
  log "Skill já instalada: duckduckgo-search"
else
  log "Instalando: duckduckgo-search (Skills Hub)"
  hermes skills install official/research/duckduckgo-search -y
  log "Instalada: duckduckgo-search"
fi

# P3.2: browser-use (local, do AG Kit)
BU_DST="$SKILLS_DIR/exocortex/browser-use"
if [ -d "$BU_DST" ]; then
  log "Skill já instalada: browser-use"
else
  BU_SRC="$PROJECT_DIR/.agent/skills/browser-use"
  if [ -d "$BU_SRC" ]; then
    mkdir -p "$BU_DST/scripts"
    cp "$BU_SRC/SKILL.md" "$BU_DST/SKILL.md"
    cp "$BU_SRC/scripts/browser-use.sh" "$BU_DST/scripts/browser-use.sh"
    log "Instalada: browser-use (do AG Kit)"
  else
    warn "browser-use AG Kit source não encontrada em $BU_SRC"
  fi
fi

# P3.3: Dependências Python
if command -v ddgs > /dev/null 2>&1; then
  log "Dependência já instalada: ddgs"
else
  log "Instalando dependência: ddgs (DuckDuckGo CLI)"
  pip install ddgs --quiet
  log "Instalada: ddgs $(ddgs --version 2>/dev/null || echo 'OK')"
fi

# P3.4: browser-use CLI (via uv)
if command -v browser-use > /dev/null 2>&1 || [ -f "$HOME/.local/bin/browser-use" ]; then
  log "Dependência já instalada: browser-use CLI"
else
  if command -v uv > /dev/null 2>&1; then
    log "Instalando: browser-use CLI via uv"
    uv tool install --python 3.13 browser-use
    log "Instalada: browser-use CLI"
  else
    warn "uv não encontrado — browser-use CLI não instalado. Instale uv primeiro."
  fi
fi

# P3.5: Tool Governance Skill (local)
TG_DST="$SKILLS_DIR/exocortex/exocortex-tool-governance"
if [ -d "$TG_DST" ]; then
  log "Skill já instalada: exocortex-tool-governance"
else
  TG_SRC="$PROJECT_DIR/.hermes/skills/exocortex/exocortex-tool-governance"
  if [ -d "$TG_SRC" ]; then
    mkdir -p "$TG_DST"
    cp -r "$TG_SRC"/* "$TG_DST/"
    log "Instalada: exocortex-tool-governance"
  else
    warn "Tool governance source não encontrada em $TG_SRC"
  fi
fi

# =============================================================================
# FASE P4: Skills de Comportamento
# =============================================================================
log "--- FASE P4: Behavior ---"

P4_SKILLS=(
  "exocortex-draft-first"
  "exocortex-vetor-ativo"
  "exocortex-canvas"
  "exocortex-briefing"
  "exocortex-onboarding"
  "exocortex-output-quality-gate"
)

for skill in "${P4_SKILLS[@]}"; do
  SKILL_SRC="$PROJECT_DIR/.hermes/skills/exocortex/$skill"
  SKILL_DST="$SKILLS_DIR/exocortex/$skill"
  
  if [ -d "$SKILL_DST" ]; then
    log "Skill já instalada: $skill"
  elif [ -d "$SKILL_SRC" ]; then
    mkdir -p "$SKILL_DST"
    cp -r "$SKILL_SRC"/* "$SKILL_DST/"
    log "Skill instalada (local): $skill"
  else
    warn "Skill source não encontrada: $SKILL_SRC — será criada via PDD prompt"
  fi
done

# =============================================================================
# FASE P3-CORE: Bundle + Profiles
# =============================================================================
log "--- FASE P3-CORE: Bundle & Profiles ---"

# P3-CORE.1: Bundle exocortex-alpha
if hermes bundles list 2>/dev/null | grep -q "exocortex-alpha"; then
  log "Bundle já existe: exocortex-alpha"
else
  log "Criando bundle: exocortex-alpha"
  hermes bundles create exocortex-alpha \
    --skill exocortex-self-test \
    --skill exocortex-prompt-log \
    --skill acervo-manager \
    --skill exocortex-new-microverso \
    --skill exocortex-tool-governance \
    --skill stop-slop \
    --skill taste-skill \
    --skill duckduckgo-search \
    --skill browser-use \
    --skill exocortex-draft-first \
    --skill exocortex-vetor-ativo \
    --skill exocortex-canvas \
    --skill exocortex-briefing \
    --skill exocortex-onboarding \
    --skill exocortex-output-quality-gate \
    -d "Bundle principal do Exocórtex.IA — carrega todas as skills core, memória, qualidade, pesquisa e comportamento." \
    -i "Você é o Exocórtex.IA. Ao carregar este bundle, siga SOUL.md e todas as governance rules."
  log "Bundle criado: exocortex-alpha (15 skills)"
fi

# P3-CORE.2: Profile exec
if hermes profile list 2>/dev/null | grep -q "exec"; then
  log "Profile já existe: exec"
else
  log "Criando profile: exec"
  hermes profile create exec \
    --clone \
    --description "Vetor de Execução — foco em FAZER. Draft-First, tools pesados, ação direta."
  log "Profile criado: exec"
fi

# Copiar profile.yaml e SOUL.md customizados para exec
EXEC_PROFILE_SRC="$PROJECT_DIR/.hermes/profiles/exec"
if [ -d "$EXEC_PROFILE_SRC" ]; then
  for pf in profile.yaml SOUL.md config.yaml; do
    if [ -f "$EXEC_PROFILE_SRC/$pf" ]; then
      cp "$EXEC_PROFILE_SRC/$pf" "$HERMES_DIR/profiles/exec/$pf"
    fi
  done
  log "Profile exec: config files sincronizados"
fi

# P3-CORE.3: Profile evol
if hermes profile list 2>/dev/null | grep -q "evol"; then
  log "Profile já existe: evol"
else
  log "Criando profile: evol"
  hermes profile create evol \
    --clone \
    --description "Vetor de Evolução — foco em PENSAR. Modo Socrático, reflexões, perguntas provocativas."
  log "Profile criado: evol"
fi

# Copiar profile.yaml e SOUL.md customizados para evol
EVOL_PROFILE_SRC="$PROJECT_DIR/.hermes/profiles/evol"
if [ -d "$EVOL_PROFILE_SRC" ]; then
  for pf in profile.yaml SOUL.md config.yaml; do
    if [ -f "$EVOL_PROFILE_SRC/$pf" ]; then
      cp "$EVOL_PROFILE_SRC/$pf" "$HERMES_DIR/profiles/evol/$pf"
    fi
  done
  log "Profile evol: config files sincronizados"
fi

# =============================================================================
# VERIFICAÇÃO FINAL
# =============================================================================
echo ""
log "--- VERIFICAÇÃO FINAL ---"

echo ""
echo "Skills instaladas:"
hermes skills list 2>/dev/null | grep -E "exocortex|duckduck|browser" || warn "Não foi possível listar skills"

echo ""
echo "Bundle:"
hermes bundles list 2>/dev/null | grep "exocortex" || warn "Nenhum bundle encontrado"

echo ""
echo "Profiles:"
hermes profile list 2>/dev/null || warn "Não foi possível listar profiles"

echo ""
echo "CLIs disponíveis:"
command -v ddgs > /dev/null 2>&1 && echo "  ✓ ddgs" || echo "  ✗ ddgs"
(command -v browser-use > /dev/null 2>&1 || [ -f "$HOME/.local/bin/browser-use" ]) && echo "  ✓ browser-use" || echo "  ✗ browser-use"

echo ""
log "Setup completo. Revise $LOG_FILE para detalhes."
echo ""

