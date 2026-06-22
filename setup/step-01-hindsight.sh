#!/usr/bin/env bash
# =============================================================================
# Step 01: Hindsight (memória operacional via Docker)
# =============================================================================
# Provisiona Hindsight local com Docker antes de qualquer outra etapa,
# garantindo que a infraestrutura de memória esteja disponível desde o início.
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

setup_hindsight_local_docker() {
  if [ "${EXOCORTEX_ENABLE_HINDSIGHT:-0}" != "1" ]; then
    info "Hindsight local não ativado por default"
    info "  Para configurar: EXOCORTEX_ENABLE_HINDSIGHT=1 bash setup.sh"
    return 0
  fi
  if ! command -v docker >/dev/null 2>&1; then
    warn "docker não encontrado; instale Docker e rode novamente"
    return 0
  fi
  local hs_dir="${EXOCORTEX_HINDSIGHT_DIR:-$HERMES_HOME/hindsight-local}"
  local hs_data="$hs_dir/data"
  local hs_compose="$hs_dir/docker-compose.yml"
  local hs_env="$hs_dir/.env"
  local hs_api_port="${EXOCORTEX_HINDSIGHT_API_PORT:-8888}"
  local hs_ui_port="${EXOCORTEX_HINDSIGHT_UI_PORT:-9999}"
  mkdir -p "$hs_data"
  if [ "${EXOCORTEX_HINDSIGHT_RESET_DATA:-0}" = "1" ]; then
    if [ "${EXOCORTEX_HINDSIGHT_CONFIRM_DELETE:-}" = "DELETE_HINDSIGHT_MEMORY" ]; then
      warn "Confirmado: removendo memória local Hindsight (data/)"
      (cd "$hs_dir" && docker compose down >/dev/null 2>&1 || true)
      rm -rf "$hs_data"
      mkdir -p "$hs_data"
      log "Memória local removida e volume recriado"
    else
      warn "Reset solicitado, mas sem confirmação explícita"
      info "  Use: EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY"
    fi
  fi
  if [ ! -f "$hs_compose" ]; then
    cat > "$hs_compose" <<EOF
services:
  hindsight:
    image: ghcr.io/vectorize-io/hindsight:latest
    container_name: exocortex-hindsight
    restart: unless-stopped
    ports:
      - "${hs_api_port}:8888"
      - "${hs_ui_port}:9999"
    env_file:
      - .env
    volumes:
      - ./data:/home/hindsight/.pg0
EOF
    log "Hindsight docker-compose criado em $hs_compose"
  else
    log "Hindsight docker-compose preservado: $hs_compose"
  fi
  local parent_env="$HERMES_HOME/.env"
  local parent_config="$HERMES_HOME/config.yaml"
  local resolved_key="CHANGE_ME"
  local resolved_model="gpt-4o-mini"
  local resolved_base=""

  if [ -f "$parent_env" ]; then
    resolved_key=$(grep "^HINDSIGHT_LLM_API_KEY=" "$parent_env" | cut -d'=' -f2- || echo "")
    if [ -z "$resolved_key" ]; then
      resolved_key=$(grep "^DEEPSEEK_API_KEY=" "$parent_env" | cut -d'=' -f2- || echo "")
      if [ -z "$resolved_key" ]; then
        resolved_key=$(grep "^OPENROUTER_API_KEY=" "$parent_env" | cut -d'=' -f2- || echo "CHANGE_ME")
      fi
    fi
  fi

  if [ -f "$parent_config" ] && command -v python3 >/dev/null 2>&1; then
    eval "$(python3 - "$parent_config" <<'PY'
import sys
import yaml
try:
    cfg = yaml.safe_load(open(sys.argv[1])) or {}
    model = cfg.get("model", {})
    default_model = model.get("default", "")
    base_url = model.get("base_url", "")
    if "deepseek" in default_model.lower():
        print("resolved_model='deepseek-v4-flash'")
        if base_url:
            print(f"resolved_base='{base_url}'")
    elif default_model:
        print(f"resolved_model='{default_model}'")
        if base_url:
            print(f"resolved_base='{base_url}'")
except Exception:
    pass
PY
)"
  fi

  if [ ! -f "$hs_env" ]; then
    cat > "$hs_env" <<EOF
HINDSIGHT_API_LLM_PROVIDER=openai
HINDSIGHT_API_LLM_API_KEY=${resolved_key}
HINDSIGHT_API_LLM_MODEL=${resolved_model}
EOF
    if [ -n "$resolved_base" ]; then
      echo "HINDSIGHT_API_LLM_BASE_URL=${resolved_base}" >> "$hs_env"
    fi
    log "Hindsight .env criado em $hs_env"
  else
    log "Hindsight .env preservado: $hs_env"
    if grep -q "CHANGE_ME" "$hs_env" && [ "$resolved_key" != "CHANGE_ME" ]; then
      sed -i "s/HINDSIGHT_API_LLM_API_KEY=CHANGE_ME/HINDSIGHT_API_LLM_API_KEY=${resolved_key}/" "$hs_env"
      log "Preenchida chave de API Hindsight a partir do ambiente pai"
    fi
  fi

  if grep -q "CHANGE_ME" "$hs_env"; then
    warn "Preencha HINDSIGHT_API_LLM_API_KEY em $hs_env antes de subir o serviço"
    return 0
  fi
  (cd "$hs_dir" && docker compose pull >/dev/null 2>&1 || true && docker compose up -d >/dev/null 2>&1)
  log "Hindsight local ativo (API: :${hs_api_port}, UI: :${hs_ui_port})"

  mkdir -p "$HERMES_HOME/hindsight"
  local target="$HERMES_HOME/hindsight/config.json"
  if [ ! -f "$target" ]; then
    cat > "$target" <<'EOF'
{
  "mode": "local_external",
  "api_url": "http://localhost:8888",
  "bank_id": "exocortex",
  "memory_mode": "tools",
  "auto_recall": false,
  "auto_retain": true,
  "retain_async": true,
  "retain_every_n_turns": 2,
  "recall_budget": "low",
  "recall_prefetch_method": "recall",
  "recall_types": "observation",
  "recall_max_tokens": 1200,
  "recall_max_input_chars": 800
}
EOF
    log "Config Hindsight criada em $target"
  else
    log "Config Hindsight preservada em $target"
    python3 - "$target" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
cfg = json.loads(path.read_text(encoding="utf-8"))
cfg.update({
    "mode": "local_external",
    "memory_mode": "tools",
    "auto_recall": False,
    "auto_retain": True,
    "recall_budget": "low",
    "recall_max_input_chars": 800,
})
path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
    log "Config Hindsight alinhada para tools-first em $target"
  fi

  if [ -f "$parent_config" ] && command -v python3 >/dev/null 2>&1; then
    python3 - "$parent_config" <<'PY'
import sys
from pathlib import Path
import yaml

cfg_path = Path(sys.argv[1])
cfg = {}
if cfg_path.exists():
    cfg = yaml.safe_load(cfg_path.read_text()) or {}

memory = cfg.get("memory")
if not isinstance(memory, dict):
    memory = {}
cfg["memory"] = memory

memory["provider"] = "hindsight"
memory["memory_enabled"] = True
memory["user_profile_enabled"] = True

cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True))
PY
    log "Config Hermes alinhada para Hindsight + memory built-in ativo"
  else
    warn "Não foi possível alinhar $parent_config para Hindsight automaticamente"
  fi
}

info "Hindsight (memória operacional via Docker/ghcr.io)..."
setup_hindsight_local_docker
