#!/usr/bin/env bash
# =============================================================================
# Step 10: Integração — Browser Automation (runtime local da skill)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

configure_browser_automation() {
  local skill_dir="$SKILLS_DST/excrtx-integrate-browser"
  local wrapper="$skill_dir/scripts/browser-use.sh"
  local runtime_root="${EXCRTX_BROWSER_RUNTIME_ROOT:-$skill_dir/.runtime}"
  local uv_install_dir="${EXCRTX_BROWSER_UV_INSTALL_DIR:-$runtime_root/uv}"
  local uv_tool_dir="${EXCRTX_BROWSER_UV_TOOL_DIR:-$runtime_root/tools}"
  local uv_tool_bin_dir="${EXCRTX_BROWSER_UV_TOOL_BIN_DIR:-$runtime_root/bin}"
  local uv_cache_dir="${EXCRTX_BROWSER_UV_CACHE_DIR:-$runtime_root/cache/uv}"
  local uv_python_install_dir="${EXCRTX_BROWSER_UV_PYTHON_INSTALL_DIR:-$runtime_root/python}"
  local playwright_dir="${EXCRTX_BROWSER_PLAYWRIGHT_DIR:-$runtime_root/ms-playwright}"
  local uv_bin="$uv_install_dir/uv"
  local browser_bin="$uv_tool_bin_dir/browser-use"
  local uv_cmd=""
  local chromium_found=false

  if [ ! -x "$wrapper" ]; then
    warn "Browser wrapper não encontrado: $wrapper"
    return 0
  fi

  mkdir -p "$runtime_root" "$uv_tool_dir" "$uv_tool_bin_dir" "$uv_cache_dir" "$uv_python_install_dir" "$playwright_dir"

  if [ -x "$uv_bin" ]; then
    uv_cmd="$uv_bin"
  elif command -v uv >/dev/null 2>&1; then
    uv_cmd="$(command -v uv)"
  else
    if ! command -v curl >/dev/null 2>&1; then
      warn "curl não encontrado; não foi possível instalar uv local para Browser Automation"
      return 0
    fi
    info "uv ausente; instalando runtime local da Browser Automation em $uv_install_dir"
    if ! curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$uv_install_dir" UV_NO_MODIFY_PATH=1 sh >/dev/null 2>&1; then
      warn "Falha ao instalar uv local em $uv_install_dir"
      return 0
    fi
    if [ ! -x "$uv_bin" ]; then
      warn "uv local não encontrado após instalação: $uv_bin"
      return 0
    fi
    uv_cmd="$uv_bin"
  fi

  export EXCRTX_BROWSER_RUNTIME_ROOT="$runtime_root"
  export EXCRTX_BROWSER_UV_INSTALL_DIR="$uv_install_dir"
  export EXCRTX_BROWSER_UV_TOOL_DIR="$uv_tool_dir"
  export EXCRTX_BROWSER_UV_TOOL_BIN_DIR="$uv_tool_bin_dir"
  export EXCRTX_BROWSER_UV_CACHE_DIR="$uv_cache_dir"
  export EXCRTX_BROWSER_UV_PYTHON_INSTALL_DIR="$uv_python_install_dir"
  export EXCRTX_BROWSER_PLAYWRIGHT_DIR="$playwright_dir"
  export UV_TOOL_DIR="$uv_tool_dir"
  export UV_TOOL_BIN_DIR="$uv_tool_bin_dir"
  export UV_CACHE_DIR="$uv_cache_dir"
  export UV_PYTHON_INSTALL_DIR="$uv_python_install_dir"
  export PLAYWRIGHT_BROWSERS_PATH="$playwright_dir"
  export PATH="$uv_install_dir:$uv_tool_bin_dir:$PATH"

  if [ ! -x "$browser_bin" ]; then
    info "Provisionando browser-use no runtime local da skill"
    if ! "$uv_cmd" tool install --python 3.13 browser-use >/dev/null 2>&1; then
      warn "Falha ao instalar browser-use no runtime local"
      return 0
    fi
  fi

  if [ -x "$browser_bin" ]; then
    log "Browser Automation runtime pronto: $browser_bin"
  else
    warn "browser-use não encontrado após provisionamento: $browser_bin"
    return 0
  fi

  for d in "$playwright_dir"/chromium-*; do
    if [ -d "$d" ]; then
      chromium_found=true
      break
    fi
  done

  if [ "$chromium_found" = false ]; then
    info "Provisionando Chromium no runtime local da Browser Automation"
    if ! "$uv_cmd" tool run --from playwright playwright install chromium >/dev/null 2>&1; then
      warn "Falha ao baixar Chromium no runtime local"
      return 0
    fi
    for d in "$playwright_dir"/chromium-*; do
      if [ -d "$d" ]; then
        chromium_found=true
        break
      fi
    done
  fi

  if [ "$chromium_found" = true ]; then
    log "Chromium disponível em $playwright_dir"
  else
    warn "Chromium não pôde ser verificado em $playwright_dir"
  fi
}

info "Browser Automation (runtime local da skill)..."
configure_browser_automation
