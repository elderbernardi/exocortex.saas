#!/usr/bin/env bash
# =============================================================================
# Step 06b: Google Auth — Provisionamento de credenciais Google Drive/Workspace
# =============================================================================
#
# O google_api.py do Hermes usa exclusivamente OAuth 2.0 (google_token.json).
# Este step garante que o runtime de auth esteja instalado e orienta sobre
# credenciais pendentes.
#
# Fluxo:
#   1. Verificar se a skill Google Workspace existe
#   2. Instalar dependências Python (google-auth-oauthlib, etc.)
#   3. Instalar gcloud CLI (user-space, sem root)
#   4. Verificar OAuth token (google_token.json)
#   5. Verificar gcloud ADC como alternativa
#   6. Se nada disponível: guiar o usuário com instruções completas
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

# ─── Constants ───────────────────────────────────────────────────────────────

GCLOUD_INSTALL_DIR="$HOME/.local/google-cloud-sdk"
GCLOUD_BIN="$GCLOUD_INSTALL_DIR/bin/gcloud"
OAUTH_TOKEN="$HERMES_HOME/google_token.json"
OAUTH_CLIENT_SECRET="$HERMES_HOME/google_client_secret.json"
ADC_FILE="$HOME/.config/gcloud/application_default_credentials.json"
GWS_SKILL_DIR="$HERMES_HOME/skills/productivity/google-workspace"
GWS_SCRIPTS="$GWS_SKILL_DIR/scripts"
SETUP_PY="$GWS_SCRIPTS/setup.py"

# ─── Helpers ─────────────────────────────────────────────────────────────────

# Check that the Google Workspace skill exists (comes from Hermes core)
_check_gws_skill() {
  if [ -d "$GWS_SKILL_DIR" ] && [ -f "$SETUP_PY" ]; then
    log "Google Workspace skill presente"
    return 0
  fi
  warn "Google Workspace skill não encontrada em $GWS_SKILL_DIR"
  warn "Esta skill é fornecida pelo Hermes Agent. Execute 'hermes skills install' ou reinstale o Hermes."
  return 1
}

# Install Python dependencies for OAuth flow
_install_gws_deps() {
  local pkgs=("google-auth-oauthlib" "google-api-python-client" "google-auth-httplib2")
  local missing=()

  for pkg in "${pkgs[@]}"; do
    if ! python3 -c "import ${pkg//-/_}" 2>/dev/null; then
      missing+=("$pkg")
    fi
  done

  if [ ${#missing[@]} -eq 0 ]; then
    log "Dependências Python do Google Workspace já instaladas"
    return 0
  fi

  info "Instalando dependências Python: ${missing[*]}..."
  if python3 -m pip install --quiet "${missing[@]}" 2>/dev/null; then
    log "Dependências Python instaladas"
    return 0
  fi

  warn "Falha ao instalar dependências Python do Google Workspace"
  return 1
}

_install_gcloud() {
  if [ -x "$GCLOUD_BIN" ]; then
    log "gcloud CLI disponível: $GCLOUD_BIN"
    return 0
  fi

  if command -v gcloud >/dev/null 2>&1; then
    log "gcloud CLI disponível no PATH: $(command -v gcloud)"
    return 0
  fi

  # Ubuntu/Debian: try snap
  if command -v snap >/dev/null 2>&1; then
    info "Instalando gcloud via snap (Ubuntu/Debian)..."
    if sudo snap install google-cloud-cli --classic 2>/dev/null; then
      log "gcloud instalado via snap"
      return 0
    fi
    warn "snap install falhou, tentando método user-space..."
  fi

  # Arch: try pacman
  if command -v pacman >/dev/null 2>&1; then
    if sudo pacman -S --noconfirm google-cloud-sdk 2>/dev/null; then
      log "gcloud instalado via pacman"
      return 0
    fi
    warn "pacman install falhou ou requer intervenção, tentando user-space..."
  fi

  # User-space install (all distros): download tar.gz
  if [ ! -d "$GCLOUD_INSTALL_DIR" ]; then
    info "Instalando gcloud CLI (user-space, sem root)..."
    local tmpdir
    tmpdir=$(mktemp -d)
    local tarball="$tmpdir/google-cloud-cli.tar.gz"

    if command -v curl >/dev/null 2>&1; then
      curl -sL -o "$tarball" \
        "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz" || {
        warn "Falha ao baixar gcloud CLI"
        rm -rf "$tmpdir"
        return 1
      }
    elif command -v wget >/dev/null 2>&1; then
      wget -q -O "$tarball" \
        "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz" || {
        warn "Falha ao baixar gcloud CLI"
        rm -rf "$tmpdir"
        return 1
      }
    else
      warn "curl/wget não disponível — necessário para baixar gcloud CLI"
      rm -rf "$tmpdir"
      return 1
    fi

    mkdir -p "$GCLOUD_INSTALL_DIR"
    tar -xzf "$tarball" -C "$GCLOUD_INSTALL_DIR" --strip-components=1 || {
      warn "Falha ao extrair gcloud CLI"
      rm -rf "$tmpdir"
      return 1
    }

    "$GCLOUD_INSTALL_DIR/install.sh" --quiet --path-update=false 2>/dev/null || true
    rm -rf "$tmpdir"
  fi

  if [ -x "$GCLOUD_BIN" ]; then
    log "gcloud CLI instalado em $GCLOUD_BIN"
    return 0
  fi

  warn "Não foi possível instalar gcloud CLI"
  return 1
}

# Check OAuth token (what google_api.py actually uses)
_check_oauth_token() {
  if [ ! -f "$OAUTH_TOKEN" ]; then
    return 1
  fi

  # Validate with setup.py --check
  if [ -f "$SETUP_PY" ]; then
    if python3 "$SETUP_PY" --check >/dev/null 2>&1; then
      return 0
    fi
    warn "OAuth token existe mas setup.py --check falhou (token expirado ou inválido)"
    return 1
  fi

  # Fallback: just check file exists
  return 0
}

# Check gcloud ADC
_check_gcloud_adc() {
  if [ -f "$ADC_FILE" ]; then
    return 0
  fi
  if [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ] && [ -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
    return 0
  fi
  return 1
}

# Generate reminder with COMPLETE step-by-step for a new user
_write_oauth_reminder() {
  mkdir -p "$HERMES_HOME/reminders"
  cat > "$HERMES_HOME/reminders/google-drive-oauth-setup.md" <<'EOF'
# Google Drive OAuth Setup — Guia Completo

O `google_api.py` do Hermes requer autenticação OAuth 2.0 para operar
com Google Drive, Gmail, Calendar e outros serviços Google.

## Visão geral

Você precisa de 3 coisas:
1. Um `client_secret.json` (obtido no Google Cloud Console)
2. Um `google_token.json` (gerado pelo fluxo OAuth)
3. A Google Drive API habilitada no seu projeto GCP

---

## Passo a passo

### 1. Criar projeto no Google Cloud Console

Acesse: https://console.cloud.google.com/

- Crie um projeto (ou selecione um existente)
- Anote o nome do projeto

### 2. Habilitar a Google Drive API

- No menu esquerdo: APIs & Services > Library
- Busque por "Google Drive API"
- Clique em "Enable"

### 3. Criar credencial OAuth

- APIs & Services > Credentials > Create Credentials > OAuth client ID
- Application type: "Desktop application"
- Nome: "Exocortex Hermes" (ou o que preferir)
- Clique em "Create"
- Baixe o JSON — este é seu `client_secret.json`

### 4. Configurar a tela de consentimento (se for primeiro uso)

- APIs & Services > OAuth consent screen
- User Type: "External" (ou "Internal" se for conta Google Workspace)
- Preencha: nome do app, email de suporte, email de desenvolvedor
- Adicione o escopo: `.../auth/drive` (sensível)
- Adicione seu email como usuário de teste
- Publique o app

### 5. Executar o fluxo OAuth no terminal

Com o `client_secret.json` em mãos, execute na ordem:

```bash
# A. Registrar o client secret
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py \
  --client-secret /caminho/ate/seu/client_secret.json

# B. Gerar a URL de autorização
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py \
  --auth-url

# C. Abrir a URL no navegador, fazer login Google, autorizar
#    Ao final, você será redirecionado para localhost — copie o
#    parâmetro "code" da URL (tudo depois de "code=" até o "&" seguinte)

# D. Trocar o código pelo token
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py \
  --auth-code "COLOQUE_O_CODIGO_AQUI"

# E. Verificar
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py \
  --check
```

Se o último comando retornar `AUTHENTICATED`, está pronto.

---

## Solução de problemas

### "Not authenticated. Run the setup script first"

Você pulou o fluxo OAuth. Execute os passos 5A a 5E acima.

### "accessNotConfigured" ou erro 403

A Google Drive API não está habilitada no projeto GCP.
Volte ao passo 2 e clique em "Enable".

### "Token is invalid. Re-run setup"

O token expirou ou foi revogado. Delete `~/.hermes/google_token.json`
e refaça os passos 5A a 5E.

### "invalid_grant" ao trocar o código

O código de autorização expira em poucos minutos. Refaça os passos
5B a 5D rapidamente.

---

## Alternativa: gcloud ADC

Se preferir usar Application Default Credentials (não usado pelo
google_api.py diretamente, mas útil para outros scripts Google):

```bash
gcloud auth application-default login
```

Isso criará `~/.config/gcloud/application_default_credentials.json`.

---

## Referência rápida

| Arquivo | Função |
|---|---|
| `google_client_secret.json` | Identidade OAuth do app (do GCP) |
| `google_token.json` | Token de acesso do usuário (gerado localmente) |
| `setup.py --check` | Verifica se o token é válido |
| `google_api.py drive search "..."` | Testa operação real no Drive |
EOF

  warn "Guia completo de OAuth criado em $HERMES_HOME/reminders/google-drive-oauth-setup.md"
}

# Guide user through OAuth flow when client_secret exists but no token
_guide_oauth_flow() {
  info "Client secret encontrado ($OAUTH_CLIENT_SECRET). Finalize o fluxo OAuth:"
  echo ""
  if [ -f "$SETUP_PY" ]; then
    echo "  Execute os comandos abaixo em ordem:"
    echo ""
    echo "  1. Gere a URL de autorização:"
    echo "     python3 $SETUP_PY --auth-url"
    echo ""
    echo "  2. Abra a URL no navegador, faça login Google, autorize"
    echo "     e copie o código da URL de redirecionamento"
    echo ""
    echo "  3. Troque o código pelo token:"
    echo "     python3 $SETUP_PY --auth-code 'CODIGO'"
    echo ""
    echo "  4. Verifique:"
    echo "     python3 $SETUP_PY --check"
  else
    warn "setup.py não encontrado em $SETUP_PY"
  fi
}

# ─── Main ─────────────────────────────────────────────────────────────────────

configure_google_auth() {
  info "Google Auth (Drive/Workspace)..."

  # 0. Prerequisite: Google Workspace skill must exist
  if ! _check_gws_skill; then
    warn "Google Workspace skill ausente — auth Google indisponível até que a skill seja instalada"
    return 0
  fi

  # 1. Install Python deps for OAuth (google-auth-oauthlib, etc.)
  _install_gws_deps || warn "Dependências Python do OAuth não instaladas — o fluxo de autorização pode falhar"

  # 2. Install gcloud CLI (user-space)
  _install_gcloud || warn "gcloud CLI não pôde ser instalado — operações Google Cloud indisponíveis"

  # 3. Check OAuth token (primary auth method for google_api.py)
  local oauth_ok=false
  if _check_oauth_token; then
    oauth_ok=true
    log "OAuth token válido (google_token.json)"
  fi

  # 4. Check gcloud ADC (alternative, not used by google_api.py directly)
  local adc_ok=false
  if _check_gcloud_adc; then
    adc_ok=true
    log "gcloud ADC disponível"
    if ! $oauth_ok; then
      warn "ADC presente, mas google_api.py usa OAuth token, não ADC. Operações via API direta ainda precisam de google_token.json."
    fi
  fi

  # 5. If nothing is available, guide user
  if ! $oauth_ok && ! $adc_ok; then
    warn "Nenhuma credencial Google configurada."

    if [ -f "$OAUTH_CLIENT_SECRET" ]; then
      # Client secret exists but no token — user needs to complete OAuth flow
      _guide_oauth_flow
    else
      # Nothing at all — full setup needed
      _write_oauth_reminder
    fi
  elif $oauth_ok; then
    log "Google Drive auth operacional (OAuth)"
  fi
}

configure_google_auth
