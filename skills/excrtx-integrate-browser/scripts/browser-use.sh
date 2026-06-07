#!/usr/bin/env bash
# Self-guarded browser-use wrapper
# Detects missing dependencies and installs them automatically.
# The runtime is provisioned inside the skill path so the executable contract
# does not depend on a globally installed uv or browser-use binary.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RUNTIME_ROOT="${EXCRTX_BROWSER_RUNTIME_ROOT:-$SKILL_DIR/.runtime}"
UV_INSTALL_DIR="${EXCRTX_BROWSER_UV_INSTALL_DIR:-$RUNTIME_ROOT/uv}"
UV_TOOL_DIR="${EXCRTX_BROWSER_UV_TOOL_DIR:-$RUNTIME_ROOT/tools}"
UV_TOOL_BIN_DIR="${EXCRTX_BROWSER_UV_TOOL_BIN_DIR:-$RUNTIME_ROOT/bin}"
UV_CACHE_DIR="${EXCRTX_BROWSER_UV_CACHE_DIR:-$RUNTIME_ROOT/cache/uv}"
UV_PYTHON_INSTALL_DIR="${EXCRTX_BROWSER_UV_PYTHON_INSTALL_DIR:-$RUNTIME_ROOT/python}"
PW_CACHE="${PLAYWRIGHT_BROWSERS_PATH:-$RUNTIME_ROOT/ms-playwright}"
HERMES_ENV_PATH="${EXCRTX_BROWSER_HERMES_ENV_PATH:-${HERMES_HOME:-$HOME/.hermes}/.env}"
LOCAL_UV_BIN="$UV_INSTALL_DIR/uv"
BU_BIN="${EXCRTX_BROWSER_BIN:-$UV_TOOL_BIN_DIR/browser-use}"

mkdir -p "$RUNTIME_ROOT" "$UV_TOOL_DIR" "$UV_TOOL_BIN_DIR" "$UV_CACHE_DIR" "$UV_PYTHON_INSTALL_DIR" "$PW_CACHE"

export EXCRTX_BROWSER_RUNTIME_ROOT="$RUNTIME_ROOT"
export EXCRTX_BROWSER_UV_INSTALL_DIR="$UV_INSTALL_DIR"
export EXCRTX_BROWSER_UV_TOOL_DIR="$UV_TOOL_DIR"
export EXCRTX_BROWSER_UV_TOOL_BIN_DIR="$UV_TOOL_BIN_DIR"
export EXCRTX_BROWSER_UV_CACHE_DIR="$UV_CACHE_DIR"
export EXCRTX_BROWSER_UV_PYTHON_INSTALL_DIR="$UV_PYTHON_INSTALL_DIR"
export UV_TOOL_DIR
export UV_TOOL_BIN_DIR
export UV_CACHE_DIR
export UV_PYTHON_INSTALL_DIR
export PLAYWRIGHT_BROWSERS_PATH="$PW_CACHE"
export PATH="$UV_INSTALL_DIR:$UV_TOOL_BIN_DIR:$PATH"

strip_wrapping_quotes() {
  local value="$1"
  if [[ "$value" == \"*\" && "$value" == *\" ]]; then
    value="${value#\"}"
    value="${value%\"}"
  elif [[ "$value" == \'*\' && "$value" == *\' ]]; then
    value="${value#\'}"
    value="${value%\'}"
  fi
  printf '%s' "$value"
}

load_hermes_openrouter_key() {
  if [ -n "${OPENROUTER_API_KEY:-}" ] || [ ! -f "$HERMES_ENV_PATH" ]; then
    return 0
  fi

  while IFS= read -r raw_line || [ -n "$raw_line" ]; do
    raw_line="${raw_line%$'\r'}"
    case "$raw_line" in
      ''|\#*) continue ;;
    esac

    if [[ "$raw_line" == OPENROUTER_API_KEY=* ]]; then
      local raw_value="${raw_line#OPENROUTER_API_KEY=}"
      export OPENROUTER_API_KEY="$(strip_wrapping_quotes "$raw_value")"
      return 0
    fi
  done < "$HERMES_ENV_PATH"
}

inject_openrouter_for_browser_use() {
  load_hermes_openrouter_key

  if [ -z "${OPENAI_API_KEY:-}" ] && [ -n "${OPENROUTER_API_KEY:-}" ]; then
    export OPENAI_API_KEY="$OPENROUTER_API_KEY"
    export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
    export BROWSER_USE_LLM_MODEL="${BROWSER_USE_LLM_MODEL:-openai/gpt-4.1-mini}"
  fi
}

inject_openrouter_for_browser_use

UV_BIN=""
chromium_found=false

# ── Step 1: Ensure uv is available ──
if [ -x "$LOCAL_UV_BIN" ]; then
  UV_BIN="$LOCAL_UV_BIN"
elif command -v uv &>/dev/null; then
  UV_BIN="$(command -v uv)"
else
  echo "📦 uv not found. Installing local runtime in $UV_INSTALL_DIR ..."
  if ! command -v curl &>/dev/null; then
    echo "❌ curl not found. Cannot install local uv runtime." >&2
    exit 1
  fi
  mkdir -p "$UV_INSTALL_DIR"
  if ! curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$UV_INSTALL_DIR" UV_NO_MODIFY_PATH=1 sh; then
    echo "❌ Failed to install local uv runtime in $UV_INSTALL_DIR" >&2
    exit 1
  fi
  if [ ! -x "$LOCAL_UV_BIN" ]; then
    echo "❌ Local uv binary not found after install: $LOCAL_UV_BIN" >&2
    exit 1
  fi
  UV_BIN="$LOCAL_UV_BIN"
fi

# ── Step 2: Ensure browser-use CLI is installed (via uv tool, pinned to Python 3.13) ──
if [ ! -x "$BU_BIN" ]; then
  echo "📦 browser-use not found. Installing via uv runtime (Python 3.13)..."
  "$UV_BIN" tool install --python 3.13 browser-use
  if [ ! -x "$BU_BIN" ]; then
    echo "❌ Installation failed. browser-use binary not found at $BU_BIN" >&2
    exit 1
  fi
  echo "✅ browser-use installed"
fi

# ── Step 3: Ensure Chromium is downloaded ──
for d in "$PW_CACHE"/chromium-*; do
  [ -d "$d" ] && chromium_found=true && break
done

if [ "$chromium_found" = false ]; then
  echo "🌐 Chromium not found. Installing Playwright Chromium into $PW_CACHE ..."
  if ! "$UV_BIN" tool run --from playwright playwright install chromium; then
    echo "❌ Chromium download failed via Playwright runtime." >&2
    exit 1
  fi

  chromium_found=false
  for d in "$PW_CACHE"/chromium-*; do
    [ -d "$d" ] && chromium_found=true && break
  done

  if [ "$chromium_found" = false ]; then
    echo "❌ Chromium download failed. Try manually: $UV_BIN tool run --from playwright playwright install chromium" >&2
    exit 1
  fi
  echo "✅ Chromium downloaded"
fi

# ── Step 4: Forward to the real binary ──
exec "$BU_BIN" "$@"
