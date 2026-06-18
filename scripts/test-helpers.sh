#!/usr/bin/env bash
# =============================================================================
# Exocórtex — Harness Helpers (test-helpers.sh)
# =============================================================================
# Funções reutilizáveis para o harness de verificação pós-provisionamento.
# Sourced por run-provisioning-tests.sh
# =============================================================================

# --- Cores ---
_RED='\033[0;31m'
_GREEN='\033[0;32m'
_YELLOW='\033[1;33m'
_CYAN='\033[0;36m'
_GRAY='\033[0;90m'
_BLUE='\033[0;34m'
_MAGENTA='\033[0;35m'
_BOLD='\033[1m'
_DIM='\033[2m'
_NC='\033[0m'

# --- Estado global ---
declare -a PASSED_FEATURES=()
declare -a FAILED_FEATURES=()
declare -a REPAIRED_FEATURES=()
declare -a PENDING_FEATURES=()
declare -a DEFINITIVE_FAILS=()
declare -A SMOKE_PROMPTS_MAP=()

# Estado do teste corrente
CURRENT_FEATURE_ID=""
CURRENT_FEATURE_NAME=""
CURRENT_FEATURE_CATEGORY=""
CURRENT_SKILL=""
CURRENT_CHECKS_PASSED=0
CURRENT_CHECKS_FAILED=0
CURRENT_CHECKS_TOTAL=0
CURRENT_FAIL_DETAILS=()
CURRENT_PASS_DETAILS=()
SMOKE_PROMPT=""

# Contadores globais
TOTAL_TESTED=0
TOTAL_PASSED=0
TOTAL_FAILED=0
TOTAL_REPAIRED=0
TOTAL_PENDING=0
TOTAL_SMOKE_SKIPPED=0

# Configuração
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"
ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"
SKILLS_DST="$HERMES_HOME/skills/excrtx"
HARNESS_MODEL="${EXOCORTEX_HARNESS_MODEL:-${EXOCORTEX_MODEL:-}}"
REPO_PATH="${EXOCORTEX_REPO_PATH:-}"
SYNC_ENABLED="${EXOCORTEX_SYNC_ENABLED:-1}"
NO_REPAIR="${NO_REPAIR:-0}"
NO_ISSUES="${NO_ISSUES:-0}"
NO_SYNC="${NO_SYNC:-0}"
NO_SMOKE="${NO_SMOKE:-0}"
SKIP_API="${SKIP_API:-0}"
FAST_FAIL="${FAST_FAIL:-0}"
VERBOSE="${VERBOSE:-0}"
MAX_REPAIR_ATTEMPTS=3

# Timestamp do run
RUN_TIMESTAMP="$(date +%Y-%m-%d-%H%M%S)"
RUN_ISO="$(date -Iseconds)"
REPORT_FILE=""
REPAIRS_DIR=""
LOG_BUFFER=""

# --- Mapa de dependências (feature → upstream deps) ---
declare -A DEPENDENCY_MAP=(
  ["EX-02"]="EX-01"
  ["EX-03"]="EX-31"
  ["EX-06"]="EX-05"
  ["EX-07"]="EX-11 EX-05"
  ["EX-10"]="EX-22 EX-11"
  ["EX-12"]="EX-11"
  ["EX-13"]="EX-11"
  ["EX-14"]="EX-11 EX-13"
  ["EX-15"]="EX-11 EX-13"
  ["EX-16"]="EX-11"
  ["EX-17"]="EX-11 EX-08 EX-22 EX-35"
  ["EX-19"]="EX-20"
  ["EX-20"]="EX-11"
  ["EX-21"]="EX-18 EX-19"
  ["EX-22"]="EX-11"
  ["EX-23"]="EX-20 EX-19 EX-25"
  ["EX-24"]="EX-18"
  ["EX-27"]="EX-17"
  ["EX-29"]="EX-28"
  ["EX-32"]="EX-33"
  ["EX-34"]="EX-33 EX-32"
)

# Feature IDs que são gates (muitos dependem delas)
GATE_FEATURES=("EX-05" "EX-11" "EX-18" "EX-20")

# --- Feature ID ↔ Skill name mapping ---
declare -A FEATURE_SKILL_MAP=(
  ["EX-01"]="excrtx-onboard-welcome"
  ["EX-02"]="excrtx-onboard-interview"
  ["EX-03"]="excrtx-assess-selftest"
  ["EX-04"]="excrtx-assess-repofit"
  ["EX-05"]="excrtx-behavior-vetor"
  ["EX-06"]="excrtx-behavior-canvas"
  ["EX-07"]="excrtx-behavior-briefing"
  ["EX-08"]="excrtx-govern-draftfirst"
  ["EX-09"]="excrtx-govern-tools"
  ["EX-10"]="excrtx-harness-kanban"
  ["EX-11"]="excrtx-memory-manager"
  ["EX-12"]="excrtx-memory-wikiadapt"
  ["EX-13"]="excrtx-memory-newmicro"
  ["EX-14"]="excrtx-memory-mvsetup"
  ["EX-15"]="excrtx-memory-mvinstall"
  ["EX-16"]="excrtx-memory-opsmemory"
  ["EX-17"]="excrtx-memory-intake"
  ["EX-18"]="excrtx-quality-antislop"
  ["EX-19"]="excrtx-quality-taste"
  ["EX-20"]="excrtx-quality-designsys"
  ["EX-21"]="excrtx-quality-gate"
  ["EX-22"]="excrtx-produce-artifacts"
  ["EX-23"]="excrtx-produce-slides"
  ["EX-24"]="excrtx-produce-oficios"
  ["EX-25"]="excrtx-integrate-gdrive"
  ["EX-26"]="excrtx-integrate-oauth"
  ["EX-27"]="excrtx-integrate-docbrain"
  ["EX-28"]="excrtx-integrate-nlmroute"
  ["EX-29"]="excrtx-integrate-nlmops"
  ["EX-30"]="excrtx-integrate-browser"
  ["EX-31"]="excrtx-harness-promptlog"
  ["EX-32"]="excrtx-harness-codexint"
  ["EX-33"]="excrtx-harness-core"
  ["EX-34"]="excrtx-harness-hermesops"
  ["EX-35"]="excrtx-harness-surfaces"
  ["EX-48"]="excrtx-harness-imbroke"
  ["EX-49"]="excrtx-behavior-accuracy"
  ["EX-50"]="excrtx-harness-tooldev"
  ["EX-51"]="excrtx-hermes-extensions"
  ["EX-52"]="excrtx-quality-gate"
)

# =============================================================================
# Logging
# =============================================================================

_log() { echo -e "$1"; LOG_BUFFER+="$1"$'\n'; }
_vlog() { [ "$VERBOSE" = "1" ] && _log "$1" || true; }

log_test_start() {
  local id="$1" name="$2"
  _log ""
  _log "${_BOLD}━━━ ${id} — ${name} ━━━${_NC}"
  _log "${_GRAY}  Início: $(date -Iseconds)${_NC}"
  _vlog "${_DIM}  Path:   $SKILLS_DST/$name/${_NC}"
  # Show upstream dependencies if any
  if [ -n "${DEPENDENCY_MAP[$id]:-}" ]; then
    _vlog "${_DIM}  Deps:   ${DEPENDENCY_MAP[$id]}${_NC}"
  fi
  # Show dependents (who needs this feature)
  if [ "$VERBOSE" = "1" ]; then
    local deps_of_me=""
    for key in "${!DEPENDENCY_MAP[@]}"; do
      if [[ " ${DEPENDENCY_MAP[$key]} " == *" $id "* ]]; then
        deps_of_me+="$key "
      fi
    done
    [ -n "$deps_of_me" ] && _vlog "${_DIM}  Needed: ${deps_of_me}(dependentes)${_NC}"
  fi
  FEATURE_START_TIME=$(date +%s%N)
}

log_check_pass() {
  local msg="$1"
  _log "  ${_GREEN}✓${_NC} ${msg}"
  CURRENT_CHECKS_PASSED=$((CURRENT_CHECKS_PASSED + 1))
  CURRENT_CHECKS_TOTAL=$((CURRENT_CHECKS_TOTAL + 1))
  CURRENT_PASS_DETAILS+=("$msg")
}

log_check_fail() {
  local msg="$1"
  _log "  ${_RED}✗${_NC} ${msg}"
  CURRENT_CHECKS_FAILED=$((CURRENT_CHECKS_FAILED + 1))
  CURRENT_CHECKS_TOTAL=$((CURRENT_CHECKS_TOTAL + 1))
  CURRENT_FAIL_DETAILS+=("$msg")
}

log_check_pending() {
  local msg="$1"
  _log "  ${_YELLOW}⏳${_NC} ${msg}"
  CURRENT_CHECKS_TOTAL=$((CURRENT_CHECKS_TOTAL + 1))
  CURRENT_PASS_DETAILS+=("PENDING: $msg")
}

log_test_result() {
  local id="$1" result="$2"
  local elapsed=""
  if [ -n "${FEATURE_START_TIME:-}" ]; then
    local end_ns=$(date +%s%N)
    local diff_ms=$(( (end_ns - FEATURE_START_TIME) / 1000000 ))
    elapsed=" [${diff_ms}ms]"
  fi
  case "$result" in
    PASS)    _log "  ${_GREEN}${_BOLD}→ PASS${_NC} (${CURRENT_CHECKS_PASSED}/${CURRENT_CHECKS_TOTAL})${_DIM}${elapsed}${_NC}" ;;
    PARTIAL) _log "  ${_YELLOW}${_BOLD}→ PARTIAL${_NC} (${CURRENT_CHECKS_PASSED}/${CURRENT_CHECKS_TOTAL})${_DIM}${elapsed}${_NC}" ;;
    FAIL)    _log "  ${_RED}${_BOLD}→ FAIL${_NC} (${CURRENT_CHECKS_PASSED}/${CURRENT_CHECKS_TOTAL})${_DIM}${elapsed}${_NC}" ;;
    PENDING) _log "  ${_YELLOW}${_BOLD}→ PENDING (API key)${_NC}${_DIM}${elapsed}${_NC}" ;;
  esac
  # In verbose, show the exact hermes command that will run in Fase 2
  if [ "$VERBOSE" = "1" ] && [ -n "$SMOKE_PROMPT" ]; then
    # Escape prompt for display (single line for short, multiline for long)
    local escaped_prompt
    escaped_prompt=$(echo "$SMOKE_PROMPT" | tr '\n' ' ' | sed 's/  */ /g')
    _vlog ""
    _vlog "${_BLUE}  \$ $HERMES_BIN chat -q \"${escaped_prompt}\" -m \"$HARNESS_MODEL\" -Q${_NC}"
  fi
}

# =============================================================================
# Check functions (Fase 1 — deterministic)
# =============================================================================

check_skill_exists() {
  local skill="$1"
  if [ -f "$SKILLS_DST/$skill/SKILL.md" ]; then
    log_check_pass "Skill '$skill' presente"
    if [ "$VERBOSE" = "1" ]; then
      local fsize=$(wc -c < "$SKILLS_DST/$skill/SKILL.md" 2>/dev/null)
      local flines=$(wc -l < "$SKILLS_DST/$skill/SKILL.md" 2>/dev/null)
      local nfiles=$(find "$SKILLS_DST/$skill" -type f 2>/dev/null | wc -l)
      _vlog "${_DIM}    ↳ SKILL.md: ${flines} linhas, ${fsize} bytes | Dir: ${nfiles} arquivo(s)${_NC}"
      # Show first line of description if available
      local desc_line
      desc_line=$(grep -m1 '^description:' "$SKILLS_DST/$skill/SKILL.md" 2>/dev/null | sed 's/^description: *//' | head -c 100)
      [ -n "$desc_line" ] && _vlog "${_DIM}    ↳ Desc: ${desc_line}${_NC}"
      # List files in the skill dir
      local extra_files
      extra_files=$(find "$SKILLS_DST/$skill" -type f ! -name 'SKILL.md' -printf '      %P\n' 2>/dev/null | head -8)
      [ -n "$extra_files" ] && _vlog "${_DIM}    ↳ Conteúdo:${_NC}" && _vlog "${_DIM}${extra_files}${_NC}"
    fi
    return 0
  else
    log_check_fail "Skill '$skill' não encontrada em $SKILLS_DST/$skill/SKILL.md"
    return 1
  fi
}

check_frontmatter() {
  local skill="$1"
  shift
  local skill_file="$SKILLS_DST/$skill/SKILL.md"
  if [ ! -f "$skill_file" ]; then
    log_check_fail "Frontmatter: arquivo não existe ($skill_file)"
    return 1
  fi

  # Check YAML frontmatter delimiters
  local first_line
  first_line=$(head -1 "$skill_file")
  if [ "$first_line" != "---" ]; then
    log_check_fail "Frontmatter: sem delimitador '---' no início ($skill)"
    return 1
  fi

  # Extract frontmatter
  local fm
  fm=$(sed -n '2,/^---$/p' "$skill_file" | head -n -1)
  if [ -z "$fm" ]; then
    log_check_fail "Frontmatter: vazio ou malformado ($skill)"
    return 1
  fi

  # Check required fields
  local all_ok=true
  for field in "$@"; do
    if echo "$fm" | grep -qE "^${field}:"; then
      if [ "$VERBOSE" = "1" ]; then
        local val
        val=$(echo "$fm" | grep -m1 "^${field}:" | sed "s/^${field}: *//" | head -c 80)
        _vlog "${_DIM}    ↳ ${field}: ${val}${_NC}"
      fi
    else
      log_check_fail "Frontmatter: campo '$field' ausente ($skill)"
      all_ok=false
    fi
  done

  if $all_ok; then
    log_check_pass "Frontmatter válido ($skill)"
    return 0
  fi
  return 1
}

check_skill_dep() {
  local dep_skill="$1"
  if [ -f "$SKILLS_DST/$dep_skill/SKILL.md" ]; then
    log_check_pass "Dep skill '$dep_skill' presente"
    if [ "$VERBOSE" = "1" ]; then
      local ver
      ver=$(grep -am1 '^version:' "$SKILLS_DST/$dep_skill/SKILL.md" 2>/dev/null | sed 's/^version: *//' || echo "?")
      _vlog "${_DIM}    ↳ v${ver} @ $SKILLS_DST/$dep_skill/${_NC}"
    fi
    return 0
  else
    log_check_fail "Dep skill '$dep_skill' ausente"
    _vlog "${_DIM}    ↳ Esperado em: $SKILLS_DST/$dep_skill/SKILL.md${_NC}"
    return 1
  fi
}

check_no_skill_deps() {
  log_check_pass "Sem dependências de skills"
  return 0
}

check_tool_in_path() {
  local tool="$1"
  local desc="${2:-$tool}"
  if command -v "$tool" >/dev/null 2>&1; then
    log_check_pass "Tool '$desc' disponível ($(command -v "$tool"))"
    return 0
  elif [ -x "$HERMES_HOME/bin/$tool" ]; then
    log_check_pass "Tool '$desc' disponível ($HERMES_HOME/bin/$tool)"
    return 0
  else
    log_check_fail "Tool '$desc' não encontrada no PATH nem em \$HERMES_HOME/bin/"
    return 1
  fi
}

check_no_tool_deps() {
  log_check_pass "Sem dependências de tools"
  return 0
}

check_file_exists() {
  local path="$1"
  local desc="${2:-$path}"
  if [ -f "$path" ]; then
    log_check_pass "Arquivo '$desc' presente"
    if [ "$VERBOSE" = "1" ]; then
      local fsize=$(wc -c < "$path" 2>/dev/null)
      local fmod=$(stat -c '%y' "$path" 2>/dev/null | cut -d. -f1)
      _vlog "${_DIM}    ↳ ${fsize} bytes, mod: ${fmod}${_NC}"
    fi
    return 0
  else
    log_check_fail "Arquivo '$desc' ausente ($path)"
    return 1
  fi
}

check_dir_exists() {
  local path="$1"
  local desc="${2:-$path}"
  if [ -d "$path" ]; then
    log_check_pass "Diretório '$desc' presente"
    if [ "$VERBOSE" = "1" ]; then
      local nfiles=$(find "$path" -maxdepth 1 -type f 2>/dev/null | wc -l)
      local ndirs=$(find "$path" -maxdepth 1 -type d 2>/dev/null | wc -l)
      ndirs=$((ndirs - 1))  # exclude self
      _vlog "${_DIM}    ↳ ${nfiles} arquivo(s), ${ndirs} subdir(s) em ${path}${_NC}"
    fi
    return 0
  else
    log_check_fail "Diretório '$desc' ausente ($path)"
    return 1
  fi
}

check_script_executable() {
  local path="$1"
  local desc="${2:-$path}"
  if [ -x "$path" ]; then
    log_check_pass "Script '$desc' executável"
    return 0
  else
    log_check_fail "Script '$desc' sem permissão de execução ($path)"
    return 1
  fi
}

check_api_key() {
  local var_name="$1"
  local desc="${2:-$var_name}"
  local val="${!var_name:-}"
  if [ -n "$val" ]; then
    log_check_pass "API key '$desc' definida"
    return 0
  elif [ "$SKIP_API" = "1" ]; then
    log_check_pending "'$desc' não definida — pendente de key"
    return 2  # special: pending
  else
    log_check_fail "API key '$desc' não definida"
    return 1
  fi
}

# =============================================================================
# Test lifecycle
# =============================================================================

reset_test_state() {
  CURRENT_CHECKS_PASSED=0
  CURRENT_CHECKS_FAILED=0
  CURRENT_CHECKS_TOTAL=0
  CURRENT_FAIL_DETAILS=()
  CURRENT_PASS_DETAILS=()
  SMOKE_PROMPT=""
  CURRENT_FEATURE_NAME=""
  CURRENT_FEATURE_CATEGORY=""
  CURRENT_SKILL=""
}

# Run a single feature test. Called by the orchestrator.
# Usage: run_feature_test "EX-01"
run_feature_test() {
  local feature_id="$1"
  local num="${feature_id#EX-}"
  num="${num#0}"  # remove leading zero
  local func_name="test_EX${num}"

  CURRENT_FEATURE_ID="$feature_id"
  reset_test_state

  # Check if test function exists
  if ! declare -f "$func_name" >/dev/null 2>&1; then
    _log "  ${_YELLOW}⚠${_NC} Sem função de teste para $feature_id (esperado: $func_name)"
    return 0
  fi

  log_test_start "$feature_id" "${FEATURE_SKILL_MAP[$feature_id]:-unknown}"

  # Execute test (Fase 1 checks)
  set +e
  "$func_name"
  set -e

  # Determine result
  local result
  if [ $CURRENT_CHECKS_FAILED -eq 0 ]; then
    result="PASS"
    PASSED_FEATURES+=("$feature_id")
    TOTAL_PASSED=$((TOTAL_PASSED + 1))
  else
    # Check if it's just pending API keys
    local only_pending=true
    for detail in "${CURRENT_FAIL_DETAILS[@]}"; do
      if [[ "$detail" != *"API key"* ]] && [[ "$detail" != *"pendente"* ]]; then
        only_pending=false
        break
      fi
    done
    if $only_pending && [ "$SKIP_API" = "1" ]; then
      result="PENDING"
      PENDING_FEATURES+=("$feature_id")
      TOTAL_PENDING=$((TOTAL_PENDING + 1))
    else
      result="FAIL"
      FAILED_FEATURES+=("$feature_id")
      TOTAL_FAILED=$((TOTAL_FAILED + 1))
    fi
  fi

  log_test_result "$feature_id" "$result"
  TOTAL_TESTED=$((TOTAL_TESTED + 1))

  # Save smoke prompt for Fase 2
  if [ -n "$SMOKE_PROMPT" ]; then
    SMOKE_PROMPTS_MAP["$feature_id"]="$SMOKE_PROMPT"
  fi

  # Fast-fail check for gate features
  if [ "$FAST_FAIL" = "1" ] && [ "$result" = "FAIL" ]; then
    for gate in "${GATE_FEATURES[@]}"; do
      if [ "$gate" = "$feature_id" ]; then
        _log ""
        _log "${_RED}${_BOLD}⛔ FAST-FAIL: $feature_id é gate feature. Abortando.${_NC}"
        return 1
      fi
    done
  fi

  return 0
}

# Run smoke test for a single feature via Hermes headless
# Called after deterministic checks pass, if SMOKE_PROMPT is set
run_smoke_test() {
  local feature_id="$1"
  local smoke_prompt="$2"
  local skill_name="${FEATURE_SKILL_MAP[$feature_id]:-unknown}"

  if [ "$NO_SMOKE" = "1" ]; then
    TOTAL_SMOKE_SKIPPED=$((TOTAL_SMOKE_SKIPPED + 1))
    return 0
  fi

  if [ -z "$smoke_prompt" ]; then
    return 0
  fi

  if [ -z "$HARNESS_MODEL" ]; then
    _log "  ${_YELLOW}⚠ Smoke test pulado — EXOCORTEX_MODEL não configurado${_NC}"
    TOTAL_SMOKE_SKIPPED=$((TOTAL_SMOKE_SKIPPED + 1))
    return 0
  fi

  if ! can_invoke_hermes; then
    _log "  ${_YELLOW}⚠ Hermes não disponível — smoke test pulado${_NC}"
    TOTAL_SMOKE_SKIPPED=$((TOTAL_SMOKE_SKIPPED + 1))
    return 0
  fi

  # Build the full prompt with context
  local full_prompt="Você é o Hermes executando smoke test pós-provisionamento.
Feature: ${feature_id} (${skill_name})
Skill: \$HERMES_HOME/skills/excrtx/${skill_name}/
Acervo: \$ACERVO/

Tarefa: ${smoke_prompt}

Responda de forma concisa. Se tudo estiver OK, diga 'SMOKE_OK'. Se encontrar problema, descreva."

  local escaped_prompt
  escaped_prompt=$(echo "$full_prompt" | tr '\n' ' ' | sed 's/  */ /g')

  _log ""
  _log "  ${_CYAN}🔥 Smoke test: $feature_id${_NC}"
  _log "  ${_BLUE}\$ $HERMES_BIN chat -q \"${escaped_prompt}\" -m \"$HARNESS_MODEL\" -Q${_NC}"

  local smoke_output
  local smoke_exit=0
  local smoke_start=$(date +%s)
  smoke_output=$($HERMES_BIN chat -q "$full_prompt" -m "$HARNESS_MODEL" -Q 2>&1) || smoke_exit=$?
  local smoke_end=$(date +%s)
  local smoke_elapsed=$(( smoke_end - smoke_start ))

  # Detect execution failures (model not found, API error, timeout, etc.)
  if [ "$smoke_exit" -ne 0 ] || echo "$smoke_output" | grep -qiE 'error|not found|invalid|unauthorized|403|401|timeout|connection refused|model.*not.*available'; then
    _log "  ${_RED}✗ Smoke test FAIL (exit $smoke_exit) — Hermes não executou o modelo${_NC}"
    if [ -n "$smoke_output" ]; then
      _log "  ${_DIM}┌─ Output:${_NC}"
      while IFS= read -r _sline; do
        _log "  ${_DIM}│ ${_sline}${_NC}"
      done <<< "$(echo "$smoke_output" | tail -10)"
      _log "  ${_DIM}└─${_NC}"
    fi
    CURRENT_CHECKS_FAILED=$((CURRENT_CHECKS_FAILED + 1))
    return 1
  fi

  _log "  ${_GRAY}Hermes respondeu em ${smoke_elapsed}s${_NC}"

  # Show output
  if [ -n "$smoke_output" ]; then
    _log "  ${_DIM}┌─ Output:${_NC}"
    while IFS= read -r _sline; do
      _log "  ${_DIM}│ ${_sline}${_NC}"
    done <<< "$(echo "$smoke_output" | tail -20)"
    _log "  ${_DIM}└─${_NC}"
  fi

  # Check for SMOKE_OK in output
  if echo "$smoke_output" | grep -qi 'SMOKE_OK'; then
    _log "  ${_GREEN}✓ Smoke test PASS${_NC}"
  else
    _log "  ${_YELLOW}⚠ Smoke test: sem confirmação SMOKE_OK (revisar output)${_NC}"
  fi
}

# =============================================================================
# Hermes headless integration (Fase 2)
# =============================================================================

# Resolved path to hermes binary
HERMES_BIN=""

can_invoke_hermes() {
  # Check PATH first
  if command -v hermes >/dev/null 2>&1; then
    HERMES_BIN="hermes"
  # Check hermes-agent venv (standard install location)
  elif [ -x "$HERMES_HOME/hermes-agent/venv/bin/hermes" ]; then
    HERMES_BIN="$HERMES_HOME/hermes-agent/venv/bin/hermes"
  # Check hermes-agent direct
  elif [ -x "$HERMES_HOME/hermes-agent/hermes" ]; then
    HERMES_BIN="$HERMES_HOME/hermes-agent/hermes"
  else
    return 1
  fi
  if [ ! -f "$HERMES_HOME/SOUL.md" ]; then
    return 1
  fi
  return 0
}

# Invoke Hermes headless for repair
# Usage: invoke_hermes_repair "EX-27" "npm not found" "excrtx-integrate-docbrain"
invoke_hermes_repair() {
  local feature_id="$1"
  local error_desc="$2"
  local skill_name="${FEATURE_SKILL_MAP[$feature_id]:-unknown}"
  local attempt=0
  local repaired=false

  while [ $attempt -lt $MAX_REPAIR_ATTEMPTS ] && ! $repaired; do
    attempt=$((attempt + 1))
    _log ""
    _log "  ${_CYAN}🔧 Repair tentativa $attempt/$MAX_REPAIR_ATTEMPTS para $feature_id${_NC}"

    local prompt="Você está executando verificação pós-provisionamento do Exocórtex.
A feature ${feature_id} (${skill_name}) falhou na verificação.

Erro detectado: ${error_desc}

Skill path: \$HERMES_HOME/skills/excrtx/${skill_name}/
Acervo: \$ACERVO/

Tente diagnosticar e consertar o problema. Logue cada ação tomada.
Se não conseguir, explique o que falta.
Não altere SOUL.md. Não instale nada sem verificar antes."

    _vlog "${_MAGENTA}  ┌─ Hermes repair prompt:${_NC}"
    _vlog "${_DIM}  │ Feature: $feature_id ($skill_name)${_NC}"
    _vlog "${_DIM}  │ Erro: $error_desc${_NC}"
    _vlog "${_DIM}  │ Modelo: $HARNESS_MODEL${_NC}"
    _vlog "${_MAGENTA}  └─${_NC}"

    # Log exact command
    local escaped_repair_prompt
    escaped_repair_prompt=$(echo "$prompt" | tr '\n' ' ' | sed 's/  */ /g')
    _log "  ${_BLUE}\$ $HERMES_BIN chat -q \"${escaped_repair_prompt}\" -m \"$HARNESS_MODEL\" -Q${_NC}"

    local repair_output
    repair_output=$($HERMES_BIN chat -q "$prompt" -m "$HARNESS_MODEL" -Q 2>&1) || true

    _log "  ${_GRAY}Hermes output (resumo):${_NC}"
    while IFS= read -r _oline; do
      _log "  ${_DIM}  │ ${_oline}${_NC}"
    done <<< "$(echo "$repair_output" | tail -10)"

    # Re-run deterministic checks
    reset_test_state
    local func_name="test_EX${feature_id#EX-0}"
    func_name="test_EX${func_name#test_EX}"
    if declare -f "$func_name" >/dev/null 2>&1; then
      set +e
      "$func_name" 2>/dev/null
      set -e
    fi

    if [ $CURRENT_CHECKS_FAILED -eq 0 ]; then
      repaired=true
      _log "  ${_GREEN}✓ Reparado na tentativa $attempt${_NC}"

      # Save repair manifest
      save_repair_manifest "$feature_id" "$skill_name" "$error_desc" \
        "$attempt" "$repair_output"
    fi
  done

  if $repaired; then
    REPAIRED_FEATURES+=("$feature_id")
    TOTAL_REPAIRED=$((TOTAL_REPAIRED + 1))
    # Remove from failed, adjust counts
    local new_failed=()
    for f in "${FAILED_FEATURES[@]}"; do
      [ "$f" != "$feature_id" ] && new_failed+=("$f")
    done
    FAILED_FEATURES=("${new_failed[@]}")
    TOTAL_FAILED=$((TOTAL_FAILED - 1))
    return 0
  else
    DEFINITIVE_FAILS+=("$feature_id")
    _log "  ${_RED}✗ Falha definitiva após $MAX_REPAIR_ATTEMPTS tentativas${_NC}"
    return 1
  fi
}

# =============================================================================
# Repair manifest
# =============================================================================

save_repair_manifest() {
  local feature_id="$1" skill_name="$2" error="$3" attempts="$4" output="$5"
  local manifest_dir="$ACERVO/_artifacts/items/repairs"
  mkdir -p "$manifest_dir"

  local manifest_file="$manifest_dir/RPR-${RUN_TIMESTAMP}-${feature_id}.json"
  local escaped_error
  escaped_error=$(echo "$error" | sed 's/"/\\"/g' | tr '\n' ' ')
  local escaped_output
  escaped_output=$(echo "$output" | sed 's/"/\\"/g' | tr '\n' ' ' | cut -c1-2000)

  cat > "$manifest_file" <<EOF
{
  "repair_id": "RPR-${RUN_TIMESTAMP}-${feature_id}",
  "timestamp": "${RUN_ISO}",
  "feature_id": "${feature_id}",
  "skill_name": "${skill_name}",
  "hostname": "$(hostname)",
  "model_used": "${HARNESS_MODEL}",
  "attempts": ${attempts},
  "error": "${escaped_error}",
  "hermes_output_summary": "${escaped_output}",
  "sync_status": "pending"
}
EOF
  _log "  ${_GRAY}Manifest: $manifest_file${_NC}"
}

# =============================================================================
# Regression
# =============================================================================

# Get features that depend on a given feature (reverse lookup)
get_dependents() {
  local feature_id="$1"
  local dependents=()
  for key in "${!DEPENDENCY_MAP[@]}"; do
    if [[ " ${DEPENDENCY_MAP[$key]} " == *" $feature_id "* ]]; then
      dependents+=("$key")
    fi
  done
  echo "${dependents[*]}"
}

run_regression() {
  local repaired_id="$1"
  local dependents
  dependents=$(get_dependents "$repaired_id")

  if [ -z "$dependents" ]; then
    _log "  ${_GRAY}Sem dependentes para regredir${_NC}"
    return 0
  fi

  _log ""
  _log "  ${_CYAN}🔄 Regressão: re-testando dependentes de $repaired_id: $dependents${_NC}"
  for dep in $dependents; do
    run_feature_test "$dep" || true
  done
}

# =============================================================================
# GitHub issue creation via Hermes
# =============================================================================

create_github_issue() {
  local feature_id="$1"
  local skill_name="${FEATURE_SKILL_MAP[$feature_id]:-unknown}"
  local fail_info="${CURRENT_FAIL_DETAILS[*]:-unknown error}"

  _log "  ${_CYAN}📋 Criando issue para $feature_id...${_NC}"

  local prompt="Crie uma issue no repositório elderbernardi/exocortex.saas com:

Título: [BUG] Feature ${feature_id} (${skill_name}) — falha pós-provisionamento
Labels: bug, testing

Corpo:
## Contexto
Falha detectada pelo harness de verificação pós-provisionamento.

## Feature
- ID: ${feature_id}
- Skill: ${skill_name}
- Categoria: ${CURRENT_FEATURE_CATEGORY:-unknown}

## Erro
${fail_info}

## Tentativas de reparo
${MAX_REPAIR_ATTEMPTS} tentativas falharam.

## Ambiente
- Host: $(hostname)
- Data: ${RUN_ISO}
- Modelo: ${HARNESS_MODEL}

Use o comando gh ou a tool de GitHub disponível."

  # Log exact command
  local escaped_issue_prompt
  escaped_issue_prompt=$(echo "$prompt" | tr '\n' ' ' | sed 's/  */ /g')
  _log "  ${_BLUE}\$ $HERMES_BIN chat -q \"${escaped_issue_prompt}\" -m \"$HARNESS_MODEL\" -Q${_NC}"

  $HERMES_BIN chat -q "$prompt" -m "$HARNESS_MODEL" -Q 2>&1 || \
    _log "  ${_YELLOW}⚠ Falha ao criar issue (sem gh CLI ou auth?)${_NC}"
}

# =============================================================================
# Report generation
# =============================================================================

generate_report() {
  local report_dir="$ACERVO/_artifacts/items"
  mkdir -p "$report_dir"
  REPORT_FILE="$report_dir/provisioning-test-${RUN_TIMESTAMP}.md"

  cat > "$REPORT_FILE" <<EOF
# Relatório de Verificação Pós-Provisionamento

**Data:** ${RUN_ISO}
**Instância:** $(hostname)
**Modelo:** ${HARNESS_MODEL}

## Resumo

| Métrica | Valor |
|---------|-------|
| Features testadas | ${TOTAL_TESTED} |
| Passaram | ${TOTAL_PASSED} |
| Reparadas | ${TOTAL_REPAIRED} |
| Pendentes (API key) | ${TOTAL_PENDING} |
| Falha definitiva | ${#DEFINITIVE_FAILS[@]} |
| Smoke tests pulados | ${TOTAL_SMOKE_SKIPPED} |

## Features — Resultado

### ✅ Passaram
$(for f in "${PASSED_FEATURES[@]}"; do echo "- ${f} — ${FEATURE_SKILL_MAP[$f]:-}"; done)

### 🔧 Reparadas
$(for f in "${REPAIRED_FEATURES[@]}"; do echo "- ${f} — ${FEATURE_SKILL_MAP[$f]:-}"; done)

### ⏳ Pendentes (API key)
$(for f in "${PENDING_FEATURES[@]}"; do echo "- ${f} — ${FEATURE_SKILL_MAP[$f]:-}"; done)

### ❌ Falha Definitiva
$(for f in "${DEFINITIVE_FAILS[@]}"; do echo "- ${f} — ${FEATURE_SKILL_MAP[$f]:-}"; done)

---
*Gerado por run-provisioning-tests.sh*
EOF

  _log ""
  _log "${_GREEN}📄 Relatório: $REPORT_FILE${_NC}"
}

# =============================================================================
# Summary
# =============================================================================

print_summary() {
  echo ""
  echo "╔═══════════════════════════════════════════════╗"
  echo "║   Verificação Pós-Provisionamento — Resumo   ║"
  echo "╚═══════════════════════════════════════════════╝"
  echo ""
  echo -e "  Testadas:    ${_BOLD}${TOTAL_TESTED}${_NC}"
  echo -e "  Passaram:    ${_GREEN}${TOTAL_PASSED}${_NC}"
  echo -e "  Reparadas:   ${_CYAN}${TOTAL_REPAIRED}${_NC}"
  echo -e "  Pendentes:   ${_YELLOW}${TOTAL_PENDING}${_NC}"
  echo -e "  Falharam:    ${_RED}${#DEFINITIVE_FAILS[@]}${_NC}"
  echo -e "  Smoke skip:  ${_YELLOW}${TOTAL_SMOKE_SKIPPED}${_NC}"
  echo ""
  if [ "$TOTAL_SMOKE_SKIPPED" -gt 0 ] && [ ${#DEFINITIVE_FAILS[@]} -eq 0 ]; then
    echo -e "  ${_YELLOW}${_BOLD}⚠ ${TOTAL_PASSED}/${TOTAL_TESTED} features passaram (determinístico), mas ${TOTAL_SMOKE_SKIPPED} smoke tests foram pulados.${_NC}"
    echo -e "  ${_YELLOW}  Defina EXOCORTEX_MODEL para validação completa: export EXOCORTEX_MODEL=\"seu-modelo\"${_NC}"
  elif [ ${#DEFINITIVE_FAILS[@]} -eq 0 ]; then
    echo -e "  ${_GREEN}${_BOLD}✅ Todas as features operacionais.${_NC}"
  else
    echo -e "  ${_RED}${_BOLD}❌ Falhas definitivas: ${DEFINITIVE_FAILS[*]}${_NC}"
  fi
  echo ""
  [ -n "$REPORT_FILE" ] && echo -e "  📄 Relatório: ${REPORT_FILE}"
  echo ""
}
