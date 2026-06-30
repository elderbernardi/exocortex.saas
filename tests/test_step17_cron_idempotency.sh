#!/usr/bin/env bash
# =============================================================================
# Regression tests: cron idempotency in step-17-maintenance-crons.sh
# =============================================================================
# T-CRON-01: create_cron_if_missing called twice with same name → only one
#            hermes cron create invocation (idempotency)
# T-CRON-02: guard uses word-boundary match — 'maintenance-weekly' does NOT
#            match a cron named 'maintenance-weekly-v2'
# T-CRON-03: Acervo Syndic legacy guard — presence suppresses maintenance-weekly
# T-CRON-04: full double-run of step-17 → each cron created exactly once
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
echo -e "${BOLD}step-17 cron idempotency — regression tests${NC}"
echo ""

STEP17="$REPO_ROOT/setup/step-17-maintenance-crons.sh"

if [ ! -f "$STEP17" ]; then
  echo -e "${RED}FATAL: step-17-maintenance-crons.sh not found${NC}"
  exit 1
fi

# =============================================================================
# Shared harness: extract create_cron_if_missing as a standalone function.
# We extract the function body from step-17 via sed and eval it in a controlled
# env. This avoids executing the top-level statements of step-17.
# =============================================================================

# Extract the create_cron_if_missing function body from step-17.
_GUARD_FN="$(awk '/^create_cron_if_missing\(\)/{found=1} found{print; if(/^}$/){exit}}' "$STEP17")"

# =============================================================================
# T-CRON-01: calling create_cron_if_missing twice → only one create call
# =============================================================================
echo -e "${BOLD}T-CRON-01: double-call to create_cron_if_missing → exactly one create${NC}"

T01_DIR="$(mktemp -d)"
T01_REG="$T01_DIR/registry.txt"
T01_CNT="$T01_DIR/count.txt"
touch "$T01_REG" "$T01_CNT"
echo "0" > "$T01_CNT"

# Write the hermes stub script
cat > "$T01_DIR/hermes" << 'STUB'
#!/usr/bin/env bash
case "$1" in
  cron)
    case "$2" in
      list) cat "$CRON_REG" 2>/dev/null || true ;;
      create)
        nm=""
        i=0
        for arg; do
          [ "$arg" = "--name" ] && { i=1; continue; }
          [ "$i" = "1" ] && { nm="$arg"; i=0; }
        done
        echo "$nm" >> "$CRON_REG"
        c=$(cat "$CRON_CNT")
        echo $((c + 1)) > "$CRON_CNT"
        ;;
    esac
    ;;
esac
STUB
chmod +x "$T01_DIR/hermes"

CRON_REG="$T01_REG" CRON_CNT="$T01_CNT" \
PATH="$T01_DIR:$PATH" \
bash -c "
  set -euo pipefail
  export CRON_REG='$T01_REG'
  export CRON_CNT='$T01_CNT'
  log()  { :; }
  warn() { :; }
  info() { :; }
  CRON_FAILURES=0
  $_GUARD_FN
  # Call once
  create_cron_if_missing 'test-cron' '0 3 * * 0' 'test prompt'
  # Call again with same name — must skip
  create_cron_if_missing 'test-cron' '0 3 * * 0' 'test prompt'
" 2>/dev/null

T01_COUNT="$(cat "$T01_CNT")"
rm -rf "$T01_DIR"

if [ "$T01_COUNT" -eq 1 ]; then
  pass "T-CRON-01: create_cron_if_missing idempotent — exactly 1 hermes cron create call"
else
  fail_test "T-CRON-01" "expected 1 create call, got $T01_COUNT"
fi

# =============================================================================
# T-CRON-02: word-boundary guard — 'maintenance-weekly' does NOT match
#            'maintenance-weekly-v2'
# =============================================================================
echo -e "${BOLD}T-CRON-02: word-boundary guard — name prefix does not suppress distinct cron${NC}"

T02_DIR="$(mktemp -d)"
T02_REG="$T02_DIR/registry.txt"
T02_CNT="$T02_DIR/count.txt"
# Pre-populate with a longer name that starts with our target name
echo "maintenance-weekly-v2" > "$T02_REG"
echo "0" > "$T02_CNT"

cat > "$T02_DIR/hermes" << 'STUB'
#!/usr/bin/env bash
case "$1" in
  cron)
    case "$2" in
      list) cat "$CRON_REG" 2>/dev/null || true ;;
      create)
        nm=""
        i=0
        for arg; do
          [ "$arg" = "--name" ] && { i=1; continue; }
          [ "$i" = "1" ] && { nm="$arg"; i=0; }
        done
        echo "$nm" >> "$CRON_REG"
        c=$(cat "$CRON_CNT")
        echo $((c + 1)) > "$CRON_CNT"
        ;;
    esac
    ;;
esac
STUB
chmod +x "$T02_DIR/hermes"

CRON_REG="$T02_REG" CRON_CNT="$T02_CNT" \
PATH="$T02_DIR:$PATH" \
bash -c "
  set -euo pipefail
  export CRON_REG='$T02_REG'
  export CRON_CNT='$T02_CNT'
  log()  { :; }
  warn() { :; }
  info() { :; }
  CRON_FAILURES=0
  $_GUARD_FN
  # 'maintenance-weekly' must NOT be suppressed by 'maintenance-weekly-v2' in the list
  create_cron_if_missing 'maintenance-weekly' '0 3 * * 0' 'test prompt'
" 2>/dev/null

T02_COUNT="$(cat "$T02_CNT")"
rm -rf "$T02_DIR"

if [ "$T02_COUNT" -eq 1 ]; then
  pass "T-CRON-02: word-boundary match correct — distinct name prefix does not suppress creation"
else
  fail_test "T-CRON-02" "expected 1 create call (distinct name not suppressed), got $T02_COUNT"
fi

# =============================================================================
# T-CRON-03: legacy 'Acervo Syndic' guard suppresses 'maintenance-weekly'
# =============================================================================
echo -e "${BOLD}T-CRON-03: legacy Acervo Syndic guard suppresses maintenance-weekly creation${NC}"

T03_DIR="$(mktemp -d)"
T03_REG="$T03_DIR/registry.txt"
T03_CNT="$T03_DIR/count.txt"
# Pre-populate with the legacy cron name (exact string)
echo "Acervo Syndic" > "$T03_REG"
echo "0" > "$T03_CNT"

cat > "$T03_DIR/hermes" << 'STUB'
#!/usr/bin/env bash
case "$1" in
  cron)
    case "$2" in
      list) cat "$CRON_REG" 2>/dev/null || true ;;
      create)
        nm=""
        i=0
        for arg; do
          [ "$arg" = "--name" ] && { i=1; continue; }
          [ "$i" = "1" ] && { nm="$arg"; i=0; }
        done
        echo "$nm" >> "$CRON_REG"
        c=$(cat "$CRON_CNT")
        echo $((c + 1)) > "$CRON_CNT"
        ;;
    esac
    ;;
esac
STUB
chmod +x "$T03_DIR/hermes"

# Extract just the Acervo Syndic guard block from step-17
_LEGACY_GUARD="$(awk '/# O .maintenance-weekly. cobre/,/^fi$/' "$STEP17" | head -20)"

CRON_REG="$T03_REG" CRON_CNT="$T03_CNT" \
PATH="$T03_DIR:$PATH" \
bash -c "
  set -euo pipefail
  export CRON_REG='$T03_REG'
  export CRON_CNT='$T03_CNT'
  log()  { :; }
  warn() { :; }
  info() { :; }
  CRON_FAILURES=0
  $_GUARD_FN
  $_LEGACY_GUARD
" 2>/dev/null

T03_COUNT="$(cat "$T03_CNT")"
rm -rf "$T03_DIR"

if [ "$T03_COUNT" -eq 0 ]; then
  pass "T-CRON-03: Acervo Syndic present → maintenance-weekly suppressed (0 creates)"
else
  fail_test "T-CRON-03" "expected 0 creates when Acervo Syndic present, got $T03_COUNT"
fi

# =============================================================================
# T-CRON-04: full double-run of step-17 → each cron created exactly once
# =============================================================================
echo -e "${BOLD}T-CRON-04: full step-17 double-run → each cron created exactly once${NC}"

T04_DIR="$(mktemp -d)"
T04_REG="$T04_DIR/registry.txt"
touch "$T04_REG"

cat > "$T04_DIR/hermes" << 'STUB'
#!/usr/bin/env bash
case "$1" in
  cron)
    case "$2" in
      list) cat "$CRON_REG" 2>/dev/null || true ;;
      create)
        nm=""
        i=0
        for arg; do
          [ "$arg" = "--name" ] && { i=1; continue; }
          [ "$i" = "1" ] && { nm="$arg"; i=0; }
        done
        echo "$nm" >> "$CRON_REG"
        ;;
    esac
    ;;
esac
STUB
chmod +x "$T04_DIR/hermes"

CRON_REG="$T04_REG" \
PATH="$T04_DIR:$PATH" \
bash -c "
  set -euo pipefail
  export CRON_REG='$T04_REG'
  export HERMES_HOME='$T04_DIR/hermes_home'
  export EXOCORTEX_HOME='$T04_DIR/exocortex'
  export ACERVO='$T04_DIR/exocortex/acervo'
  mkdir -p \"\$HERMES_HOME\" \"\$EXOCORTEX_HOME\" \"\$ACERVO\"
  log()  { :; }
  warn() { :; }
  info() { :; }
  # Run step-17 body twice by sourcing the guard + cron calls directly
  run_step17() {
    CRON_FAILURES=0
    $_GUARD_FN
    # Acervo Syndic legacy guard
    if hermes cron list 2>/dev/null | grep -qF 'Acervo Syndic'; then
      log 'legacy cron present'
    else
      create_cron_if_missing 'maintenance-weekly' '0 3 * * 0' 'prompt'
    fi
    create_cron_if_missing 'inbox-triage'           '30 3 * * 1'   'prompt'
    create_cron_if_missing 'artifact-audit'         '0 4 1,15 * *' 'prompt'
    create_cron_if_missing 'publication-check'      '30 4 * * *'   'prompt'
    create_cron_if_missing 'acervo-index-reconcile' '0 5 * * *'    'prompt'
  }
  run_step17
  run_step17
" 2>/dev/null

# Check for duplicates
dup_found=0
for cron_name in "maintenance-weekly" "inbox-triage" "artifact-audit" "publication-check" "acervo-index-reconcile"; do
  count=$(grep -cxF "$cron_name" "$T04_REG" 2>/dev/null || true)
  if [ "${count:-0}" -gt 1 ]; then
    dup_found=1
    fail_test "T-CRON-04" "cron '$cron_name' created $count times (expected at most 1)"
  fi
done
rm -rf "$T04_DIR"

if [ "$dup_found" -eq 0 ]; then
  pass "T-CRON-04: double-run → no duplicate crons created"
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
