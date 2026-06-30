#!/usr/bin/env bash
# =============================================================================
# Tier-routing tests: setup/step-11c-integration-firecrawl.sh
# =============================================================================
# T-FC01: Tier 1 (self-host) — EXOCORTEX_ENABLE_FIRECRAWL=1 + docker present
#         → install script IS invoked.
# T-FC02: Tier 1 gate broken-check — toggle=0 must NOT invoke install (proves
#         the Tier-1 gate keys off the toggle, not just docker presence).
# T-FC03: Tier 2 (existing server) — toggle=0 but FIRECRAWL_BASE_URL health
#         probe succeeds → uses existing, does NOT install, logs "existing".
# T-FC04: Tier 3 (degrade) — toggle=0 AND probe fails → reminder written,
#         install NOT invoked, exit 0 (never fails the run).
# T-FC05: Tier 1 with docker absent → warn + skip (no install, exit 0).
# T-FC06: idempotent re-run of Tier 3 → still exit 0, reminder present.
#
# Strategy: source the step with EXOCORTEX_FIRECRAWL_SKIP_AUTORUN=1 so the
# bottom-of-file invocation does not fire, then call configure_firecrawl()
# directly with stubbed docker/curl/hermes on PATH and a stub install script
# (FIRECRAWL_INSTALL_SCRIPT) that drops a marker file when run.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STEP="$REPO_ROOT/setup/step-11c-integration-firecrawl.sh"

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
echo -e "${BOLD}step-11c Firecrawl tier routing — tests${NC}"
echo ""

if [ ! -f "$STEP" ]; then
  echo -e "${RED}FATAL: step-11c-integration-firecrawl.sh not found${NC}"
  exit 1
fi

# -----------------------------------------------------------------------------
# Build a sandbox: stub bin dir (docker/curl/hermes), HERMES_HOME, install stub.
# $1 = docker behavior: "present" | "absent"
# $2 = curl behavior:   "up" (any http response) | "down" (000 / refused)
# Echoes the sandbox dir path.
# -----------------------------------------------------------------------------
make_sandbox() {
  local docker_mode="$1" curl_mode="$2"
  local box; box="$(mktemp -d)"
  mkdir -p "$box/bin" "$box/hermes_home"

  # ── docker stub ──
  if [ "$docker_mode" = "present" ]; then
    cat > "$box/bin/docker" <<'STUB'
#!/usr/bin/env bash
# minimal: `docker compose version` ok; everything else ok
exit 0
STUB
    chmod +x "$box/bin/docker"
  else
    # Absent mode: drop a marker; run_tier shadows `command -v docker`.
    # (PATH manipulation alone can't hide the system docker binary reliably.)
    touch "$box/DOCKER_ABSENT"
  fi

  # ── curl stub ──
  cat > "$box/bin/curl" <<STUB
#!/usr/bin/env bash
mode="$curl_mode"
if [ "\$mode" = "up" ]; then
  # -sf success path
  for a in "\$@"; do [ "\$a" = "-sf" ] && exit 0; done
  # http_code probe
  for a in "\$@"; do [ "\$a" = "-w" ] && { echo "200"; exit 0; }; done
  exit 0
else
  # down: -sf fails; http_code prints 000
  for a in "\$@"; do [ "\$a" = "-w" ] && { echo "000"; exit 7; }; done
  exit 7
fi
STUB
  chmod +x "$box/bin/curl"

  # ── hermes stub (mcp list/add) ──
  cat > "$box/bin/hermes" <<'STUB'
#!/usr/bin/env bash
case "$1 $2" in
  "mcp list") echo "" ;;   # nothing configured yet
  "mcp add")  exit 0 ;;
  *)          exit 0 ;;
esac
STUB
  chmod +x "$box/bin/hermes"

  # ── install stub: writes a marker so the test can detect invocation ──
  cat > "$box/install_stub.sh" <<STUB
#!/usr/bin/env bash
echo "installed" > "$box/INSTALL_RAN"
exit 0
STUB
  chmod +x "$box/install_stub.sh"

  echo "$box"
}

# Run configure_firecrawl in a clean subshell with the sandbox wired in.
# Captures combined output; returns the function's exit code.
run_tier() {
  local box="$1" toggle="$2" base_url="$3"
  (
    set +e
    export PATH="$box/bin:$PATH"
    export HERMES_HOME="$box/hermes_home"
    export EXOCORTEX_FIRECRAWL_SKIP_AUTORUN=1
    export EXOCORTEX_ENABLE_FIRECRAWL="$toggle"
    export FIRECRAWL_BASE_URL="$base_url"
    export FIRECRAWL_INSTALL_SCRIPT="$box/install_stub.sh"
    # Clear positional args before sourcing: common.sh parses "$@" as setup
    # flags, and the sandbox path would be rejected as an unsupported flag.
    set --
    source "$STEP" >/dev/null 2>&1
    # Absent mode: shadow `command` so `command -v docker` reports missing,
    # mirroring the technique in tests/test_step01_hindsight_health.sh (T-HS03).
    if [ -f "$box/DOCKER_ABSENT" ]; then
      command() {
        if [ "$1" = "-v" ] && [ "$2" = "docker" ]; then return 1; fi
        builtin command "$@"
      }
    fi
    configure_firecrawl > "$box/OUT" 2>&1
    echo "$?" > "$box/RC"
  )
  cat "$box/RC"
}

# =============================================================================
# T-FC01: Tier 1 self-host → install invoked
# =============================================================================
echo -e "${BOLD}T-FC01: Tier 1 (toggle=1, docker present) → install runs${NC}"
BOX="$(make_sandbox present down)"
RC="$(run_tier "$BOX" "1" "http://127.0.0.1:3002")"
if [ -f "$BOX/INSTALL_RAN" ] && [ "$RC" = "0" ]; then
  pass "T-FC01: install invoked, exit 0"
else
  fail_test "T-FC01" "expected install marker + exit 0; rc=$RC ran=$([ -f "$BOX/INSTALL_RAN" ] && echo yes || echo no); out=$(cat "$BOX/OUT")"
fi
rm -rf "$BOX"

# =============================================================================
# T-FC02: gate proof — toggle=0 must NOT install (even with docker present)
# =============================================================================
echo -e "${BOLD}T-FC02: gate proof (toggle=0, docker present, url down) → no install${NC}"
BOX="$(make_sandbox present down)"
RC="$(run_tier "$BOX" "0" "http://127.0.0.1:3002")"
if [ ! -f "$BOX/INSTALL_RAN" ]; then
  pass "T-FC02: Tier-1 correctly gated off when toggle=0"
else
  fail_test "T-FC02" "install ran with toggle=0 — Tier-1 gate is broken; out=$(cat "$BOX/OUT")"
fi
rm -rf "$BOX"

# =============================================================================
# T-FC03: Tier 2 existing server → use existing, no install
# =============================================================================
echo -e "${BOLD}T-FC03: Tier 2 (toggle=0, url reachable) → use existing${NC}"
BOX="$(make_sandbox present up)"
RC="$(run_tier "$BOX" "0" "http://existing.example:3002")"
OUT="$(cat "$BOX/OUT")"
if [ ! -f "$BOX/INSTALL_RAN" ] && [ "$RC" = "0" ] && echo "$OUT" | grep -qi "existing"; then
  pass "T-FC03: existing server used, no install, exit 0"
else
  fail_test "T-FC03" "expected no install + 'existing' log + exit 0; rc=$RC ran=$([ -f "$BOX/INSTALL_RAN" ] && echo yes || echo no); out=$OUT"
fi
rm -rf "$BOX"

# =============================================================================
# T-FC04: Tier 3 degrade → reminder written, no install, exit 0
# =============================================================================
echo -e "${BOLD}T-FC04: Tier 3 (toggle=0, url down) → degrade with reminder${NC}"
BOX="$(make_sandbox present down)"
RC="$(run_tier "$BOX" "0" "http://127.0.0.1:3002")"
REMINDER="$BOX/hermes_home/reminders/firecrawl.md"
if [ ! -f "$BOX/INSTALL_RAN" ] && [ "$RC" = "0" ] && [ -f "$REMINDER" ]; then
  pass "T-FC04: degraded cleanly — reminder written, exit 0, no install"
else
  fail_test "T-FC04" "rc=$RC ran=$([ -f "$BOX/INSTALL_RAN" ] && echo yes || echo no) reminder=$([ -f "$REMINDER" ] && echo yes || echo no); out=$(cat "$BOX/OUT")"
fi
rm -rf "$BOX"

# =============================================================================
# T-FC05: Tier 1 but docker absent → warn + skip, no install, exit 0
# =============================================================================
echo -e "${BOLD}T-FC05: Tier 1 (toggle=1, docker ABSENT) → warn + skip${NC}"
BOX="$(make_sandbox absent down)"
RC="$(run_tier "$BOX" "1" "http://127.0.0.1:3002")"
if [ ! -f "$BOX/INSTALL_RAN" ] && [ "$RC" = "0" ]; then
  pass "T-FC05: docker absent → skipped install, exit 0"
else
  fail_test "T-FC05" "expected no install + exit 0; rc=$RC ran=$([ -f "$BOX/INSTALL_RAN" ] && echo yes || echo no); out=$(cat "$BOX/OUT")"
fi
rm -rf "$BOX"

# =============================================================================
# T-FC06: idempotent re-run of Tier 3 → exit 0, reminder still present
# =============================================================================
echo -e "${BOLD}T-FC06: Tier 3 re-run is idempotent${NC}"
BOX="$(make_sandbox present down)"
run_tier "$BOX" "0" "http://127.0.0.1:3002" >/dev/null
RC="$(run_tier "$BOX" "0" "http://127.0.0.1:3002")"
REMINDER="$BOX/hermes_home/reminders/firecrawl.md"
if [ "$RC" = "0" ] && [ -f "$REMINDER" ]; then
  pass "T-FC06: second run exit 0, reminder present"
else
  fail_test "T-FC06" "rc=$RC reminder=$([ -f "$REMINDER" ] && echo yes || echo no)"
fi
rm -rf "$BOX"

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${BOLD}=== Summary ===${NC}"
echo -e "  Total: $TOTAL  |  ${GREEN}Pass: $PASSED${NC}  |  ${RED}Fail: $FAILED${NC}"
echo ""
if [ "$FAILED" -gt 0 ]; then
  echo -e "${RED}${BOLD}$FAILED test(s) failed.${NC}"
  exit 1
else
  echo -e "${GREEN}${BOLD}All tests passed.${NC}"
  exit 0
fi
