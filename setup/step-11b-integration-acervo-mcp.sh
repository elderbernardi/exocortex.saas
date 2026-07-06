#!/usr/bin/env bash
# =============================================================================
# Step 11b: Integração — Acervo MCP (control plane semântico local)
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

_acervo_mcp_reminder() {
  local reason="$1"
  local python_hint
  python_hint="$(command -v python3 2>/dev/null || printf 'python3')"
  mkdir -p "$HERMES_HOME/reminders"
  cat > "$HERMES_HOME/reminders/acervo-mcp.md" <<EOF
# Pendência — health do Acervo MCP

O MCP local do Acervo não ficou saudável durante o setup.

Motivo observado: ${reason}

## Recuperação manual

No diretório do repositório Exocórtex, execute:

```bash
export ACERVO="$ACERVO"
export EXOCORTEX_HOME="$EXOCORTEX_HOME"
export HERMES_HOME="$HERMES_HOME"
"$python_hint" "$SCRIPT_DIR/scripts/acervo_mcp_server.py" --self-test --acervo-root "$ACERVO"
hermes mcp test acervo
```

## Modo degradado permitido

Enquanto o MCP não voltar:
- use `python3 scripts/acervoctl.py` para operações semânticas locais
- humano, infra e manutenção podem acessar arquivos diretamente
- agentes continuam restritos ao caminho semântico oficial quando o MCP estiver disponível
EOF
}

_acervo_mcp_exists() {
  # Check the target config file directly. The `hermes mcp` CLI always reads the
  # default ~/.hermes and ignores $HERMES_HOME, so it cannot answer this for a
  # custom/isolated home (and using it would clobber the real config).
  local cfg="$HERMES_HOME/config.yaml"
  [ -f "$cfg" ] || return 1
  python3 - "$cfg" <<'PY'
import sys
from pathlib import Path

import yaml

cfg = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
servers = cfg.get("mcp_servers")
sys.exit(0 if isinstance(servers, dict) and "acervo" in servers else 1)
PY
}

_acervo_patch_config() {
  local python_bin="$1"
  local server_script="$2"
  HERMES_CONFIG="$HERMES_HOME/config.yaml" python3 - "$python_bin" "$server_script" "$ACERVO" "$EXOCORTEX_HOME" "$HERMES_HOME" <<'PY'
import os
import sys
from pathlib import Path

import yaml

config_path = Path(os.environ["HERMES_CONFIG"])
python_bin, server_script, acervo_root, exocortex_home, hermes_home = sys.argv[1:6]
cfg = {}
if config_path.exists():
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
servers = cfg.get("mcp_servers")
if not isinstance(servers, dict):
    servers = {}
servers["acervo"] = {
    "command": python_bin,
    "args": [server_script],
    "env": {
        "ACERVO": acervo_root,
        "EXOCORTEX_HOME": exocortex_home,
        "HERMES_HOME": hermes_home,
    },
    "enabled": True,
    "connect_timeout": 60,
    "timeout": 120,
}
cfg["mcp_servers"] = servers
config_path.write_text(
    yaml.dump(cfg, default_flow_style=False, sort_keys=False, allow_unicode=True),
    encoding="utf-8",
)
print("PATCHED")
PY
}

configure_acervo_mcp() {
  info "Acervo MCP (control plane semântico local)..."

  if ! command -v hermes >/dev/null 2>&1; then
    warn "hermes CLI não encontrado; pulando Acervo MCP"
    _acervo_mcp_reminder "hermes CLI ausente no PATH"
    return 0
  fi

  if ! command -v python3 >/dev/null 2>&1; then
    warn "python3 não encontrado; pulando Acervo MCP"
    _acervo_mcp_reminder "python3 ausente no PATH"
    return 0
  fi

  local server_script="$SCRIPT_DIR/scripts/acervo_mcp_server.py"
  if [ ! -f "$server_script" ]; then
    warn "Servidor MCP do Acervo ausente: $server_script"
    _acervo_mcp_reminder "script do servidor MCP ausente"
    return 0
  fi

  local python_bin
  python_bin="$(command -v python3)"

  # Durable log dir — falls back to /tmp with a warning if HERMES_HOME is unset.
  local _log_dir
  if [ -n "${HERMES_HOME:-}" ]; then
    _log_dir="$HERMES_HOME/logs/setup"
    mkdir -p "$_log_dir"
  else
    warn "HERMES_HOME não definido; logs de setup em /tmp (fallback)"
    _log_dir=/tmp
  fi
  local _ts
  _ts="$(date +%Y%m%d_%H%M%S)"

  local self_test_log="$_log_dir/step-11b_selftest_${_ts}.log"
  if "$python_bin" "$server_script" --self-test --acervo-root "$ACERVO" >"$self_test_log" 2>&1; then
    log "Acervo MCP self-test local: OK"
  else
    warn "Acervo MCP self-test falhou; veja $self_test_log"
    _acervo_mcp_reminder "self-test local falhou; veja $self_test_log"
    return 0
  fi

  # The `hermes mcp` CLI operates on the default ~/.hermes and ignores $HERMES_HOME.
  # Only touch it when provisioning that real home; for a custom/isolated HERMES_HOME
  # (custom install, tests) write the config file directly so we never clobber the
  # real config with the wrong ACERVO.
  local _cli_home _use_cli=0
  _cli_home="$(readlink -f "${HOME}/.hermes" 2>/dev/null || echo "${HOME}/.hermes")"
  if [ "$(readlink -f "$HERMES_HOME" 2>/dev/null || echo "$HERMES_HOME")" = "$_cli_home" ]; then
    _use_cli=1
  fi

  if _acervo_mcp_exists; then
    log "MCP server 'acervo' já configurado — reconciliando config"
  elif [ "$_use_cli" = 1 ]; then
    local add_log="$_log_dir/step-11b_mcp_add_${_ts}.log"
    if printf 'y\n' | hermes mcp add acervo \
      --command "$python_bin" \
      --env "ACERVO=$ACERVO" "EXOCORTEX_HOME=$EXOCORTEX_HOME" "HERMES_HOME=$HERMES_HOME" \
      --args "$server_script" >"$add_log" 2>&1; then
      log "MCP server 'acervo' bootstrap via hermes mcp add: OK"
    else
      warn "Falha no bootstrap via hermes mcp add; reconciliando config direto (veja $add_log)"
    fi
  fi

  if _acervo_patch_config "$python_bin" "$server_script" >/dev/null 2>&1; then
    log "Config do MCP server 'acervo' reconciliada"
  else
    warn "Falha ao reconciliar config.yaml para o MCP 'acervo'"
    _acervo_mcp_reminder "falha ao reconciliar config.yaml do MCP 'acervo'"
    return 0
  fi

  local health_log="$_log_dir/step-11b_health_${_ts}.log"
  local _healthy=0
  if [ "$_use_cli" = 1 ]; then
    if hermes mcp test acervo >"$health_log" 2>&1; then _healthy=1; fi
  else
    # The CLI cannot target a non-default home; the local self-test above is the
    # health proof for a custom/isolated HERMES_HOME.
    _healthy=1
  fi
  if [ "$_healthy" = 1 ]; then
    log "MCP server 'acervo' registrado e saudável"
    rm -f "$HERMES_HOME/reminders/acervo-mcp.md"
  else
    warn "MCP server 'acervo' registrado mas health check falhou; veja $health_log"
    _acervo_mcp_reminder "health check falhou; veja $health_log"
  fi
}

configure_acervo_mcp
