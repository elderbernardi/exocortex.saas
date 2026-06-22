#!/usr/bin/env bash
# =============================================================================
# Step 12: Verificação de keys + OpenRouter + Telegram + Google credentials
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

configure_openrouter_free_router() {
  local router_script="$SCRIPT_DIR/scripts/openrouter_free_model_router.py"
  local report_path="$HERMES_HOME/model-routing/openrouter-free-models.json"

  if [ ! -f "$router_script" ]; then
    warn "Roteador OpenRouter free não encontrado: $router_script"
    return 0
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    warn "python3 não encontrado; pulando roteador OpenRouter free"
    return 0
  fi

  # A contingência --imbroke precisa de uma credencial OpenRouter (sk-or-…).
  # O roteador a busca nos papéis LLM (qualquer papel com provider openrouter)
  # ou nas vars legadas. Aqui só decidimos se há como APLICAR (precisa de chave)
  # ou apenas RANQUEAR.
  exocortex_resolve_role default
  _imbroke_key="${OPENROUTER_API_KEY:-}"
  case "$ROLE_API_KEY" in sk-or-*) _imbroke_key="$ROLE_API_KEY" ;; esac
  if [ -z "$_imbroke_key" ]; then
    info "Sem credencial OpenRouter (sk-or-…) nos papéis/legado; gerando ranking de contingência sem aplicar provider/model"
    if python3 "$router_script" --imbroke --report-path "$report_path" --format text >/dev/null 2>&1; then
      log "Ranking OpenRouter free gerado em $report_path"
    else
      warn "Falha ao gerar ranking OpenRouter free"
    fi
    return 0
  fi

  if ! command -v hermes >/dev/null 2>&1; then
    warn "hermes CLI não encontrado; roteador OpenRouter free não pode aplicar config"
    return 0
  fi

  # Use --activate for full circuit breaker setup (sentinel + watchdog cron)
  if python3 "$router_script" --imbroke --activate --report-path "$report_path" --format text >/dev/null 2>&1; then
    log "Roteador OpenRouter free ativado com circuit breaker; relatório em $report_path"
  else
    # Fallback to legacy --apply if --activate fails (e.g., hermes cron unavailable)
    warn "Falha no --activate; tentando --apply legado"
    if python3 "$router_script" --imbroke --apply --report-path "$report_path" --format text >/dev/null 2>&1; then
      log "Roteador OpenRouter free aplicado (modo legado); relatório em $report_path"
    else
      warn "Falha ao configurar roteador OpenRouter free"
    fi
  fi
}

# ─── Provedores LLM (3 papéis) ───────────────────────────────────────────────
# Fonte única: EXOCORTEX_{DEFAULT,VISION,AUX}_*. vision/aux herdam o default.
# Resolução, herança e catálogo de providers vivem em scripts/lib/llm_roles.py
# (via setup/lib/llm-roles.sh). Aqui: resolver → reportar → PING real → gravar
# config.yaml a partir do papel 'default'.

source "$(dirname "${BASH_SOURCE[0]}")/lib/llm-roles.sh"

info "Verificando provedores LLM (papéis default / vision / auxiliar)..."

# Mascara uma chave para exibição.
_mask_key() { local v="$1"; [ -z "$v" ] && { echo "(vazia)"; return; }; [ "${#v}" -le 8 ] && { echo "****"; return; }; echo "${v:0:4}...${v: -4}"; }

# Reporta + (opcionalmente) faz ping de um papel. $1=papel $2=rótulo $3=obrigatório
verify_role() {
  local role="$1" label="$2" required="${3:-0}"
  exocortex_resolve_role "$role"
  if [ "$ROLE_USABLE" != "1" ]; then
    if [ "$required" = "1" ]; then
      warn "Papel '$label' NÃO configurado (provider=$ROLE_PROVIDER model=$ROLE_MODEL key=$(_mask_key "$ROLE_API_KEY"))."
      warn "  Configure EXOCORTEX_DEFAULT_* no .env.local — é o papel obrigatório. Rode: bash setup.sh"
    else
      info "Papel '$label' não configurado — herdará o 'default' em runtime."
    fi
    return 0
  fi

  # F-030: model ids com maiúsculas costumam ser rejeitados por gateways.
  if [ "$ROLE_MODEL" != "$(printf '%s' "$ROLE_MODEL" | tr '[:upper:]' '[:lower:]')" ]; then
    warn "model '$ROLE_MODEL' ($label) tem maiúsculas — muitos gateways rejeitam (ex.: minimax-m3)."
  fi

  log "Papel '$label': provider=$ROLE_PROVIDER model=$ROLE_MODEL key=$(_mask_key "$ROLE_API_KEY")"
  info "  endpoint: $ROLE_CHAT_URL"

  # PING real (1 chamada) — pula em modo não-interativo (--yes/CI) ou EXOCORTEX_NO_PING=1.
  if [ "${INTERACTIVE_MODE:-1}" = "1" ] && [ "${EXOCORTEX_NO_PING:-0}" != "1" ]; then
    info "  testando conexão (ping)..."
    if exocortex_ping_role "$role"; then
      log "  ✓ ping OK (HTTP $PING_STATUS) — chave+modelo+endpoint válidos"
    else
      case "$PING_STATUS" in
        401|403) warn "  ✗ ping HTTP $PING_STATUS — chave de API inválida/sem permissão para '$label'." ;;
        404)     warn "  ✗ ping HTTP $PING_STATUS — modelo '$ROLE_MODEL' ou endpoint não encontrado. Confira o id do modelo." ;;
        400)     warn "  ✗ ping HTTP $PING_STATUS — requisição rejeitada (modelo '$ROLE_MODEL' provavelmente inválido para este provider)." ;;
        no-curl) info "  curl ausente; ping pulado." ;;
        000)     warn "  ✗ sem resposta do endpoint $ROLE_CHAT_URL (rede/URL). Verifique provider/base_url." ;;
        *)       warn "  ✗ ping HTTP $PING_STATUS para '$label' (provider=$ROLE_PROVIDER model=$ROLE_MODEL)." ;;
      esac
      warn "  Ajuste EXOCORTEX_$(printf '%s' "$role" | tr '[:lower:]' '[:upper:]')_* no .env.local e rode novamente."
    fi
  fi
}

verify_role default  "default"   1
verify_role vision   "vision"    0
verify_role aux      "auxiliar"  0

# ─── Gravar config.yaml a partir do papel 'default' ──────────────────────────
# O runtime Hermes lê model.provider/default/base_url de $HERMES_HOME/config.yaml.
# Em vez de só inspecionar, projetamos o papel 'default' nele (fonte única).
exocortex_resolve_role default
if [ "$ROLE_USABLE" = "1" ]; then
  if command -v hermes >/dev/null 2>&1; then
    hermes config set model.provider "$ROLE_PROVIDER" >/dev/null 2>&1 || true
    hermes config set model.default  "$ROLE_MODEL"    >/dev/null 2>&1 || true
    hermes config set model.base_url "$ROLE_BASE_URL" >/dev/null 2>&1 || true
    log "config.yaml sincronizado com o papel 'default' (provider=$ROLE_PROVIDER model=$ROLE_MODEL)"
  elif command -v python3 >/dev/null 2>&1; then
    HERMES_CONFIG="$HERMES_HOME/config.yaml" python3 - "$ROLE_PROVIDER" "$ROLE_MODEL" "$ROLE_BASE_URL" <<'PY' || true
import os, sys
try:
    import yaml
    path = os.environ["HERMES_CONFIG"]
    cfg = {}
    if os.path.exists(path):
        with open(path) as f:
            cfg = yaml.safe_load(f) or {}
    model = cfg.get("model", {}) or {}
    model["provider"], model["default"], model["base_url"] = sys.argv[1], sys.argv[2], sys.argv[3]
    cfg["model"] = model
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)
    print("ok")
except Exception as e:
    print(f"skip: {e}", file=sys.stderr)
PY
    log "config.yaml gravado a partir do papel 'default' (provider=$ROLE_PROVIDER model=$ROLE_MODEL)"
  fi
fi

# Serviços não-LLM verificados abaixo.
if [ -n "${CONTEXT7_API_KEY:-}" ]; then
  log "CONTEXT7_API_KEY definida"
else
  info "CONTEXT7_API_KEY não definida (opcional — context7 pode ser adicionado depois)"
fi
if [ -n "${FIRECRAWL_API_KEY:-}" ]; then
  log "FIRECRAWL_API_KEY definida"
  info "FIRECRAWL_BASE_URL efetiva: ${FIRECRAWL_BASE_URL:-http://127.0.0.1:3002}"
else
  info "FIRECRAWL_API_KEY não definida (opcional — crawling/extract pode ser adicionado depois)"
  info "Se você subir Firecrawl localmente, use por default: ${FIRECRAWL_BASE_URL:-http://127.0.0.1:3002}"
fi

# ─── last30days skill keys ───────────────────────────────────────────────────

info "Verificando keys para last30days (pesquisa multi-plataforma)..."
# Reasoning do last30days vem do papel 'default' (provider openrouter/gemini/
# openai/xai); vision do papel 'vision'. Ver setup/lib/llm-roles.sh.
exocortex_resolve_role default
if [ "$ROLE_USABLE" = "1" ]; then
  log "Reasoning do last30days via papel 'default' (provider=$ROLE_PROVIDER)"
else
  info "Papel 'default' não configurado — last30days usará fallback determinístico para planejamento"
fi
if [ -n "${XAI_API_KEY:-}" ]; then
  log "XAI_API_KEY definida — last30days X/Twitter ativado"
else
  info "XAI_API_KEY não definida (opcional — X/Twitter desabilitado no last30days)"
fi
if [ -n "${BRAVE_API_KEY:-}" ]; then
  log "BRAVE_API_KEY definida — last30days web search ativado"
else
  info "BRAVE_API_KEY não definida (opcional — auto-resolve desabilitado no last30days)"
fi
if [ -n "${SCRAPECREATORS_API_KEY:-}" ]; then
  log "SCRAPECREATORS_API_KEY definida — last30days TikTok/Instagram/Threads/Pinterest ativados"
else
  info "SCRAPECREATORS_API_KEY não definida (opcional — fontes sociais visuais desabilitadas)"
fi
if [ -n "${BSKY_HANDLE:-}" ] && [ -n "${BSKY_APP_PASSWORD:-}" ]; then
  log "BSKY_HANDLE+BSKY_APP_PASSWORD definidos — last30days Bluesky ativado"
else
  info "BSKY_HANDLE/BSKY_APP_PASSWORD não definidos (opcional — Bluesky desabilitado no last30days)"
fi

# ─── OpenRouter Free Router ─────────────────────────────────────────────────

if [ "$IMBROKE_MODE" = "1" ]; then
  info "Modo --imbroke ativo: configurando roteador OpenRouter free..."
  configure_openrouter_free_router
else
  info "Modo OpenRouter free desativado por default; use --imbroke para acionar a contingência"
fi

# ─── Telegram ────────────────────────────────────────────────────────────────

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

# ─── Google Credentials ─────────────────────────────────────────────────────

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
