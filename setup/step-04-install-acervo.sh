#!/usr/bin/env bash
# =============================================================================
# Step 04: Copiar acervo (seed + ops + templates + tools + codex)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

info "Instalando acervo..."

copy_acervo_seed() {
  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --exclude '__pycache__' \
      --exclude 'micro/exocortex-ops/***' \
      "$ACERVO_SRC/" "$ACERVO/"
  else
    warn "rsync não encontrado; cópia genérica do Acervo pulada para evitar overwrite acidental"
  fi
}

provision_exocortex_ops_seed() {
  local ops_src="$ACERVO_SRC/micro/exocortex-ops"
  local ops_dst="$ACERVO/micro/exocortex-ops"

  mkdir -p "$ops_dst"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
  mkdir -p "$ops_dst/_meta"/{snapshots,drafts,indices}

  if [ -d "$ops_src" ]; then
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --ignore-existing --exclude '__pycache__' "$ops_src/" "$ops_dst/"
      log "Microverso base exocortex-ops instalado/preservado"
    else
      warn "rsync não encontrado; exocortex-ops seed não copiado para evitar overwrite acidental"
    fi
  else
    warn "Microverso base exocortex-ops source não encontrado: $ops_src"
  fi
}

if [ "$ACERVO_SRC" -ef "$ACERVO" ]; then
  log "Acervo source e destination são o mesmo diretório. Cópia local pulada."
else
  if [ -d "$ACERVO_SRC" ]; then
    copy_acervo_seed
    provision_exocortex_ops_seed
    log "Acervo: $(find "$ACERVO" -type f 2>/dev/null | wc -l) arquivos"
  else
    fail "Acervo source não encontrado: $ACERVO_SRC"
  fi

  # Verificar WELCOME.md
  WELCOME_SRC="$ACERVO_SRC/global/knowledge/WELCOME.md"
  if [ -f "$WELCOME_SRC" ]; then
    mkdir -p "$ACERVO/global/knowledge"
    cp "$WELCOME_SRC" "$ACERVO/global/knowledge/WELCOME.md"
    log "WELCOME.md instalado em acervo/global/knowledge/"
  else
    warn "WELCOME.md não encontrado em $WELCOME_SRC"
  fi

  # Instalar templates canônicos v0.4
  TEMPLATES_SRC="$SCRIPT_DIR/acervo/global/templates/harness-v0.4"
  TEMPLATES_DST="$ACERVO/global/templates/harness-v0.4"
  if [ -d "$TEMPLATES_SRC" ]; then
    cp -r "$TEMPLATES_SRC"/* "$TEMPLATES_DST/" 2>/dev/null || true
    log "Templates v0.4: $(ls -1 "$TEMPLATES_DST" 2>/dev/null | wc -l) arquivos"
  fi

  # Instalar ferramentas globais do Acervo
  ROOT_TOOLS_SRC="$SCRIPT_DIR/acervo/global/tools"
  ROOT_TOOLS_DST="$ACERVO/global/tools"
  if [ -d "$ROOT_TOOLS_SRC" ]; then
    mkdir -p "$ROOT_TOOLS_DST"
    find "$ROOT_TOOLS_SRC" -maxdepth 1 -type f -name '*.py' -exec cp {} "$ROOT_TOOLS_DST/" \;
    chmod +x "$ROOT_TOOLS_DST"/*.py 2>/dev/null || true
    log "Global tools: $(ls -1 "$ROOT_TOOLS_DST"/*.py 2>/dev/null | wc -l) scripts"
  fi

  # Instalar ferramentas determinísticas do harness
  TOOLS_SRC="$SCRIPT_DIR/acervo/global/tools/harness"
  TOOLS_DST="$ACERVO/global/tools/harness"
  if [ -d "$TOOLS_SRC" ]; then
    cp -r "$TOOLS_SRC"/* "$TOOLS_DST/" 2>/dev/null || true
    chmod +x "$TOOLS_DST"/*.py 2>/dev/null || true
    log "Harness tools: $(ls -1 "$TOOLS_DST"/*.py 2>/dev/null | wc -l) scripts"
  fi
fi

# Instalar wrappers do Codex Core Harness (EX-33)
CODEX_WRAPPERS_SRC="$SCRIPT_DIR/scripts/codex_learning"
CODEX_WRAPPERS_DST="$HERMES_HOME/scripts/codex_learning"
CODEX_LEARNING_DST="$HERMES_HOME/codex-learning"
if [ -d "$CODEX_WRAPPERS_SRC" ]; then
  mkdir -p "$CODEX_WRAPPERS_DST"
  mkdir -p "$CODEX_LEARNING_DST"/{runs,events,reviews}
  cp -r "$CODEX_WRAPPERS_SRC"/* "$CODEX_WRAPPERS_DST/" 2>/dev/null || true
  chmod +x "$CODEX_WRAPPERS_DST"/*.py 2>/dev/null || true
  log "Codex wrappers: $(ls -1 "$CODEX_WRAPPERS_DST"/*.py 2>/dev/null | wc -l) scripts"
  log "Codex learning dir pronto: $CODEX_LEARNING_DST"
else
  warn "Wrappers do Codex não encontrados: $CODEX_WRAPPERS_SRC"
fi
