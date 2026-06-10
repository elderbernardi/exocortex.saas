#!/usr/bin/env bash
# =============================================================================
# Step 02: Criar estrutura base (Camada 1 — Infraestrutura)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

info "[Camada 1] Criando estrutura base..."

# Runtime Hermes
mkdir -p "$HERMES_HOME/skills/excrtx"
mkdir -p "$HERMES_HOME/profiles"
mkdir -p "$HERMES_HOME/skill-bundles"
mkdir -p "$HERMES_HOME/memories"

# Workspace Exocórtex
mkdir -p "$EXOCORTEX_HOME"

# Acervo 4 camadas + diretórios funcionais v0.4
mkdir -p "$ACERVO/macro/assets"
mkdir -p "$ACERVO/global"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
mkdir -p "$ACERVO/micro/_template"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
mkdir -p "$ACERVO/micro/exocortex-ops"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
mkdir -p "$ACERVO/micro/exocortex-ops/_meta"/{snapshots,drafts,indices}
mkdir -p "$ACERVO/shared"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive,cross-refs}

# Diretórios operacionais v0.4 (harness canônico)
mkdir -p "$ACERVO/_tasks"
mkdir -p "$ACERVO/_routines"
mkdir -p "$ACERVO/_automations"
mkdir -p "$ACERVO/_inbox"/{incoming,processing,promoted,_archive}
mkdir -p "$ACERVO/_artifacts/items"
mkdir -p "$ACERVO/_artifacts/views"/{by_microverso,by_task,by_status,by_type}
mkdir -p "$ACERVO/_artifacts/_ops"
mkdir -p "$ACERVO/global/templates/harness-v0.4"
mkdir -p "$ACERVO/global/tools/harness"

# Compatibilidade: symlink se acervo não está em ~/.hermes
if [ "$ACERVO" != "$HERMES_HOME/acervo" ] && [ ! -e "$HERMES_HOME/acervo" ]; then
  ln -s "$ACERVO" "$HERMES_HOME/acervo" 2>/dev/null || true
  log "Symlink de compatibilidade: $HERMES_HOME/acervo -> $ACERVO"
fi

log "Estrutura de diretórios criada (runtime + workspace + v0.4 operacional)"
