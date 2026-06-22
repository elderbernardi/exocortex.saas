#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Testes do Setup Interativo
# =============================================================================
# Suite de testes para o novo fluxo interativo do setup.sh.
# Pode rodar localmente ou dentro do Docker container de teste.
#
# Uso:
#   bash tests/test_interactive_setup.sh                 # todos os testes
#   bash tests/test_interactive_setup.sh --only T01      # teste específico
#   bash tests/test_interactive_setup.sh --docker        # build + run Docker
#
# Ref: ADR-012-interactive-setup.md
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ─── Colors ──────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ─── Counters ─────────────────────────────────────────────────────────────────

TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0
ONLY_TEST="${2:-}"

# ─── Helpers ─────────────────────────────────────────────────────────────────

pass() { PASSED=$((PASSED + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${GREEN}✅ PASS${NC} $1"; }
fail_test() { FAILED=$((FAILED + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${RED}❌ FAIL${NC} $1 — $2"; }
skip() { SKIPPED=$((SKIPPED + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${DIM}⏭  SKIP${NC} $1 — $2"; }

should_run() {
  local id="$1"
  if [ -n "$ONLY_TEST" ] && [ "$ONLY_TEST" != "$id" ]; then
    return 1
  fi
  return 0
}

# Create isolated temp directory for each test
setup_test_env() {
  local test_dir
  test_dir=$(mktemp -d)
  export HERMES_HOME="$test_dir/hermes"
  export EXOCORTEX_HOME="$test_dir/exocortex"
  export ACERVO="$EXOCORTEX_HOME/acervo"
  export HOME="$test_dir/home"
  mkdir -p "$HERMES_HOME/skills" "$HERMES_HOME/memories" "$HERMES_HOME/profiles"
  mkdir -p "$EXOCORTEX_HOME" "$HOME"
  echo "$test_dir"
}

cleanup_test_env() {
  local test_dir="$1"
  rm -rf "$test_dir"
}

# ─── Parse args ──────────────────────────────────────────────────────────────

for arg in "$@"; do
  case "$arg" in
    --docker)
      echo -e "${BOLD}Building and running Docker test container...${NC}"
      docker build -t exocortex-setup-test -f "$SCRIPT_DIR/Dockerfile.setup-test" "$REPO_ROOT"
      docker run --rm exocortex-setup-test
      exit $?
      ;;
    --only)
      # Next arg is the test ID
      ;;
    --help|-h)
      echo "Uso: bash $0 [--docker] [--only T01] [--help]"
      exit 0
      ;;
  esac
done

echo ""
echo -e "${BOLD}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   Exocórtex — Testes do Setup Interativo             ║${NC}"
echo -e "${BOLD}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# T01: validate-environment.sh executa sem erros de sintaxe
# =============================================================================

if should_run "T01"; then
  echo -e "${BOLD}T01: validate-environment.sh executa sem erros de sintaxe${NC}"
  if bash -n "$REPO_ROOT/scripts/validate-environment.sh" 2>/dev/null; then
    pass "T01: syntax check OK"
  else
    fail_test "T01" "syntax error em validate-environment.sh"
  fi
fi

# =============================================================================
# T02: validate-environment.sh --json produz JSON válido
# =============================================================================

if should_run "T02"; then
  echo -e "${BOLD}T02: validate-environment.sh --json produz JSON válido${NC}"
  test_dir=$(setup_test_env)

  json_output=$(bash "$REPO_ROOT/scripts/validate-environment.sh" --json 2>/dev/null || true)

  if echo "$json_output" | python3 -m json.tool >/dev/null 2>&1; then
    # Check required fields
    if echo "$json_output" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'summary' in d and 'results' in d" 2>/dev/null; then
      pass "T02: JSON output válido com campos obrigatórios"
    else
      fail_test "T02" "JSON válido mas faltam campos 'summary' ou 'results'"
    fi
  else
    fail_test "T02" "saída não é JSON válido"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T03: validate-skills-deps.sh executa sem erros de sintaxe
# =============================================================================

if should_run "T03"; then
  echo -e "${BOLD}T03: validate-skills-deps.sh executa sem erros de sintaxe${NC}"
  if bash -n "$REPO_ROOT/scripts/validate-skills-deps.sh" 2>/dev/null; then
    pass "T03: syntax check OK"
  else
    fail_test "T03" "syntax error em validate-skills-deps.sh"
  fi
fi

# =============================================================================
# T04: setup/interactive.sh executa sem erros de sintaxe
# =============================================================================

if should_run "T04"; then
  echo -e "${BOLD}T04: setup/interactive.sh executa sem erros de sintaxe${NC}"
  if bash -n "$REPO_ROOT/setup/interactive.sh" 2>/dev/null; then
    pass "T04: syntax check OK"
  else
    fail_test "T04" "syntax error em interactive.sh"
  fi
fi

# =============================================================================
# T05: setup/common.sh executa sem erros de sintaxe
# =============================================================================

if should_run "T05"; then
  echo -e "${BOLD}T05: setup/common.sh executa sem erros de sintaxe${NC}"
  if bash -n "$REPO_ROOT/setup/common.sh" 2>/dev/null; then
    pass "T05: syntax check OK"
  else
    fail_test "T05" "syntax error em common.sh"
  fi
fi

# =============================================================================
# T06: setup.sh executa sem erros de sintaxe
# =============================================================================

if should_run "T06"; then
  echo -e "${BOLD}T06: setup.sh executa sem erros de sintaxe${NC}"
  if bash -n "$REPO_ROOT/setup.sh" 2>/dev/null; then
    pass "T06: syntax check OK"
  else
    fail_test "T06" "syntax error em setup.sh"
  fi
fi

# =============================================================================
# T07: common.sh parse --yes flag corretamente
# =============================================================================

if should_run "T07"; then
  echo -e "${BOLD}T07: common.sh parse --yes flag${NC}"
  test_dir=$(setup_test_env)

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    source '$REPO_ROOT/setup/common.sh' --yes 2>/dev/null
    echo \$INTERACTIVE_MODE
  " 2>/dev/null || true)

  if [ "$result" = "0" ]; then
    pass "T07: --yes sets INTERACTIVE_MODE=0"
  else
    fail_test "T07" "INTERACTIVE_MODE='$result' (esperado '0')"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T08: common.sh parse --init-only flag
# =============================================================================

if should_run "T08"; then
  echo -e "${BOLD}T08: common.sh parse --init-only flag${NC}"
  test_dir=$(setup_test_env)

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    source '$REPO_ROOT/setup/common.sh' --init-only 2>/dev/null
    echo \$INIT_ONLY
  " 2>/dev/null || true)

  if [ "$result" = "1" ]; then
    pass "T08: --init-only sets INIT_ONLY=1"
  else
    fail_test "T08" "INIT_ONLY='$result' (esperado '1')"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T09: common.sh parse --skip-env-check flag
# =============================================================================

if should_run "T09"; then
  echo -e "${BOLD}T09: common.sh parse --skip-env-check flag${NC}"
  test_dir=$(setup_test_env)

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    source '$REPO_ROOT/setup/common.sh' --skip-env-check 2>/dev/null
    echo \$SKIP_ENV_CHECK
  " 2>/dev/null || true)

  if [ "$result" = "1" ]; then
    pass "T09: --skip-env-check sets SKIP_ENV_CHECK=1"
  else
    fail_test "T09" "SKIP_ENV_CHECK='$result' (esperado '1')"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T10: .env.local loading — values are loaded by common.sh
# =============================================================================

if should_run "T10"; then
  echo -e "${BOLD}T10: .env.local loading${NC}"
  test_dir=$(setup_test_env)

  # Create a .env.local in the REPO_ROOT (simulated)
  local_env_file="$REPO_ROOT/.env.local.test-$$"
  cat > "$local_env_file" <<'EOF'
TEST_ENVLOCAL_VAR="hello_from_envlocal"
EOF

  # Test loading
  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    # Temporarily swap .env.local
    cp '$local_env_file' '$REPO_ROOT/.env.local'
    source '$REPO_ROOT/setup/common.sh' 2>/dev/null
    echo \$TEST_ENVLOCAL_VAR
    rm -f '$REPO_ROOT/.env.local'
  " 2>/dev/null || true)

  rm -f "$local_env_file"
  rm -f "$REPO_ROOT/.env.local"

  if [ "$result" = "hello_from_envlocal" ]; then
    pass "T10: .env.local values loaded correctly"
  else
    fail_test "T10" "TEST_ENVLOCAL_VAR='$result' (esperado 'hello_from_envlocal')"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T11: .env.local does NOT override existing env vars
# =============================================================================

if should_run "T11"; then
  echo -e "${BOLD}T11: .env.local não sobrescreve env vars existentes${NC}"
  test_dir=$(setup_test_env)

  local_env_file="$REPO_ROOT/.env.local.test-$$"
  cat > "$local_env_file" <<'EOF'
HERMES_HOME="/should/not/override"
EOF

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    export HERMES_HOME='/already/set'
    cp '$local_env_file' '$REPO_ROOT/.env.local'
    source '$REPO_ROOT/setup/common.sh' 2>/dev/null
    echo \$HERMES_HOME
    rm -f '$REPO_ROOT/.env.local'
  " 2>/dev/null || true)

  rm -f "$local_env_file"
  rm -f "$REPO_ROOT/.env.local"

  if [ "$result" = "/already/set" ]; then
    pass "T11: env vars não são sobrescritas por .env.local"
  else
    fail_test "T11" "HERMES_HOME='$result' (esperado '/already/set')"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T12: interactive.sh mask_value works correctly
# =============================================================================

if should_run "T12"; then
  echo -e "${BOLD}T12: mask_value funciona corretamente${NC}"

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    source '$REPO_ROOT/setup/common.sh' --yes 2>/dev/null
    source '$REPO_ROOT/setup/interactive.sh' 2>/dev/null
    echo \$(mask_value 'sk-or-v1-MOCK_KEY_356f')
  " 2>/dev/null || true)

  if echo "$result" | grep -q "sk-or-" && echo "$result" | grep -q "356f" && echo "$result" | grep -q "\.\.\."; then
    pass "T12: mask_value mostra prefixo...sufixo"
  else
    fail_test "T12" "resultado='$result' (esperado formato 'sk-or-...356f')"
  fi
fi

# =============================================================================
# T13: interactive.sh mask_value handles empty
# =============================================================================

if should_run "T13"; then
  echo -e "${BOLD}T13: mask_value com valor vazio${NC}"

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    source '$REPO_ROOT/setup/common.sh' --yes 2>/dev/null
    source '$REPO_ROOT/setup/interactive.sh' 2>/dev/null
    echo \$(mask_value '')
  " 2>/dev/null || true)

  if echo "$result" | grep -q "vazio"; then
    pass "T13: mask_value retorna '(vazio)' para string vazia"
  else
    fail_test "T13" "resultado='$result' (esperado '(vazio)')"
  fi
fi

# =============================================================================
# T14: setup.sh --yes --skip-env-check --init-only completes without prompts
# =============================================================================

if should_run "T14"; then
  echo -e "${BOLD}T14: setup.sh --yes --skip-env-check --init-only${NC}"
  t14_dir=$(mktemp -d)
  t14_hermes="$t14_dir/hermes"
  t14_exo="$t14_dir/exocortex"
  mkdir -p "$t14_hermes/skills" "$t14_hermes/memories" "$t14_hermes/profiles" "$t14_exo"

  output=$(bash -c "
    export HERMES_HOME='$t14_hermes'
    export EXOCORTEX_HOME='$t14_exo'
    export HOME='$t14_dir/home'
    mkdir -p \"\$HOME\"
    cd '$REPO_ROOT'
    bash setup.sh --yes --skip-env-check --init-only 2>&1
  " 2>/dev/null || true)
  exit_code=$?

  if echo "$output" | grep -qi "init-only\|configuração salva"; then
    pass "T14: --init-only para sem executar steps"
  else
    fail_test "T14" "saída inesperada (exit=$exit_code)"
  fi

  rm -rf "$t14_dir"
fi

# =============================================================================
# T15: .env.local.example is valid (no syntax errors if sourced)
# =============================================================================

if should_run "T15"; then
  echo -e "${BOLD}T15: .env.local.example é válido${NC}"
  if [ -f "$REPO_ROOT/.env.local.example" ]; then
    # Verify it's parseable (all lines are either comments or KEY=VALUE)
    invalid_lines=$(grep -vnE '^\s*#|^\s*$|^[A-Z_]+=' "$REPO_ROOT/.env.local.example" 2>/dev/null | wc -l)
    if [ "$invalid_lines" -eq 0 ]; then
      pass "T15: .env.local.example tem formato válido"
    else
      fail_test "T15" "$invalid_lines linhas com formato inválido"
    fi
  else
    fail_test "T15" ".env.local.example não encontrado"
  fi
fi

# =============================================================================
# T16: hermes-stub responds to all expected subcommands
# =============================================================================

if should_run "T16"; then
  echo -e "${BOLD}T16: hermes-stub responde a subcommands${NC}"
  stub="$REPO_ROOT/tests/fixtures/hermes-stub"
  if [ -x "$stub" ] || [ -f "$stub" ]; then
    chmod +x "$stub"
    all_ok=true

    v=$("$stub" --version 2>/dev/null)
    echo "$v" | grep -q "2026.4.10" || { all_ok=false; echo "    --version falhou"; }

    m=$("$stub" mcp list 2>/dev/null)
    [ $? -eq 0 ] || { all_ok=false; echo "    mcp list falhou"; }

    g=$("$stub" gateway list 2>/dev/null)
    [ $? -eq 0 ] || { all_ok=false; echo "    gateway list falhou"; }

    if $all_ok; then
      pass "T16: hermes-stub responde corretamente"
    else
      fail_test "T16" "alguns subcommands falharam"
    fi
  else
    fail_test "T16" "hermes-stub não encontrado"
  fi
fi

# =============================================================================
# T17: ADR-012 exists and has required sections
# =============================================================================

if should_run "T17"; then
  echo -e "${BOLD}T17: ADR-012 existe com seções obrigatórias${NC}"
  adr="$REPO_ROOT/docs/ADR/ADR-012-interactive-setup.md"
  if [ -f "$adr" ]; then
    missing=0
    for section in "Contexto" "Decisão" "Consequências"; do
      if ! grep -qi "$section" "$adr"; then
        echo "    Seção faltando: $section"
        missing=$((missing + 1))
      fi
    done
    if [ $missing -eq 0 ]; then
      pass "T17: ADR-012 com todas as seções"
    else
      fail_test "T17" "$missing seção(ões) faltando"
    fi
  else
    fail_test "T17" "ADR-012 não encontrado"
  fi
fi

# =============================================================================
# T18: .gitignore contains .env.local
# =============================================================================

if should_run "T18"; then
  echo -e "${BOLD}T18: .gitignore contém .env.local${NC}"
  if grep -q "^\.env\.local$" "$REPO_ROOT/.gitignore" 2>/dev/null; then
    pass "T18: .env.local está no .gitignore"
  else
    fail_test "T18" ".env.local não encontrado no .gitignore"
  fi
fi

# =============================================================================
# T19: save_to_env_local creates file with correct permissions
# =============================================================================

if should_run "T19"; then
  echo -e "${BOLD}T19: save_to_env_local cria arquivo com permissões corretas${NC}"
  test_dir=$(setup_test_env)

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$test_dir'
    export SCRIPT_DIR='$test_dir'
    export ENV_LOCAL_FILE='$test_dir/.env.local'
    source '$REPO_ROOT/setup/common.sh' --yes 2>/dev/null
    source '$REPO_ROOT/setup/interactive.sh' 2>/dev/null
    save_to_env_local 'TEST_KEY' 'test_value'
    stat -c '%a' '$test_dir/.env.local' 2>/dev/null || stat -f '%Lp' '$test_dir/.env.local' 2>/dev/null
  " 2>/dev/null || true)

  if [ "$result" = "600" ]; then
    pass "T19: arquivo criado com permissão 600"
  else
    fail_test "T19" "permissão='$result' (esperado '600')"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T20: save_to_env_local writes and reads back correctly
# =============================================================================

if should_run "T20"; then
  echo -e "${BOLD}T20: save_to_env_local persist e recupera valor${NC}"
  test_dir=$(setup_test_env)

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$test_dir'
    export SCRIPT_DIR='$test_dir'
    export ENV_LOCAL_FILE='$test_dir/.env.local'
    source '$REPO_ROOT/setup/common.sh' --yes 2>/dev/null
    source '$REPO_ROOT/setup/interactive.sh' 2>/dev/null
    save_to_env_local 'MY_KEY' 'my_value_123'
    grep 'MY_KEY' '$test_dir/.env.local' | cut -d= -f2 | tr -d '\"'
  " 2>/dev/null || true)

  if [ "$result" = "my_value_123" ]; then
    pass "T20: valor persistido e recuperado corretamente"
  else
    fail_test "T20" "resultado='$result' (esperado 'my_value_123')"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T21: setup.sh cancelado pelo usuário retorna 130 e não segue como sucesso
# =============================================================================

if should_run "T21"; then
  echo -e "${BOLD}T21: setup.sh cancelado retorna 130${NC}"

  if ! command -v script >/dev/null 2>&1; then
    skip "T21" "comando 'script' não disponível neste ambiente"
  else
    test_dir=$(setup_test_env)
    output_file="$test_dir/setup-cancel.log"
    input_file="$test_dir/setup-cancel.input"
    printf '\n\n' > "$input_file"

    if script -e -q -c "cd '$REPO_ROOT' && bash setup.sh" /dev/null < "$input_file" > "$output_file" 2>&1; then
      exit_code=0
    else
      exit_code=$?
    fi

    if [ "$exit_code" -eq 130 ] \
      && grep -q "Setup cancelado pelo usuário" "$output_file" \
      && ! grep -q "instalado com sucesso" "$output_file"; then
      pass "T21: cancelamento interrompe o setup com exit 130"
    else
      fail_test "T21" "exit=$exit_code; ver $output_file"
    fi

    cleanup_test_env "$test_dir"
  fi
fi

# =============================================================================
# T22: install.sh não exibe sucesso quando setup é cancelado
# =============================================================================

if should_run "T22"; then
  echo -e "${BOLD}T22: install.sh interrompe sem banner de sucesso ao cancelar setup${NC}"

  if ! command -v script >/dev/null 2>&1; then
    skip "T22" "comando 'script' não disponível neste ambiente"
  else
    test_dir=$(mktemp -d)
    home_dir="$test_dir/home"
    installer_dir="$test_dir/.exocortex-installer"
    output_file="$test_dir/install-cancel.log"
    input_file="$test_dir/install-cancel.input"
    mkdir -p "$home_dir"
    cp -a "$REPO_ROOT" "$installer_dir"
    echo "main" > "$installer_dir/.exocortex-version"
    printf '\n\n' > "$input_file"

    if env HOME="$home_dir" EXOCORTEX_INSTALLER_DIR="$installer_dir" VERSION="main" \
      script -e -q -c "bash '$REPO_ROOT/install.sh'" /dev/null < "$input_file" > "$output_file" 2>&1; then
      exit_code=0
    else
      exit_code=$?
    fi

    if [ "$exit_code" -eq 130 ] \
      && grep -q "Instalação interrompida antes do provisionamento completo" "$output_file" \
      && ! grep -q "Exocórtex.IA instalado com sucesso" "$output_file" \
      && [ ! -d "$home_dir/.hermes/skills/excrtx" ]; then
      pass "T22: install.sh respeita cancelamento do setup"
    else
      fail_test "T22" "exit=$exit_code; ver $output_file"
    fi

    cleanup_test_env "$test_dir"
  fi
fi

# =============================================================================
# T23: common.sh parse --step-by-step flag
# =============================================================================

if should_run "T23"; then
  echo -e "${BOLD}T23: common.sh parse --step-by-step flag${NC}"
  test_dir=$(setup_test_env)

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    source '$REPO_ROOT/setup/common.sh' --step-by-step 2>/dev/null
    echo \$STEP_BY_STEP_MODE
  " 2>/dev/null || true)

  if [ "$result" = "1" ]; then
    pass "T23: --step-by-step sets STEP_BY_STEP_MODE=1"
  else
    fail_test "T23" "STEP_BY_STEP_MODE='$result' (esperado '1')"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T24: install.sh --help documenta revisão guiada
# =============================================================================

if should_run "T24"; then
  echo -e "${BOLD}T24: install.sh --help documenta step-by-step${NC}"

  help_output=$(bash "$REPO_ROOT/install.sh" --help 2>/dev/null || true)

  if echo "$help_output" | grep -q -- "--step-by-step"; then
    pass "T24: --help expõe a flag --step-by-step"
  else
    fail_test "T24" "ajuda não menciona --step-by-step"
  fi
fi

# =============================================================================
# T25: verify-keys resolve o papel 'default' e sincroniza o config.yaml
# =============================================================================

if should_run "T25"; then
  echo -e "${BOLD}T25: step-12 resolve papel 'default' e grava config.yaml${NC}"
  test_dir=$(setup_test_env)

  output=$(bash -c "
    export HERMES_HOME='$test_dir/hermes'
    export HOME='$test_dir/home'
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    export INTERACTIVE_MODE=0 EXOCORTEX_NO_PING=1
    export EXOCORTEX_DEFAULT_PROVIDER='deepseek'
    export EXOCORTEX_DEFAULT_MODEL='deepseek-v4-pro'
    export EXOCORTEX_DEFAULT_API_KEY='test-default-key'
    bash '$REPO_ROOT/setup/step-12-verify-keys.sh' 2>&1
  " 2>/dev/null || true)

  if echo "$output" | grep -q "Papel 'default'" \
    && echo "$output" | grep -q "config.yaml" \
    && echo "$output" | grep -q "deepseek-v4-pro"; then
    pass "T25: papel 'default' resolvido e projetado no config.yaml"
  else
    fail_test "T25" "saída não trouxe o relatório de papel/config esperado"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T26: verify-keys usa Firecrawl local na porta 3002 por default
# =============================================================================

if should_run "T26"; then
  echo -e "${BOLD}T26: step-12 anuncia Firecrawl local em 3002${NC}"
  test_dir=$(setup_test_env)

  output=$(bash -c "
    export HERMES_HOME='$test_dir/hermes'
    export HOME='$test_dir/home'
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    bash '$REPO_ROOT/setup/step-12-verify-keys.sh' 2>&1
  " 2>/dev/null || true)

  if echo "$output" | grep -q "http://127.0.0.1:3002"; then
    pass "T26: guidance do Firecrawl aponta para porta 3002"
  else
    fail_test "T26" "saída não menciona o endpoint default do Firecrawl"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T27: install.sh --yes funciona sem TTY
# =============================================================================

if should_run "T27"; then
  echo -e "${BOLD}T27: install.sh --yes funciona sem TTY${NC}"
  test_dir=$(mktemp -d)
  home_dir="$test_dir/home"
  installer_dir="$test_dir/.exocortex-installer"
  mkdir -p "$home_dir"

  output=$(env HOME="$home_dir" HERMES_HOME="$home_dir/.hermes" EXOCORTEX_HOME="$home_dir/exocortex" \
    EXOCORTEX_INSTALLER_DIR="$installer_dir" EXOCORTEX_REPO_URL="$REPO_ROOT" VERSION="main" \
    OPENROUTER_API_KEY='test-openrouter-key' \
    bash "$REPO_ROOT/install.sh" --yes --init-only --skip-env-check 2>&1 || true)

  if echo "$output" | grep -q "Modo --init-only: configuração salva em .env.local" \
    && ! echo "$output" | grep -q "/dev/tty"; then
    pass "T27: install.sh roda headless com --yes"
  else
    fail_test "T27" "instalação headless não produziu a saída esperada"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T28: install.sh faz preflight mascarado antes do Hermes
# =============================================================================

if should_run "T28"; then
  echo -e "${BOLD}T28: install.sh narra preflight e mascara segredos${NC}"
  test_dir=$(mktemp -d)
  home_dir="$test_dir/home"
  installer_dir="$test_dir/.exocortex-installer"
  bin_dir="$test_dir/bin"
  secret="sk-or-v1-supersecret3456"
  mkdir -p "$home_dir" "$bin_dir"

  cat > "$bin_dir/hermes" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = "--version" ]; then
  echo "2026.4.8"
  exit 0
fi
exit 0
EOF
  chmod +x "$bin_dir/hermes"

  output=$(env PATH="$bin_dir:/usr/bin:/bin:/usr/local/bin:/usr/local/sbin" \
    HOME="$home_dir" HERMES_HOME="$home_dir/.hermes" EXOCORTEX_HOME="$home_dir/exocortex" \
    EXOCORTEX_INSTALLER_DIR="$installer_dir" EXOCORTEX_REPO_URL="$REPO_ROOT" VERSION="main" \
    EXOCORTEX_DEFAULT_API_KEY="$secret" FIRECRAWL_BASE_URL="http://127.0.0.1:3002" \
    bash "$REPO_ROOT/install.sh" --yes --init-only --skip-env-check 2>&1 || true)

  if echo "$output" | grep -q "Preflight do bootstrap Hermes" \
    && echo "$output" | grep -q "Modo headless (--yes)" \
    && echo "$output" | grep -q "sk-or-...3456" \
    && ! echo "$output" | grep -q "$secret"; then
    pass "T28: preflight narra o modo e mascara a chave do papel default"
  else
    fail_test "T28" "preflight não exibiu a narrativa/mascara esperadas"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T29: install.sh reporta contexto útil quando bootstrap Hermes falha
# =============================================================================

if should_run "T29"; then
  echo -e "${BOLD}T29: install.sh traz contexto ao falhar no bootstrap Hermes${NC}"
  test_dir=$(mktemp -d)
  home_dir="$test_dir/home"
  installer_dir="$test_dir/.exocortex-installer"
  secret="sk-or-v1-bootstrap4321"
  missing_installer="file:///tmp/exocortex-missing-hermes-installer.sh"
  mkdir -p "$home_dir"

  if output=$(env PATH="/usr/bin:/bin:/usr/local/bin:/usr/local/sbin" \
    HOME="$home_dir" HERMES_HOME="$home_dir/.hermes" EXOCORTEX_HOME="$home_dir/exocortex" \
    EXOCORTEX_INSTALLER_DIR="$installer_dir" EXOCORTEX_HERMES_INSTALLER="$missing_installer" \
    OPENROUTER_API_KEY="$secret" \
    bash "$REPO_ROOT/install.sh" --yes --init-only --skip-env-check 2>&1); then
    exit_code=0
  else
    exit_code=$?
  fi

  if [ "$exit_code" -ne 0 ] \
    && echo "$output" | grep -q "Falha na etapa: Bootstrap Hermes" \
    && echo "$output" | grep -q "URL do instalador: $missing_installer" \
    && ! echo "$output" | grep -q "$secret"; then
    pass "T29: falha no bootstrap Hermes vem com contexto sanitizado"
  else
    fail_test "T29" "exit=$exit_code; saída sem o contexto esperado"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T30: setup.sh narra melhor o comportamento default interativo
# =============================================================================

if should_run "T30"; then
  echo -e "${BOLD}T30: setup.sh explica o comportamento default${NC}"

  if ! command -v script >/dev/null 2>&1; then
    skip "T30" "comando 'script' não disponível neste ambiente"
  else
    test_dir=$(setup_test_env)
    output_file="$test_dir/setup-default-mode.log"
    input_file="$test_dir/setup-default-mode.input"
    printf '\n\n' > "$input_file"

    if env HOME="$test_dir/home" HERMES_HOME="$test_dir/hermes" EXOCORTEX_HOME="$test_dir/exocortex" \
      script -e -q -c "cd '$REPO_ROOT' && bash setup.sh --skip-env-check" /dev/null < "$input_file" > "$output_file" 2>&1; then
      exit_code=0
    else
      exit_code=$?
    fi

    if [ "$exit_code" -eq 130 ] \
      && grep -q "Modo padrão: \[continuar\] mantém o que já foi detectado" "$output_file"; then
      pass "T30: setup default descreve continuar/editar/passo a passo"
    else
      fail_test "T30" "exit=$exit_code; ver $output_file"
    fi

    cleanup_test_env "$test_dir"
  fi
fi

# =============================================================================
# T31: validate_secret_format avisa sobre chaves malformadas
# =============================================================================

if should_run "T31"; then
  echo -e "${BOLD}T31: validate_secret_format detecta chave malformada${NC}"

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    source '$REPO_ROOT/setup/common.sh' --yes 2>/dev/null
    source '$REPO_ROOT/setup/interactive.sh' 2>/dev/null
    validate_secret_format 'OPENROUTER_API_KEY' 'sk-with space'
    validate_secret_format 'DEEPSEEK_API_KEY' 'short'
    validate_secret_format 'OPENROUTER_API_KEY' 'sk-or-v1-long-and-valid-looking-key'
  " 2>&1 || true)

  if echo "$result" | grep -q "contém espaço" \
    && echo "$result" | grep -q "curta demais" \
    && [ "$(echo "$result" | grep -c "API_KEY")" -eq 2 ]; then
    pass "T31: avisa em whitespace e chave curta, silencioso em chave válida"
  else
    fail_test "T31" "saída inesperada: $result"
  fi
fi

# =============================================================================
# T32: show_api_key_guidance explica os 3 papéis e a herança
# =============================================================================

if should_run "T32"; then
  echo -e "${BOLD}T32: guidance explica os 3 papéis (default/vision/auxiliar)${NC}"

  result=$(bash -c "
    export _EXOCORTEX_SCRIPT_DIR='$REPO_ROOT'
    source '$REPO_ROOT/setup/common.sh' --yes 2>/dev/null
    source '$REPO_ROOT/setup/interactive.sh' 2>/dev/null
    show_api_key_guidance
  " 2>&1 || true)

  if echo "$result" | grep -q "default" \
    && echo "$result" | grep -q "vision" \
    && echo "$result" | grep -q "auxiliar" \
    && echo "$result" | grep -qi "herda o default"; then
    pass "T32: guidance expõe os 3 papéis e a regra de herança"
  else
    fail_test "T32" "guidance não trouxe os 3 papéis esperados"
  fi
fi

# =============================================================================
# T33: setup.sh anuncia os 3 estágios antes dos prompts
# =============================================================================

if should_run "T33"; then
  echo -e "${BOLD}T33: setup.sh explica os 3 estágios no preâmbulo${NC}"
  test_dir=$(setup_test_env)

  output=$(bash -c "
    export HERMES_HOME='$test_dir/hermes'
    export EXOCORTEX_HOME='$test_dir/exocortex'
    export HOME='$test_dir/home'
    cd '$REPO_ROOT'
    bash setup.sh --skip-env-check < /dev/null 2>&1
  " 2>/dev/null || true)

  if echo "$output" | grep -q "roda em 3 estágios" \
    && echo "$output" | grep -q "Validação de pré-requisitos" \
    && echo "$output" | grep -q "Confirmação final antes do provisionamento"; then
    pass "T33: preâmbulo descreve os 3 estágios"
  else
    fail_test "T33" "setup.sh não anunciou os 3 estágios"
  fi

  cleanup_test_env "$test_dir"
fi

# =============================================================================
# T34: install.sh e setup.sh compartilham a mesma identidade visual
# =============================================================================

if should_run "T34"; then
  echo -e "${BOLD}T34: install.sh e setup.sh com banner coerente${NC}"

  if grep -q "◆  Hermes Agent  ◆" "$REPO_ROOT/install.sh" \
    && grep -q "◆  Hermes Agent  ◆" "$REPO_ROOT/setup.sh" \
    && grep -q "c o g n i ç ã o   e s t e n d i d a" "$REPO_ROOT/install.sh" \
    && grep -q "c o g n i ç ã o   e s t e n d i d a" "$REPO_ROOT/setup.sh"; then
    pass "T34: ambos usam o mesmo motivo visual (Hermes Agent + cognição estendida)"
  else
    fail_test "T34" "identidade visual não compartilhada entre install.sh e setup.sh"
  fi
fi

# =============================================================================
# Summary
# =============================================================================

echo ""
echo -e "${BOLD}═══ Resumo ═══${NC}"
echo -e "  Total: $TOTAL  |  ${GREEN}Pass: $PASSED${NC}  |  ${RED}Fail: $FAILED${NC}  |  ${DIM}Skip: $SKIPPED${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
  echo -e "${RED}${BOLD}⛔ $FAILED teste(s) falharam.${NC}"
  exit 1
else
  echo -e "${GREEN}${BOLD}✅ Todos os testes passaram.${NC}"
  exit 0
fi
