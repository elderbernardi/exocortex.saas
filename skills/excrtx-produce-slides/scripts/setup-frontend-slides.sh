#!/usr/bin/env bash
# setup-frontend-slides.sh — dependency checker/installer draft for Exocórtex Frontend Slides
#
# Modes:
#   --check                Check dependencies only. No installs.
#   --install-python       Install python-pptx for current user.
#   --install-node         Install PptxGenJS 4.0.1 with npm -g.
#   --install-playwright   Install Playwright Chromium via npx.
#   --install-local        Install Python + Node + Playwright dependencies.
#
# Deliberate non-goals:
#   - No global npm install by default.
#   - No Vercel login.
#   - No deploy.
#   - No modification of user shell profile.
set -euo pipefail

MODE="${1:---check}"

if [[ "$MODE" != "--check" && "$MODE" != "--install-python" && "$MODE" != "--install-node" && "$MODE" != "--install-playwright" && "$MODE" != "--install-local" ]]; then
  cat >&2 <<'USAGE'
Usage:
  setup-frontend-slides.sh --check
  setup-frontend-slides.sh --install-python
  setup-frontend-slides.sh --install-node
  setup-frontend-slides.sh --install-playwright
  setup-frontend-slides.sh --install-local
USAGE
  exit 2
fi

ok() { printf 'OK   %s\n' "$*"; }
warn() { printf 'WARN %s\n' "$*"; }
fail() { printf 'FAIL %s\n' "$*"; }

missing=0

need_cmd() {
  local cmd="$1"
  local hint="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "$cmd: $(command -v "$cmd")"
  else
    fail "$cmd missing. $hint"
    missing=$((missing + 1))
  fi
}

check_python_pptx() {
  if python3 - <<'PY' >/dev/null 2>&1
import pptx
PY
  then
    ok "python-pptx import works"
  else
    fail "python-pptx missing. Install with: python3 -m pip install --user python-pptx"
    missing=$((missing + 1))
  fi
}

check_pptxgenjs() {
  local npm_root
  npm_root="$(npm root -g 2>/dev/null || true)"
  if [[ -n "$npm_root" ]] && npm list -g --depth=0 pptxgenjs@4.0.1 >/dev/null 2>&1 && \
      NODE_PATH="${npm_root}${NODE_PATH:+:$NODE_PATH}" node -e "require('pptxgenjs')" \
      >/dev/null 2>&1; then
    ok "PptxGenJS 4.0.1 import works via $npm_root"
  else
    fail "PptxGenJS 4.0.1 missing. Install with: npm install --global pptxgenjs@4.0.1"
    missing=$((missing + 1))
  fi
}

check_playwright() {
  if npx --yes playwright --version >/dev/null 2>&1; then
    ok "playwright CLI available via npx"
  else
    warn "playwright CLI not available yet. Install/check with: npx --yes playwright --version"
  fi
}

check_marp_optional() {
  if npx --yes @marp-team/marp-cli --version >/dev/null 2>&1; then
    ok "Marp CLI available via npx"
  else
    warn "Marp CLI not available via npx yet. Optional unless using Marp compatibility/export."
  fi
}

check_vercel_optional() {
  if npx --yes vercel --version >/dev/null 2>&1; then
    ok "Vercel CLI available via npx (deploy remains Draft-First gated)"
  else
    warn "Vercel CLI not available. Optional; only needed for approved public deploy."
  fi
}

install_python() {
  need_cmd python3 "Install Python 3 first."
  python3 -m pip install --user python-pptx
  check_python_pptx
}

install_node() {
  need_cmd node "Install Node.js 18+ first."
  need_cmd npm "Install npm with Node.js first."
  npm install --global --silent pptxgenjs@4.0.1
  check_pptxgenjs
}

install_playwright() {
  need_cmd node "Install Node.js LTS first."
  need_cmd npm "Install npm with Node.js first."
  need_cmd npx "Install npx/npm with Node.js first."
  npx --yes playwright install chromium
  check_playwright
}

run_checks() {
  need_cmd python3 "Required for PPTX extraction."
  need_cmd node "Required for PDF export via Playwright."
  need_cmd npm "Required for Node tooling."
  need_cmd npx "Required for Playwright/Marp/Vercel CLI calls."
  check_python_pptx
  check_pptxgenjs
  check_playwright
  check_marp_optional
  check_vercel_optional

  if [[ "$missing" -eq 0 ]]; then
    ok "Frontend Slides baseline dependencies are ready."
  else
    fail "$missing required check(s) failed."
    return 1
  fi
}

case "$MODE" in
  --check)
    run_checks
    ;;
  --install-python)
    install_python
    ;;
  --install-node)
    install_node
    ;;
  --install-playwright)
    install_playwright
    ;;
  --install-local)
    install_python
    install_node
    install_playwright
    run_checks
    ;;
esac
