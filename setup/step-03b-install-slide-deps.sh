#!/usr/bin/env bash
# =============================================================================
# Step 03b: Instalar dependências Node da produção de slides
# =============================================================================

if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

PPTXGENJS_SPEC="pptxgenjs@4.0.1"

info "Verificando dependências Node para apresentações editáveis..."

if ! command -v node >/dev/null 2>&1; then
  fail "Node.js não encontrado. O PptxGenJS exige Node.js 18 ou superior."
fi

if ! command -v npm >/dev/null 2>&1; then
  fail "npm não encontrado. Instale Node.js com npm e execute o setup novamente."
fi

npm_global_root="$(npm root -g)"

pptxgenjs_resolves() {
  NODE_PATH="${npm_global_root}${NODE_PATH:+:$NODE_PATH}" \
    node -e "require('pptxgenjs')" \
    >/dev/null 2>&1
}

if npm list -g --depth=0 "$PPTXGENJS_SPEC" >/dev/null 2>&1 && pptxgenjs_resolves; then
  log "PptxGenJS 4.0.1 já disponível em $npm_global_root"
  return 0 2>/dev/null || exit 0
fi

info "Instalando $PPTXGENJS_SPEC no prefixo global do usuário atual..."
if ! npm install --global --silent "$PPTXGENJS_SPEC"; then
  fail "Falha ao instalar $PPTXGENJS_SPEC. Verifique o prefixo do npm e as permissões de escrita."
fi

npm_global_root="$(npm root -g)"
if ! npm list -g --depth=0 "$PPTXGENJS_SPEC" >/dev/null 2>&1 || ! pptxgenjs_resolves; then
  fail "PptxGenJS foi instalado, mas o Node.js não conseguiu resolvê-lo via NODE_PATH=$npm_global_root."
fi

log "PptxGenJS 4.0.1 instalado e resolvido via $npm_global_root"
