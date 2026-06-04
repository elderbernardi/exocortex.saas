#!/usr/bin/env bash
# =============================================================================
# migrate_skill_names.sh — Rename all 33 skills to excrtx-{TYPE}-{NAME} convention
# =============================================================================
# Ref: ADR-015 (Skill Naming Convention)
#
# Usage:
#   bash migrate_skill_names.sh [--dry-run]
#
# Must be run from plans/pdd_v2/artifacts/
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$ARTIFACTS_DIR/skills"
BUNDLE_FILE="$ARTIFACTS_DIR/skill-bundles/exocortex-alpha.yaml"
PROFILE_FILE="$ARTIFACTS_DIR/profiles/manut/profile.yaml"
SOUL_FILE="$ARTIFACTS_DIR/SOUL_SEED.md"
BACKLOG_FILE="$ARTIFACTS_DIR/BACKLOG_TEMPLATE.md"
SETUP_FILE="$ARTIFACTS_DIR/setup.sh"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
dry() { echo -e "${CYAN}[DRY-RUN]${NC} $1"; }

# Mapping: old_name -> new_name
declare -A SKILL_MAP=(
  ["acervo-llm-wiki-adapter"]="excrtx-memory-wikiadapt"
  ["acervo-manager"]="excrtx-memory-manager"
  ["browser-use"]="excrtx-integrate-browser"
  ["codex-harness"]="excrtx-harness-core"
  ["codex-integration"]="excrtx-harness-codexint"
  ["codex-ops-hermes"]="excrtx-harness-hermesops"
  ["docbrain-cli-api"]="excrtx-integrate-docbrain"
  ["exocortex-base-microverso-setup"]="excrtx-memory-mvsetup"
  ["exocortex-briefing"]="excrtx-behavior-briefing"
  ["exocortex-canvas"]="excrtx-behavior-canvas"
  ["exocortex-design-system"]="excrtx-quality-designsys"
  ["exocortex-draft-first"]="excrtx-govern-draftfirst"
  ["exocortex-kanban-backlog"]="excrtx-harness-kanban"
  ["exocortex-new-microverso"]="excrtx-memory-newmicro"
  ["exocortex-notebooklm-knowledge-router"]="excrtx-integrate-nlmroute"
  ["exocortex-notebooklm-operational-workflow"]="excrtx-integrate-nlmops"
  ["exocortex-onboarding"]="excrtx-onboard-welcome"
  ["exocortex-operational-memory"]="excrtx-memory-opsmemory"
  ["exocortex-output-quality-gate"]="excrtx-quality-gate"
  ["exocortex-prompt-log"]="excrtx-harness-promptlog"
  ["exocortex-self-test"]="excrtx-assess-selftest"
  ["exocortex-slides"]="excrtx-produce-slides"
  ["exocortex-tool-governance"]="excrtx-govern-tools"
  ["exocortex-vetor-ativo"]="excrtx-behavior-vetor"
  ["gerador-oficios"]="excrtx-produce-oficios"
  ["google-drive-direct-api"]="excrtx-integrate-gdrive"
  ["hermes-mcp-oauth-integrations"]="excrtx-integrate-oauth"
  ["hermes-surface-architecture"]="excrtx-harness-surfaces"
  ["personal-artifact-workspace"]="excrtx-produce-artifacts"
  ["personal-intake-workspace"]="excrtx-memory-intake"
  ["stop-slop"]="excrtx-quality-antislop"
  ["taste-skill"]="excrtx-quality-taste"
  ["technical-repo-fit-assessment"]="excrtx-assess-repofit"
)

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Skill Name Migration (ADR-015)             ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

if $DRY_RUN; then
  warn "DRY-RUN mode — no changes will be made"
  echo ""
fi

ERRORS=0
RENAMED=0
UPDATED_REFS=0

# ─── Step 1: Rename skill directories ────────────────────────────────────────
info "Step 1: Renaming skill directories..."

for old_name in "${!SKILL_MAP[@]}"; do
  new_name="${SKILL_MAP[$old_name]}"
  old_dir="$SKILLS_DIR/$old_name"
  new_dir="$SKILLS_DIR/$new_name"

  if [ -d "$old_dir" ]; then
    if $DRY_RUN; then
      dry "mv $old_name → $new_name"
    else
      mv "$old_dir" "$new_dir"
      log "Renamed: $old_name → $new_name"
    fi
    RENAMED=$((RENAMED + 1))
  elif [ -d "$new_dir" ]; then
    info "Already renamed: $new_name"
  else
    warn "Missing: $old_name (not found)"
    ERRORS=$((ERRORS + 1))
  fi
done

echo "  Renamed: $RENAMED directories"
echo ""

# ─── Step 2: Update name: in SKILL.md frontmatter ───────────────────────────
info "Step 2: Updating SKILL.md frontmatter..."

for old_name in "${!SKILL_MAP[@]}"; do
  new_name="${SKILL_MAP[$old_name]}"
  skill_md="$SKILLS_DIR/$new_name/SKILL.md"

  if [ -f "$skill_md" ]; then
    if $DRY_RUN; then
      if grep -q "name: $old_name" "$skill_md"; then
        dry "Update frontmatter: $new_name/SKILL.md"
      fi
    else
      sed -i "s/^name: ${old_name}$/name: ${new_name}/" "$skill_md"
    fi
  fi
done

log "Frontmatter updated"
echo ""

# ─── Step 3: Update references in all SKILL.md files ────────────────────────
info "Step 3: Updating cross-references in all SKILL.md files..."

for skill_md in "$SKILLS_DIR"/*/SKILL.md; do
  if [ -f "$skill_md" ]; then
    for old_name in "${!SKILL_MAP[@]}"; do
      new_name="${SKILL_MAP[$old_name]}"
      if grep -q "$old_name" "$skill_md" 2>/dev/null; then
        if $DRY_RUN; then
          dry "Update ref in $(basename "$(dirname "$skill_md")")/SKILL.md: $old_name → $new_name"
        else
          sed -i "s/${old_name}/${new_name}/g" "$skill_md"
        fi
        UPDATED_REFS=$((UPDATED_REFS + 1))
      fi
    done
  fi
done

log "Cross-references updated ($UPDATED_REFS refs)"
echo ""

# ─── Step 4: Update bundle YAML ─────────────────────────────────────────────
info "Step 4: Updating bundle (exocortex-alpha.yaml)..."

if [ -f "$BUNDLE_FILE" ]; then
  for old_name in "${!SKILL_MAP[@]}"; do
    new_name="${SKILL_MAP[$old_name]}"
    if grep -q "  - $old_name" "$BUNDLE_FILE" 2>/dev/null; then
      if $DRY_RUN; then
        dry "Bundle: $old_name → $new_name"
      else
        sed -i "s/  - ${old_name}$/  - ${new_name}/" "$BUNDLE_FILE"
      fi
    fi
  done
  log "Bundle updated"
else
  warn "Bundle file not found: $BUNDLE_FILE"
  ERRORS=$((ERRORS + 1))
fi
echo ""

# ─── Step 5: Update profile YAML ────────────────────────────────────────────
info "Step 5: Updating profile (manut/profile.yaml)..."

if [ -f "$PROFILE_FILE" ]; then
  for old_name in "${!SKILL_MAP[@]}"; do
    new_name="${SKILL_MAP[$old_name]}"
    if grep -q "- $old_name" "$PROFILE_FILE" 2>/dev/null; then
      if $DRY_RUN; then
        dry "Profile: $old_name → $new_name"
      else
        sed -i "s/- ${old_name}$/- ${new_name}/" "$PROFILE_FILE"
      fi
    fi
  done
  log "Profile updated"
else
  warn "Profile file not found: $PROFILE_FILE"
  ERRORS=$((ERRORS + 1))
fi
echo ""

# ─── Step 6: Update SOUL_SEED.md ────────────────────────────────────────────
info "Step 6: Updating SOUL_SEED.md..."

if [ -f "$SOUL_FILE" ]; then
  for old_name in "${!SKILL_MAP[@]}"; do
    new_name="${SKILL_MAP[$old_name]}"
    if grep -q "$old_name" "$SOUL_FILE" 2>/dev/null; then
      if $DRY_RUN; then
        dry "SOUL_SEED: $old_name → $new_name"
      else
        sed -i "s/${old_name}/${new_name}/g" "$SOUL_FILE"
      fi
    fi
  done
  log "SOUL_SEED.md updated"
else
  warn "SOUL_SEED.md not found: $SOUL_FILE"
  ERRORS=$((ERRORS + 1))
fi
echo ""

# ─── Step 7: Update BACKLOG_TEMPLATE.md ──────────────────────────────────────
info "Step 7: Updating BACKLOG_TEMPLATE.md..."

if [ -f "$BACKLOG_FILE" ]; then
  for old_name in "${!SKILL_MAP[@]}"; do
    new_name="${SKILL_MAP[$old_name]}"
    if grep -q "$old_name" "$BACKLOG_FILE" 2>/dev/null; then
      if $DRY_RUN; then
        dry "BACKLOG: $old_name → $new_name"
      else
        sed -i "s/${old_name}/${new_name}/g" "$BACKLOG_FILE"
      fi
    fi
  done
  log "BACKLOG_TEMPLATE.md updated"
else
  info "BACKLOG_TEMPLATE.md not found (optional)"
fi
echo ""

# ─── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════"
echo "  Migration Summary"
echo "═══════════════════════════════════════════════"
echo "  Directories renamed: $RENAMED"
echo "  Cross-refs updated:  $UPDATED_REFS"
echo "  Errors:              $ERRORS"
if $DRY_RUN; then
  warn "DRY-RUN — no actual changes made"
fi
echo ""

# ─── Post-migration verification ────────────────────────────────────────────
if ! $DRY_RUN; then
  info "Post-migration verification..."

  # Check no old names remain in key files
  OLD_REFS=0
  for old_name in "${!SKILL_MAP[@]}"; do
    if grep -rq "$old_name" "$BUNDLE_FILE" "$PROFILE_FILE" "$SOUL_FILE" 2>/dev/null; then
      warn "Stale reference found: $old_name"
      OLD_REFS=$((OLD_REFS + 1))
    fi
  done

  if [ $OLD_REFS -eq 0 ]; then
    log "Zero stale references in bundle/profile/SOUL ✓"
  else
    warn "$OLD_REFS stale references remain"
  fi

  # Count new skill dirs
  NEW_COUNT=$(find "$SKILLS_DIR" -maxdepth 1 -type d -name "excrtx-*" | wc -l)
  info "excrtx-* skill directories: $NEW_COUNT"
fi

exit $ERRORS
