#!/usr/bin/env bash
# =============================================================================
# Step 13: Verificação Final
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

echo ""
info "=== VERIFICAÇÃO FINAL ==="
echo ""

ERRORS=0

echo "Skills instaladas:"
SKILL_COUNT=0
for d in "$SKILLS_DST"/*/; do
  [ -d "$d" ] && echo "  ✓ $(basename "$d")" && SKILL_COUNT=$((SKILL_COUNT + 1))
done
echo "  Total: $SKILL_COUNT"

EXPECTED_SKILLS=(
  # Core + Onboard
  "excrtx-assess-selftest" "excrtx-harness-promptlog" "excrtx-onboard-welcome" "excrtx-onboard-interview"
  # Quality
  "excrtx-quality-antislop" "excrtx-quality-taste" "excrtx-quality-designsys" "excrtx-quality-gate"
  "excrtx-quality-skilljudge" "excrtx-quality-gepa"
  # Memory
  "excrtx-memory-manager" "excrtx-memory-wikiadapt" "excrtx-memory-newmicro"
  "excrtx-memory-mvsetup" "excrtx-memory-mvinstall" "excrtx-memory-opsmemory"
  # Behavior + Govern
  "excrtx-govern-draftfirst" "excrtx-behavior-vetor" "excrtx-behavior-canvas"
  "excrtx-behavior-briefing" "excrtx-govern-tools" "excrtx-harness-kanban"
  "excrtx-behavior-accuracy"
  # Workspace
  "excrtx-produce-artifacts" "excrtx-memory-intake" "excrtx-github-issue-planning"
  # Production
  "excrtx-produce-slides" "excrtx-produce-oficios" "excrtx-brandkit-generator"
  "assessment-question-authoring"
  # Integration
  "excrtx-harness-core" "excrtx-harness-codexint" "excrtx-harness-hermesops"
  "excrtx-harness-delivery" "excrtx-harness-maintenance"
  "excrtx-integrate-docbrain"
  "excrtx-integrate-nlmroute" "excrtx-integrate-nlmops" "excrtx-harness-imbroke" "excrtx-harness-tooldev"
  "excrtx-hermes-extensions"
  # Platform
  "excrtx-integrate-gdrive" "excrtx-integrate-oauth" "excrtx-integrate-mcp" "excrtx-harness-surfaces"
  # External
  "excrtx-integrate-browser"
  # Assessment
  "excrtx-assess-repofit"
)
MISSING_SKILLS=()
for skill in "${EXPECTED_SKILLS[@]}"; do
  if [ ! -f "$SKILLS_DST/$skill/SKILL.md" ]; then
    MISSING_SKILLS+=("$skill")
  fi
done
if [ ${#MISSING_SKILLS[@]} -gt 0 ]; then
  warn "Skills faltando: ${MISSING_SKILLS[*]}"
  ERRORS=$((ERRORS + ${#MISSING_SKILLS[@]}))
else
  log "Todas as ${#EXPECTED_SKILLS[@]} skills esperadas presentes"
fi
echo ""

echo "Acervo (4 camadas + v0.4 funcionais):"
for layer in macro global micro shared; do
  if [ -d "$ACERVO/$layer" ]; then
    count=$(find "$ACERVO/$layer" -type f 2>/dev/null | wc -l)
    echo "  ✓ $layer/: $count arquivos"
  else
    echo "  ✗ $layer/ (MISSING)"
    ERRORS=$((ERRORS + 1))
  fi
done
echo ""

echo "Microverso base exocortex-ops:"
if [ -d "$ACERVO/micro/exocortex-ops" ]; then
  echo "  ✓ micro/exocortex-ops/"
else
  echo "  ✗ micro/exocortex-ops/ (MISSING)"
  ERRORS=$((ERRORS + 1))
fi
EXPECTED_OPS_FILES=(
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
for f in "${EXPECTED_OPS_FILES[@]}"; do
  if [ ! -f "$ACERVO/micro/exocortex-ops/$f" ]; then
    echo "  ✗ micro/exocortex-ops/$f (MISSING)"
    ERRORS=$((ERRORS + 1))
  fi
done
echo ""

echo "Diretórios operacionais v0.4:"
for opdir in _tasks _routines _automations _inbox _artifacts; do
  if [ -d "$ACERVO/$opdir" ]; then
    echo "  ✓ $opdir/"
  else
    echo "  ✗ $opdir/ (MISSING)"
    ERRORS=$((ERRORS + 1))
  fi
done
echo ""

echo "Templates v0.4:"
ls "$ACERVO/global/templates/harness-v0.4/" 2>/dev/null | while read -r t; do echo "  ✓ $t"; done
echo ""

echo "Harness tools:"
ls "$ACERVO/global/tools/harness/"*.py 2>/dev/null | while read -r t; do echo "  ✓ $(basename "$t")"; done
echo ""

echo "Profiles:"
echo "  ✓ default (exec+evol unificado — SOUL.md com vetor-ativo)"
if [ -f "$PROFILES_DST/manut/profile.yaml" ]; then
  echo "  ✓ manut (background/zelador)"
else
  echo "  ✗ manut (MISSING)"
  ERRORS=$((ERRORS + 1))
fi
echo ""

if [ -f "$HERMES_HOME/SOUL.md" ]; then
  log "SOUL.md presente"
else
  warn "SOUL.md ausente em $HERMES_HOME"
  ERRORS=$((ERRORS + 1))
fi

if [ -f "$BUNDLES_DST/exocortex-alpha.yaml" ]; then
  log "Bundle exocortex-alpha.yaml presente"
else
  warn "Bundle manifest ausente"
  ERRORS=$((ERRORS + 1))
fi

if command -v hermes > /dev/null 2>&1; then
  log "hermes CLI: $(hermes --version 2>/dev/null | head -1)"
else
  warn "hermes CLI não encontrado no PATH"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
  echo "╔═══════════════════════════════════════════════╗"
  echo "║   ✅ Setup Candidate-Release completo.        ║"
  echo "║   Zero erros.                                 ║"
  echo "╚═══════════════════════════════════════════════╝"
else
  echo "╔═══════════════════════════════════════════════╗"
  echo "║   ⚠ Setup concluído com $ERRORS erro(s).       ║"
  echo "╚═══════════════════════════════════════════════╝"
fi
echo ""
info "Runtime Hermes:      $HERMES_HOME"
info "Workspace Exocórtex: $EXOCORTEX_HOME"
info "Acervo canônico:     $ACERVO"
info "Profiles:            default (interativo) + manut (background)"
info "Uso:                 hermes (default) | hermes -p manut"
echo ""
