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
      # Sincroniza apenas o conteúdo distribuível. Runtimes e caches locais são
      # preservados e nunca voltam para o pacote numa reinstalação.
      rsync -a \
        --exclude='.runtime/' \
        --exclude='.venv/' \
        --exclude='node_modules/' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        "$skill_dir" "$SKILLS_DST/$skill_name/"
      log "Skill: $skill_name"
    fi
  done
else
  fail "Skills source não encontrado: $SKILLS_SRC"
fi
