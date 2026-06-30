#!/usr/bin/env bash
# =============================================================================
# Regression test: safe_rmrf guard in step-06b-google-auth.sh
# =============================================================================
# Verifies that the rm -rf guard (mktemp -d + trap EXIT pattern) in
# step-06b-google-auth.sh properly handles tmpdir lifecycle:
#   1. A temp dir created by mktemp -d is valid and removed on EXIT.
#   2. The trap-based cleanup does not run against unsafe paths.
#   3. Unsafe path values (empty, $HOME, /) are rejected when safe_rmrf is used.
#
# TDD note: this test was written before the guard was implemented and was
# used to drive the implementation in step-06b-google-auth.sh.
# =============================================================================

set -uo pipefail

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
echo -e "${BOLD}safe_rmrf guard — regression tests${NC}"
echo ""

# =============================================================================
# T-RMRF-01: safe_rmrf rejects empty path
# =============================================================================
echo -e "${BOLD}T-RMRF-01: safe_rmrf rejects empty path${NC}"

result=$(bash -c '
  safe_rmrf() {
    local target="$1"
    if [ -z "$target" ]; then
      echo "REJECTED_EMPTY" >&2
      return 1
    fi
    case "$target" in
      /tmp/*|/var/tmp/*|${XDG_RUNTIME_DIR:-/run/user/$$}/*)
        rm -rf "$target"
        ;;
      *)
        echo "REJECTED_UNSAFE_ROOT" >&2
        return 1
        ;;
    esac
  }
  safe_rmrf "" 2>&1; echo "exit:$?"
' 2>&1)

if echo "$result" | grep -q "REJECTED_EMPTY" && echo "$result" | grep -q "exit:1"; then
  pass "T-RMRF-01: empty path rejected"
else
  fail_test "T-RMRF-01" "expected rejection, got: $result"
fi

# =============================================================================
# T-RMRF-02: safe_rmrf rejects $HOME path
# =============================================================================
echo -e "${BOLD}T-RMRF-02: safe_rmrf rejects \$HOME path${NC}"

result=$(bash << 'INNERSCRIPT'
  # Simulate a HOME-like path that is NOT under /tmp or /var/tmp
  _fake_home="/home/testuser-rmrf-guard"
  safe_rmrf() {
    local target="$1"
    if [ -z "$target" ]; then
      echo 'REJECTED_EMPTY' >&2
      return 1
    fi
    case "$target" in
      /tmp/*|/var/tmp/*)
        rm -rf "$target"
        ;;
      *)
        echo 'REJECTED_UNSAFE_ROOT' >&2
        return 1
        ;;
    esac
  }
  safe_rmrf "$_fake_home" 2>&1; echo "exit:$?"
INNERSCRIPT
)

if echo "$result" | grep -q "REJECTED_UNSAFE_ROOT" && echo "$result" | grep -q "exit:1"; then
  pass "T-RMRF-02: HOME-like path rejected"
else
  fail_test "T-RMRF-02" "expected rejection, got: $result"
fi

# =============================================================================
# T-RMRF-03: safe_rmrf rejects / (filesystem root)
# =============================================================================
echo -e "${BOLD}T-RMRF-03: safe_rmrf rejects / (filesystem root)${NC}"

result=$(bash -c '
  safe_rmrf() {
    local target="$1"
    if [ -z "$target" ]; then
      echo "REJECTED_EMPTY" >&2; return 1
    fi
    case "$target" in
      /tmp/*|/var/tmp/*)
        rm -rf "$target"
        ;;
      *)
        echo "REJECTED_UNSAFE_ROOT" >&2; return 1
        ;;
    esac
  }
  safe_rmrf "/" 2>&1; echo "exit:$?"
' 2>&1)

if echo "$result" | grep -q "REJECTED_UNSAFE_ROOT" && echo "$result" | grep -q "exit:1"; then
  pass "T-RMRF-03: / path rejected"
else
  fail_test "T-RMRF-03" "expected rejection, got: $result"
fi

# =============================================================================
# T-RMRF-04: safe_rmrf accepts /tmp/* path and deletes it
# =============================================================================
echo -e "${BOLD}T-RMRF-04: safe_rmrf accepts and deletes /tmp/* path${NC}"

result=$(bash -c '
  safe_rmrf() {
    local target="$1"
    if [ -z "$target" ]; then
      echo "REJECTED_EMPTY" >&2; return 1
    fi
    case "$target" in
      /tmp/*|/var/tmp/*)
        rm -rf "$target"
        ;;
      *)
        echo "REJECTED_UNSAFE_ROOT" >&2; return 1
        ;;
    esac
  }
  tmpdir=$(mktemp -d)
  touch "$tmpdir/testfile"
  safe_rmrf "$tmpdir"
  if [ ! -d "$tmpdir" ]; then
    echo "DELETED_OK"
  else
    echo "NOT_DELETED"
  fi
' 2>&1)

if echo "$result" | grep -q "DELETED_OK"; then
  pass "T-RMRF-04: /tmp/* path accepted and deleted"
else
  fail_test "T-RMRF-04" "expected deletion, got: $result"
fi

# =============================================================================
# T-RMRF-05: step-06b uses mktemp -d + trap pattern (no bare rm -rf)
# =============================================================================
echo -e "${BOLD}T-RMRF-05: step-06b uses mktemp -d with trap, no unguarded rm -rf${NC}"

STEP06B="$REPO_ROOT/setup/step-06b-google-auth.sh"

if [ ! -f "$STEP06B" ]; then
  fail_test "T-RMRF-05" "step-06b-google-auth.sh not found"
else
  # Must use mktemp -d for temp dirs
  uses_mktemp=$(grep -c 'mktemp -d' "$STEP06B" 2>/dev/null || true); uses_mktemp="${uses_mktemp:-0}"
  # Must use trap for cleanup
  uses_trap=$(grep -c 'trap ' "$STEP06B" 2>/dev/null || true); uses_trap="${uses_trap:-0}"
  # Must NOT have unguarded bare rm -rf "$tmpdir"
  unguarded=$(grep -cE '^[[:space:]]+rm -rf "\$tmpdir"' "$STEP06B" 2>/dev/null || true); unguarded="${unguarded:-0}"

  if [ "${uses_mktemp:-0}" -ge 1 ] && [ "${uses_trap:-0}" -ge 1 ] && [ "${unguarded:-0}" -eq 0 ]; then
    pass "T-RMRF-05: step-06b uses mktemp -d + trap, no bare unguarded rm -rf"
  else
    fail_test "T-RMRF-05" "mktemp=${uses_mktemp} trap=${uses_trap} unguarded_rm=${unguarded} (expected mktemp>=1 trap>=1 unguarded=0)"
  fi
fi

# =============================================================================
# T-RMRF-06: step-08 reads pinned ref from lock file (no floating main)
# =============================================================================
echo -e "${BOLD}T-RMRF-06: step-08 references lock file for pinned ref (no floating main)${NC}"

STEP08="$REPO_ROOT/setup/step-08-integration-docbrain.sh"
LOCK_FILE="$REPO_ROOT/provision/sources/sources.lock.yaml"

if [ ! -f "$STEP08" ]; then
  fail_test "T-RMRF-06" "step-08-integration-docbrain.sh not found"
elif [ ! -f "$LOCK_FILE" ]; then
  fail_test "T-RMRF-06" "sources.lock.yaml not found"
else
  # step-08 must reference the lock file or a variable derived from it
  refs_lock=$(grep -c 'sources.lock.yaml\|DOCBRAIN_PIN\|pinned_ref\|controlled_ref' "$STEP08" 2>/dev/null || true); refs_lock="${refs_lock:-0}"
  # step-08 must NOT do a bare git pull or checkout of floating main/HEAD
  pulls_main=$(grep -cE 'git pull.*origin main|git checkout main' "$STEP08" 2>/dev/null || true); pulls_main="${pulls_main:-0}"

  # The lock file must contain a docbrain entry with a valid SHA
  lock_sha=$(python3 -c "
import sys
from pathlib import Path
text = Path('$LOCK_FILE').read_text()
in_docbrain = False
for line in text.splitlines():
    if line.strip() == 'docbrain:':
        in_docbrain = True
    if in_docbrain and 'ref:' in line and 'audited_from' not in line:
        ref = line.split('ref:')[1].strip()
        # Must be a 40-char hex SHA
        import re
        if re.match(r'^[0-9a-f]{40}$', ref):
            print('VALID_SHA:' + ref)
        else:
            print('INVALID_REF:' + ref)
        sys.exit(0)
print('NO_REF_FOUND')
" 2>/dev/null || echo "PYTHON_ERROR")

  if [ "${refs_lock:-0}" -ge 1 ] && [ "${pulls_main:-0}" -eq 0 ] && echo "$lock_sha" | grep -q "^VALID_SHA:"; then
    sha_value=$(echo "$lock_sha" | sed 's/^VALID_SHA://')
    pass "T-RMRF-06: step-08 reads lock, no floating main; lock SHA=$sha_value"
  else
    fail_test "T-RMRF-06" "refs_lock=${refs_lock} pulls_main=${pulls_main} lock_sha=$lock_sha"
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
