1|#!/usr/bin/env bash
2|# =============================================================================
3|# Exocórtex — Harness Helpers (test-helpers.sh)
4|# =============================================================================
5|# Funções reutilizáveis para o harness de verificação pós-provisionamento.
6|# Sourced por run-provisioning-tests.sh
7|# =============================================================================
8|
9|# --- Cores ---
10|_RED='\033[0;31m'
11|_GREEN='\033[0;32m'
12|_YELLOW='\033[1;33m'
13|_CYAN='\033[0;36m'
14|_GRAY='\033[0;90m'
15|_BLUE='\033[0;34m'
16|_MAGENTA='\033[0;35m'
17|_BOLD='\033[1m'
18|_DIM='\033[2m'
19|_NC='\033[0m'
20|
21|# --- Estado global ---
22|declare -a PASSED_FEATURES=()
23|declare -a FAILED_FEATURES=()
24|declare -a REPAIRED_FEATURES=()
25|declare -a PENDING_FEATURES=()
26|declare -a DEFINITIVE_FAILS=()
27|declare -A SMOKE_PROMPTS_MAP=()
28|
29|# Estado do teste corrente
30|CURRENT_FEATURE_ID=""
31|CURRENT_FEATURE_NAME=""
32|CURRENT_FEATURE_CATEGORY=""
33|CURRENT_SKILL=""
34|CURRENT_CHECKS_PASSED=0
35|CURRENT_CHECKS_FAILED=0
36|CURRENT_CHECKS_TOTAL=0
37|CURRENT_FAIL_DETAILS=()
38|CURRENT_PASS_DETAILS=()
39|SMOKE_PROMPT=""
40|
41|# Contadores globais
42|TOTAL_TESTED=0
43|TOTAL_PASSED=0
44|TOTAL_FAILED=0
45|TOTAL_REPAIRED=0
46|TOTAL_PENDING=0
47|
48|# Configuração
49|HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
50|EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"
51|ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"
52|SKILLS_DST="$HERMES_HOME/skills/excrtx"
53|HARNESS_MODEL="${EXOCORTEX_HARNESS_MODEL:-openai/gpt-5.4}"
54|REPO_PATH="${EXOCORTEX_REPO_PATH:-}"
55|SYNC_ENABLED="${EXOCORTEX_SYNC_ENABLED:-1}"
56|NO_REPAIR="${NO_REPAIR:-0}"
57|NO_ISSUES="${NO_ISSUES:-0}"
58|NO_SYNC="${NO_SYNC:-0}"
59|NO_SMOKE="${NO_SMOKE:-0}"
60|SKIP_API="${SKIP_API:-0}"
61|FAST_FAIL="${FAST_FAIL:-0}"
62|VERBOSE="${VERBOSE:-0}"
63|MAX_REPAIR_ATTEMPTS=3
64|
65|# Timestamp do run
66|RUN_TIMESTAMP="$(date +%Y-%m-%d-%H%M%S)"
67|RUN_ISO="$(date -Iseconds)"
68|REPORT_FILE=""
69|REPAIRS_DIR=""
70|LOG_BUFFER=""
71|
72|# --- Mapa de dependências (feature → upstream deps) ---
73|declare -A DEPENDENCY_MAP=(
74|  ["EX-02"]="EX-01"
75|  ["EX-03"]="EX-31"
76|  ["EX-06"]="EX-05"
77|  ["EX-07"]="EX-11 EX-05"
78|  ["EX-10"]="EX-22 EX-11"
79|  ["EX-12"]="EX-11"
80|  ["EX-13"]="EX-11"
81|  ["EX-14"]="EX-11 EX-13"
82|  ["EX-15"]="EX-11 EX-13"
83|  ["EX-16"]="EX-11"
84|  ["EX-17"]="EX-11 EX-08 EX-22 EX-35"
85|  ["EX-19"]="EX-20"
86|  ["EX-20"]="EX-11"
87|  ["EX-21"]="EX-18 EX-19"
88|  ["EX-22"]="EX-11"
89|  ["EX-23"]="EX-20 EX-19 EX-25"
90|  ["EX-24"]="EX-18"
91|  ["EX-27"]="EX-17"
92|  ["EX-29"]="EX-28"
93|  ["EX-32"]="EX-33"
94|  ["EX-34"]="EX-33 EX-32"
95|)
96|
97|# Feature IDs que são gates (muitos dependem delas)
98|GATE_FEATURES=("EX-05" "EX-11" "EX-18" "EX-20")
99|
100|# --- Feature ID ↔ Skill name mapping ---
101|declare -A FEATURE_SKILL_MAP=(
102|  ["EX-01"]="excrtx-onboard-welcome"
103|  ["EX-02"]="excrtx-onboard-interview"
104|  ["EX-03"]="excrtx-assess-selftest"
105|  ["EX-04"]="excrtx-assess-repofit"
106|  ["EX-05"]="excrtx-behavior-vetor"
107|  ["EX-06"]="excrtx-behavior-canvas"
108|  ["EX-07"]="excrtx-behavior-briefing"
109|  ["EX-08"]="excrtx-govern-draftfirst"
110|  ["EX-09"]="excrtx-govern-tools"
111|  ["EX-10"]="excrtx-harness-kanban"
112|  ["EX-11"]="excrtx-memory-manager"
113|  ["EX-12"]="excrtx-memory-wikiadapt"
114|  ["EX-13"]="excrtx-memory-newmicro"
115|  ["EX-14"]="excrtx-memory-mvsetup"
116|  ["EX-15"]="excrtx-memory-mvinstall"
117|  ["EX-16"]="excrtx-memory-opsmemory"
118|  ["EX-17"]="excrtx-memory-intake"
119|  ["EX-18"]="excrtx-quality-antislop"
120|  ["EX-19"]="excrtx-quality-taste"
121|  ["EX-20"]="excrtx-quality-designsys"
122|  ["EX-21"]="excrtx-quality-gate"
123|  ["EX-22"]="excrtx-produce-artifacts"
124|  ["EX-23"]="excrtx-produce-slides"
125|  ["EX-24"]="excrtx-produce-oficios"
126|  ["EX-25"]="excrtx-integrate-gdrive"
127|  ["EX-26"]="excrtx-integrate-oauth"
128|  ["EX-27"]="excrtx-integrate-docbrain"
129|  ["EX-28"]="excrtx-integrate-nlmroute"
130|  ["EX-29"]="excrtx-integrate-nlmops"
131|  ["EX-30"]="excrtx-integrate-browser"
132|  ["EX-31"]="excrtx-harness-promptlog"
133|  ["EX-32"]="excrtx-harness-codexint"
134|  ["EX-33"]="excrtx-harness-core"
135|  ["EX-34"]="excrtx-harness-hermesops"
136|  ["EX-35"]="excrtx-harness-surfaces"
137|  ["EX-48"]="excrtx-harness-imbroke"
138|  ["EX-49"]="excrtx-behavior-accuracy"
139|  ["EX-50"]="excrtx-harness-tooldev"
140|  ["EX-51"]="excrtx-hermes-extensions"
141|  ["EX-52"]="excrtx-quality-gate"
142|)
143|
144|# =============================================================================
145|# Logging
146|# =============================================================================
147|
148|_log() { echo -e "$1"; LOG_BUFFER+="$1"$'\n'; }
149|_vlog() { [ "$VERBOSE" = "1" ] && _log "$1" || true; }
150|
151|log_test_start() {
152|  local id="$1" name="$2"
153|  _log ""
154|  _log "${_BOLD}━━━ ${id} — ${name} ━━━${_NC}"
155|  _log "${_GRAY}  Início: $(date -Iseconds)${_NC}"
156|  _vlog "${_DIM}  Path:   $SKILLS_DST/$name/${_NC}"
157|  # Show upstream dependencies if any
158|  if [ -n "${DEPENDENCY_MAP[$id]:-}" ]; then
159|    _vlog "${_DIM}  Deps:   ${DEPENDENCY_MAP[$id]}${_NC}"
160|  fi
161|  # Show dependents (who needs this feature)
162|  if [ "$VERBOSE" = "1" ]; then
163|    local deps_of_me=""
164|    for key in "${!DEPENDENCY_MAP[@]}"; do
165|      if [[ " ${DEPENDENCY_MAP[$key]} " == *" $id "* ]]; then
166|        deps_of_me+="$key "
167|      fi
168|    done
169|    [ -n "$deps_of_me" ] && _vlog "${_DIM}  Needed: ${deps_of_me}(dependentes)${_NC}"
170|  fi
171|  FEATURE_START_TIME=$(date +%s%N)
172|}
173|
174|log_check_pass() {
175|  local msg="$1"
176|  _log "  ${_GREEN}✓${_NC} ${msg}"
177|  CURRENT_CHECKS_PASSED=$((CURRENT_CHECKS_PASSED + 1))
178|  CURRENT_CHECKS_TOTAL=$((CURRENT_CHECKS_TOTAL + 1))
179|  CURRENT_PASS_DETAILS+=("$msg")
180|}
181|
182|log_check_fail() {
183|  local msg="$1"
184|  _log "  ${_RED}✗${_NC} ${msg}"
185|  CURRENT_CHECKS_FAILED=$((CURRENT_CHECKS_FAILED + 1))
186|  CURRENT_CHECKS_TOTAL=$((CURRENT_CHECKS_TOTAL + 1))
187|  CURRENT_FAIL_DETAILS+=("$msg")
188|}
189|
190|log_check_pending() {
191|  local msg="$1"
192|  _log "  ${_YELLOW}⏳${_NC} ${msg}"
193|  CURRENT_CHECKS_TOTAL=$((CURRENT_CHECKS_TOTAL + 1))
194|  CURRENT_PASS_DETAILS+=("PENDING: $msg")
195|}
196|
197|log_test_result() {
198|  local id="$1" result="$2"
199|  local elapsed=""
200|  if [ -n "${FEATURE_START_TIME:-}" ]; then
201|    local end_ns=$(date +%s%N)
202|    local diff_ms=$(( (end_ns - FEATURE_START_TIME) / 1000000 ))
203|    elapsed=" [${diff_ms}ms]"
204|  fi
205|  case "$result" in
206|    PASS)    _log "  ${_GREEN}${_BOLD}→ PASS${_NC} (${CURRENT_CHECKS_PASSED}/${CURRENT_CHECKS_TOTAL})${_DIM}${elapsed}${_NC}" ;;
207|    PARTIAL) _log "  ${_YELLOW}${_BOLD}→ PARTIAL${_NC} (${CURRENT_CHECKS_PASSED}/${CURRENT_CHECKS_TOTAL})${_DIM}${elapsed}${_NC}" ;;
208|    FAIL)    _log "  ${_RED}${_BOLD}→ FAIL${_NC} (${CURRENT_CHECKS_PASSED}/${CURRENT_CHECKS_TOTAL})${_DIM}${elapsed}${_NC}" ;;
209|    PENDING) _log "  ${_YELLOW}${_BOLD}→ PENDING (API key)${_NC}${_DIM}${elapsed}${_NC}" ;;
210|  esac
211|  # In verbose, show the exact hermes command that will run in Fase 2
212|  if [ "$VERBOSE" = "1" ] && [ -n "$SMOKE_PROMPT" ]; then
213|    # Escape prompt for display (single line for short, multiline for long)
214|    local escaped_prompt
215|    escaped_prompt=$(echo "$SMOKE_PROMPT" | tr '\n' ' ' | sed 's/  */ /g')
216|    _vlog ""
217|    _vlog "${_BLUE}  \$ $HERMES_BIN chat -q \"${escaped_prompt}\" -m \"$HARNESS_MODEL\" -Q${_NC}"
218|  fi
219|}
220|
221|# =============================================================================
222|# Check functions (Fase 1 — deterministic)
223|# =============================================================================
224|
225|check_skill_exists() {
226|  local skill="$1"
227|  if [ -f "$SKILLS_DST/$skill/SKILL.md" ]; then
228|    log_check_pass "Skill '$skill' presente"
229|    if [ "$VERBOSE" = "1" ]; then
230|      local fsize=$(wc -c < "$SKILLS_DST/$skill/SKILL.md" 2>/dev/null)
231|      local flines=$(wc -l < "$SKILLS_DST/$skill/SKILL.md" 2>/dev/null)
232|      local nfiles=$(find "$SKILLS_DST/$skill" -type f 2>/dev/null | wc -l)
233|      _vlog "${_DIM}    ↳ SKILL.md: ${flines} linhas, ${fsize} bytes | Dir: ${nfiles} arquivo(s)${_NC}"
234|      # Show first line of description if available
235|      local desc_line
236|      desc_line=$(grep -m1 '^description:' "$SKILLS_DST/$skill/SKILL.md" 2>/dev/null | sed 's/^description: *//' | head -c 100)
237|      [ -n "$desc_line" ] && _vlog "${_DIM}    ↳ Desc: ${desc_line}${_NC}"
238|      # List files in the skill dir
239|      local extra_files
240|      extra_files=$(find "$SKILLS_DST/$skill" -type f ! -name 'SKILL.md' -printf '      %P\n' 2>/dev/null | head -8)
241|      [ -n "$extra_files" ] && _vlog "${_DIM}    ↳ Conteúdo:${_NC}" && _vlog "${_DIM}${extra_files}${_NC}"
242|    fi
243|    return 0
244|  else
245|    log_check_fail "Skill '$skill' não encontrada em $SKILLS_DST/$skill/SKILL.md"
246|    return 1
247|  fi
248|}
249|
250|check_frontmatter() {
251|  local skill="$1"
252|  shift
253|  local skill_file="$SKILLS_DST/$skill/SKILL.md"
254|  if [ ! -f "$skill_file" ]; then
255|    log_check_fail "Frontmatter: arquivo não existe ($skill_file)"
256|    return 1
257|  fi
258|
259|  # Check YAML frontmatter delimiters
260|  local first_line
261|  first_line=$(head -1 "$skill_file")
262|  if [ "$first_line" != "---" ]; then
263|    log_check_fail "Frontmatter: sem delimitador '---' no início ($skill)"
264|    return 1
265|  fi
266|
267|  # Extract frontmatter
268|  local fm
269|  fm=$(sed -n '2,/^---$/p' "$skill_file" | head -n -1)
270|  if [ -z "$fm" ]; then
271|    log_check_fail "Frontmatter: vazio ou malformado ($skill)"
272|    return 1
273|  fi
274|
275|  # Check required fields
276|  local all_ok=true
277|  for field in "$@"; do
278|    if echo "$fm" | grep -qE "^${field}:"; then
279|      if [ "$VERBOSE" = "1" ]; then
280|        local val
281|        val=$(echo "$fm" | grep -m1 "^${field}:" | sed "s/^${field}: *//" | head -c 80)
282|        _vlog "${_DIM}    ↳ ${field}: ${val}${_NC}"
283|      fi
284|    else
285|      log_check_fail "Frontmatter: campo '$field' ausente ($skill)"
286|      all_ok=false
287|    fi
288|  done
289|
290|  if $all_ok; then
291|    log_check_pass "Frontmatter válido ($skill)"
292|    return 0
293|  fi
294|  return 1
295|}
296|
297|check_skill_dep() {
298|  local dep_skill="$1"
299|  if [ -f "$SKILLS_DST/$dep_skill/SKILL.md" ]; then
300|    log_check_pass "Dep skill '$dep_skill' presente"
301|    if [ "$VERBOSE" = "1" ]; then
302|      local ver
303|      ver=$(grep -am1 '^version:' "$SKILLS_DST/$dep_skill/SKILL.md" 2>/dev/null | sed 's/^version: *//' || echo "?")
304|      _vlog "${_DIM}    ↳ v${ver} @ $SKILLS_DST/$dep_skill/${_NC}"
305|    fi
306|    return 0
307|  else
308|    log_check_fail "Dep skill '$dep_skill' ausente"
309|    _vlog "${_DIM}    ↳ Esperado em: $SKILLS_DST/$dep_skill/SKILL.md${_NC}"
310|    return 1
311|  fi
312|}
313|
314|check_no_skill_deps() {
315|  log_check_pass "Sem dependências de skills"
316|  return 0
317|}
318|
319|check_tool_in_path() {
320|  local tool="$1"
321|  local desc="${2:-$tool}"
322|  if command -v "$tool" >/dev/null 2>&1; then
323|    log_check_pass "Tool '$desc' disponível ($(command -v "$tool"))"
324|    return 0
325|  elif [ -x "$HERMES_HOME/bin/$tool" ]; then
326|    log_check_pass "Tool '$desc' disponível ($HERMES_HOME/bin/$tool)"
327|    return 0
328|  else
329|    log_check_fail "Tool '$desc' não encontrada no PATH nem em \$HERMES_HOME/bin/"
330|    return 1
331|  fi
332|}
333|
334|check_no_tool_deps() {
335|  log_check_pass "Sem dependências de tools"
336|  return 0
337|}
338|
339|check_file_exists() {
340|  local path="$1"
341|  local desc="${2:-$path}"
342|  if [ -f "$path" ]; then
343|    log_check_pass "Arquivo '$desc' presente"
344|    if [ "$VERBOSE" = "1" ]; then
345|      local fsize=$(wc -c < "$path" 2>/dev/null)
346|      local fmod=$(stat -c '%y' "$path" 2>/dev/null | cut -d. -f1)
347|      _vlog "${_DIM}    ↳ ${fsize} bytes, mod: ${fmod}${_NC}"
348|    fi
349|    return 0
350|  else
351|    log_check_fail "Arquivo '$desc' ausente ($path)"
352|    return 1
353|  fi
354|}
355|
356|check_dir_exists() {
357|  local path="$1"
358|  local desc="${2:-$path}"
359|  if [ -d "$path" ]; then
360|    log_check_pass "Diretório '$desc' presente"
361|    if [ "$VERBOSE" = "1" ]; then
362|      local nfiles=$(find "$path" -maxdepth 1 -type f 2>/dev/null | wc -l)
363|      local ndirs=$(find "$path" -maxdepth 1 -type d 2>/dev/null | wc -l)
364|      ndirs=$((ndirs - 1))  # exclude self
365|      _vlog "${_DIM}    ↳ ${nfiles} arquivo(s), ${ndirs} subdir(s) em ${path}${_NC}"
366|    fi
367|    return 0
368|  else
369|    log_check_fail "Diretório '$desc' ausente ($path)"
370|    return 1
371|  fi
372|}
373|
374|check_script_executable() {
375|  local path="$1"
376|  local desc="${2:-$path}"
377|  if [ -x "$path" ]; then
378|    log_check_pass "Script '$desc' executável"
379|    return 0
380|  else
381|    log_check_fail "Script '$desc' sem permissão de execução ($path)"
382|    return 1
383|  fi
384|}
385|
386|check_api_key() {
387|  local var_name="$1"
388|  local desc="${2:-$var_name}"
389|  local val="${!var_name:-}"
390|  if [ -n "$val" ]; then
391|    log_check_pass "API key '$desc' definida"
392|    return 0
393|  elif [ "$SKIP_API" = "1" ]; then
394|    log_check_pending "'$desc' não definida — pendente de key"
395|    return 2  # special: pending
396|  else
397|    log_check_fail "API key '$desc' não definida"
398|    return 1
399|  fi
400|}
401|
402|# =============================================================================
403|# Test lifecycle
404|# =============================================================================
405|
406|reset_test_state() {
407|  CURRENT_CHECKS_PASSED=0
408|  CURRENT_CHECKS_FAILED=0
409|  CURRENT_CHECKS_TOTAL=0
410|  CURRENT_FAIL_DETAILS=()
411|  CURRENT_PASS_DETAILS=()
412|  SMOKE_PROMPT=""
413|  CURRENT_FEATURE_NAME=""
414|  CURRENT_FEATURE_CATEGORY=""
415|  CURRENT_SKILL=""
416|}
417|
418|# Run a single feature test. Called by the orchestrator.
419|# Usage: run_feature_test "EX-01"
420|run_feature_test() {
421|  local feature_id="$1"
422|  local num="${feature_id#EX-}"
423|  num="${num#0}"  # remove leading zero
424|  local func_name="test_EX${num}"
425|
426|  CURRENT_FEATURE_ID="$feature_id"
427|  reset_test_state
428|
429|  # Check if test function exists
430|  if ! declare -f "$func_name" >/dev/null 2>&1; then
431|    _log "  ${_YELLOW}⚠${_NC} Sem função de teste para $feature_id (esperado: $func_name)"
432|    return 0
433|  fi
434|
435|  log_test_start "$feature_id" "${FEATURE_SKILL_MAP[$feature_id]:-unknown}"
436|
437|  # Execute test (Fase 1 checks)
438|  set +e
439|  "$func_name"
440|  set -e
441|
442|  # Determine result
443|  local result
444|  if [ $CURRENT_CHECKS_FAILED -eq 0 ]; then
445|    result="PASS"
446|    PASSED_FEATURES+=("$feature_id")
447|    TOTAL_PASSED=$((TOTAL_PASSED + 1))
448|  else
449|    # Check if it's just pending API keys
450|    local only_pending=true
451|    for detail in "${CURRENT_FAIL_DETAILS[@]}"; do
452|      if [[ "$detail" != *"API key"* ]] && [[ "$detail" != *"pendente"* ]]; then
453|        only_pending=false
454|        break
455|      fi
456|    done
457|    if $only_pending && [ "$SKIP_API" = "1" ]; then
458|      result="PENDING"
459|      PENDING_FEATURES+=("$feature_id")
460|      TOTAL_PENDING=$((TOTAL_PENDING + 1))
461|    else
462|      result="FAIL"
463|      FAILED_FEATURES+=("$feature_id")
464|      TOTAL_FAILED=$((TOTAL_FAILED + 1))
465|    fi
466|  fi
467|
468|  log_test_result "$feature_id" "$result"
469|  TOTAL_TESTED=$((TOTAL_TESTED + 1))
470|
471|  # Save smoke prompt for Fase 2
472|  if [ -n "$SMOKE_PROMPT" ]; then
473|    SMOKE_PROMPTS_MAP["$feature_id"]="$SMOKE_PROMPT"
474|  fi
475|
476|  # Fast-fail check for gate features
477|  if [ "$FAST_FAIL" = "1" ] && [ "$result" = "FAIL" ]; then
478|    for gate in "${GATE_FEATURES[@]}"; do
479|      if [ "$gate" = "$feature_id" ]; then
480|        _log ""
481|        _log "${_RED}${_BOLD}⛔ FAST-FAIL: $feature_id é gate feature. Abortando.${_NC}"
482|        return 1
483|      fi
484|    done
485|  fi
486|
487|  return 0
488|}
489|
490|# Run smoke test for a single feature via Hermes headless
491|# Called after deterministic checks pass, if SMOKE_PROMPT is set
492|run_smoke_test() {
493|  local feature_id="$1"
494|  local smoke_prompt="$2"
495|  local skill_name="${FEATURE_SKILL_MAP[$feature_id]:-unknown}"
496|
497|  if [ "$NO_SMOKE" = "1" ]; then
498|    return 0
499|  fi
500|
501|