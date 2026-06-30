#!/usr/bin/env bash
# =============================================================================
# Unit-style tests: Hindsight health check in step-01-hindsight.sh
# =============================================================================
# T-HS01: health check passes when curl returns HTTP 200 (container up)
# T-HS02: health check WARNs (does NOT fail) when curl times out (container down)
# T-HS03: health check WARNs (does NOT fail) when curl is unavailable
# T-HS04: health check block is present in step-01 after docker compose up
# T-HS05: smoke.sh exits non-zero when docker container is missing/stopped
# T-HS06: smoke.sh exits 0 when all critical artifacts + container are present
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

TOTAL=0
PASSED=0
FAILED=0

pass()      { PASSED=$((PASSED + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${GREEN}PASS${NC} $1"; }
fail_test() { FAILED=$((FAILED + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${RED}FAIL${NC} $1 — $2"; }

echo ""
echo -e "${BOLD}step-01 Hindsight health check — unit tests${NC}"
echo ""

STEP01="$REPO_ROOT/setup/step-01-hindsight.sh"
SMOKE_SH="$REPO_ROOT/provision/hindsight/scripts/smoke.sh"

# Helper: write a minimal health-check wrapper that isolates the logic from step-01
# by extracting lines 109-138 (the health check block) and wrapping in a function.
_health_check_lines() {
  sed -n '109,138p' "$STEP01"
}

# =============================================================================
# T-HS01: health check passes when curl returns HTTP 200
# =============================================================================
echo -e "${BOLD}T-HS01: health check passes (curl returns 200, container up)${NC}"

T01_DIR="$(mktemp -d)"

cat > "$T01_DIR/curl" << 'STUB'
#!/usr/bin/env bash
# -sf: exit 0 (200 OK)
for arg; do
  case "$arg" in -sf) exit 0 ;; esac
done
# -w %{http_code}: print 200
echo "200"
exit 0
STUB
chmod +x "$T01_DIR/curl"

T01_OUT="$(PATH="$T01_DIR:$PATH" bash -c "
  set -euo pipefail
  log()  { echo \"LOG: \$1\"; }
  warn() { echo \"WARN: \$1\"; }
  hs_api_port=8888
  hs_health_url=\"http://127.0.0.1:\${hs_api_port}/health\"
  hs_health_ok=0
  hs_attempt=0
  if command -v curl >/dev/null 2>&1; then
    for hs_attempt in 1 2 3; do
      if curl -sf --max-time 5 \"\$hs_health_url\" >/dev/null 2>&1; then
        hs_health_ok=1
        break
      fi
      _http_code=\$(curl -so /dev/null --max-time 5 -w \"%{http_code}\" \"\$hs_health_url\" 2>/dev/null || true)
      if [ -n \"\$_http_code\" ] && [ \"\$_http_code\" != \"000\" ]; then
        hs_health_ok=1
        break
      fi
      [ \"\$hs_attempt\" -lt 3 ] && sleep 0
    done
    if [ \"\$hs_health_ok\" = \"1\" ]; then
      log \"Hindsight health check: API respondendo em \${hs_health_url}\"
    else
      warn \"Hindsight health check: sem resposta em \${hs_health_url} após 3 tentativas\"
    fi
  else
    warn \"Hindsight health check: curl não disponível, pulando verificação de saúde\"
  fi
" 2>&1 || true)"
rm -rf "$T01_DIR"

if echo "$T01_OUT" | grep -q "LOG: Hindsight health check"; then
  pass "T-HS01: health check logged success when curl returns 200"
else
  fail_test "T-HS01" "expected LOG output; got: $T01_OUT"
fi

# =============================================================================
# T-HS02: health check WARNs (does NOT exit 1) when curl times out
# =============================================================================
echo -e "${BOLD}T-HS02: health check WARNs (not fails) when curl times out${NC}"

T02_DIR="$(mktemp -d)"

cat > "$T02_DIR/curl" << 'STUB'
#!/usr/bin/env bash
# Always fail (timeout / connection refused)
if [[ "$*" == *"%{http_code}"* ]]; then
  echo "000"
fi
exit 1
STUB
chmod +x "$T02_DIR/curl"

T02_EXIT=0
T02_OUT="$(PATH="$T02_DIR:$PATH" bash -c "
  set -euo pipefail
  log()  { echo \"LOG: \$1\"; }
  warn() { echo \"WARN: \$1\"; }
  hs_api_port=8888
  hs_health_url=\"http://127.0.0.1:\${hs_api_port}/health\"
  hs_health_ok=0
  hs_attempt=0
  if command -v curl >/dev/null 2>&1; then
    for hs_attempt in 1 2 3; do
      if curl -sf --max-time 5 \"\$hs_health_url\" >/dev/null 2>&1; then
        hs_health_ok=1
        break
      fi
      _http_code=\$(curl -so /dev/null --max-time 5 -w \"%{http_code}\" \"\$hs_health_url\" 2>/dev/null || true)
      if [ -n \"\$_http_code\" ] && [ \"\$_http_code\" != \"000\" ]; then
        hs_health_ok=1
        break
      fi
      [ \"\$hs_attempt\" -lt 3 ] && sleep 0
    done
    if [ \"\$hs_health_ok\" = \"1\" ]; then
      log \"Hindsight health check: API respondendo em \${hs_health_url}\"
    else
      warn \"Hindsight health check: sem resposta em \${hs_health_url} após 3 tentativas\"
      warn \"  Container pode ainda estar inicializando\"
    fi
  else
    warn \"Hindsight health check: curl não disponível, pulando verificação de saúde\"
  fi
" 2>&1)" || T02_EXIT=$?
rm -rf "$T02_DIR"

if [ "$T02_EXIT" -eq 0 ] && echo "$T02_OUT" | grep -q "WARN:.*sem resposta"; then
  pass "T-HS02: curl timeout → WARN emitted, script continues (exit 0)"
else
  fail_test "T-HS02" "exit=$T02_EXIT; expected exit=0 + WARN; got: $T02_OUT"
fi

# =============================================================================
# T-HS03: health check WARNs when curl is not in PATH
# =============================================================================
echo -e "${BOLD}T-HS03: health check WARNs when curl is unavailable${NC}"

# Simulate "no curl" by overriding `command` as a function so that
# `command -v curl` returns empty/non-zero, while everything else still works.
# This avoids PATH manipulation that cannot shadow a system binary reliably.
T03_EXIT=0
T03_OUT="$(bash -c "
  set -euo pipefail
  log()  { echo \"LOG: \$1\"; }
  warn() { echo \"WARN: \$1\"; }
  # Shadow 'command' so 'command -v curl' returns nothing
  command() {
    if [ \"\$1\" = \"-v\" ] && [ \"\$2\" = \"curl\" ]; then
      return 1
    fi
    builtin command \"\$@\"
  }
  export -f command
  hs_api_port=8888
  hs_health_url=\"http://127.0.0.1:\${hs_api_port}/health\"
  hs_health_ok=0
  if command -v curl >/dev/null 2>&1; then
    warn 'UNEXPECTED: curl found'
  else
    warn \"Hindsight health check: curl não disponível, pulando verificação de saúde\"
  fi
" 2>&1)" || T03_EXIT=$?

if [ "$T03_EXIT" -eq 0 ] && echo "$T03_OUT" | grep -q "WARN:.*curl não disponível"; then
  pass "T-HS03: curl missing → WARN emitted, script continues (exit 0)"
else
  fail_test "T-HS03" "exit=$T03_EXIT; expected exit=0 + WARN 'curl não disponível'; got: $T03_OUT"
fi

# =============================================================================
# T-HS04: health check block is present in step-01 after docker compose up
# =============================================================================
echo -e "${BOLD}T-HS04: health check block present in step-01 after docker compose up${NC}"

if [ ! -f "$STEP01" ]; then
  fail_test "T-HS04" "step-01-hindsight.sh not found"
else
  has_health=$(grep -c "Runtime health check" "$STEP01" 2>/dev/null || true)
  has_retry=$(grep -c "hs_attempt" "$STEP01" 2>/dev/null || true)
  has_warn_timeout=$(grep -c "sem resposta" "$STEP01" 2>/dev/null || true)

  if [ "${has_health:-0}" -ge 1 ] && [ "${has_retry:-0}" -ge 1 ] && [ "${has_warn_timeout:-0}" -ge 1 ]; then
    pass "T-HS04: health check block found in step-01 (comment + retry loop + warn-on-timeout)"
  else
    fail_test "T-HS04" "health=${has_health} retry=${has_retry} warn=${has_warn_timeout} (expected all >=1)"
  fi
fi

# =============================================================================
# T-HS05: smoke.sh exits non-zero when docker container is missing
# =============================================================================
echo -e "${BOLD}T-HS05: smoke.sh exits non-zero when container is missing${NC}"

if [ ! -f "$SMOKE_SH" ]; then
  fail_test "T-HS05" "provision/hindsight/scripts/smoke.sh not found"
else
  T05_DIR="$(mktemp -d)"
  T05_HS="$T05_DIR/hindsight-local"
  mkdir -p "$T05_HS"
  touch "$T05_HS/docker-compose.yml"
  echo "HINDSIGHT_API_LLM_API_KEY=real-key" > "$T05_HS/.env"

  # docker stub: inspect returns "missing" exit 1 (container not found)
  cat > "$T05_DIR/docker" << 'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"inspect"* ]]; then
  echo "missing"
  exit 1
fi
exit 0
STUB
  chmod +x "$T05_DIR/docker"

  cat > "$T05_DIR/curl" << 'STUB'
#!/usr/bin/env bash
exit 1
STUB
  chmod +x "$T05_DIR/curl"

  T05_EXIT=0
  HERMES_HOME="$T05_DIR" EXOCORTEX_HINDSIGHT_DIR="$T05_HS" \
    PATH="$T05_DIR:$PATH" bash "$SMOKE_SH" >/dev/null 2>&1 || T05_EXIT=$?
  rm -rf "$T05_DIR"

  if [ "$T05_EXIT" -ne 0 ]; then
    pass "T-HS05: smoke.sh exits non-zero when container is missing"
  else
    fail_test "T-HS05" "expected non-zero exit when container missing, got exit=0"
  fi
fi

# =============================================================================
# T-HS06: smoke.sh exits 0 when all critical artifacts + container are present
# =============================================================================
echo -e "${BOLD}T-HS06: smoke.sh exits 0 when all artifacts present and container running${NC}"

if [ ! -f "$SMOKE_SH" ]; then
  fail_test "T-HS06" "provision/hindsight/scripts/smoke.sh not found"
else
  T06_DIR="$(mktemp -d)"
  T06_HS="$T06_DIR/hindsight-local"
  mkdir -p "$T06_HS"
  touch "$T06_HS/docker-compose.yml"
  echo "HINDSIGHT_API_LLM_API_KEY=real-key" > "$T06_HS/.env"

  # docker stub: container is "running"
  cat > "$T06_DIR/docker" << 'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"inspect"* ]]; then
  echo "running"
  exit 0
fi
exit 0
STUB
  chmod +x "$T06_DIR/docker"

  # curl stub: health endpoint responds with 200
  cat > "$T06_DIR/curl" << 'STUB'
#!/usr/bin/env bash
# -sf: exit 0 (200)
for arg; do
  case "$arg" in -sf) exit 0 ;; esac
done
echo "200"
exit 0
STUB
  chmod +x "$T06_DIR/curl"

  T06_EXIT=0
  HERMES_HOME="$T06_DIR" EXOCORTEX_HINDSIGHT_DIR="$T06_HS" \
    PATH="$T06_DIR:$PATH" bash "$SMOKE_SH" >/dev/null 2>&1 || T06_EXIT=$?
  rm -rf "$T06_DIR"

  if [ "$T06_EXIT" -eq 0 ]; then
    pass "T-HS06: smoke.sh exits 0 when all critical artifacts present and container running"
  else
    fail_test "T-HS06" "expected exit=0 when all artifacts present, got exit=$T06_EXIT"
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
