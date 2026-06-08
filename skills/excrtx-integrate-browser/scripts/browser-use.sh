#!/usr/bin/env bash
# Self-guarded browser-use wrapper
# Detects missing dependencies and installs them automatically.
# The mise shim points to Python 3.14 which has asyncio incompatibilities,
# so this script always resolves to the uv-managed Python 3.13 installation.

set -euo pipefail

BU_BIN="$HOME/.local/bin/browser-use"
PW_CACHE="$HOME/.cache/ms-playwright"

# ── Step 1: Ensure uv is available ──
if ! command -v uv &>/dev/null; then
  echo "❌ uv not found. Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

# ── Step 2: Ensure browser-use CLI is installed (via uv tool, pinned to Python 3.13) ──
if [ ! -x "$BU_BIN" ]; then
  echo "📦 browser-use not found. Installing via uv (Python 3.13)..."
  uv tool install --python 3.13 browser-use
  if [ ! -x "$BU_BIN" ]; then
    echo "❌ Installation failed. browser-use binary not found at $BU_BIN" >&2
    exit 1
  fi
  echo "✅ browser-use installed"
fi

# ── Step 3: Ensure Chromium is downloaded ──
if [ ! -d "$PW_CACHE/chromium"* ] 2>/dev/null; then
  # Check with glob expansion
  chromium_found=false
  for d in "$PW_CACHE"/chromium-*; do
    [ -d "$d" ] && chromium_found=true && break
  done

  if [ "$chromium_found" = false ]; then
    echo "🌐 Chromium not found. Installing via Playwright..."
    # Try the built-in install; it may fail on system deps (needs sudo) but
    # the browser binary itself will still be downloaded.
    "$BU_BIN" install 2>&1 || true

    # Verify the download succeeded even if system deps failed
    chromium_found=false
    for d in "$PW_CACHE"/chromium-*; do
      [ -d "$d" ] && chromium_found=true && break
    done

    if [ "$chromium_found" = false ]; then
      echo "❌ Chromium download failed. Try manually: $BU_BIN install" >&2
      exit 1
    fi
    echo "✅ Chromium downloaded (system deps may need: sudo $BU_BIN install)"
  fi
fi

# ── Step 4: Forward to the real binary ──
exec "$BU_BIN" "$@"
