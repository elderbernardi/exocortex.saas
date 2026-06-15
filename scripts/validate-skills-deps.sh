#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Validação de Dependências de Skills e Microversos
# =============================================================================
# Verifica dependências runtime específicas de cada skill e dos microversos
# que serão instalados pelo setup.
#
# Uso:
#   bash scripts/validate-skills-deps.sh [--json]
#
# Ref: ADR-012-interactive-setup.md
# =============================================================================

set -uo pipefail

# ─── Colors ──────────────────────────────────────────────────────────────────

if [ -t 1 ]; then
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

OUTPUT_JSON=false
[ "${1:-}" = "--json" ] && OUTPUT_JSON=true

# ─── Skill Dependency Definitions ───────────────────────────────────────────

# Each entry: skill_name|dep_type|dep_name|check_command|install_hint|auto_installed
SKILL_DEPS=(
  # excrtx-integrate-browser
  "excrtx-integrate-browser|binary|uv|command -v uv|curl -LsSf https://astral.sh/uv/install.sh \| sh|true"
  "excrtx-integrate-browser|binary|browser-use|command -v browser-use|uv tool install browser-use|true"
  "excrtx-integrate-browser|runtime|chromium|test -d \"\${HOME}/.cache/ms-playwright/chromium-\"* 2>/dev/null|browser-use install|true"

  # excrtx-produce-slides
  "excrtx-produce-slides|binary|node|command -v node|Instale Node.js >= 18|false"
  "excrtx-produce-slides|binary|npm|command -v npm|Instalado com Node.js|false"
  "excrtx-produce-slides|python|python-pptx|python3 -c 'import pptx' 2>/dev/null|pip3 install python-pptx|false"

  # excrtx-produce-oficios
  "excrtx-produce-oficios|python|PyYAML|python3 -c 'import yaml' 2>/dev/null|pip3 install PyYAML|false"

  # excrtx-integrate-docbrain
  "excrtx-integrate-docbrain|binary|git|command -v git|Instale git|false"
  "excrtx-integrate-docbrain|binary|npm|command -v npm|Instale Node.js + npm|false"

  # excrtx-integrate-nlmops / excrtx-integrate-nlmroute
  "excrtx-integrate-nlmops|binary|nlm|command -v nlm|uv tool install notebooklm-mcp-cli|true"
  "excrtx-integrate-nlmroute|binary|nlm|command -v nlm|uv tool install notebooklm-mcp-cli|true"

  # excrtx-integrate-gdrive / excrtx-integrate-oauth
  "excrtx-integrate-gdrive|python|google-auth-oauthlib|python3 -c 'import google_auth_oauthlib' 2>/dev/null|pip3 install google-auth-oauthlib|true"
  "excrtx-integrate-oauth|python|google-api-python-client|python3 -c 'import googleapiclient' 2>/dev/null|pip3 install google-api-python-client|true"

  # excrtx-quality-skilljudge
  "excrtx-quality-skilljudge|python|PyYAML|python3 -c 'import yaml' 2>/dev/null|pip3 install PyYAML|false"

  # excrtx-brandkit-generator
  "excrtx-brandkit-generator|binary|python3|command -v python3|Instale Python 3|false"
)

# ─── Microverso Dependency Definitions ──────────────────────────────────────

MICROVERSO_DEPS=(
  "exocortex-ops|binary|rsync|command -v rsync|Instale rsync (obrigatório para provisionamento)|false"
)

# Canonical files that must exist after setup for exocortex-ops
EXOCORTEX_OPS_FILES=(
  "microverso.yaml"
  "_meta/SCHEMA.md"
  "_meta/index.md"
  "_meta/log.md"
  "contracts/operating-boundaries.md"
  "contracts/profile-isolation.md"
  "contracts/canonical-path-policy.md"
  "contracts/draftfirst-change-policy.md"
  "contracts/secret-handling-policy.md"
  "contracts/memory-authority-policy.md"
  "contracts/runtime-verification-policy.md"
  "contracts/rollback-policy.md"
  "workflows/setup-change-draftfirst.md"
  "workflows/runtime-drift-audit.md"
  "workflows/self-check.md"
  "workflows/base-microverse-provisioning.md"
  "workflows/post-change-validation.md"
  "knowledge/runtime-map.md"
  "knowledge/profile-registry.md"
  "knowledge/mcp-registry.md"
  "knowledge/cron-registry.md"
  "knowledge/version-matrix.md"
)

# ─── Check Logic ────────────────────────────────────────────────────────────

declare -a JSON_RESULTS=()
TOTAL_OK=0
TOTAL_WARN=0
TOTAL_FAIL=0

check_dep() {
  local skill="$1" dep_type="$2" dep_name="$3" check_cmd="$4" install_hint="$5" auto="$6"

  if eval "$check_cmd" >/dev/null 2>&1; then
    echo -e "  ${GREEN}✅${NC} ${DIM}[$skill]${NC} $dep_name"
    TOTAL_OK=$((TOTAL_OK + 1))
    JSON_RESULTS+=("$(printf '{"skill":"%s","dep":"%s","type":"%s","status":"OK","auto":"%s"}' "$skill" "$dep_name" "$dep_type" "$auto")")
  elif [ "$auto" = "true" ]; then
    echo -e "  ${DIM}⏭  [$skill]${NC} $dep_name ${DIM}(será instalado pelo setup)${NC}"
    JSON_RESULTS+=("$(printf '{"skill":"%s","dep":"%s","type":"%s","status":"SKIP","auto":"true"}' "$skill" "$dep_name" "$dep_type")")
  else
    echo -e "  ${YELLOW}⚠${NC}  ${DIM}[$skill]${NC} $dep_name"
    echo -e "     ${DIM}→ $install_hint${NC}"
    TOTAL_WARN=$((TOTAL_WARN + 1))
    JSON_RESULTS+=("$(printf '{"skill":"%s","dep":"%s","type":"%s","status":"WARN","hint":"%s"}' "$skill" "$dep_name" "$dep_type" "$install_hint")")
  fi
}

# ─── Main ────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   Validação de Dependências de Skills & Microversos  ║${NC}"
echo -e "${BOLD}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BOLD}─── Skills ───${NC}"

current_skill=""
for entry in "${SKILL_DEPS[@]}"; do
  IFS='|' read -r skill dep_type dep_name check_cmd install_hint auto <<< "$entry"
  if [ "$skill" != "$current_skill" ]; then
    current_skill="$skill"
  fi
  check_dep "$skill" "$dep_type" "$dep_name" "$check_cmd" "$install_hint" "$auto"
done

echo ""
echo -e "${BOLD}─── Microversos ───${NC}"

for entry in "${MICROVERSO_DEPS[@]}"; do
  IFS='|' read -r mv dep_type dep_name check_cmd install_hint auto <<< "$entry"
  check_dep "$mv" "$dep_type" "$dep_name" "$check_cmd" "$install_hint" "$auto"
done

# Check canonical files if acervo source exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OPS_SRC="$REPO_ROOT/acervo/micro/exocortex-ops"

echo ""
echo -e "${BOLD}─── Arquivos Canônicos (exocortex-ops seed) ───${NC}"

if [ -d "$OPS_SRC" ]; then
  ops_ok=0
  ops_missing=0
  for f in "${EXOCORTEX_OPS_FILES[@]}"; do
    if [ -f "$OPS_SRC/$f" ]; then
      ops_ok=$((ops_ok + 1))
    else
      echo -e "  ${YELLOW}⚠${NC}  $f ${DIM}(faltando no seed)${NC}"
      ops_missing=$((ops_missing + 1))
      TOTAL_WARN=$((TOTAL_WARN + 1))
    fi
  done
  echo -e "  ${GREEN}✅${NC} $ops_ok/${#EXOCORTEX_OPS_FILES[@]} arquivos canônicos presentes no seed"
  if [ $ops_missing -gt 0 ]; then
    echo -e "  ${YELLOW}⚠${NC}  $ops_missing arquivo(s) faltando no seed source"
  fi
else
  echo -e "  ${DIM}ℹ  Diretório seed $OPS_SRC não encontrado (normal se executando fora do repo)${NC}"
fi

echo ""
echo -e "${BOLD}═══ Resumo ═══${NC}"
echo -e "  ${GREEN}✅ OK: $TOTAL_OK${NC}  |  ${YELLOW}⚠ Warn: $TOTAL_WARN${NC}  |  ${RED}❌ Fail: $TOTAL_FAIL${NC}"
echo ""

if $OUTPUT_JSON; then
  echo "{"
  echo "  \"timestamp\": \"$(date -Iseconds)\","
  echo "  \"summary\": {\"ok\": $TOTAL_OK, \"warn\": $TOTAL_WARN, \"fail\": $TOTAL_FAIL},"
  echo "  \"results\": ["
  local first=true
  for entry in "${JSON_RESULTS[@]}"; do
    if $first; then first=false; else echo ","; fi
    echo -n "    $entry"
  done
  echo ""
  echo "  ]"
  echo "}"
fi

if [ $TOTAL_FAIL -gt 0 ]; then exit 1
elif [ $TOTAL_WARN -gt 0 ]; then exit 2
else exit 0
fi
