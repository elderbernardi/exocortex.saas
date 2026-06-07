#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Candidate-Release Setup Script (Camada 1 + 2)
# =============================================================================
# Provisiona infraestrutura (Camada 1) e identidade (Camada 2) do Exocórtex
# sobre Hermes Agent, seguindo ADR-010 (layered deployment).
#
# Uso:
#   HERMES_HOME=/path/to/hermes EXOCORTEX_HOME=~/exocortex bash setup.sh
#
# Requer:
#   - HERMES_HOME definido (runtime do Hermes)
#   - EXOCORTEX_HOME definido (workspace cognitivo, default: ~/exocortex)
#   - Este script rodado a partir do diretório plans/pdd_v2/artifacts/
#
# Ref: docs/ADR/ADR-010-layered-deployment.md
#      micro/hermes-setup/decisions/hermes-runtime-cwd-exocortex-home.md
# =============================================================================

set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"
ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

patch_google_drive_search() {
  local gapi="$HERMES_HOME/skills/productivity/google-workspace/scripts/google_api.py"

  if [ ! -f "$gapi" ]; then
    warn "google_api.py não encontrado em $gapi (patch Drive não aplicado)"
    return 0
  fi

  local patch_status
  patch_status=$(python3 - "$gapi" <<'PY'
import py_compile
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

pattern = r"def drive_search\(args\):\n(?:.*\n)*?\n\ndef drive_get\(args\):"
replacement = r'''def drive_search(args):
    if args.max < 1:
        print("ERROR: --max must be >= 1", file=sys.stderr)
        sys.exit(1)

    if args.raw_query:
        query = args.query
    else:
        # Escape single quotes in Drive query literals and ignore trashed items by default.
        escaped = args.query.replace('\\\\', '\\\\\\\\').replace("'", "\\\\'")
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

if new_text == text:
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError:
        print("SKIP")
        raise SystemExit(0)
    else:
        print("ALREADY")
        raise SystemExit(0)

path.write_text(new_text, encoding="utf-8")
print("PATCHED")
PY
)

  case "$patch_status" in
    ALREADY) log "Google Drive search hardening já presente" ;;
    PATCHED) log "Google Drive search hardening aplicado" ;;
    *) warn "Falha ao aplicar patch de Drive (bloco não encontrado)" ;;
  esac
}

enforce_email_baseline() {
  local himalaya_skill="$HERMES_HOME/skills/email/himalaya"
  local hymalaia_skill="$HERMES_HOME/skills/email/hymalaia"

  if [ -d "$himalaya_skill" ]; then
    rm -rf "$himalaya_skill"
    log "Email baseline: skill 'himalaya' removida; padrão é 'productivity/google-workspace'"
  elif [ -d "$hymalaia_skill" ]; then
    rm -rf "$hymalaia_skill"
    log "Email baseline: skill 'hymalaia' removida; padrão é 'productivity/google-workspace'"
  else
    log "Email baseline OK: skill 'himalaya/hymalaia' ausente; padrão é 'productivity/google-workspace'"
  fi
}

enforce_mcp_baseline() {
  if ! command -v hermes >/dev/null 2>&1; then
    warn "hermes CLI não encontrado; pulando baseline MCP"
    return 0
  fi
  if hermes mcp list 2>/dev/null | grep -q "composio"; then
    if printf 'y\n' | hermes mcp remove composio >/dev/null 2>&1; then
      log "MCP baseline: 'composio' removido"
    else
      warn "Falha ao remover MCP server 'composio'"
    fi
  else
    log "MCP baseline OK: 'composio' já ausente"
  fi
}

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
  if [ ! -f "$hs_env" ]; then
    cat > "$hs_env" <<'EOF'
HINDSIGHT_API_LLM_PROVIDER=openai
HINDSIGHT_API_LLM_API_KEY=CHANGE_ME
EOF
    log "Hindsight .env template criado em $hs_env"
  else
    log "Hindsight .env preservado: $hs_env"
  fi
  if grep -q "CHANGE_ME" "$hs_env"; then
    warn "Preencha HINDSIGHT_API_LLM_API_KEY em $hs_env antes de subir o serviço"
    return 0
  fi
  (cd "$hs_dir" && docker compose pull >/dev/null 2>&1 || true && docker compose up -d >/dev/null 2>&1)
  log "Hindsight local ativo (API: :${hs_api_port}, UI: :${hs_ui_port})"
}

configure_docbrain_engine() {
  local docbrain_dir="${EXOCORTEX_DOCBRAIN_DIR:-$EXOCORTEX_HOME/tools/docbrain}"
  local repo="https://github.com/ProjetoBB/docBrainBB.git"
  if ! command -v git >/dev/null 2>&1; then
    warn "git não encontrado; pulando clone do DocBrain"
    return 0
  fi
  if ! command -v npm >/dev/null 2>&1; then
    warn "npm não encontrado; pulando setup do DocBrain"
    return 0
  fi
  mkdir -p "$(dirname "$docbrain_dir")"
  if [ ! -d "$docbrain_dir/.git" ]; then
    info "Clonando DocBrain em $docbrain_dir"
    git clone "$repo" "$docbrain_dir" >/dev/null 2>&1 || {
      warn "Falha ao clonar DocBrain"
      return 0
    }
  else
    log "Repositório DocBrain encontrado: $docbrain_dir"
  fi
  (cd "$docbrain_dir" && git pull --ff-only origin main >/dev/null 2>&1 || true && npm install >/dev/null 2>&1 || true && npm run build >/dev/null 2>&1 || true)
  log "DocBrain dependências/build verificados"
  if [ -n "${OPENROUTER_API_KEY:-}" ] || [ -n "${DOCBRAIN_LLM_API_KEY:-}" ]; then
    log "Key LLM disponível para DocBrain"
  else
    mkdir -p "$HERMES_HOME/reminders"
    cat > "$HERMES_HOME/reminders/docbrain-llm-key.md" <<'EOF'
# Pending DocBrain LLM key
DocBrain is installed, but no LLM key was available during setup.
Configure OPENROUTER_API_KEY in the Hermes environment.
EOF
    info "Sem key LLM; lembrete criado em $HERMES_HOME/reminders/docbrain-llm-key.md"
  fi
}

configure_notebooklm_integration() {
  if ! command -v nlm >/dev/null 2>&1; then
    if command -v uv >/dev/null 2>&1; then
      info "Instalando nlm via uv tool install notebooklm-mcp-cli"
      uv tool install notebooklm-mcp-cli >/dev/null 2>&1 || {
        warn "Falha ao instalar notebooklm-mcp-cli via uv"
        return 0
      }
    else
      warn "nlm CLI não encontrado. Instale com: uv tool install notebooklm-mcp-cli"
      return 0
    fi
  fi
  log "nlm CLI disponível: $(command -v nlm)"
  if nlm login --check >/dev/null 2>&1; then
    log "nlm autenticado"
  else
    mkdir -p "$HERMES_HOME/reminders"
    cat > "$HERMES_HOME/reminders/notebooklm-login.md" <<'EOF'
# Pending NotebookLM login
nlm CLI instalado mas autenticação não está ativa.
No terminal: nlm login && nlm login --check
EOF
    warn "nlm sem auth ativa; lembrete criado"
  fi
  if command -v hermes >/dev/null 2>&1 && command -v notebooklm-mcp >/dev/null 2>&1; then
    if hermes mcp list 2>/dev/null | grep -q "notebooklm"; then
      log "MCP server 'notebooklm' já configurado"
    else
      printf 'y\n' | hermes mcp add notebooklm --command notebooklm-mcp >/dev/null 2>&1 && \
        log "MCP server 'notebooklm' adicionado" || \
        warn "Falha ao adicionar MCP server 'notebooklm'"
    fi
  fi
}

configure_context7_mcp() {
  if ! command -v hermes >/dev/null 2>&1; then
    warn "hermes CLI não encontrado; pulando context7 MCP"
    return 0
  fi
  if hermes mcp list 2>/dev/null | grep -q "context7"; then
    log "MCP server 'context7' já configurado"
    return 0
  fi
  if [ -z "${CONTEXT7_API_KEY:-}" ]; then
    mkdir -p "$HERMES_HOME/reminders"
    cat > "$HERMES_HOME/reminders/context7-api-key.md" <<'EOF'
# Pending Context7 API Key

Context7 MCP não foi configurado porque CONTEXT7_API_KEY não estava definida.
Context7 fornece documentação atualizada de tech stacks (Next.js, React, etc.).

Para configurar:
1. Obtenha uma API key em https://context7.com
2. Execute: CONTEXT7_API_KEY=<key> bash setup.sh
   ou configure manualmente: hermes mcp add context7 --command "npx -y @context7/mcp" --env CONTEXT7_API_KEY=<key>
EOF
    info "CONTEXT7_API_KEY não definida; lembrete criado"
    info "  Context7 pode ser adicionado depois: hermes mcp add context7 --command 'npx -y @context7/mcp'"
    return 0
  fi
  printf 'y\n' | hermes mcp add context7 \
    --command "npx -y @context7/mcp" \
    --env "CONTEXT7_API_KEY=${CONTEXT7_API_KEY}" \
    >/dev/null 2>&1 && \
    log "MCP server 'context7' adicionado (documentação de tech stacks)" || \
    warn "Falha ao adicionar MCP server 'context7'"
}

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Exocórtex.IA — Candidate-Release Setup     ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

info "HERMES_HOME:    $HERMES_HOME"
info "EXOCORTEX_HOME: $EXOCORTEX_HOME"
info "ACERVO:         $ACERVO"
info "ARTIFACTS:      $SCRIPT_DIR"

# =============================================================================
# Step 1: Criar estrutura base (Camada 1 — Infraestrutura)
# =============================================================================
info "[Camada 1] Criando estrutura base..."

# Runtime Hermes
mkdir -p "$HERMES_HOME/skills/exocortex"
mkdir -p "$HERMES_HOME/profiles"
mkdir -p "$HERMES_HOME/skill-bundles"
mkdir -p "$HERMES_HOME/memories"

# Workspace Exocórtex
mkdir -p "$EXOCORTEX_HOME"

# Acervo 4 camadas + diretórios funcionais v0.4
mkdir -p "$ACERVO/macro/assets"
mkdir -p "$ACERVO/global"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
mkdir -p "$ACERVO/micro/_template"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
mkdir -p "$ACERVO/micro/exocortex-ops"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
mkdir -p "$ACERVO/micro/exocortex-ops/_meta"/{snapshots,drafts,indices}
mkdir -p "$ACERVO/shared"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive,cross-refs}

# Diretórios operacionais v0.4 (harness canônico)
mkdir -p "$ACERVO/_tasks"
mkdir -p "$ACERVO/_routines"
mkdir -p "$ACERVO/_automations"
mkdir -p "$ACERVO/_inbox"/{incoming,processing,promoted,_archive}
mkdir -p "$ACERVO/_artifacts/items"
mkdir -p "$ACERVO/_artifacts/views"/{by_microverso,by_task,by_status,by_type}
mkdir -p "$ACERVO/_artifacts/_ops"
mkdir -p "$ACERVO/global/templates/harness-v0.4"
mkdir -p "$ACERVO/global/tools/harness"

# Compatibilidade: symlink se acervo não está em ~/.hermes
if [ "$ACERVO" != "$HERMES_HOME/acervo" ] && [ ! -e "$HERMES_HOME/acervo" ]; then
  ln -s "$ACERVO" "$HERMES_HOME/acervo" 2>/dev/null || true
  log "Symlink de compatibilidade: $HERMES_HOME/acervo -> $ACERVO"
fi

log "Estrutura de diretórios criada (runtime + workspace + v0.4 operacional)"

# =============================================================================
# Step 2: Copiar skills
# =============================================================================
info "Instalando skills..."

SKILLS_SRC="$SCRIPT_DIR/skills"
SKILLS_DST="$HERMES_HOME/skills/exocortex"

if [ -d "$SKILLS_SRC" ]; then
  for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name=$(basename "$skill_dir")
    if [ -d "$skill_dir" ]; then
      mkdir -p "$SKILLS_DST/$skill_name"
      cp -r "$skill_dir"* "$SKILLS_DST/$skill_name/" 2>/dev/null || true
      log "Skill: $skill_name"
    fi
  done
else
  fail "Skills source não encontrado: $SKILLS_SRC"
fi

# =============================================================================
# Step 3: Copiar acervo (para ACERVO, não HERMES_HOME/acervo)
# =============================================================================
info "Instalando acervo..."

ACERVO_SRC="$SCRIPT_DIR/acervo"

copy_acervo_seed() {
  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --exclude '__pycache__' \
      --exclude 'micro/exocortex-ops/***' \
      "$ACERVO_SRC/" "$ACERVO/"
  else
    warn "rsync não encontrado; cópia genérica do Acervo pulada para evitar overwrite acidental"
  fi
}

provision_exocortex_ops_seed() {
  local ops_src="$ACERVO_SRC/micro/exocortex-ops"
  local ops_dst="$ACERVO/micro/exocortex-ops"

  mkdir -p "$ops_dst"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
  mkdir -p "$ops_dst/_meta"/{snapshots,drafts,indices}

  if [ -d "$ops_src" ]; then
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --ignore-existing --exclude '__pycache__' "$ops_src/" "$ops_dst/"
      log "Microverso base exocortex-ops instalado/preservado"
    else
      warn "rsync não encontrado; exocortex-ops seed não copiado para evitar overwrite acidental"
    fi
  else
    warn "Microverso base exocortex-ops source não encontrado: $ops_src"
  fi
}

if [ -d "$ACERVO_SRC" ]; then
  copy_acervo_seed
  provision_exocortex_ops_seed
  log "Acervo: $(find "$ACERVO" -type f 2>/dev/null | wc -l) arquivos"
else
  fail "Acervo source não encontrado: $ACERVO_SRC"
fi

# Verificar WELCOME.md
WELCOME_SRC="$ACERVO_SRC/global/knowledge/WELCOME.md"
if [ -f "$WELCOME_SRC" ]; then
  mkdir -p "$ACERVO/global/knowledge"
  cp "$WELCOME_SRC" "$ACERVO/global/knowledge/WELCOME.md"
  log "WELCOME.md instalado em acervo/global/knowledge/"
else
  warn "WELCOME.md não encontrado em $WELCOME_SRC"
fi

# Instalar templates canônicos v0.4
TEMPLATES_SRC="$SCRIPT_DIR/acervo/global/templates/harness-v0.4"
TEMPLATES_DST="$ACERVO/global/templates/harness-v0.4"
if [ -d "$TEMPLATES_SRC" ]; then
  cp -r "$TEMPLATES_SRC"/* "$TEMPLATES_DST/" 2>/dev/null || true
  log "Templates v0.4: $(ls -1 "$TEMPLATES_DST" 2>/dev/null | wc -l) arquivos"
fi

# Instalar ferramentas determinísticas do harness
TOOLS_SRC="$SCRIPT_DIR/acervo/global/tools/harness"
TOOLS_DST="$ACERVO/global/tools/harness"
if [ -d "$TOOLS_SRC" ]; then
  cp -r "$TOOLS_SRC"/* "$TOOLS_DST/" 2>/dev/null || true
  chmod +x "$TOOLS_DST"/*.py 2>/dev/null || true
  log "Harness tools: $(ls -1 "$TOOLS_DST"/*.py 2>/dev/null | wc -l) scripts"
fi

# =============================================================================
# Step 4: Copiar profiles
# =============================================================================
info "Instalando profiles..."

PROFILES_SRC="$SCRIPT_DIR/profiles"
PROFILES_DST="$HERMES_HOME/profiles"

if [ -d "$PROFILES_SRC" ]; then
  cp -r "$PROFILES_SRC"/* "$PROFILES_DST/" 2>/dev/null || true
  log "Profiles: $(ls -1d "$PROFILES_DST"/*/ 2>/dev/null | wc -l) profiles"
fi

# =============================================================================
# Step 5: Copiar bundle
# =============================================================================
info "Instalando bundles..."

BUNDLES_SRC="$SCRIPT_DIR/skill-bundles"
BUNDLES_DST="$HERMES_HOME/skill-bundles"

if [ -d "$BUNDLES_SRC" ]; then
  cp -r "$BUNDLES_SRC"/* "$BUNDLES_DST/" 2>/dev/null || true
  log "Bundle copiado"
fi

# =============================================================================
# Step 5.1: Hardening Drive Search no google-workspace
# =============================================================================
info "Aplicando hardening de Google Drive search..."
patch_google_drive_search

# =============================================================================
# Step 5.2: Baselines de segurança
# =============================================================================
info "Aplicando baseline de email: Google Workspace como padrão..."
enforce_email_baseline

info "Aplicando baseline MCP: removendo composio..."
enforce_mcp_baseline

# =============================================================================
# Step 6: Identidade (SOUL_SEED)
# =============================================================================
if [ -f "$SCRIPT_DIR/SOUL_SEED.md" ]; then
  cp "$SCRIPT_DIR/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"
  log "SOUL.md instalado (de SOUL_SEED.md)"
fi

# =============================================================================
# Step 7: Integrações (Hindsight, DocBrain, NotebookLM)
# =============================================================================
info "Verificando integrações..."

info "Hindsight (memória operacional via Docker/ghcr.io)..."
setup_hindsight_local_docker

info "DocBrain (parser engine via GitHub clone)..."
configure_docbrain_engine

info "NotebookLM (CLI + MCP)..."
configure_notebooklm_integration

info "Context7 (documentação de tech stacks via MCP)..."
configure_context7_mcp

# =============================================================================
# Step 8: Verificação de keys
# =============================================================================
info "Verificando keys de API..."
if [ -n "${OPENROUTER_API_KEY:-}" ]; then
  log "OPENROUTER_API_KEY definida"
else
  warn "OPENROUTER_API_KEY não definida — DocBrain e LLM routing podem falhar"
fi
if [ -n "${CONTEXT7_API_KEY:-}" ]; then
  log "CONTEXT7_API_KEY definida"
else
  info "CONTEXT7_API_KEY não definida (opcional — context7 pode ser adicionado depois)"
fi

# =============================================================================
# Step 8.1: Verificação de Telegram token
# =============================================================================
info "Verificando Telegram gateway..."
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  log "TELEGRAM_BOT_TOKEN definida"
  if command -v hermes >/dev/null 2>&1; then
    if hermes gateway list 2>/dev/null | grep -q "telegram"; then
      log "Gateway Telegram já configurado"
    else
      hermes gateway setup telegram --token "${TELEGRAM_BOT_TOKEN}" >/dev/null 2>&1 && \
        log "Gateway Telegram configurado com token" || \
        warn "Falha ao configurar gateway Telegram"
    fi
  fi
else
  mkdir -p "$HERMES_HOME/reminders"
  cat > "$HERMES_HOME/reminders/telegram-setup.md" <<'EOF'
# Configuração do Telegram pendente

O Telegram é o gateway recomendado para começar.

## Como configurar:
1. Abra @BotFather no Telegram
2. Envie /newbot e siga as instruções
3. Copie o token fornecido
4. Execute: TELEGRAM_BOT_TOKEN="seu_token" bash setup.sh
   ou: hermes gateway setup telegram --token "seu_token"
EOF
  info "TELEGRAM_BOT_TOKEN não definida; reminder criado"
  info "  Configure depois: TELEGRAM_BOT_TOKEN=<token> bash setup.sh"
fi

# =============================================================================
# Step 8.2: Verificação de Google credentials
# =============================================================================
info "Verificando Google credentials..."
GOOGLE_CREDS_OK=false
if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
  GOOGLE_CREDS_OK=true
  log "Google Application Default Credentials encontradas"
elif [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ] && [ -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
  GOOGLE_CREDS_OK=true
  log "Google credentials via GOOGLE_APPLICATION_CREDENTIALS"
elif command -v gcloud >/dev/null 2>&1; then
  if gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>/dev/null | grep -q "@"; then
    GOOGLE_CREDS_OK=true
    log "Google auth ativa via gcloud CLI"
  fi
fi

if ! $GOOGLE_CREDS_OK; then
  mkdir -p "$HERMES_HOME/reminders"
  cat > "$HERMES_HOME/reminders/google-credentials.md" <<'EOF'
# Google Credentials pendentes

Para integração com Gmail, Calendar e Drive (Draft-First Protocol):

## Opção 1: Application Default Credentials
```bash
gcloud auth application-default login
```

## Opção 2: Service Account
Exporte GOOGLE_APPLICATION_CREDENTIALS apontando para o JSON da service account.

## Opção 3: OAuth2 Client
Crie um OAuth2 Client ID no Google Cloud Console (tipo Desktop).
EOF
  warn "Google credentials não encontradas; reminder criado"
  info "  Configure: gcloud auth application-default login"
fi

# =============================================================================
# Step 9: Verificação Final
# =============================================================================
echo ""
info "=== VERIFICAÇÃO FINAL ==="
echo ""

ERRORS=0

echo "Skills instaladas:"
SKILL_COUNT=0
for d in "$SKILLS_DST"/*/; do
  [ -d "$d" ] && echo "  ✓ $(basename "$d")" && SKILL_COUNT=$((SKILL_COUNT + 1))
done
echo "  Total: $SKILL_COUNT"

EXPECTED_SKILLS=(
  # Core + Onboard
  "excrtx-assess-selftest" "excrtx-harness-promptlog" "excrtx-onboard-welcome" "excrtx-onboard-interview"
  # Quality
  "excrtx-quality-antislop" "excrtx-quality-taste" "excrtx-quality-designsys" "excrtx-quality-gate"
  # Memory
  "excrtx-memory-manager" "excrtx-memory-wikiadapt" "excrtx-memory-newmicro"
  "excrtx-memory-mvsetup" "excrtx-memory-mvinstall" "excrtx-memory-opsmemory"
  # Behavior + Govern
  "excrtx-govern-draftfirst" "excrtx-behavior-vetor" "excrtx-behavior-canvas"
  "excrtx-behavior-briefing" "excrtx-govern-tools" "excrtx-harness-kanban"
  # Workspace
  "excrtx-produce-artifacts" "excrtx-memory-intake"
  # Production
  "excrtx-produce-slides" "excrtx-produce-oficios"
  # Integration
  "excrtx-harness-core" "excrtx-harness-codexint" "excrtx-harness-hermesops" "excrtx-integrate-docbrain"
  "excrtx-integrate-nlmroute" "excrtx-integrate-nlmops"
  # Platform
  "excrtx-integrate-gdrive" "excrtx-integrate-oauth" "excrtx-harness-surfaces"
  # External
  "excrtx-integrate-browser"
  # Assessment
  "excrtx-assess-repofit"
)
MISSING_SKILLS=()
for skill in "${EXPECTED_SKILLS[@]}"; do
  if [ ! -f "$SKILLS_DST/$skill/SKILL.md" ]; then
    MISSING_SKILLS+=("$skill")
  fi
done
if [ ${#MISSING_SKILLS[@]} -gt 0 ]; then
  warn "Skills faltando: ${MISSING_SKILLS[*]}"
  ERRORS=$((ERRORS + ${#MISSING_SKILLS[@]}))
else
  log "Todas as ${#EXPECTED_SKILLS[@]} skills esperadas presentes"
fi
echo ""

echo "Acervo (4 camadas + v0.4 funcionais):"
for layer in macro global micro shared; do
  if [ -d "$ACERVO/$layer" ]; then
    count=$(find "$ACERVO/$layer" -type f 2>/dev/null | wc -l)
    echo "  ✓ $layer/: $count arquivos"
  else
    echo "  ✗ $layer/ (MISSING)"
    ERRORS=$((ERRORS + 1))
  fi
done
echo ""

echo "Microverso base exocortex-ops:"
if [ -d "$ACERVO/micro/exocortex-ops" ]; then
  echo "  ✓ micro/exocortex-ops/"
else
  echo "  ✗ micro/exocortex-ops/ (MISSING)"
  ERRORS=$((ERRORS + 1))
fi
EXPECTED_OPS_FILES=(
  "microverso.yaml"
  "_meta/SCHEMA.md"
  "_meta/index.md"
  "_meta/log.md"
  "contracts/operating-boundaries.md"
  "contracts/profile-isolation.md"
  "contracts/canonical-path-policy.md"
  "contracts/draftfirst-change-policy.md"
  "contracts/secret-handling-policy.md"
  "contracts/memory-authority-policy.md"
  "contracts/runtime-verification-policy.md"
  "contracts/rollback-policy.md"
  "workflows/setup-change-draftfirst.md"
  "workflows/runtime-drift-audit.md"
  "workflows/self-check.md"
  "workflows/base-microverse-provisioning.md"
  "workflows/post-change-validation.md"
  "knowledge/runtime-map.md"
  "knowledge/profile-registry.md"
  "knowledge/mcp-registry.md"
  "knowledge/cron-registry.md"
  "knowledge/version-matrix.md"
)
for f in "${EXPECTED_OPS_FILES[@]}"; do
  if [ ! -f "$ACERVO/micro/exocortex-ops/$f" ]; then
    echo "  ✗ micro/exocortex-ops/$f (MISSING)"
    ERRORS=$((ERRORS + 1))
  fi
done
echo ""

echo "Diretórios operacionais v0.4:"
for opdir in _tasks _routines _automations _inbox _artifacts; do
  if [ -d "$ACERVO/$opdir" ]; then
    echo "  ✓ $opdir/"
  else
    echo "  ✗ $opdir/ (MISSING)"
    ERRORS=$((ERRORS + 1))
  fi
done
echo ""

echo "Templates v0.4:"
ls "$ACERVO/global/templates/harness-v0.4/" 2>/dev/null | while read -r t; do echo "  ✓ $t"; done
echo ""

echo "Harness tools:"
ls "$ACERVO/global/tools/harness/"*.py 2>/dev/null | while read -r t; do echo "  ✓ $(basename "$t")"; done
echo ""

echo "Profiles:"
echo "  ✓ default (exec+evol unificado — SOUL.md com vetor-ativo)"
if [ -f "$PROFILES_DST/manut/profile.yaml" ]; then
  echo "  ✓ manut (background/zelador)"
else
  echo "  ✗ manut (MISSING)"
  ERRORS=$((ERRORS + 1))
fi
echo ""

if [ -f "$HERMES_HOME/SOUL.md" ]; then
  log "SOUL.md presente"
else
  warn "SOUL.md ausente em $HERMES_HOME"
  ERRORS=$((ERRORS + 1))
fi

if [ -f "$BUNDLES_DST/exocortex-alpha.yaml" ]; then
  log "Bundle exocortex-alpha.yaml presente"
else
  warn "Bundle manifest ausente"
  ERRORS=$((ERRORS + 1))
fi

if command -v hermes > /dev/null 2>&1; then
  log "hermes CLI: $(hermes --version 2>/dev/null | head -1)"
else
  warn "hermes CLI não encontrado no PATH"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
  echo "╔═══════════════════════════════════════════════╗"
  echo "║   ✅ Setup Candidate-Release completo.        ║"
  echo "║   Zero erros.                                 ║"
  echo "╚═══════════════════════════════════════════════╝"
else
  echo "╔═══════════════════════════════════════════════╗"
  echo "║   ⚠ Setup concluído com $ERRORS erro(s).       ║"
  echo "╚═══════════════════════════════════════════════╝"
fi
echo ""
info "Runtime Hermes:      $HERMES_HOME"
info "Workspace Exocórtex: $EXOCORTEX_HOME"
info "Acervo canônico:     $ACERVO"
info "Profiles:            default (interativo) + manut (background)"
info "Uso:                 hermes (default) | hermes -p manut"
echo ""

# =============================================================================
# Step 10: Verificação pós-provisionamento
# =============================================================================
info "Iniciando verificação pós-provisionamento..."
if [ -x "$SCRIPT_DIR/scripts/post-provisioning-verify.sh" ]; then
  bash "$SCRIPT_DIR/scripts/post-provisioning-verify.sh" || \
    warn "Verificação pós-provisionamento reportou falhas (veja relatório no Acervo)"
else
  warn "Script de verificação não encontrado: $SCRIPT_DIR/scripts/post-provisioning-verify.sh"
fi
