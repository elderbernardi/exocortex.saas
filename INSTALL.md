# Exocórtex.IA — Guia de Instalação para Agentes

> **Propósito**: Este documento é um runbook estruturado para agentes de IA
> executarem a instalação do Exocórtex.IA sobre o Hermes Agent runtime.
> Equivale funcionalmente ao `setup.sh`, mas em formato legível e executável
> passo-a-passo por agentes (Claude, Gemini, GPT, etc.).
>
> **Para humanos**: Use `bash setup.sh`, `bash setup.sh --step-by-step`
> ou `curl ... | bash -s -- --step-by-step`.
> Este `.md` é para agentes que precisam instalar/diagnosticar o sistema
> via terminal.

---

## Variáveis de Ambiente

Defina ANTES de iniciar qualquer step. Se não definidas, use os defaults.

```bash
# Obrigatórias (com defaults)
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"
ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"

# O diretório raiz do repositório exocortex.saas (onde este arquivo está)
SCRIPT_DIR="$(pwd)"  # assumindo que o agente está na raiz do repo

# Derivadas
SKILLS_SRC="$SCRIPT_DIR/skills"
SKILLS_DST="$HERMES_HOME/skills/excrtx"
PROFILES_SRC="$SCRIPT_DIR/profiles"
PROFILES_DST="$HERMES_HOME/profiles"
BUNDLES_SRC="$SCRIPT_DIR/skill-bundles"
BUNDLES_DST="$HERMES_HOME/skill-bundles"
ACERVO_SRC="$SCRIPT_DIR/acervo"
```

### Configuração de LLM — os 3 Papéis

Toda configuração de LLM neste repo é consolidada em **3 papéis**, cada um um
quádruplo de env vars (`{PROVIDER,MODEL,API_KEY,BASE_URL}`):

| Papel | Env vars | Uso | Herança |
|-------|----------|-----|---------|
| **default** | `EXOCORTEX_DEFAULT_{PROVIDER,MODEL,API_KEY,BASE_URL}` | LLM principal — reasoning / routing / todas as skills. **SEMPRE usado; obrigatório.** | — |
| **vision** | `EXOCORTEX_VISION_{PROVIDER,MODEL,API_KEY,BASE_URL}` | Modelo com visão (imagens, OCR multimodal) | Campo vazio **herda o default** campo a campo |
| **auxiliar** | `EXOCORTEX_AUX_{PROVIDER,MODEL,API_KEY,BASE_URL}` | Softwares externos: DocBrain, backend LLM do Hindsight | Campo vazio **herda o default** campo a campo |

- `BASE_URL` vazia → derivada automaticamente do catálogo `setup/providers.json`
  (providers: `openrouter`, `deepseek`, `openai`, `gemini`, `xai`, `opencode`, `opencode-go`).
- Resolvedores: `scripts/lib/llm_roles.py` (Python) e `setup/lib/llm-roles.sh` (shell).
  Inspecione o estado resolvido com `python3 scripts/lib/llm_roles.py all`.
- Instalações antigas são migradas **uma vez** por `scripts/migrate-env-roles.py`
  (roda automaticamente no `setup.sh`): `OPENROUTER`/`DEEPSEEK`/`OPENCODE` → **default**,
  `DOCBRAIN_LLM` → **auxiliar**, `OPENAI`/`GEMINI`/`GOOGLE` → **vision**. As chaves legadas
  são comentadas; as chaves de serviço não-LLM são preservadas.

### Variáveis Opcionais

| Variável | Default | Descrição |
|----------|---------|-----------|
| `EXOCORTEX_DEFAULT_*` | — | Papel **default** (PROVIDER/MODEL/API_KEY/BASE_URL). Obrigatório — LLM principal |
| `EXOCORTEX_VISION_*` | herda default | Papel **vision** (modelo multimodal); campos vazios herdam o default |
| `EXOCORTEX_AUX_*` | herda default | Papel **auxiliar** (DocBrain, backend LLM do Hindsight); campos vazios herdam o default |
| `TELEGRAM_BOT_TOKEN` | — | Token do bot Telegram (@BotFather) |
| `CONTEXT7_API_KEY` | — | Chave Context7 para docs de tech stacks |
| `FIRECRAWL_API_KEY` | — | Chave Firecrawl para crawling/extract (endpoint via `FIRECRAWL_BASE_URL`) |
| `FIRECRAWL_BASE_URL` | `http://127.0.0.1:3002` | Endpoint local padrão do Firecrawl |
| `EXOCORTEX_ENABLE_HINDSIGHT` | `0` | `1` para ativar Hindsight local (Docker) |
| `EXOCORTEX_ENABLE_HERMES_WEBUI` | `0` | `1` para ativar WebUI cockpit |

### Mapeamento de providers/keys

- **LLM:** defina apenas o papel **default** (`EXOCORTEX_DEFAULT_*`) para a maioria dos
  casos. Os papéis **vision** e **auxiliar** herdam o default campo a campo quando vazios —
  só os preencha se quiser um provider/modelo distinto para visão ou para softwares externos.
- **DocBrain:** configurado pelo papel **auxiliar** (`EXOCORTEX_AUX_*`); o step-08 gera o
  `.env` do DocBrain a partir dele. Se o papel aux estiver vazio, herda o default.
- **Firecrawl:** a chave (`FIRECRAWL_API_KEY`) e o endpoint (`FIRECRAWL_BASE_URL`,
  default `http://127.0.0.1:3002`) andam juntos — documente/ajuste ambos ao subir uma instância local.

---

## Pré-requisitos do Sistema

### Verificação

```bash
# Verifique todos os pré-requisitos de uma vez:
bash scripts/validate-environment.sh

# Smoke check do control plane local do Acervo
python3 scripts/acervoctl.py list-microversos
python3 scripts/acervo_mcp_server.py --self-test --acervo-root "$PWD/acervo"
```

### Binários Obrigatórios

| Binário | Versão mínima | Verificação |
|---------|---------------|-------------|
| `bash` | ≥ 4.0 | `bash --version \| head -1` |
| `python3` | ≥ 3.10 | `python3 --version` |
| `git` | qualquer | `git --version` |
| `curl` | qualquer | `curl --version \| head -1` |
| `rsync` | qualquer | `rsync --version \| head -1` |
| `hermes` | ≥ 2026.4.8 | `hermes --version` |

### Módulos Python Obrigatórios

```bash
python3 -c "import yaml; print(yaml.__version__)"
python3 -c "import google.auth; print('ok')"
python3 -c "import pptx; print(pptx.__version__)"
```

Se faltarem: `pip3 install PyYAML google-auth-oauthlib google-api-python-client google-auth-httplib2 python-pptx`

---

## Step 00 — Compatibilidade do Hermes

**Objetivo**: Verificar que a versão do Hermes instalada é compatível.

### Pré-condição
- `hermes` presente no PATH

### Execução

```bash
HERMES_VERSION=$(hermes --version 2>/dev/null | grep -oP '\d{4}\.\d+\.\d+' | head -1)
echo "Hermes version: $HERMES_VERSION"
```

### Verificação
- Versão mínima: `2026.4.8`
- Versão máxima testada: `2026.6.5`
- Se `$HERMES_VERSION` estiver abaixo do mínimo → **ABORTAR**
- Se acima do máximo testado → **WARNING** (pode funcionar)

### Verificar estrutura de diretórios

```bash
test -d "$HERMES_HOME/skills"   && echo "✓ skills dir"   || echo "✗ skills dir MISSING"
test -d "$HERMES_HOME/memories" && echo "✓ memories dir"  || echo "✗ memories dir MISSING"
mkdir -p "$HERMES_HOME/profiles"
```

---

## Step 01 — Hindsight (Memória Operacional via Docker)

**Objetivo**: Provisionar Hindsight local. **Opcional** — só executa se `EXOCORTEX_ENABLE_HINDSIGHT=1`.

### Pré-condição
- `docker` e `docker compose` disponíveis
- `EXOCORTEX_ENABLE_HINDSIGHT=1`

### Execução (pular se `EXOCORTEX_ENABLE_HINDSIGHT != 1`)

```bash
HS_DIR="$HERMES_HOME/hindsight-local"
mkdir -p "$HS_DIR/data"

# Criar docker-compose.yml se não existir
cat > "$HS_DIR/docker-compose.yml" <<'EOF'
services:
  hindsight:
    image: ghcr.io/vectorize-io/hindsight:latest
    container_name: exocortex-hindsight
    restart: unless-stopped
    ports:
      - "8888:8888"
      - "9999:9999"
    env_file:
      - .env
    volumes:
      - ./data:/home/hindsight/.pg0
EOF

# Criar .env se não existir — backend LLM do Hindsight usa o papel auxiliar
# (EXOCORTEX_AUX_*; herda o default se vazio). Resolva via scripts/lib/llm_roles.py.
cat > "$HS_DIR/.env" <<EOF
HINDSIGHT_API_LLM_PROVIDER=${EXOCORTEX_AUX_PROVIDER:-${EXOCORTEX_DEFAULT_PROVIDER:-openai}}
HINDSIGHT_API_LLM_API_KEY=${EXOCORTEX_AUX_API_KEY:-${EXOCORTEX_DEFAULT_API_KEY:-CHANGE_ME}}
HINDSIGHT_API_LLM_MODEL=${EXOCORTEX_AUX_MODEL:-${EXOCORTEX_DEFAULT_MODEL:-gpt-4o-mini}}
EOF

# Subir container
cd "$HS_DIR" && docker compose pull && docker compose up -d
```

### Verificação
```bash
docker ps | grep exocortex-hindsight
curl -s http://localhost:8888/health | head -1
```

---

## Step 02 — Criar Estrutura de Diretórios

**Objetivo**: Criar a árvore de diretórios do runtime e workspace.

### Execução

```bash
# Runtime Hermes
mkdir -p "$HERMES_HOME/skills/excrtx"
mkdir -p "$HERMES_HOME/profiles"
mkdir -p "$HERMES_HOME/skill-bundles"
mkdir -p "$HERMES_HOME/memories"

# Workspace Exocórtex
mkdir -p "$EXOCORTEX_HOME"

# Acervo 4 camadas
mkdir -p "$ACERVO/macro/assets"
mkdir -p "$ACERVO/global"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
mkdir -p "$ACERVO/micro/_template"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
mkdir -p "$ACERVO/micro/exocortex-ops"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}
mkdir -p "$ACERVO/micro/exocortex-ops/_meta"/{snapshots,drafts,indices}
mkdir -p "$ACERVO/shared"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive,cross-refs}

# Diretórios operacionais v0.4
mkdir -p "$ACERVO/_tasks"
mkdir -p "$ACERVO/_routines"
mkdir -p "$ACERVO/_automations"
mkdir -p "$ACERVO/_inbox"/{incoming,processing,promoted,_archive}
mkdir -p "$ACERVO/_artifacts/items"
mkdir -p "$ACERVO/_artifacts/views"/{by_microverso,by_task,by_status,by_type}
mkdir -p "$ACERVO/_artifacts/_ops"
mkdir -p "$ACERVO/global/templates/harness-v0.4"
mkdir -p "$ACERVO/global/tools/harness"

# Symlink de compatibilidade
if [ "$ACERVO" != "$HERMES_HOME/acervo" ] && [ ! -e "$HERMES_HOME/acervo" ]; then
  ln -s "$ACERVO" "$HERMES_HOME/acervo"
fi
```

### Verificação
```bash
test -d "$ACERVO/macro"  && echo "✓ macro"  || echo "✗ macro"
test -d "$ACERVO/global" && echo "✓ global" || echo "✗ global"
test -d "$ACERVO/micro"  && echo "✓ micro"  || echo "✗ micro"
test -d "$ACERVO/shared" && echo "✓ shared" || echo "✗ shared"
test -d "$ACERVO/_tasks" && echo "✓ _tasks" || echo "✗ _tasks"
```

---

## Step 03 — Instalar Skills (50 skills excrtx-*)

**Objetivo**: Copiar todas as 50 skills `excrtx-*` (mais as skills empacotadas `last30days` e `assessment-question-authoring`, 52 pacotes no total) do repositório para o runtime do Hermes.

### Execução

```bash
for skill_dir in "$SKILLS_SRC"/*/; do
  skill_name=$(basename "$skill_dir")
  mkdir -p "$SKILLS_DST/$skill_name"
  cp -r "$skill_dir"* "$SKILLS_DST/$skill_name/" 2>/dev/null || true
  echo "✓ $skill_name"
done
```

### Verificação
```bash
INSTALLED=$(find "$SKILLS_DST" -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "Skills instaladas: $INSTALLED (esperado: ≥ 50 excrtx-*)"
test "$INSTALLED" -ge 50 && echo "✓ OK" || echo "✗ FALHA"
```

---

## Step 04 — Instalar Acervo (seed + ops + templates + tools)

**Objetivo**: Copiar o seed do Acervo, microverso exocortex-ops, templates e ferramentas.

### Execução

```bash
# Copiar seed do acervo (exceto exocortex-ops que tem tratamento especial)
rsync -a --exclude '__pycache__' --exclude 'micro/exocortex-ops/***' \
  "$ACERVO_SRC/" "$ACERVO/"

# Instalar microverso base exocortex-ops (preservando dados existentes)
rsync -a --ignore-existing --exclude '__pycache__' \
  "$ACERVO_SRC/micro/exocortex-ops/" "$ACERVO/micro/exocortex-ops/"

# Templates v0.4
cp -r "$SCRIPT_DIR/acervo/global/templates/harness-v0.4/"* \
  "$ACERVO/global/templates/harness-v0.4/" 2>/dev/null || true

# Ferramentas globais
find "$SCRIPT_DIR/acervo/global/tools" -maxdepth 1 -type f -name '*.py' \
  -exec cp {} "$ACERVO/global/tools/" \;
chmod +x "$ACERVO/global/tools/"*.py 2>/dev/null || true

# Ferramentas do harness
cp -r "$SCRIPT_DIR/acervo/global/tools/harness/"* \
  "$ACERVO/global/tools/harness/" 2>/dev/null || true
chmod +x "$ACERVO/global/tools/harness/"*.py 2>/dev/null || true

# Codex wrappers (EX-33)
mkdir -p "$HERMES_HOME/scripts/codex_learning"
mkdir -p "$HERMES_HOME/codex-learning"/{runs,events,reviews}
cp -r "$SCRIPT_DIR/scripts/codex_learning/"* \
  "$HERMES_HOME/scripts/codex_learning/" 2>/dev/null || true
```

### Verificação
```bash
echo "Acervo total: $(find "$ACERVO" -type f | wc -l) arquivos"
test -f "$ACERVO/micro/exocortex-ops/microverso.yaml" \
  && echo "✓ exocortex-ops seed" || echo "✗ exocortex-ops MISSING"
```

---

## Step 05 — Instalar Profiles e Bundles

**Objetivo**: Copiar os profiles (default, manut, chat) e o bundle manifest.

### Execução

```bash
cp -r "$PROFILES_SRC/"* "$PROFILES_DST/" 2>/dev/null || true
cp -r "$BUNDLES_SRC/"* "$BUNDLES_DST/" 2>/dev/null || true
```

### Verificação
```bash
test -f "$PROFILES_DST/manut/profile.yaml" \
  && echo "✓ profile manut" || echo "✗ profile manut MISSING"
test -f "$BUNDLES_DST/exocortex-alpha.yaml" \
  && echo "✓ bundle manifest" || echo "✗ bundle MISSING"
```

---

## Step 05b — Compilar SOUL.md

**Objetivo**: Compilar as regras comportamentais de todas as skills em SOUL.md.

### Execução

```bash
python3 "$SCRIPT_DIR/scripts/compile_soul.py" \
  --skills-dir "$HERMES_HOME/skills/excrtx" \
  --soul "$HERMES_HOME/SOUL.md" 2>&1 \
  || echo "⚠ compile_soul.py falhou — SOUL.md pode estar desatualizado"
```

### Verificação
```bash
test -f "$HERMES_HOME/SOUL.md" \
  && echo "✓ SOUL.md ($(wc -l < "$HERMES_HOME/SOUL.md") linhas)" \
  || echo "✗ SOUL.md MISSING"
```

---

## Step 06 — Hardening

**Objetivo**: Aplicar patches de segurança e baselines.

### 6a. Patch do Google Drive Search (paginação + trashed filter)

```bash
GAPI="$HERMES_HOME/skills/productivity/google-workspace/scripts/google_api.py"
if [ -f "$GAPI" ]; then
  # O patch é complexo — executar via step script
  bash "$SCRIPT_DIR/setup/step-06-hardening.sh"
else
  echo "ℹ google_api.py não presente — patch pulado (harmless)"
fi
```

### 6b. Remover skill de email legada

```bash
rm -rf "$HERMES_HOME/skills/email/himalaya" 2>/dev/null || true
rm -rf "$HERMES_HOME/skills/email/hymalaia" 2>/dev/null || true
```

### 6c. Remover MCP composio

```bash
if command -v hermes >/dev/null 2>&1; then
  if hermes mcp list 2>/dev/null | grep -q "composio"; then
    printf 'y\n' | hermes mcp remove composio >/dev/null 2>&1
    echo "✓ composio removido"
  fi
fi
```

---

## Step 06b — Google Auth (Drive/Workspace)

**Objetivo**: Instalar dependências OAuth e verificar credenciais Google.

### Execução

```bash
# Instalar dependências Python
pip3 install -q google-auth-oauthlib google-api-python-client google-auth-httplib2

# Instalar gcloud CLI (se necessário)
# O step-06b instala automaticamente em $HOME/.local/google-cloud-sdk
bash "$SCRIPT_DIR/setup/step-06b-google-auth.sh"
```

### Verificação
```bash
# OAuth token
test -f "$HERMES_HOME/google_token.json" \
  && echo "✓ OAuth token presente" \
  || echo "⚠ OAuth token ausente (configurar manualmente)"

# gcloud ADC
test -f "$HOME/.config/gcloud/application_default_credentials.json" \
  && echo "✓ gcloud ADC presente" \
  || echo "ℹ gcloud ADC ausente (opcional)"
```

### Se credenciais pendentes
O script cria um reminder em `$HERMES_HOME/reminders/google-drive-oauth-setup.md` com instruções detalhadas.

---

## Step 07 — Instalar Identidade (SOUL_SEED → SOUL.md)

**Objetivo**: Copiar o SOUL_SEED.md para SOUL.md e instalar branding.

### Execução

```bash
cp "$SCRIPT_DIR/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"

# Branding (logo)
BRANDING="$ACERVO/global/branding"
test -f "$BRANDING/exocortex-ascii-logo.txt" && \
  cp "$BRANDING/exocortex-ascii-logo.txt" "$HERMES_HOME/"
test -f "$BRANDING/exocortex-logo.sh" && \
  cp "$BRANDING/exocortex-logo.sh" "$HERMES_HOME/" && \
  chmod +x "$HERMES_HOME/exocortex-logo.sh"
```

---

## Step 08 — Integração DocBrain

**Objetivo**: Clonar e compilar o parser DocBrain.

### Pré-condição
- `git` e `npm` disponíveis

### Execução

```bash
DOCBRAIN_DIR="${EXOCORTEX_DOCBRAIN_DIR:-$EXOCORTEX_HOME/tools/docbrain}"
REPO="https://github.com/ProjetoBB/docBrainBB.git"

mkdir -p "$(dirname "$DOCBRAIN_DIR")"
if [ ! -d "$DOCBRAIN_DIR/.git" ]; then
  git clone "$REPO" "$DOCBRAIN_DIR"
fi
cd "$DOCBRAIN_DIR"
git pull --ff-only origin main 2>/dev/null || true
npm install 2>/dev/null || true
npm run build 2>/dev/null || true
```

### Verificação
```bash
test -d "$DOCBRAIN_DIR/node_modules" \
  && echo "✓ DocBrain instalado" || echo "⚠ DocBrain sem node_modules"
```

---

## Step 09 — Integração NotebookLM

**Objetivo**: Instalar `nlm` CLI e registrar MCP server.

### Execução

```bash
# Instalar nlm via uv (preferido) ou pip (fallback)
if command -v uv >/dev/null 2>&1; then
  uv tool install notebooklm-mcp-cli --force 2>/dev/null
else
  python3 -m pip install --upgrade --quiet notebooklm-mcp-cli
fi

# Verificar auth
nlm login --check 2>/dev/null && echo "✓ nlm autenticado" || echo "⚠ Executar: nlm login"

# Registrar MCP server
if command -v hermes >/dev/null 2>&1 && command -v notebooklm-mcp >/dev/null 2>&1; then
  if ! hermes mcp list 2>/dev/null | grep -q "notebooklm"; then
    printf 'y\n' | hermes mcp add notebooklm --command notebooklm-mcp 2>/dev/null
  fi
fi
```

---

## Step 10 — Browser Automation

**Objetivo**: Provisionar runtime local com `browser-use` e Chromium.

### Execução

```bash
# O provisionamento é automático no primeiro uso do wrapper:
WRAPPER="$SKILLS_DST/excrtx-integrate-browser/scripts/browser-use.sh"
if [ -x "$WRAPPER" ]; then
  echo "✓ Browser wrapper presente"
  echo "ℹ Chromium será baixado no primeiro uso"
else
  echo "⚠ Browser wrapper não encontrado"
fi
```

Para provisionar antecipadamente:
```bash
bash "$SCRIPT_DIR/setup/step-10-integration-browser.sh"
```

---

## Step 10b — Hermes WebUI (Opcional)

**Objetivo**: Instalar o cockpit web. **Só executa se `EXOCORTEX_ENABLE_HERMES_WEBUI=1`.**

### Execução (pular se WebUI não ativado)

```bash
if [ "${EXOCORTEX_ENABLE_HERMES_WEBUI:-0}" = "1" ]; then
  bash "$SCRIPT_DIR/provision/hermes-webui/scripts/install.sh"
  echo "⚠ WebUI instalado mas NÃO inicia automaticamente"
  echo "  Iniciar: cd ~/.hermes/hermes-webui && ./ctl.sh start"
fi
```

---

## Step 10c — Provisionar Workspace do Acervo na WebUI (Opcional)

**Objetivo**: Registrar o Acervo como o espaço **"Acervo Cognitivo"** dentro da WebUI do Hermes. Só faz sentido se o Step 10b instalou a WebUI. Idempotente — não duplica o registro se já existir.

### Execução (pular se WebUI não ativado)

```bash
bash "$SCRIPT_DIR/setup/step-10c-provision-acervo-workspace.sh"
```

---

## Step 11 — Context7 MCP

**Objetivo**: Registrar o MCP server Context7 (documentação de tech stacks).

### Execução

```bash
if command -v hermes >/dev/null 2>&1; then
  if ! hermes mcp list 2>/dev/null | grep -q "context7"; then
    if [ -n "${CONTEXT7_API_KEY:-}" ]; then
      printf 'y\n' | hermes mcp add context7 \
        --command "npx -y @context7/mcp" \
        --env "CONTEXT7_API_KEY=${CONTEXT7_API_KEY}" 2>/dev/null
      echo "✓ Context7 MCP adicionado"
    else
      echo "ℹ CONTEXT7_API_KEY não definida — Context7 pode ser adicionado depois"
    fi
  else
    echo "✓ Context7 MCP já configurado"
  fi
fi
```

---

## Step 11b — Acervo MCP

**Objetivo**: Registrar o MCP semântico local do Acervo e validar saúde do control plane agentic.

### Execução

```bash
bash "$SCRIPT_DIR/setup/step-11b-integration-acervo-mcp.sh"
```

### O que este step faz

1. roda `python3 scripts/acervo_mcp_server.py --self-test --acervo-root "$ACERVO"`
2. registra `acervo` via `hermes mcp add` com `python3` + `scripts/acervo_mcp_server.py`
3. reconcilia `config.yaml` para fixar `ACERVO`, `EXOCORTEX_HOME` e `HERMES_HOME`
4. executa `hermes mcp test acervo`
5. se falhar, grava reminder em `$HERMES_HOME/reminders/acervo-mcp.md`

### Modo degradado

Se o MCP não ficar saudável, a operação continua com:
- `python3 scripts/acervoctl.py` como superfície local oficial
- acesso direto a arquivos para humano, infra e manutenção

---

## Step 12 — Verificação de Keys

**Objetivo**: Verificar se as chaves de API estão configuradas e criar reminders para pendentes.

### Execução

```bash
bash "$SCRIPT_DIR/setup/step-12-verify-keys.sh"
```

> **Papéis LLM e config.** Este step faz um **ping real (1 chamada) por papel**
> (default, vision, auxiliar) e grava o `$HERMES_HOME/config.yaml` a partir do papel
> **default** (`EXOCORTEX_DEFAULT_{PROVIDER,MODEL,API_KEY,BASE_URL}`). Inspecione o estado
> resolvido com `python3 scripts/lib/llm_roles.py all`. Para reconfigurar o modelo use `hermes model`.
>
> **Contingência `--imbroke`.** Rodar `bash setup.sh --imbroke` (ou exportar `IMBROKE_MODE=1`) ativa o roteador OpenRouter free (`configure_openrouter_free_router`): gera um ranking de modelos gratuitos e, com a key OpenRouter presente, aplica um circuit breaker (sentinela + watchdog cron). Por padrão essa contingência fica **desativada**.

### Verificação Manual

| Key | Status | Ação se pendente |
|-----|--------|------------------|
| Papel **default** | `test -n "${EXOCORTEX_DEFAULT_API_KEY:-}"` | Obrigatório — configurar via `bash setup.sh` ou `.env.local` |
| Papéis vision/aux | `python3 scripts/lib/llm_roles.py all` | Vazio = herda o default (OK). Preencher só se quiser provider distinto |
| `FIRECRAWL_BASE_URL` | `printf '%s\n' "${FIRECRAWL_BASE_URL:-http://127.0.0.1:3002}"` | Para Firecrawl local, usar porta 3002 |
| `TELEGRAM_BOT_TOKEN` | `test -n "${TELEGRAM_BOT_TOKEN:-}"` | Criar bot em @BotFather |
| Google Credentials | `test -f "$HOME/.config/gcloud/application_default_credentials.json"` | `gcloud auth application-default login` |

---

## Step 13 — Verificação Final

**Objetivo**: Validar que todos os componentes foram instalados corretamente.

### Execução

```bash
bash "$SCRIPT_DIR/setup/step-13-final-verification.sh"
```

### Critérios de Sucesso (o script verifica tudo automaticamente)

1. **≥ 50 skills excrtx-*** instaladas em `$SKILLS_DST`
2. **4 camadas** do Acervo presentes (macro, global, micro, shared)
3. **5 diretórios operacionais** v0.4 (_tasks, _routines, _automations, _inbox, _artifacts)
4. **Microverso exocortex-ops** com todos os arquivos esperados
5. **Profile manut** presente
6. **Bundle exocortex-alpha.yaml** presente
7. **SOUL.md** presente
8. **hermes CLI** disponível no PATH
9. **Acervo MCP** presente, auto-registrado e saudável (`self-test` + `hermes mcp test acervo`)

### Resultado
- `0 erros` → ✅ Instalação completa
- `N erros` → ⚠ Investigar items faltantes

---

## Step 14 — Pós-provisionamento

**Objetivo**: Executar verificações pós-provisionamento.

```bash
bash "$SCRIPT_DIR/scripts/post-provisioning-verify.sh" 2>/dev/null || true
```

---

## Step 15 — Calibração (Opcional)

**Objetivo**: Calibrar comportamento do LLM via prompts interativos.

### Pré-condição
- Flag `--calibrate` passada

### Execução (pular se não for calibrar)

```bash
bash "$SCRIPT_DIR/scripts/calibrate-hermes.sh"
```

---

## Step 16 — Skin EXCRTX no WebUI (Opcional)

**Objetivo**: Aplicar identidade visual Exocórtex no Hermes WebUI.

### Pré-condição
- WebUI instalado em `$HERMES_HOME/hermes-webui`

### Execução

```bash
if [ -d "$HERMES_HOME/hermes-webui" ]; then
  python3 "$SCRIPT_DIR/setup/provision/scripts/provision-excrtx-skin.py"
fi
```

---

## Step 17 — Cron Jobs de Manutenção

**Objetivo**: Agendar rotinas automáticas de zeladoria (síndico).

### Pré-condição
- `hermes` CLI disponível com suporte a `hermes cron`

### Execução

```bash
bash "$SCRIPT_DIR/setup/step-17-maintenance-crons.sh"
```

### Crons Criados

| Nome | Schedule | Descrição |
|------|----------|-----------|
| `maintenance-weekly` | `0 3 * * 0` | Manutenção completa semanal (domingos 03h) |
| `inbox-triage` | `30 3 * * 1` | Triagem de inbox (segundas 03h30) |
| `artifact-audit` | `0 4 1,15 * *` | Auditoria de artefatos (quinzenal 04h) |
| `publication-check` | `30 4 * * *` | Verificação de publicações pendentes (diário 04h30) |

---

## Verificação Final Completa

Após todos os steps, execute esta checklist de verificação:

```bash
echo "=== Exocórtex Release Verification ==="

# 1. Skills
SKILL_COUNT=$(find "$SKILLS_DST" -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "Skills: $SKILL_COUNT (esperado: ≥ 50 excrtx-*)"

# 2. Acervo
for layer in macro global micro shared; do
  test -d "$ACERVO/$layer" && echo "✓ $layer" || echo "✗ $layer"
done

# 3. SOUL
test -f "$HERMES_HOME/SOUL.md" && echo "✓ SOUL.md" || echo "✗ SOUL.md"

# 4. Bundle
test -f "$BUNDLES_DST/exocortex-alpha.yaml" && echo "✓ Bundle" || echo "✗ Bundle"

# 5. Profile
test -f "$PROFILES_DST/manut/profile.yaml" && echo "✓ Profile manut" || echo "✗ Profile manut"

# 6. Hermes CLI
command -v hermes >/dev/null && echo "✓ hermes $(hermes --version 2>/dev/null | head -1)" || echo "✗ hermes"

# 7. Acervo MCP
python3 "$SCRIPT_DIR/scripts/acervo_mcp_server.py" --self-test --acervo-root "$ACERVO" >/dev/null && echo "✓ acervo mcp self-test" || echo "✗ acervo mcp self-test"
hermes mcp list 2>/dev/null | grep -Eq '^[[:space:]]*acervo[[:space:]]' && echo "✓ acervo registrado" || echo "✗ acervo não registrado"
hermes mcp test acervo >/dev/null 2>&1 && echo "✓ acervo health check" || echo "✗ acervo health check"

echo ""
echo "Paths:"
echo "  HERMES_HOME:    $HERMES_HOME"
echo "  EXOCORTEX_HOME: $EXOCORTEX_HOME"
echo "  ACERVO:         $ACERVO"
echo ""
echo "Próximos passos:"
echo "  hermes              # sessão interativa"
echo "  hermes -p manut     # modo manutenção"
```

---

## Troubleshooting

### "hermes CLI not found"
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Skills faltando após instalação
```bash
# Re-executar apenas o step de skills:
bash setup/step-03-install-skills.sh
```

### SOUL.md vazio ou desatualizado
```bash
python3 scripts/compile_soul.py \
  --skills-dir "$HERMES_HOME/skills/excrtx" \
  --soul "$HERMES_HOME/SOUL.md"
```

### Verificar integridade do acervo exocortex-ops
```bash
for f in microverso.yaml _meta/SCHEMA.md _meta/index.md contracts/operating-boundaries.md; do
  test -f "$ACERVO/micro/exocortex-ops/$f" \
    && echo "✓ $f" || echo "✗ $f MISSING"
done
```

### Rodar suite de testes completa
```bash
python3 -m pytest tests/ -v --tb=short
bash scripts/validate-environment.sh
```
