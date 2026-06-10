#!/usr/bin/env bash
# =============================================================================
# Step 03: Copiar skills
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

info "Instalando skills..."

if [ -d "$SKILLS_SRC" ]; then
  for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name=$(basename "$skill_dir")
    if [ -d "$skill_dir" ]; then
      mkdir -p "$SKILLS_DST/$skill_name"
      cp -r "$skill_dir"* "$SKILLS_DST/$skill_name/" 2>/dev/null || true
      log "Skill: $skill_name"
    fi
  done
else
  fail "Skills source não encontrado: $SKILLS_SRC"
fi
