#!/usr/bin/env bash
# =============================================================================
# Regression tests: model-id validation in step-12-verify-keys.sh (_verify_model_id)
# =============================================================================
# T-MV-01: model id present in /v1/models → exit 0, PASS log
# T-MV-02: model id absent, wrong-case near-match → non-zero exit + "did you mean" hint
# T-MV-03: /v1/models endpoint unreachable (000) → warns, exit 0
# T-MV-04: /v1/models returns non-2xx → warns, exit 0
# T-MV-05: model id absent, no near-match → non-zero exit, no "did you mean"
#
# These tests extract _verify_model_id from step-12, stub curl + python3, and
# exercise each branch in isolation.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
BOLD='\033[1m'
NC='\033[0m'

TOTAL=0
PASSED=0
FAILED=0

pass()      { PASSED=$((PASSED + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${GREEN}PASS${NC} $1"; }
fail_test() { FAILED=$((FAILED + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${RED}FAIL${NC} $1 — $2"; }

echo ""
echo -e "${BOLD}step-12 model-id validation — regression tests${NC}"
echo ""

STEP12="$REPO_ROOT/setup/step-12-verify-keys.sh"

# Check the script exists and has _verify_model_id
if [ ! -f "$STEP12" ]; then
  echo -e "${RED}FATAL: step-12-verify-keys.sh not found${NC}"
  exit 1
fi

# =============================================================================
# Shared harness: run _verify_model_id in a subshell with stubbed curl+python3.
#
# Stubs:
#   STUB_HTTP_CODE   — curl exit code (000 = unreachable)
#   STUB_MODELS_JSON — JSON body for /v1/models
# =============================================================================

_run_verify() {
  local test_model="$1"
  local stub_http="$2"
  local stub_json="$3"

  bash -c '
    set -euo pipefail

    # ── Env for the role resolver ──────────────────────────────────────────
    export HERMES_HOME="$(mktemp -d)"
    export EXOCORTEX_HOME="$HERMES_HOME/exocortex"
    export ACERVO="$EXOCORTEX_HOME/acervo"
    export INTERACTIVE_MODE=0      # suppress ping in verify_role
    export EXOCORTEX_NO_PING=1
    # Role env vars
    export EXOCORTEX_DEFAULT_PROVIDER=testprovider
    export EXOCORTEX_DEFAULT_MODEL="$1"
    export EXOCORTEX_DEFAULT_API_KEY=sk-test-key
    export EXOCORTEX_DEFAULT_BASE_URL=http://localhost:9999

    STUB_HTTP="$2"
    STUB_JSON="$3"

    # ── Stub curl ─────────────────────────────────────────────────────────
    # curl -o <file> --write-out %{http_code} ... → write body to file, print code
    curl() {
      local out_file="" write_fmt=""
      local args=("$@")
      for ((i=0; i<${#args[@]}; i++)); do
        case "${args[$i]}" in
          -o) out_file="${args[$((i+1))]}" ;;
          --write-out) write_fmt="${args[$((i+1))]}" ;;
        esac
      done
      [ -n "$out_file" ] && printf "%s" "$STUB_JSON" > "$out_file"
      [ "$write_fmt" = "%{http_code}" ] && printf "%s" "$STUB_HTTP"
      return 0
    }
    export -f curl

    # ── Stub llm-roles.sh exocortex_resolve_role ──────────────────────────
    exocortex_resolve_role() {
      ROLE_PROVIDER="testprovider"
      ROLE_MODEL="$EXOCORTEX_DEFAULT_MODEL"
      ROLE_API_KEY="$EXOCORTEX_DEFAULT_API_KEY"
      ROLE_BASE_URL="$EXOCORTEX_DEFAULT_BASE_URL"
      ROLE_CHAT_URL="$EXOCORTEX_DEFAULT_BASE_URL/v1/chat/completions"
      ROLE_USABLE="1"
    }
    export -f exocortex_resolve_role

    # ── Stub common.sh helpers ───────────────────────────────────────────
    log()  { echo "LOG: $*"; }
    warn() { echo "WARN: $*"; }
    info() { echo "INFO: $*"; }
    fail() { echo "FAIL: $*"; exit 1; }
    export -f log warn info fail

    # ── Source only _verify_model_id from step-12 ─────────────────────────
    # We parse it out with sed to avoid running the top-level statements.
    STEP12="'"$STEP12"'"
    eval "$(sed -n "/_verify_model_id()/,/^}/p" "$STEP12")"

    _verify_model_id default "default"
    STATUS=$?
    rm -rf "$HERMES_HOME"
    exit $STATUS
  ' -- "$test_model" "$stub_http" "$stub_json" 2>&1
}

# =============================================================================
# T-MV-01: model present in /v1/models → exit 0
# =============================================================================
echo -e "${BOLD}T-MV-01: model id present → pass (exit 0)${NC}"

JSON='{"data":[{"id":"minimax-m3"},{"id":"gpt-4o"}]}'
out=""
out=$(_run_verify "minimax-m3" "200" "$JSON" 2>&1 || true)
exit_code=0
_run_verify "minimax-m3" "200" "$JSON" >/dev/null 2>&1 || exit_code=$?

if [ "$exit_code" -eq 0 ] && echo "$out" | grep -q "confirmado em /v1/models"; then
  pass "T-MV-01: model present → exit 0 + confirmation log"
else
  fail_test "T-MV-01" "exit_code=$exit_code output: $out"
fi

# =============================================================================
# T-MV-02: wrong-case id → non-zero + "did you mean" hint
# =============================================================================
echo -e "${BOLD}T-MV-02: wrong-case model id → non-zero exit + 'did you mean' hint${NC}"

JSON='{"data":[{"id":"minimax-m3"}]}'
out=""
out=$(_run_verify "MiniMax-M3" "200" "$JSON" 2>&1 || true)
exit_code=0
_run_verify "MiniMax-M3" "200" "$JSON" >/dev/null 2>&1 || exit_code=$?

if [ "$exit_code" -ne 0 ] && echo "$out" | grep -qi "did you mean\|você quis dizer"; then
  pass "T-MV-02: wrong-case id → non-zero exit + did-you-mean hint"
elif [ "$exit_code" -ne 0 ]; then
  fail_test "T-MV-02" "non-zero exit but no 'did you mean' hint in output: $out"
else
  fail_test "T-MV-02" "expected non-zero exit, got 0. output: $out"
fi

# =============================================================================
# T-MV-03: endpoint unreachable (000) → warns, exit 0
# =============================================================================
echo -e "${BOLD}T-MV-03: endpoint unreachable → warns, exit 0${NC}"

out=""
out=$(_run_verify "minimax-m3" "000" "" 2>&1 || true)
exit_code=0
_run_verify "minimax-m3" "000" "" >/dev/null 2>&1 || exit_code=$?

if [ "$exit_code" -eq 0 ] && echo "$out" | grep -qi "inalcançável\|offline\|air-gapped"; then
  pass "T-MV-03: endpoint unreachable → exit 0 + warn about offline"
elif [ "$exit_code" -eq 0 ]; then
  fail_test "T-MV-03" "exit 0 but no offline/unreachable message. output: $out"
else
  fail_test "T-MV-03" "expected exit 0 on unreachable endpoint, got $exit_code. output: $out"
fi

# =============================================================================
# T-MV-04: endpoint returns non-2xx (e.g. 501) → warns, exit 0
# =============================================================================
echo -e "${BOLD}T-MV-04: endpoint returns non-2xx (501) → warns, exit 0${NC}"

out=""
out=$(_run_verify "minimax-m3" "501" "" 2>&1 || true)
exit_code=0
_run_verify "minimax-m3" "501" "" >/dev/null 2>&1 || exit_code=$?

if [ "$exit_code" -eq 0 ] && echo "$out" | grep -q "501"; then
  pass "T-MV-04: non-2xx → exit 0 + warn with status code"
elif [ "$exit_code" -eq 0 ]; then
  fail_test "T-MV-04" "exit 0 but no mention of status code 501. output: $out"
else
  fail_test "T-MV-04" "expected exit 0, got $exit_code. output: $out"
fi

# =============================================================================
# T-MV-05: model absent, no near-match → non-zero exit, no "did you mean"
# =============================================================================
echo -e "${BOLD}T-MV-05: model absent, no near-match → non-zero exit without 'did you mean'${NC}"

JSON='{"data":[{"id":"gpt-4o"},{"id":"gpt-3.5-turbo"}]}'
out=""
out=$(_run_verify "completely-unknown-model" "200" "$JSON" 2>&1 || true)
exit_code=0
_run_verify "completely-unknown-model" "200" "$JSON" >/dev/null 2>&1 || exit_code=$?

if [ "$exit_code" -ne 0 ] && ! echo "$out" | grep -qi "did you mean\|você quis dizer"; then
  pass "T-MV-05: absent model, no match → non-zero, no false 'did you mean'"
elif [ "$exit_code" -ne 0 ]; then
  # Exit non-zero is correct; if "did you mean" appears, that's a false positive
  if echo "$out" | grep -qi "did you mean\|você quis dizer"; then
    fail_test "T-MV-05" "non-zero exit (good) but false 'did you mean' hint for unrelated model. output: $out"
  else
    pass "T-MV-05: absent model, no match → non-zero, no false 'did you mean'"
  fi
else
  fail_test "T-MV-05" "expected non-zero exit for missing model, got 0. output: $out"
fi

# =============================================================================
# Summary
# =============================================================================

echo ""
echo -e "${BOLD}=== Summary ===${NC}"
echo -e "  Total: $TOTAL  |  ${GREEN}Pass: $PASSED${NC}  |  ${RED}Fail: $FAILED${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
  echo -e "${RED}${BOLD}$FAILED test(s) failed.${NC}"
  exit 1
else
  echo -e "${GREEN}${BOLD}All tests passed.${NC}"
  exit 0
fi
