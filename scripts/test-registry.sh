#!/usr/bin/env bash
# =============================================================================
# Exocórtex — Test Registry (test-registry.sh)
# =============================================================================
# Uma função test_EXNN() por feature. Sourced por run-provisioning-tests.sh.
# Cada função define checks determinísticos (Fase 1) e SMOKE_PROMPT (Fase 2).
# =============================================================================

# --- 1. Onboarding & Assessment ---

test_EX1() {
  CURRENT_FEATURE_NAME="Welcome & Onboarding"
  CURRENT_FEATURE_CATEGORY="Onboarding & Assessment"
  local skill="excrtx-onboard-welcome"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps
  check_no_tool_deps
  check_file_exists "$ACERVO/global/knowledge/WELCOME.md" "WELCOME.md para onboarding"

  SMOKE_PROMPT="Verifique se a skill excrtx-onboard-welcome funciona:
    1. O WELCOME.md existe e tem conteúdo válido?
    2. O SOUL_SEED.md tem placeholders corretos para o onboarding preencher?"
}

test_EX2() {
  CURRENT_FEATURE_NAME="Entrevista de Onboarding"
  CURRENT_FEATURE_CATEGORY="Onboarding & Assessment"
  local skill="excrtx-onboard-interview"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-onboard-welcome"
  check_no_tool_deps

  SMOKE_PROMPT="Verifique se a skill de entrevista está configurada:
    1. Os 5 blocos de entrevista estão definidos no SKILL.md?
    2. A skill referencia corretamente excrtx-onboard-welcome?"
}

test_EX3() {
  CURRENT_FEATURE_NAME="Self-Test / Auto-diagnóstico"
  CURRENT_FEATURE_CATEGORY="Onboarding & Assessment"
  local skill="excrtx-assess-selftest"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-harness-promptlog"
  check_no_tool_deps

  SMOKE_PROMPT="Execute self-test e reporte o score N/5."
}

test_EX4() {
  CURRENT_FEATURE_NAME="Repo Fit Assessment"
  CURRENT_FEATURE_CATEGORY="Onboarding & Assessment"
  local skill="excrtx-assess-repofit"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps
  check_tool_in_path "git"

  SMOKE_PROMPT="Verifique se a skill de repo fit assessment tem procedimento completo no SKILL.md."
}

# --- 2. Behavior & Governance ---

test_EX5() {
  CURRENT_FEATURE_NAME="Classificador de Vetor"
  CURRENT_FEATURE_CATEGORY="Behavior & Governance"
  local skill="excrtx-behavior-vetor"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps
  check_no_tool_deps

  SMOKE_PROMPT="Teste classificação de vetor:
    1. 'faça um relatório' → Execução?
    2. 'como você vê o futuro?' → Evolução?
    3. 'revise pendências' → Manutenção?"
}

test_EX6() {
  CURRENT_FEATURE_NAME="Canvas Cognitivo"
  CURRENT_FEATURE_CATEGORY="Behavior & Governance"
  local skill="excrtx-behavior-canvas"
  local skill_file="$SKILLS_DST/$skill/SKILL.md"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-behavior-vetor"
  check_no_tool_deps

  if grep -q 'Microverso não é sala\. A tarefa é a sala\.' "$skill_file"; then
    log_check_pass "Canvas preserva distinção: Microverso ≠ sala; tarefa = sala"
  else
    log_check_fail "Canvas não declara explicitamente que Microverso não é sala"
  fi

  if grep -q 'macroverso.status' "$skill_file"; then
    log_check_pass "Canvas exige status explícito do Macroverso"
  else
    log_check_fail "Canvas não exige status explícito do Macroverso"
  fi

  if grep -q 'microversos.sharing_constraints' "$skill_file" && grep -q 'allow > deny' "$skill_file"; then
    log_check_pass "Canvas modela sharing constraints com precedência allow > deny"
  else
    log_check_fail "Canvas não modela adequadamente sharing constraints allow/deny"
  fi

  SMOKE_PROMPT="Teste a feature EX-06 Canvas Cognitivo com este input: 'Cruze os microversos gabinete e juridico para redigir um ofício, mas jurídico tem deny: [ALL] e allow: [gabinete].' Verifique se a resposta explicita: (1) macroverso.status, (2) microverso principal, (3) microverso secundário, (4) tarefa como sala operacional, (5) sharing constraint com precedência allow > deny. Se todos aparecerem, responda SMOKE_OK; senão, SMOKE_FAIL com o que faltou."
}

test_EX7() {
  CURRENT_FEATURE_NAME="Briefing Contextual"
  CURRENT_FEATURE_CATEGORY="Behavior & Governance"
  local skill="excrtx-behavior-briefing"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-memory-manager"
  check_skill_dep "excrtx-behavior-vetor"
  check_no_tool_deps

  SMOKE_PROMPT="Verifique se o briefing consegue ler macro/ e global/ do Acervo."
}

test_EX8() {
  CURRENT_FEATURE_NAME="Draft-First Protocol"
  CURRENT_FEATURE_CATEGORY="Behavior & Governance"
  local skill="excrtx-govern-draftfirst"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps
  check_no_tool_deps

  SMOKE_PROMPT="Teste Draft-First: peça para enviar email fictício e verifique se gera DRAFT."
}

test_EX9() {
  CURRENT_FEATURE_NAME="Tool Governance"
  CURRENT_FEATURE_CATEGORY="Behavior & Governance"
  local skill="excrtx-govern-tools"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps
  check_no_tool_deps

  SMOKE_PROMPT="Verifique se a skill define classificação de tools (Internos, Pesquisa, Comunicação, Criação)."
}

test_EX10() {
  CURRENT_FEATURE_NAME="Kanban Backlog"
  CURRENT_FEATURE_CATEGORY="Behavior & Governance"
  local skill="excrtx-harness-kanban"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-produce-artifacts"
  check_skill_dep "excrtx-memory-manager"

  SMOKE_PROMPT="Verifique se o Hermes Kanban nativo está acessível via hermes kanban list."
}

test_EX49() {
  CURRENT_FEATURE_NAME="Verificação de Precisão"
  CURRENT_FEATURE_CATEGORY="Behavior & Governance"
  local skill="excrtx-behavior-accuracy"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps
  check_no_tool_deps

  # Check key content markers
  local skill_file="$SKILLS_DST/$skill/SKILL.md"
  if [ -f "$skill_file" ]; then
    if grep -q '| Ação' "$skill_file"; then
      log_check_pass "Tabela de ações verificáveis presente"
    else
      log_check_fail "Tabela de ações verificáveis ausente no SKILL.md"
    fi

    if grep -q 'Anti-Padrões' "$skill_file"; then
      log_check_pass "Anti-padrões documentados"
    else
      log_check_fail "Anti-padrões não documentados no SKILL.md"
    fi
  fi

  SMOKE_PROMPT="Teste a feature EX-49 Verificação de Precisão:
    1. A tabela de ações verificáveis (issue, commit, push, arquivo, config, mensagem) está completa?
    2. Os anti-padrões (afirmar antes de executar, afirmar sem verificar, assumir sucesso, ignorar erros) estão documentados?
    3. O formato de reporte com prova está definido?
    Se todos estiverem presentes, responda SMOKE_OK."
}

# --- 3. Memory & Acervo ---

test_EX11() {
  CURRENT_FEATURE_NAME="Acervo Manager"
  CURRENT_FEATURE_CATEGORY="Memory & Acervo"
  local skill="excrtx-memory-manager"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps  # skill raiz
  check_dir_exists "$ACERVO" "Diretório raiz do Acervo"

  for layer in macro global micro shared; do
    check_dir_exists "$ACERVO/$layer" "Acervo camada $layer"
  done
  for opdir in _inbox _artifacts _tasks _routines _automations; do
    check_dir_exists "$ACERVO/$opdir" "Dir operacional $opdir"
  done

  SMOKE_PROMPT="Verifique se o Acervo Manager opera:
    1. Leia macro/ e global/index.md
    2. Liste microversos existentes
    3. Verifique as 7 Natures na estrutura"
}

test_EX12() {
  CURRENT_FEATURE_NAME="Wiki Adapter"
  CURRENT_FEATURE_CATEGORY="Memory & Acervo"
  local skill="excrtx-memory-wikiadapt"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-memory-manager"

  SMOKE_PROMPT="Verifique se o wiki adapter traduz categorias LLM Wiki para Ontologia Multifocal v2."
}

test_EX13() {
  CURRENT_FEATURE_NAME="Criar Microverso"
  CURRENT_FEATURE_CATEGORY="Memory & Acervo"
  local skill="excrtx-memory-newmicro"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-memory-manager"
  check_dir_exists "$ACERVO/micro/_template" "Template de microverso"

  SMOKE_PROMPT="Verifique se o template de microverso em micro/_template/ tem os 15+ diretórios."
}

test_EX14() {
  CURRENT_FEATURE_NAME="Setup de Microverso Base"
  CURRENT_FEATURE_CATEGORY="Memory & Acervo"
  local skill="excrtx-memory-mvsetup"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-memory-manager"
  check_skill_dep "excrtx-memory-newmicro"
  check_dir_exists "$ACERVO/micro/exocortex-ops" "Microverso base exocortex-ops"

  SMOKE_PROMPT="Verifique se exocortex-ops tem microverso.yaml, SCHEMA.md, index.md, log.md."
}

test_EX15() {
  CURRENT_FEATURE_NAME="Microverso Package Installer"
  CURRENT_FEATURE_CATEGORY="Memory & Acervo"
  local skill="excrtx-memory-mvinstall"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-memory-manager"
  check_skill_dep "excrtx-memory-newmicro"
  check_tool_in_path "rsync"

  SMOKE_PROMPT="Verifique se a skill define schema excrtx/v1 para microverso.yaml."
}

test_EX16() {
  CURRENT_FEATURE_NAME="Memória Operacional"
  CURRENT_FEATURE_CATEGORY="Memory & Acervo"
  local skill="excrtx-memory-opsmemory"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-memory-manager"

  SMOKE_PROMPT="Verifique se a skill define precedência de providers de memória."
}

test_EX17() {
  CURRENT_FEATURE_NAME="Intake Multicanal"
  CURRENT_FEATURE_CATEGORY="Memory & Acervo"
  local skill="excrtx-memory-intake"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-memory-manager"
  check_skill_dep "excrtx-govern-draftfirst"
  check_skill_dep "excrtx-produce-artifacts"
  check_skill_dep "excrtx-harness-surfaces"
  check_dir_exists "$ACERVO/_inbox/incoming" "Inbox incoming"
  check_dir_exists "$ACERVO/_inbox/processing" "Inbox processing"
  check_dir_exists "$ACERVO/_inbox/promoted" "Inbox promoted"

  SMOKE_PROMPT="Verifique se o pipeline _inbox tem os 4 estágios e o IntakeEnvelope está documentado."
}

# --- 4. Quality Gates ---

test_EX18() {
  CURRENT_FEATURE_NAME="Anti-Slop Textual"
  CURRENT_FEATURE_CATEGORY="Quality Gates"
  local skill="excrtx-quality-antislop"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps
  check_no_tool_deps

  SMOKE_PROMPT="Teste anti-slop: dê um texto com 'Vamos explorar essa ideia fascinante' e verifique se é rejeitado."
}

test_EX19() {
  CURRENT_FEATURE_NAME="Anti-Slop Visual / Taste"
  CURRENT_FEATURE_CATEGORY="Quality Gates"
  local skill="excrtx-quality-taste"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-quality-designsys"

  # Check sub-skills
  local taste_dir="$SKILLS_DST/$skill"
  for sub in gpt-taste brandkit brutalist; do
    if [ -f "$taste_dir/${sub}.md" ] || grep -ql "$sub" "$taste_dir/SKILL.md" 2>/dev/null; then
      log_check_pass "Sub-skill '$sub' referenciada"
    else
      log_check_fail "Sub-skill '$sub' não encontrada em $taste_dir/"
    fi
  done

  SMOKE_PROMPT="Verifique se os 3 sub-skills (gpt-taste, brandkit, brutalist) estão definidos."
}

test_EX20() {
  CURRENT_FEATURE_NAME="Design System"
  CURRENT_FEATURE_CATEGORY="Quality Gates"
  local skill="excrtx-quality-designsys"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-memory-manager"

  SMOKE_PROMPT="Verifique se a skill define operações RESOLVE, CREATE, UPDATE, LINT, EXPORT."
}

test_EX21() {
  CURRENT_FEATURE_NAME="Quality Gate Unificado"
  CURRENT_FEATURE_CATEGORY="Quality Gates"
  local skill="excrtx-quality-gate"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-quality-antislop"
  check_skill_dep "excrtx-quality-taste"

  SMOKE_PROMPT="Verifique se o orquestrador classifica output como prosa/visual/técnico."
}

# --- 5. Production & Artifacts ---

test_EX22() {
  CURRENT_FEATURE_NAME="Artifacts Manager"
  CURRENT_FEATURE_CATEGORY="Production & Artifacts"
  local skill="excrtx-produce-artifacts"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-memory-manager"
  check_dir_exists "$ACERVO/_artifacts/items" "Artifacts items"
  check_dir_exists "$ACERVO/_artifacts/views/by_microverso" "View by_microverso"
  check_dir_exists "$ACERVO/_artifacts/views/by_task" "View by_task"
  check_dir_exists "$ACERVO/_artifacts/views/by_status" "View by_status"
  check_dir_exists "$ACERVO/_artifacts/views/by_type" "View by_type"

  SMOKE_PROMPT="Verifique se o artifacts manager consegue listar artefatos existentes."
}

test_EX23() {
  CURRENT_FEATURE_NAME="Gerador de Slides"
  CURRENT_FEATURE_CATEGORY="Production & Artifacts"
  local skill="excrtx-produce-slides"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-quality-designsys"
  check_skill_dep "excrtx-quality-taste"
  check_skill_dep "excrtx-integrate-gdrive"

  local scripts_dir="$SKILLS_DST/$skill/scripts"
  if [ -d "$scripts_dir" ]; then
    for s in export-pdf.sh extract-pptx.py package-deck.sh setup-frontend-slides.sh; do
      check_file_exists "$scripts_dir/$s" "Script slides/$s"
    done
  fi

  SMOKE_PROMPT="Verifique se os scripts de slides existem e são executáveis."
}

test_EX24() {
  CURRENT_FEATURE_NAME="Gerador de Ofícios"
  CURRENT_FEATURE_CATEGORY="Production & Artifacts"
  local skill="excrtx-produce-oficios"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-quality-antislop"

  local script="$SKILLS_DST/$skill/scripts/gerar_oficio.py"
  if [ -f "$script" ]; then
    log_check_pass "Script gerar_oficio.py presente"
    check_tool_in_path "python3"
  else
    log_check_fail "Script gerar_oficio.py ausente"
  fi

  SMOKE_PROMPT="Verifique se gerar_oficio.py importa sem erros: python3 -c 'import importlib; importlib.import_module(\"gerar_oficio\")'."
}

# --- 6. Integration ---

test_EX25() {
  CURRENT_FEATURE_NAME="Google Drive"
  CURRENT_FEATURE_CATEGORY="Integration"
  local skill="excrtx-integrate-gdrive"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"

  # Check Google credentials
  local creds_ok=false
  if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
    creds_ok=true
  elif [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ] && [ -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
    creds_ok=true
  elif command -v gcloud >/dev/null 2>&1; then
    if gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>/dev/null | grep -q "@"; then
      creds_ok=true
    fi
  fi

  if $creds_ok; then
    log_check_pass "Google credentials disponíveis"
  elif [ "$SKIP_API" = "1" ]; then
    log_check_pending "Google credentials — pendente de auth"
  else
    log_check_fail "Google credentials não encontradas"
  fi

  SMOKE_PROMPT="Verifique se o patch de Drive search (trashed=false, nextPageToken) está aplicado."
}

test_EX26() {
  CURRENT_FEATURE_NAME="OAuth MCP"
  CURRENT_FEATURE_CATEGORY="Integration"
  local skill="excrtx-integrate-oauth"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps

  SMOKE_PROMPT="Verifique se a skill documenta validação em 3 camadas (mcp list, mcp test, sessão)."
}

test_EX27() {
  CURRENT_FEATURE_NAME="DocBrain Parser"
  CURRENT_FEATURE_CATEGORY="Integration"
  local skill="excrtx-integrate-docbrain"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-memory-intake"
  check_tool_in_path "git"
  check_tool_in_path "npm"

  local docbrain_dir="${EXOCORTEX_DOCBRAIN_DIR:-$EXOCORTEX_HOME/tools/docbrain}"
  check_dir_exists "$docbrain_dir" "DocBrain repo"

  check_api_key "OPENROUTER_API_KEY" "DocBrain LLM routing"

  SMOKE_PROMPT="Verifique se o DocBrain repo está clonado e buildado em $docbrain_dir."
}

test_EX28() {
  CURRENT_FEATURE_NAME="NotebookLM Router"
  CURRENT_FEATURE_CATEGORY="Integration"
  local skill="excrtx-integrate-nlmroute"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps
  check_tool_in_path "uv"
  check_tool_in_path "notebooklm-mcp"

  if command -v nlm >/dev/null 2>&1; then
    log_check_pass "nlm CLI disponível"
    if nlm login --check >/dev/null 2>&1; then
      log_check_pass "nlm autenticado"
    elif [ "$SKIP_API" = "1" ]; then
      log_check_pending "nlm login não autenticado — pendente de credencial"
    else
      log_check_fail "nlm login não autenticado"
    fi
  elif [ "$SKIP_API" = "1" ]; then
    log_check_pending "nlm CLI não instalado — pendente"
  else
    log_check_fail "nlm CLI não encontrado"
  fi

  SMOKE_PROMPT="Verifique se nlm CLI está funcional e o MCP server notebooklm está registrado."
}

test_EX29() {
  CURRENT_FEATURE_NAME="NotebookLM Ops"
  CURRENT_FEATURE_CATEGORY="Integration"
  local skill="excrtx-integrate-nlmops"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_skill_dep "excrtx-integrate-nlmroute"

  SMOKE_PROMPT="Verifique se a skill define as 6 etapas do workflow NLM."
}

test_EX30() {
  CURRENT_FEATURE_NAME="Browser Automation"
  CURRENT_FEATURE_CATEGORY="Integration"
  local skill="excrtx-integrate-browser"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps

  local browser_script="$SKILLS_DST/$skill/scripts/browser-use.sh"
  local browser_runtime="$SKILLS_DST/$skill/.runtime"
  local browser_uv="$browser_runtime/uv/uv"
  if [ -f "$browser_script" ]; then
    check_script_executable "$browser_script" "browser-use.sh"
  else
    log_check_fail "Script browser-use.sh ausente"
  fi

  if command -v uv >/dev/null 2>&1; then
    log_check_pass "uv disponível no PATH ($(command -v uv))"
  elif [ -x "$browser_uv" ]; then
    log_check_pass "uv disponível no runtime local da skill ($browser_uv)"
  else
    log_check_fail "uv ausente no PATH e no runtime local da Browser Automation ($browser_uv)"
  fi

  SMOKE_PROMPT="Verifique se browser-use.sh responde a 'state' sem erro fatal."
}

# --- 7. Harness & Infrastructure ---

test_EX31() {
  CURRENT_FEATURE_NAME="Prompt Log"
  CURRENT_FEATURE_CATEGORY="Harness & Infrastructure"
  local skill="excrtx-harness-promptlog"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps
  check_no_tool_deps

  SMOKE_PROMPT="Verifique se MEMORY.md existe e contém registros de prompts."
}

test_EX32() {
  CURRENT_FEATURE_NAME="Codex Integration"
  CURRENT_FEATURE_CATEGORY="Harness & Infrastructure"
  local skill="excrtx-harness-codexint"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description"
  check_skill_dep "excrtx-harness-core"

  SMOKE_PROMPT="Verifique se a skill define os dois modos (CLI e provider)."
}

test_EX33() {
  CURRENT_FEATURE_NAME="Codex Core Harness"
  CURRENT_FEATURE_CATEGORY="Harness & Infrastructure"
  local skill="excrtx-harness-core"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description"
  check_no_skill_deps
  check_tool_in_path "python3"

  SMOKE_PROMPT="Verifique se os scripts runner e review existem."
}

test_EX34() {
  CURRENT_FEATURE_NAME="Hermes Ops"
  CURRENT_FEATURE_CATEGORY="Harness & Infrastructure"
  local skill="excrtx-harness-hermesops"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description"
  check_skill_dep "excrtx-harness-core"
  check_skill_dep "excrtx-harness-codexint"

  SMOKE_PROMPT="Verifique se a skill define Trilho A (CLI) e Trilho B (Delegação)."
}

test_EX35() {
  CURRENT_FEATURE_NAME="Surface Architecture"
  CURRENT_FEATURE_CATEGORY="Harness & Infrastructure"
  local skill="excrtx-harness-surfaces"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps

  SMOKE_PROMPT="Verifique se a skill define Gateway, UI/Web e TUI como superfícies."
}

test_EX48() {
  CURRENT_FEATURE_NAME="Modo imbroke"
  CURRENT_FEATURE_CATEGORY="Behavior & Governance"
  local skill="excrtx-harness-imbroke"

  check_skill_exists "$skill"
  check_frontmatter "$skill" "name" "description" "version"
  check_no_skill_deps

  local repo_root
  repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  local script="$repo_root/scripts/openrouter_free_model_router.py"

  check_file_exists "$script" "Roteador OpenRouter free"

  if python3 "$script" --status >/dev/null 2>&1; then
    log_check_pass "Script do roteador funcional (--status exit 0)"
  else
    log_check_fail "Script do roteador falhou (--status exit diferente de 0)"
  fi

  SMOKE_PROMPT="Verifique o status do modo imbroke e garanta que o rating na escala 1-10 e warnings correspondentes são exibidos."
}

# =============================================================================
# Dogfood conversacional reproduzível
# =============================================================================
# Este arquivo continua podendo ser sourced por run-provisioning-tests.sh.
# Quando executado diretamente, expõe alvos pequenos para o novo harness.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  set -euo pipefail
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

  case "${1:-}" in
    dogfood-catalog)
      python "$REPO_ROOT/scripts/dogfood_validate_catalog.py" \
        --root "$REPO_ROOT"
      ;;
    dogfood-p0)
      run_id="dogfood-p0-$(date +%Y%m%d-%H%M%S)"
      for feature_id in EX-08 EX-25 EX-30 EX-33 EX-48; do
        python "$REPO_ROOT/scripts/dogfood_features.py" run "$feature_id" \
          --root "$REPO_ROOT" \
          --run-id "$run_id" \
          --dry-run-agent >/dev/null
      done
      python "$REPO_ROOT/scripts/dogfood_features.py" summarize "$REPO_ROOT/.dogfood/runs/$run_id"
      ;;
    dogfood-real-ex08)
      run_id="dogfood-real-ex08-$(date +%Y%m%d-%H%M%S)"
      python "$REPO_ROOT/scripts/dogfood_features.py" run EX-08 \
        --root "$REPO_ROOT" \
        --run-id "$run_id" \
        --real-agent >/dev/null
      python "$REPO_ROOT/scripts/dogfood_features.py" summarize "$REPO_ROOT/.dogfood/runs/$run_id"
      ;;
    dogfood-real-p0)
      run_id="dogfood-real-p0-$(date +%Y%m%d-%H%M%S)"
      for feature_id in EX-08 EX-25 EX-30 EX-33 EX-48; do
        DOGFOOD_AGENT_TIMEOUT="${DOGFOOD_AGENT_TIMEOUT:-120}" \
          python "$REPO_ROOT/scripts/dogfood_features.py" run "$feature_id" \
          --root "$REPO_ROOT" \
          --run-id "$run_id" \
          --real-agent >/dev/null
      done
      python "$REPO_ROOT/scripts/dogfood_features.py" summarize "$REPO_ROOT/.dogfood/runs/$run_id"
      ;;
    ""|--help|-h)
      cat <<'USAGE'
Uso direto:
  ./scripts/test-registry.sh dogfood-catalog
  ./scripts/test-registry.sh dogfood-p0
  ./scripts/test-registry.sh dogfood-real-ex08
  ./scripts/test-registry.sh dogfood-real-p0

Uso tradicional:
  source scripts/test-registry.sh  # feito por run-provisioning-tests.sh
USAGE
      ;;
    *)
      echo "Alvo desconhecido: $1" >&2
      echo "Use: dogfood-catalog | dogfood-p0 | dogfood-real-ex08 | dogfood-real-p0" >&2
      exit 2
      ;;
  esac
fi
