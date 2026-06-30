#!/usr/bin/env bash
# =============================================================================
# Unit-style tests: toggle gate in setup/step-11-integration-context7.sh
# =============================================================================
# T-CTX-01: toggle OFF + no key → step-11 skips cleanly (exit 0, no hermes call)
# T-CTX-02: toggle ON + no key → proceeds, reminder file written
# T-CTX-03: key present (toggle unset) → back-compat, hermes mcp add called
# T-CTX-04: toggle gate check is present in step-11 (structural)
# T-CTX-05: smoke.sh exits non-zero when hermes not in PATH
# T-CTX-06: smoke.sh exits non-zero when context7 not listed in hermes mcp list
# T-CTX-07: smoke.sh exits 0 when context7 is listed in hermes mcp list
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
echo -e "${BOLD}step-11 Context7 toggle gate — unit tests${NC}"
echo ""

STEP11="$REPO_ROOT/setup/step-11-integration-context7.sh"
SMOKE_SH="$REPO_ROOT/provision/context7/scripts/smoke.sh"

if [ ! -f "$STEP11" ]; then
  echo -e "${RED}FATAL: step-11-integration-context7.sh not found${NC}"
  exit 1
fi

# Helper: run step-11 with a controlled environment.
# Injects stub common.sh functions (info/warn/log/fail) so the system 'info'
# binary is never reached. Also stubs 'hermes' via a PATH prefix.
#
# Usage: _run_step11 <tmp_dir> [env_pairs...]
# All env vars must be set in the CALLING environment before calling this fn.
_wrap_step11() {
  local tmp="$1"
  # Write a stub common.sh functions script loaded via _EXOCORTEX_COMMON_LOADED guard bypass.
  # We supply the functions directly in the subprocess env.
  HERMES_HOME="$tmp" \
    _EXOCORTEX_COMMON_LOADED=1 \
    PATH="$tmp:$PATH" \
    bash -c "
      set -euo pipefail
      # Provide stub logging functions so system 'info' is never invoked
      info() { echo \"INFO: \$*\"; }
      warn() { echo \"WARN: \$*\"; }
      log()  { echo \"LOG: \$*\"; }
      fail() { echo \"FAIL: \$*\"; exit 1; }
      export -f info warn log fail
      source '$STEP11'
    " 2>&1
}

# =============================================================================
# T-CTX-01: toggle OFF + no key → step-11 skips cleanly (exit 0, no hermes call)
# =============================================================================
echo -e "${BOLD}T-CTX-01: toggle OFF + no key → skip (exit 0, no hermes call)${NC}"

T01_DIR="$(mktemp -d)"

# hermes stub: logs every invocation so we can detect unexpected calls
cat > "$T01_DIR/hermes" << 'STUB'
#!/usr/bin/env bash
echo "hermes_called" >> "$T01_DIR/calls.log"
exit 0
STUB
# T01_DIR is not in scope in the here-doc; embed it directly:
sed -i "s|\\\$T01_DIR|$T01_DIR|g" "$T01_DIR/hermes"
chmod +x "$T01_DIR/hermes"

T01_EXIT=0
T01_OUT="$(EXOCORTEX_ENABLE_CONTEXT7="" \
  CONTEXT7_API_KEY="" \
  T01_DIR="$T01_DIR" \
  HERMES_HOME="$T01_DIR" \
  _EXOCORTEX_COMMON_LOADED=1 \
  PATH="$T01_DIR:$PATH" \
  bash -c "
    set -euo pipefail
    info() { echo \"INFO: \$*\"; }
    warn() { echo \"WARN: \$*\"; }
    log()  { echo \"LOG: \$*\"; }
    fail() { echo \"FAIL: \$*\"; exit 1; }
    export -f info warn log fail
    source '$STEP11'
  " 2>&1)" || T01_EXIT=$?

_hermes_called=0
[ -f "$T01_DIR/calls.log" ] && _hermes_called=1
rm -rf "$T01_DIR"

if [ "$T01_EXIT" -eq 0 ] && \
   echo "$T01_OUT" | grep -qi "não ativado\|não ativ\|Context7 não\|INFO.*configurar" && \
   [ "$_hermes_called" -eq 0 ]; then
  pass "T-CTX-01: toggle OFF + no key → skipped cleanly, no hermes call"
else
  fail_test "T-CTX-01" "exit=$T01_EXIT hermes_called=$_hermes_called; expected exit=0 + skip message; output: $(echo "$T01_OUT" | head -5)"
fi

# =============================================================================
# T-CTX-02: toggle ON + no key → proceeds, reminder file written
# =============================================================================
echo -e "${BOLD}T-CTX-02: toggle ON + no key → proceeds, reminder written${NC}"

T02_DIR="$(mktemp -d)"

# hermes stub: mcp list → nothing, mcp add → succeeds
cat > "$T02_DIR/hermes" << 'STUB'
#!/usr/bin/env bash
case "$1 $2" in
  "mcp list") exit 0 ;;
  "mcp add")  exit 0 ;;
esac
exit 0
STUB
chmod +x "$T02_DIR/hermes"

T02_EXIT=0
T02_OUT="$(EXOCORTEX_ENABLE_CONTEXT7="1" \
  CONTEXT7_API_KEY="" \
  HERMES_HOME="$T02_DIR" \
  _EXOCORTEX_COMMON_LOADED=1 \
  PATH="$T02_DIR:$PATH" \
  bash -c "
    set -euo pipefail
    info() { echo \"INFO: \$*\"; }
    warn() { echo \"WARN: \$*\"; }
    log()  { echo \"LOG: \$*\"; }
    fail() { echo \"FAIL: \$*\"; exit 1; }
    export -f info warn log fail
    source '$STEP11'
  " 2>&1)" || T02_EXIT=$?

_reminder="$T02_DIR/reminders/context7-api-key.md"
_reminder_exists=0
[ -f "$_reminder" ] && _reminder_exists=1
rm -rf "$T02_DIR"

if [ "$T02_EXIT" -eq 0 ] && [ "$_reminder_exists" -eq 1 ]; then
  pass "T-CTX-02: toggle ON + no key → proceeded, reminder file written"
else
  fail_test "T-CTX-02" "exit=$T02_EXIT reminder_exists=$_reminder_exists; expected exit=0+reminder; output: $(echo "$T02_OUT" | head -5)"
fi

# =============================================================================
# T-CTX-03: key present (toggle unset) → back-compat, mcp add called
# =============================================================================
echo -e "${BOLD}T-CTX-03: key present (toggle unset) → back-compat proceeds${NC}"

T03_DIR="$(mktemp -d)"

# hermes stub: mcp list → nothing (context7 not yet registered); mcp add → logs call
cat > "$T03_DIR/hermes" << 'STUB'
#!/usr/bin/env bash
CALLLOG="PLACEHOLDER/calls.log"
case "$1 $2" in
  "mcp list") exit 0 ;;
  "mcp add")
    echo "add_called" >> "$CALLLOG"
    exit 0
    ;;
esac
exit 0
STUB
# Replace PLACEHOLDER with actual T03_DIR
sed -i "s|PLACEHOLDER|$T03_DIR|g" "$T03_DIR/hermes"
chmod +x "$T03_DIR/hermes"

T03_EXIT=0
T03_OUT="$(EXOCORTEX_ENABLE_CONTEXT7="" \
  CONTEXT7_API_KEY="ctx7-backcompat-key" \
  HERMES_HOME="$T03_DIR" \
  _EXOCORTEX_COMMON_LOADED=1 \
  PATH="$T03_DIR:$PATH" \
  bash -c "
    set -euo pipefail
    info() { echo \"INFO: \$*\"; }
    warn() { echo \"WARN: \$*\"; }
    log()  { echo \"LOG: \$*\"; }
    fail() { echo \"FAIL: \$*\"; exit 1; }
    export -f info warn log fail
    source '$STEP11'
  " 2>&1)" || T03_EXIT=$?

_add_called=0
[ -f "$T03_DIR/calls.log" ] && grep -q "add_called" "$T03_DIR/calls.log" && _add_called=1
rm -rf "$T03_DIR"

if [ "$T03_EXIT" -eq 0 ] && [ "$_add_called" -eq 1 ]; then
  pass "T-CTX-03: key present with toggle unset → back-compat, hermes mcp add called"
else
  fail_test "T-CTX-03" "exit=$T03_EXIT add_called=$_add_called; expected exit=0+add; output: $(echo "$T03_OUT" | head -5)"
fi

# =============================================================================
# T-CTX-04: toggle gate is structurally present in step-11
# =============================================================================
echo -e "${BOLD}T-CTX-04: toggle gate structurally present in step-11${NC}"

_has_toggle=$(grep -c "EXOCORTEX_ENABLE_CONTEXT7" "$STEP11" 2>/dev/null || true)
_has_backcompat=$(grep -c "CONTEXT7_API_KEY" "$STEP11" 2>/dev/null || true)

if [ "${_has_toggle:-0}" -ge 1 ] && [ "${_has_backcompat:-0}" -ge 2 ]; then
  pass "T-CTX-04: toggle gate + back-compat key check present in step-11"
else
  fail_test "T-CTX-04" "toggle_refs=${_has_toggle} key_refs=${_has_backcompat} (expected toggle>=1, key>=2)"
fi

# =============================================================================
# T-CTX-05: smoke.sh exits non-zero when hermes not in PATH
# =============================================================================
echo -e "${BOLD}T-CTX-05: smoke.sh exits non-zero when hermes missing${NC}"

if [ ! -f "$SMOKE_SH" ]; then
  fail_test "T-CTX-05" "provision/context7/scripts/smoke.sh not found"
else
  T05_DIR="$(mktemp -d)"

  # PATH with no hermes binary; use /usr/bin only to keep basic shell tools
  T05_EXIT=0
  HERMES_HOME="$T05_DIR" PATH="$T05_DIR:/usr/bin:/bin" \
    bash "$SMOKE_SH" >/dev/null 2>&1 || T05_EXIT=$?
  rm -rf "$T05_DIR"

  if [ "$T05_EXIT" -ne 0 ]; then
    pass "T-CTX-05: smoke.sh exits non-zero when hermes missing"
  else
    fail_test "T-CTX-05" "expected non-zero exit when hermes absent, got exit=0"
  fi
fi

# =============================================================================
# T-CTX-06: smoke.sh exits non-zero when context7 not in hermes mcp list
# =============================================================================
echo -e "${BOLD}T-CTX-06: smoke.sh exits non-zero when context7 not registered${NC}"

if [ ! -f "$SMOKE_SH" ]; then
  fail_test "T-CTX-06" "provision/context7/scripts/smoke.sh not found"
else
  T06_DIR="$(mktemp -d)"

  # hermes stub: mcp list prints nothing → context7 absent
  cat > "$T06_DIR/hermes" << 'STUB'
#!/usr/bin/env bash
exit 0
STUB
  chmod +x "$T06_DIR/hermes"

  T06_EXIT=0
  HERMES_HOME="$T06_DIR" PATH="$T06_DIR:$PATH" \
    bash "$SMOKE_SH" >/dev/null 2>&1 || T06_EXIT=$?
  rm -rf "$T06_DIR"

  if [ "$T06_EXIT" -ne 0 ]; then
    pass "T-CTX-06: smoke.sh exits non-zero when context7 not in mcp list"
  else
    fail_test "T-CTX-06" "expected non-zero exit when context7 absent, got exit=0"
  fi
fi

# =============================================================================
# T-CTX-07: smoke.sh exits 0 when context7 is registered in hermes mcp list
# =============================================================================
echo -e "${BOLD}T-CTX-07: smoke.sh exits 0 when context7 registered${NC}"

if [ ! -f "$SMOKE_SH" ]; then
  fail_test "T-CTX-07" "provision/context7/scripts/smoke.sh not found"
else
  T07_DIR="$(mktemp -d)"

  # hermes stub: mcp list prints a line containing "context7"
  cat > "$T07_DIR/hermes" << 'STUB'
#!/usr/bin/env bash
case "$1 $2" in
  "mcp list") echo "context7   npx -y @context7/mcp   registered" ;;
esac
exit 0
STUB
  chmod +x "$T07_DIR/hermes"

  T07_EXIT=0
  HERMES_HOME="$T07_DIR" PATH="$T07_DIR:$PATH" \
    bash "$SMOKE_SH" >/dev/null 2>&1 || T07_EXIT=$?
  rm -rf "$T07_DIR"

  if [ "$T07_EXIT" -eq 0 ]; then
    pass "T-CTX-07: smoke.sh exits 0 when context7 registered in mcp list"
  else
    fail_test "T-CTX-07" "expected exit=0 when context7 registered, got exit=$T07_EXIT"
  fi
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
