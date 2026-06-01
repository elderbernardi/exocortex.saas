#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Setup Reproduzível
# =============================================================================
# Este script reproduz TODA a configuração do Hermes para o Exocórtex.IA.
# Executar em um Hermes limpo para recriar o ambiente completo.
#
# Pré-requisitos:
#   - hermes-agent instalado e funcional (`hermes doctor` OK)
#   - OPENROUTER_API_KEY configurado em ~/.hermes/.env
#   - Python 3.11+ com pip
#   - uv (para browser-use CLI)
#
# Uso:
#   chmod +x setup.sh && ./setup.sh
#
# Log: Cada ação é registrada em plans/pdd/logs/setup_replay.log
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
HERMES_DIR="$HOME/.hermes"
SKILLS_DIR="$HERMES_DIR/skills"
LOG_FILE="$PROJECT_DIR/plans/pdd/logs/setup_replay.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
  local msg="[$(date -Iseconds)] $1"
  echo -e "${GREEN}✓${NC} $msg"
  echo "$msg" >> "$LOG_FILE"
}

warn() {
  local msg="[$(date -Iseconds)] WARN: $1"
  echo -e "${YELLOW}⚠${NC} $msg"
  echo "$msg" >> "$LOG_FILE"
}

fail() {
  local msg="[$(date -Iseconds)] FAIL: $1"
  echo -e "${RED}✗${NC} $msg"
  echo "$msg" >> "$LOG_FILE"
  exit 1
}

check_prereq() {
  command -v "$1" > /dev/null 2>&1 || fail "Pré-requisito ausente: $1"
}

patch_google_drive_search() {
  local gapi="$HOME/.hermes/skills/productivity/google-workspace/scripts/google_api.py"

  if [ ! -f "$gapi" ]; then
    warn "google_api.py não encontrado em $gapi (patch Drive não aplicado)"
    return 0
  fi

  local patch_status
  patch_status=$(python3 - "$gapi" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

if "trashed = false" in text and "nextPageToken, files(" in text:
    print("ALREADY")
    raise SystemExit(0)

pattern = r"def drive_search\(args\):\n(?:.*\n)*?\n\ndef drive_get\(args\):"
replacement = '''def drive_search(args):
    if args.max < 1:
        print("ERROR: --max must be >= 1", file=sys.stderr)
        sys.exit(1)

    if args.raw_query:
        query = args.query
    else:
        # Escape single quotes in Drive query literals and ignore trashed items by default.
        escaped = args.query.replace("\\", "\\\\").replace("'", "\\'")
        query = f"fullText contains '{escaped}' and trashed = false"

    fields = "nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)"
    page_size = min(args.max, 1000)
    files = []
    page_token = None

    if _gws_binary():
        while len(files) < args.max:
            params = {
                "q": query,
                "pageSize": min(page_size, args.max - len(files)),
                "fields": fields,
            }
            if page_token:
                params["pageToken"] = page_token
            results = _run_gws(["drive", "files", "list"], params=params)
            files.extend(results.get("files", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break
        print(json.dumps(files[: args.max], indent=2, ensure_ascii=False))
        return

    service = build_service("drive", "v3")
    while len(files) < args.max:
        results = service.files().list(
            q=query,
            pageSize=min(page_size, args.max - len(files)),
            fields=fields,
            pageToken=page_token,
        ).execute()
        files.extend(results.get("files", []))
        page_token = results.get("nextPageToken")
        if not page_token:
            break
    print(json.dumps(files[: args.max], indent=2, ensure_ascii=False))


def drive_get(args):'''

new_text, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
if count != 1:
    print("SKIP")
    raise SystemExit(0)

path.write_text(new_text, encoding="utf-8")
print("PATCHED")
PY
)

  case "$patch_status" in
    ALREADY) log "Google Drive search hardening já presente" ;;
    PATCHED) log "Google Drive search hardening aplicado" ;;
    *) warn "Não foi possível aplicar patch automático de Drive (bloco não encontrado)" ;;
  esac
}

configure_notebooklm() {
  if ! command -v nlm > /dev/null 2>&1; then
    if command -v uv > /dev/null 2>&1; then
      log "Instalando nlm por fonte oficial: uv tool install notebooklm-mcp-cli"
      uv tool install notebooklm-mcp-cli > /dev/null 2>&1 || {
        warn "Falha ao instalar notebooklm-mcp-cli via uv"
        return 0
      }
    else
      warn "nlm CLI ausente e uv não disponível (instale uv e rode: uv tool install notebooklm-mcp-cli)"
      return 0
    fi
  fi

  log "NotebookLM CLI detectado: $(command -v nlm)"

  if command -v notebooklm-mcp > /dev/null 2>&1; then
    log "NotebookLM MCP detectado"
  else
    warn "notebooklm-mcp ausente; fallback MCP indisponível"
  fi

  if nlm login --check > /dev/null 2>&1; then
    log "NotebookLM autenticado"
  else
    mkdir -p "$HERMES_DIR/reminders"
    cat > "$HERMES_DIR/reminders/notebooklm-login.md" <<'EOF'
# Pending NotebookLM login

No terminal:

```bash
nlm login
nlm login --check
```

Se precisar concluir via Telegram:
1) O agente envia URL de autorização
2) Você autoriza no navegador
3) Cola a URL final completa no chat
4) O agente conclui o exchange local
EOF
    warn "NotebookLM sem auth ativa; lembrete criado em $HERMES_DIR/reminders/notebooklm-login.md"
  fi

  if command -v hermes > /dev/null 2>&1 && command -v notebooklm-mcp > /dev/null 2>&1; then
    if hermes mcp list 2>/dev/null | grep -q "notebooklm"; then
      log "MCP server 'notebooklm' já configurado"
    else
      if printf 'y\n' | hermes mcp add notebooklm --command notebooklm-mcp > /dev/null 2>&1; then
        log "MCP server 'notebooklm' configurado"
      else
        warn "Falha ao configurar MCP server 'notebooklm'"
      fi
    fi
  fi
}

enforce_mcp_baseline() {
  if ! command -v hermes > /dev/null 2>&1; then
    warn "hermes CLI ausente; não foi possível validar baseline MCP"
    return 0
  fi

  if hermes mcp list 2>/dev/null | grep -q "composio"; then
    if printf 'y\n' | hermes mcp remove composio > /dev/null 2>&1; then
      log "MCP server 'composio' removido do baseline"
    else
      warn "Falha ao remover MCP server 'composio'"
    fi
  else
    log "Baseline MCP OK: 'composio' já está ausente"
  fi
}

setup_hindsight_local_docker() {
  if [ "${EXOCORTEX_ENABLE_HINDSIGHT:-0}" != "1" ]; then
    log "Hindsight local não ativado por default (use EXOCORTEX_ENABLE_HINDSIGHT=1)"
    return 0
  fi

  if ! command -v docker > /dev/null 2>&1; then
    warn "docker não encontrado; pulando setup local do Hindsight"
    return 0
  fi

  local hs_dir="${EXOCORTEX_HINDSIGHT_DIR:-$HERMES_DIR/hindsight-local}"
  local hs_data="$hs_dir/data"
  local hs_compose="$hs_dir/docker-compose.yml"
  local hs_env="$hs_dir/.env"
  local hs_api_port="${EXOCORTEX_HINDSIGHT_API_PORT:-8888}"
  local hs_ui_port="${EXOCORTEX_HINDSIGHT_UI_PORT:-9999}"

  mkdir -p "$hs_data"

  if [ "${EXOCORTEX_HINDSIGHT_RESET_DATA:-0}" = "1" ]; then
    if [ "${EXOCORTEX_HINDSIGHT_CONFIRM_DELETE:-}" = "DELETE_HINDSIGHT_MEMORY" ]; then
      warn "Confirmação recebida: limpando memória local Hindsight (data/)"
      (cd "$hs_dir" && docker compose down > /dev/null 2>&1 || true)
      rm -rf "$hs_data"
      mkdir -p "$hs_data"
      log "Memória local Hindsight removida e volume recriado"
    else
      warn "Reset solicitado sem confirmação explícita; memória preservada"
      warn "Para excluir: EXOCORTEX_HINDSIGHT_RESET_DATA=1 EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY"
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
    log "docker-compose do Hindsight criado em $hs_compose"
  else
    log "docker-compose do Hindsight preservado: $hs_compose"
  fi

  if [ ! -f "$hs_env" ]; then
    cat > "$hs_env" <<'EOF'
# Hindsight local docker env
HINDSIGHT_API_LLM_PROVIDER=openai
HINDSIGHT_API_LLM_API_KEY=CHANGE_ME
# Exemplo opcional:
# HINDSIGHT_API_LLM_MODEL=gpt-4o-mini
EOF
    log ".env do Hindsight criado em $hs_env"
  else
    log ".env do Hindsight preservado: $hs_env"
  fi

  if grep -q "CHANGE_ME" "$hs_env"; then
    warn "Preencha HINDSIGHT_API_LLM_API_KEY em $hs_env antes de subir o Hindsight"
    return 0
  fi

  (
    cd "$hs_dir"
    docker compose pull > /dev/null 2>&1 || true
    docker compose up -d > /dev/null 2>&1
  )

  log "Hindsight local ativo: API http://localhost:${hs_api_port} | UI http://localhost:${hs_ui_port}"

  mkdir -p "$HERMES_DIR/hindsight"
  local template="$HERMES_DIR/acervo/micro/hermes-setup/templates/hindsight-config.local_embedded.json"
  local target="$HERMES_DIR/hindsight/config.json"

  if [ -f "$target" ]; then
    log "Config Hindsight preservada: $target"
  elif [ -f "$template" ]; then
    cp "$template" "$target"
    log "Template Hindsight copiado para $target"
  else
    warn "Template Hindsight não encontrado em $template"
  fi

  if [ -f "$target" ]; then
    python3 - "$HERMES_DIR/config.yaml" "$target" <<'PY' >/dev/null 2>&1 || true
import json
import sys
from pathlib import Path
import yaml

cfg = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
model = (cfg.get("model") or {}).get("default")
base = (cfg.get("model") or {}).get("base_url")

if data.get("llm_model") == "CHANGE_ME" and model:
    data["llm_model"] = model
if data.get("llm_base_url") == "CHANGE_ME" and base:
    data["llm_base_url"] = base

Path(sys.argv[2]).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
  fi

  if [ -f "$target" ] && grep -q "CHANGE_ME" "$target"; then
    warn "Config Hindsight ainda contém CHANGE_ME em $target"
    return 0
  fi

  hermes config set memory.provider hindsight >/dev/null 2>&1 || warn "Falha ao setar memory.provider=hindsight"
  hermes config set memory.memory_enabled false >/dev/null 2>&1 || warn "Falha ao desativar memory.memory_enabled"
  hermes config set memory.user_profile_enabled false >/dev/null 2>&1 || warn "Falha ao desativar memory.user_profile_enabled"
  log "Memória simples local desativada; Hindsight configurado como provider"
}

mkdir -p "$(dirname "$LOG_FILE")"
echo "# Setup Replay Log — $(date -Iseconds)" > "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║   Exocórtex.IA — Setup Reproduzível       ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# =============================================================================
# FASE 0: Pré-requisitos
# =============================================================================
log "Verificando pré-requisitos..."
check_prereq hermes
check_prereq python3
check_prereq pip
log "Pré-requisitos OK"

# =============================================================================
# FASE P1: Skills de Identidade
# =============================================================================
log "--- FASE P1: Identity ---"

# P1.1: Skills locais (exocortex category)
LOCAL_SKILLS=(
  "exocortex-self-test"
  "exocortex-prompt-log"
  "stop-slop"
  "taste-skill"
  "exocortex-design-system"
  "exocortex-google-drive-hardening"
  "exocortex-notebooklm-knowledge-router"
  "exocortex-notebooklm-operational-workflow"
)

for skill in "${LOCAL_SKILLS[@]}"; do
  SKILL_SRC="$PROJECT_DIR/.hermes/skills/exocortex/$skill"
  SKILL_DST="$SKILLS_DIR/exocortex/$skill"
  
  if [ -d "$SKILL_DST" ]; then
    log "Skill já instalada: $skill"
  elif [ -d "$SKILL_SRC" ]; then
    mkdir -p "$SKILL_DST"
    cp -r "$SKILL_SRC"/* "$SKILL_DST/"
    log "Skill instalada (local): $skill"
  else
    warn "Skill source não encontrada: $SKILL_SRC — será criada via PDD prompt"
  fi
done

# =============================================================================
# FASE P2: Skills de Memória
# =============================================================================
log "--- FASE P2: Memory ---"

P2_SKILLS=(
  "acervo-manager"
  "exocortex-new-microverso"
)

for skill in "${P2_SKILLS[@]}"; do
  SKILL_SRC="$PROJECT_DIR/.hermes/skills/exocortex/$skill"
  SKILL_DST="$SKILLS_DIR/exocortex/$skill"
  
  if [ -d "$SKILL_DST" ]; then
    log "Skill já instalada: $skill"
  elif [ -d "$SKILL_SRC" ]; then
    mkdir -p "$SKILL_DST"
    cp -r "$SKILL_SRC"/* "$SKILL_DST/"
    log "Skill instalada (local): $skill"
  else
    warn "Skill source não encontrada: $SKILL_SRC — será criada via PDD prompt"
  fi
done

# P2.2: Acervo (4-layer knowledge base)
ACERVO_SRC="$PROJECT_DIR/.hermes/acervo"
ACERVO_DST="$HERMES_DIR/acervo"
if [ -d "$ACERVO_DST" ] && [ "$(find "$ACERVO_DST" -type f | wc -l)" -gt 5 ]; then
  log "Acervo já populado: $(find "$ACERVO_DST" -type f | wc -l) arquivos"
else
  if [ -d "$ACERVO_SRC" ]; then
    mkdir -p "$ACERVO_DST"
    cp -r "$ACERVO_SRC"/* "$ACERVO_DST/"
    log "Acervo instalado: macro/ global/ micro/_template/ shared/ ($(find "$ACERVO_DST" -type f | wc -l) arquivos)"
  else
    warn "Acervo source não encontrada em $ACERVO_SRC"
  fi
fi

# =============================================================================
# FASE P3: Skills de Tools + Pesquisa
# =============================================================================
log "--- FASE P3: Tools & Research ---"

# P3.1: DuckDuckGo Search (Skills Hub oficial)
if hermes skills list 2>/dev/null | grep -q "duckduckgo-search"; then
  log "Skill já instalada: duckduckgo-search"
else
  log "Instalando: duckduckgo-search (Skills Hub)"
  hermes skills install official/research/duckduckgo-search -y
  log "Instalada: duckduckgo-search"
fi

# P3.2: browser-use (local, do AG Kit)
BU_DST="$SKILLS_DIR/exocortex/browser-use"
if [ -d "$BU_DST" ]; then
  log "Skill já instalada: browser-use"
else
  BU_SRC="$PROJECT_DIR/.agent/skills/browser-use"
  if [ -d "$BU_SRC" ]; then
    mkdir -p "$BU_DST/scripts"
    cp "$BU_SRC/SKILL.md" "$BU_DST/SKILL.md"
    cp "$BU_SRC/scripts/browser-use.sh" "$BU_DST/scripts/browser-use.sh"
    log "Instalada: browser-use (do AG Kit)"
  else
    warn "browser-use AG Kit source não encontrada em $BU_SRC"
  fi
fi

# P3.3: Dependências Python
if command -v ddgs > /dev/null 2>&1; then
  log "Dependência já instalada: ddgs"
else
  log "Instalando dependência: ddgs (DuckDuckGo CLI)"
  pip install ddgs --quiet
  log "Instalada: ddgs $(ddgs --version 2>/dev/null || echo 'OK')"
fi

# P3.4: browser-use CLI (via uv)
if command -v browser-use > /dev/null 2>&1 || [ -f "$HOME/.local/bin/browser-use" ]; then
  log "Dependência já instalada: browser-use CLI"
else
  if command -v uv > /dev/null 2>&1; then
    log "Instalando: browser-use CLI via uv"
    uv tool install --python 3.13 browser-use
    log "Instalada: browser-use CLI"
  else
    warn "uv não encontrado — browser-use CLI não instalado. Instale uv primeiro."
  fi
fi

# P3.5: Tool Governance Skill (local)
TG_DST="$SKILLS_DIR/exocortex/exocortex-tool-governance"
if [ -d "$TG_DST" ]; then
  log "Skill já instalada: exocortex-tool-governance"
else
  TG_SRC="$PROJECT_DIR/.hermes/skills/exocortex/exocortex-tool-governance"
  if [ -d "$TG_SRC" ]; then
    mkdir -p "$TG_DST"
    cp -r "$TG_SRC"/* "$TG_DST/"
    log "Instalada: exocortex-tool-governance"
  else
    warn "Tool governance source não encontrada em $TG_SRC"
  fi
fi

# P3.6: Workspace skills (entrada/saída operacional)
P3_WORKSPACE_SKILLS=(
  "personal-artifact-workspace"
  "personal-intake-workspace"
  "exocortex-frontend-slides"
)

for skill in "${P3_WORKSPACE_SKILLS[@]}"; do
  SKILL_SRC="$PROJECT_DIR/.hermes/skills/exocortex/$skill"
  SKILL_DST="$SKILLS_DIR/exocortex/$skill"

  if [ -d "$SKILL_DST" ]; then
    log "Skill já instalada: $skill"
  elif [ -d "$SKILL_SRC" ]; then
    mkdir -p "$SKILL_DST"
    cp -r "$SKILL_SRC"/* "$SKILL_DST/"
    log "Skill instalada (local): $skill"
  else
    warn "Workspace skill source não encontrada: $SKILL_SRC"
  fi
done

# P3.7: Hardening Google Drive search (escape + pagination + trashed=false)
patch_google_drive_search

# P3.8: NotebookLM CLI-first + MCP fallback
configure_notebooklm

# P3.9: Baseline MCP (sem Composio)
enforce_mcp_baseline

# P3.10: Hindsight local (Docker único + memória persistente)
setup_hindsight_local_docker

# =============================================================================
# FASE P4: Skills de Comportamento
# =============================================================================
log "--- FASE P4: Behavior ---"

P4_SKILLS=(
  "exocortex-draft-first"
  "exocortex-vetor-ativo"
  "exocortex-canvas"
  "exocortex-briefing"
  "exocortex-onboarding"
  "exocortex-output-quality-gate"
)

for skill in "${P4_SKILLS[@]}"; do
  SKILL_SRC="$PROJECT_DIR/.hermes/skills/exocortex/$skill"
  SKILL_DST="$SKILLS_DIR/exocortex/$skill"
  
  if [ -d "$SKILL_DST" ]; then
    log "Skill já instalada: $skill"
  elif [ -d "$SKILL_SRC" ]; then
    mkdir -p "$SKILL_DST"
    cp -r "$SKILL_SRC"/* "$SKILL_DST/"
    log "Skill instalada (local): $skill"
  else
    warn "Skill source não encontrada: $SKILL_SRC — será criada via PDD prompt"
  fi
done

# =============================================================================
# FASE P3-CORE: Bundle + Profiles
# =============================================================================
log "--- FASE P3-CORE: Bundle & Profiles ---"

# P3-CORE.1: Bundle exocortex-alpha
if hermes bundles list 2>/dev/null | grep -q "exocortex-alpha"; then
  log "Bundle já existe: exocortex-alpha"
else
  log "Criando bundle: exocortex-alpha"
  hermes bundles create exocortex-alpha \
    --skill exocortex-self-test \
    --skill exocortex-prompt-log \
    --skill acervo-manager \
    --skill exocortex-new-microverso \
    --skill exocortex-tool-governance \
    --skill exocortex-google-drive-hardening \
    --skill exocortex-notebooklm-knowledge-router \
    --skill exocortex-notebooklm-operational-workflow \
    --skill personal-artifact-workspace \
    --skill personal-intake-workspace \
    --skill exocortex-frontend-slides \
    --skill stop-slop \
    --skill taste-skill \
    --skill duckduckgo-search \
    --skill browser-use \
    --skill exocortex-draft-first \
    --skill exocortex-vetor-ativo \
    --skill exocortex-canvas \
    --skill exocortex-briefing \
    --skill exocortex-onboarding \
    --skill exocortex-output-quality-gate \
    -d "Bundle principal do Exocórtex.IA — carrega todas as skills core, memória, qualidade, pesquisa e comportamento." \
    -i "Você é o Exocórtex.IA. Ao carregar este bundle, siga SOUL.md e todas as governance rules."
  log "Bundle criado: exocortex-alpha (21 skills)"
fi

# P3-CORE.2: Profile exec
if hermes profile list 2>/dev/null | grep -q "exec"; then
  log "Profile já existe: exec"
else
  log "Criando profile: exec"
  hermes profile create exec \
    --clone \
    --description "Vetor de Execução — foco em FAZER. Draft-First, tools pesados, ação direta."
  log "Profile criado: exec"
fi

# Copiar profile.yaml e SOUL.md customizados para exec
EXEC_PROFILE_SRC="$PROJECT_DIR/.hermes/profiles/exec"
if [ -d "$EXEC_PROFILE_SRC" ]; then
  for pf in profile.yaml SOUL.md config.yaml; do
    if [ -f "$EXEC_PROFILE_SRC/$pf" ]; then
      cp "$EXEC_PROFILE_SRC/$pf" "$HERMES_DIR/profiles/exec/$pf"
    fi
  done
  log "Profile exec: config files sincronizados"
fi

# P3-CORE.3: Profile evol
if hermes profile list 2>/dev/null | grep -q "evol"; then
  log "Profile já existe: evol"
else
  log "Criando profile: evol"
  hermes profile create evol \
    --clone \
    --description "Vetor de Evolução — foco em PENSAR. Modo Socrático, reflexões, perguntas provocativas."
  log "Profile criado: evol"
fi

# Copiar profile.yaml e SOUL.md customizados para evol
EVOL_PROFILE_SRC="$PROJECT_DIR/.hermes/profiles/evol"
if [ -d "$EVOL_PROFILE_SRC" ]; then
  for pf in profile.yaml SOUL.md config.yaml; do
    if [ -f "$EVOL_PROFILE_SRC/$pf" ]; then
      cp "$EVOL_PROFILE_SRC/$pf" "$HERMES_DIR/profiles/evol/$pf"
    fi
  done
  log "Profile evol: config files sincronizados"
fi

# =============================================================================
# VERIFICAÇÃO FINAL
# =============================================================================
echo ""
log "--- VERIFICAÇÃO FINAL ---"

echo ""
echo "Skills instaladas:"
hermes skills list 2>/dev/null | grep -E "exocortex|duckduck|browser" || warn "Não foi possível listar skills"

echo ""
echo "Bundle:"
hermes bundles list 2>/dev/null | grep "exocortex" || warn "Nenhum bundle encontrado"

echo ""
echo "Profiles:"
hermes profile list 2>/dev/null || warn "Não foi possível listar profiles"

echo ""
echo "CLIs disponíveis:"
command -v ddgs > /dev/null 2>&1 && echo "  ✓ ddgs" || echo "  ✗ ddgs"
(command -v browser-use > /dev/null 2>&1 || [ -f "$HOME/.local/bin/browser-use" ]) && echo "  ✓ browser-use" || echo "  ✗ browser-use"

echo ""
log "Setup completo. Revise $LOG_FILE para detalhes."
echo ""
