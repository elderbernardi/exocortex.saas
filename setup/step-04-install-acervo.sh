#!/usr/bin/env bash
# =============================================================================
# Step 04: Copiar acervo (seed + ops + templates + tools)
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
      --exclude 'micro/estudio-editorial/***' \
      --exclude 'global/_meta/microversos.yaml' \
      "$ACERVO_SRC/" "$ACERVO/"
  else
    warn "rsync não encontrado; cópia genérica do Acervo pulada para evitar overwrite acidental"
  fi
}

provision_estudio_editorial_seed() {
  local editorial_src="$ACERVO_SRC/micro/estudio-editorial"
  local editorial_dst="$ACERVO/micro/estudio-editorial"

  mkdir -p "$editorial_dst"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}

  if [ -d "$editorial_src" ]; then
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --ignore-existing --exclude '__pycache__' "$editorial_src/" "$editorial_dst/"
      log "Microverso base estudio-editorial instalado/preservado"
    else
      warn "rsync não encontrado; estudio-editorial seed não copiado para evitar overwrite acidental"
    fi
  else
    warn "Microverso base estudio-editorial source não encontrado: $editorial_src"
  fi
}

provision_microversos_registry() {
  # Registro append-only de microversos instalados (mantido por microverso_install.py).
  # Semeado apenas se ausente — nunca sobrescreve o histórico de runtime.
  local reg_src="$ACERVO_SRC/global/_meta/microversos.yaml"
  local reg_dst="$ACERVO/global/_meta/microversos.yaml"
  if [ ! -f "$reg_dst" ] && [ -f "$reg_src" ]; then
    mkdir -p "$(dirname "$reg_dst")"
    cp "$reg_src" "$reg_dst"
    log "Registro de microversos semeado: $reg_dst"
  else
    log "Registro de microversos preservado: $reg_dst"
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
    provision_estudio_editorial_seed
    provision_microversos_registry
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

# Inicializar estrutura de quarentena do lifecycle (ADR-015)
QUARANTINE_DIR="$ACERVO/.quarantine"
if [ ! -d "$QUARANTINE_DIR" ]; then
  mkdir -p "$QUARANTINE_DIR"
  touch "$QUARANTINE_DIR/.purge_log"
  cat > "$QUARANTINE_DIR/README.md" <<'EOF'
# .quarantine/

Diretório de quarentena do Acervo Cognitivo (ADR-015).

Arquivos aqui estão aguardando purge definitivo após janela de 30 dias.
Durante esse período, o executivo pode restaurá-los com `excrtx-memory-quarantine`.

Não edite arquivos aqui diretamente. Use as skills do lifecycle:
- `excrtx-memory-quarantine` — mover, restaurar
- `excrtx-memory-syndic` — ciclo autônomo de scan/purge

`.purge_log` registra todas as operações de purge (append-only).
EOF
  log "Quarentena inicializada: $QUARANTINE_DIR"
else
  log "Quarentena já existe: $QUARANTINE_DIR"
fi
