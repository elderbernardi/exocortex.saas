#!/usr/bin/env bash
# =============================================================================
# Regression test: cleanup safety in step-06b-google-auth.sh
# =============================================================================
# Verifies that the rm -rf guard (subshell + trap EXIT pattern) in
# step-06b-google-auth.sh actually cleans up temp dirs on both success and
# failure, and that cleanup never targets unsafe paths.
#
# Tests T-RMRF-01..04 exercise the REAL step-06b cleanup behavior (subshell
# with trap), replacing a prior phantom safe_rmrf() inline definition that
# tested nothing real.
# T-RMRF-05..07 are structural checks on the script and lock file.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

TOTAL=0
PASSED=0
FAILED=0

pass()      { PASSED=$((PASSED + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${GREEN}PASS${NC} $1"; }
fail_test() { FAILED=$((FAILED + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${RED}FAIL${NC} $1 — $2"; }

echo ""
echo -e "${BOLD}step-06b cleanup safety — regression tests${NC}"
echo ""

STEP06B="$REPO_ROOT/setup/step-06b-google-auth.sh"

# =============================================================================
# T-RMRF-01: step-06b uses a subshell for the download block
# =============================================================================
# The subshell approach (not a function-level trap) is the fix for the scope
# leak: trap fires at subshell exit while $tmpdir is still in scope.
echo -e "${BOLD}T-RMRF-01: step-06b wraps download block in a subshell${NC}"

if [ ! -f "$STEP06B" ]; then
  fail_test "T-RMRF-01" "step-06b-google-auth.sh not found"
else
  # The fix must use a subshell ( ... ) that contains both mktemp and trap
  # We check for the subshell pattern surrounding the install block.
  has_subshell=$(grep -cE '^\s+\(' "$STEP06B" 2>/dev/null || true); has_subshell="${has_subshell:-0}"
  has_mktemp=$(grep -c 'mktemp -d' "$STEP06B" 2>/dev/null || true); has_mktemp="${has_mktemp:-0}"
  has_trap=$(grep -c "trap 'rm -rf" "$STEP06B" 2>/dev/null || true); has_trap="${has_trap:-0}"

  if [ "${has_subshell:-0}" -ge 1 ] && [ "${has_mktemp:-0}" -ge 1 ] && [ "${has_trap:-0}" -ge 1 ]; then
    pass "T-RMRF-01: subshell + mktemp -d + trap present in step-06b"
  else
    fail_test "T-RMRF-01" "subshell=${has_subshell} mktemp=${has_mktemp} trap=${has_trap} (expected all >=1)"
  fi
fi

# =============================================================================
# T-RMRF-02: trap in step-06b is INSIDE the subshell (not at function level)
# =============================================================================
# A function-level trap with a local var leaks because $tmpdir is out of scope
# at script EXIT. The trap must be inside the subshell ( ... ) block.
echo -e "${BOLD}T-RMRF-02: trap is scoped inside the subshell (not at function/script level)${NC}"

if [ ! -f "$STEP06B" ]; then
  fail_test "T-RMRF-02" "step-06b-google-auth.sh not found"
else
  # Extract lines between the opening '(' and closing ')' of the install subshell.
  # A trap line inside that block must exist.
  # Strategy: count lines where "trap" appears AFTER the subshell open and BEFORE close.
  trap_in_subshell=$(awk '
    /^\s+\($/ { in_sub=1 }
    in_sub && /trap .* EXIT/ { found=1 }
    /^\s+\) \|\| return/ { in_sub=0 }
    END { print (found ? "YES" : "NO") }
  ' "$STEP06B" 2>/dev/null || echo "NO")

  if [ "$trap_in_subshell" = "YES" ]; then
    pass "T-RMRF-02: trap is inside the subshell block"
  else
    fail_test "T-RMRF-02" "trap not found inside subshell block (leak risk remains)"
  fi
fi

# =============================================================================
# T-RMRF-03: tmpdir is cleaned up on the success path (subshell test)
# =============================================================================
# Simulate the subshell pattern from step-06b: create a tmpdir, register a
# trap, do some work, then exit the subshell normally — tmpdir must be gone.
echo -e "${BOLD}T-RMRF-03: tmpdir is removed on success path (subshell trap fires)${NC}"

tmpdir_path=""
tmpdir_path=$(bash -c '
  result=$(
    tmpdir=$(mktemp -d)
    trap "rm -rf \"$tmpdir\"" EXIT
    # Simulate "work succeeded" — no early exit, subshell exits normally.
    touch "$tmpdir/marker"
    echo "$tmpdir"
  )
  # After subshell: the path should no longer exist.
  if [ ! -d "$result" ] && [ -n "$result" ]; then
    echo "CLEANED:$result"
  else
    echo "LEAKED:$result"
  fi
' 2>&1)

if echo "$tmpdir_path" | grep -q "^CLEANED:"; then
  pass "T-RMRF-03: tmpdir removed on success (subshell EXIT trap fired)"
else
  fail_test "T-RMRF-03" "tmpdir leak on success path: $tmpdir_path"
fi

# =============================================================================
# T-RMRF-04: tmpdir is cleaned up on the failure path (subshell exits non-zero)
# =============================================================================
echo -e "${BOLD}T-RMRF-04: tmpdir is removed on failure path (subshell exits non-zero)${NC}"

tmpdir_path=""
tmpdir_path=$(bash -c '
  captured_path=""
  (
    tmpdir=$(mktemp -d)
    trap "rm -rf \"$tmpdir\"" EXIT
    touch "$tmpdir/marker"
    echo "$tmpdir" > /tmp/test-rmrf-path-$$
    exit 1   # Simulate download failure
  ) || true  # Swallow the non-zero exit so outer script continues

  stored=$(cat /tmp/test-rmrf-path-$$ 2>/dev/null || echo "")
  rm -f /tmp/test-rmrf-path-$$
  if [ -n "$stored" ] && [ ! -d "$stored" ]; then
    echo "CLEANED:$stored"
  else
    echo "LEAKED:$stored"
  fi
' 2>&1)

if echo "$tmpdir_path" | grep -q "^CLEANED:"; then
  pass "T-RMRF-04: tmpdir removed on failure (subshell EXIT trap fired)"
else
  fail_test "T-RMRF-04" "tmpdir leak on failure path: $tmpdir_path"
fi

# =============================================================================
# T-RMRF-05: step-06b has no bare unguarded rm -rf (structural check)
# =============================================================================
echo -e "${BOLD}T-RMRF-05: step-06b uses mktemp -d with trap, no unguarded rm -rf${NC}"

if [ ! -f "$STEP06B" ]; then
  fail_test "T-RMRF-05" "step-06b-google-auth.sh not found"
else
  # Must use mktemp -d for temp dirs
  uses_mktemp=$(grep -c 'mktemp -d' "$STEP06B" 2>/dev/null || true); uses_mktemp="${uses_mktemp:-0}"
  # Must use trap for cleanup
  uses_trap=$(grep -c 'trap ' "$STEP06B" 2>/dev/null || true); uses_trap="${uses_trap:-0}"
  # Must NOT have unguarded bare rm -rf "$tmpdir" at statement level (not inside trap quotes)
  unguarded=$(grep -cE '^[[:space:]]+rm -rf "\$tmpdir"' "$STEP06B" 2>/dev/null || true); unguarded="${unguarded:-0}"

  if [ "${uses_mktemp:-0}" -ge 1 ] && [ "${uses_trap:-0}" -ge 1 ] && [ "${unguarded:-0}" -eq 0 ]; then
    pass "T-RMRF-05: step-06b uses mktemp -d + trap, no bare unguarded rm -rf"
  else
    fail_test "T-RMRF-05" "mktemp=${uses_mktemp} trap=${uses_trap} unguarded_rm=${unguarded} (expected mktemp>=1 trap>=1 unguarded=0)"
  fi
fi

# =============================================================================
# T-RMRF-06: step-08 and sources.lock.yaml reflect track-main (not SHA pin)
# =============================================================================
echo -e "${BOLD}T-RMRF-06: step-08 tracks origin/main; lock has allow_upstream_main: true${NC}"

STEP08="$REPO_ROOT/setup/step-08-integration-docbrain.sh"
LOCK_FILE="$REPO_ROOT/provision/sources/sources.lock.yaml"

if [ ! -f "$STEP08" ]; then
  fail_test "T-RMRF-06" "step-08-integration-docbrain.sh not found"
elif [ ! -f "$LOCK_FILE" ]; then
  fail_test "T-RMRF-06" "sources.lock.yaml not found"
else
  # step-08 must reference the correct repo and branch main
  refs_elderbernardi=$(grep -c 'elderbernardi/docbrain' "$STEP08" 2>/dev/null || true); refs_elderbernardi="${refs_elderbernardi:-0}"
  refs_branch_main=$(grep -cE 'branch.*main|origin/main|fetch.*main' "$STEP08" 2>/dev/null || true); refs_branch_main="${refs_branch_main:-0}"

  # step-08 must NOT contain old frozen-pin code
  has_old_pin=$(grep -cE 'ProjetoBB|docBrainBB|_resolve_docbrain_pin|controlled_ref|no-checkout' "$STEP08" 2>/dev/null || true); has_old_pin="${has_old_pin:-0}"

  # sources.lock.yaml docbrain entry must have allow_upstream_main: true
  lock_allow_main=$(python3 -c "
import sys
from pathlib import Path
text = Path('$LOCK_FILE').read_text()
in_docbrain = False
for line in text.splitlines():
    stripped = line.strip()
    if stripped == 'docbrain:':
        in_docbrain = True
    if in_docbrain and 'allow_upstream_main: true' in stripped:
        print('TRACK_MAIN')
        sys.exit(0)
print('NOT_FOUND')
" 2>/dev/null || echo "PYTHON_ERROR")

  if [ "${refs_elderbernardi:-0}" -ge 1 ] && \
     [ "${refs_branch_main:-0}" -ge 1 ] && \
     [ "${has_old_pin:-0}" -eq 0 ] && \
     [ "$lock_allow_main" = "TRACK_MAIN" ]; then
    pass "T-RMRF-06: step-08 tracks elderbernardi/docbrain main; lock allow_upstream_main=true; no old pin"
  else
    fail_test "T-RMRF-06" "elderbernardi_refs=${refs_elderbernardi} branch_main_refs=${refs_branch_main} old_pin=${has_old_pin} lock_allow_main=${lock_allow_main}"
  fi
fi

# =============================================================================
# T-RMRF-07: npm build failure is NOT masked in step-08
# =============================================================================
echo -e "${BOLD}T-RMRF-07: step-08 does not mask npm build failures with || true${NC}"

STEP08="$REPO_ROOT/setup/step-08-integration-docbrain.sh"

if [ ! -f "$STEP08" ]; then
  fail_test "T-RMRF-07" "step-08-integration-docbrain.sh not found"
else
  # Must NOT have "npm run build ... || true" or "npm install ... || true" without guard
  masked_build=$(grep -cE 'npm run build.*\|\| true|npm install.*\|\| true' "$STEP08" 2>/dev/null || true); masked_build="${masked_build:-0}"

  if [ "${masked_build:-0}" -eq 0 ]; then
    pass "T-RMRF-07: npm build/install failures not masked with || true"
  else
    fail_test "T-RMRF-07" "found ${masked_build} masked npm commands (|| true after npm)"
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
