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

  if [ -z "${OPENROUTER_API_KEY:-}" ]; then
    info "OPENROUTER_API_KEY ausente; gerando ranking de contingência sem aplicar provider/model"
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

# ─── API Keys ────────────────────────────────────────────────────────────────

info "Verificando keys de API..."
if [ -n "${OPENROUTER_API_KEY:-}" ]; then
  log "OPENROUTER_API_KEY definida [recomendada]"
else
  warn "OPENROUTER_API_KEY não definida [recomendada] — integrações que exigem essa env var literal podem falhar. Obtenha em openrouter.ai/keys"
fi
if [ -n "${DEEPSEEK_API_KEY:-}" ]; then
  log "DEEPSEEK_API_KEY definida [opcional]"
else
  info "DEEPSEEK_API_KEY não definida [opcional] — DeepSeek direto ficará indisponível; não substitui OPENROUTER_API_KEY por nome"
fi
if [ -n "${OPENROUTER_API_KEY:-}" ] || [ -n "${DEEPSEEK_API_KEY:-}" ]; then
  log "Rota de reasoning remoto disponível para fluxos multiagente / Mixture of Agents"
else
  warn "Nem OPENROUTER_API_KEY nem DEEPSEEK_API_KEY foram definidas — reasoning remoto ficará limitado"
fi
if [ -z "${OPENROUTER_API_KEY:-}" ] && [ -n "${DEEPSEEK_API_KEY:-}" ]; then
  info "DeepSeek direto está disponível, mas componentes que checam OPENROUTER_API_KEY por nome ainda exigirão essa variável."
fi
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

# ─── Modelo LLM canônico (deepseek-v4-pro) ───────────────────────────────────
# Validação não-destrutiva do modelo configurado. O id do modelo vive em
# $HERMES_HOME/config.yaml (escrito pelo runtime Hermes, não pelo Exocórtex), por
# isso aqui apenas inspecionamos e orientamos — nunca reescrevemos o config.
# Resolve F-030 (case errado, ex.: 'MiniMax-M3' rejeitado por gateway que serve
# 'minimax-m3') e F-031 (provider/var de key incompatível).

CANONICAL_MODEL="deepseek-v4-pro"
info "Verificando modelo LLM (canônico/testado: $CANONICAL_MODEL via DEEPSEEK_API_KEY)..."

HERMES_CONFIG="$HERMES_HOME/config.yaml"
if [ -f "$HERMES_CONFIG" ] && command -v python3 >/dev/null 2>&1; then
  eval "$(python3 - "$HERMES_CONFIG" <<'PY' || true
import sys
try:
    import yaml
    cfg = yaml.safe_load(open(sys.argv[1])) or {}
    model = cfg.get("model", {}) or {}
    default_model = str(model.get("default", "") or "")
    provider = str(model.get("provider", "") or "")
    print(f"CFG_MODEL={default_model!r}".replace('"', ''))
    print(f"CFG_PROVIDER={provider!r}".replace('"', ''))
except Exception:
    pass
PY
)"
  CFG_MODEL="${CFG_MODEL:-}"
  CFG_PROVIDER="${CFG_PROVIDER:-}"
  if [ -n "$CFG_MODEL" ]; then
    info "config.yaml: model.default='$CFG_MODEL'${CFG_PROVIDER:+ provider='$CFG_PROVIDER'}"
    # F-030: gateways de model id servem ids minúsculos; um id com maiúsculas é
    # frequentemente rejeitado (ex.: 'MiniMax-M3' vs 'minimax-m3').
    if [ "$CFG_MODEL" != "$(printf '%s' "$CFG_MODEL" | tr '[:upper:]' '[:lower:]')" ]; then
      warn "model.default '$CFG_MODEL' tem letras maiúsculas — muitos gateways rejeitam (ex.: minimax-m3)."
      warn "  Se o agente falhar com 'Model ... is not supported', reconfigure: hermes model"
    fi
    # F-031: provider rotulado mas sem a var de key correspondente.
    if [ -n "$CFG_PROVIDER" ]; then
      PROVIDER_KEY_VAR="$(printf '%s' "$CFG_PROVIDER" | tr '[:lower:]' '[:upper:]')_API_KEY"
      if [ -z "${!PROVIDER_KEY_VAR:-}" ]; then
        info "provider '$CFG_PROVIDER' normalmente exige $PROVIDER_KEY_VAR (não definida)."
        info "  Se o gateway usa outra credencial (ex.: OPENCODE_API_KEY), mapeie: export $PROVIDER_KEY_VAR=\$OPENCODE_API_KEY"
      fi
    fi
  else
    info "config.yaml sem model.default — Hermes usará seu default. Recomendado: $CANONICAL_MODEL."
  fi
else
  info "config.yaml ainda não existe (será criado pelo runtime Hermes)."
  info "  Modelo recomendado/testado: $CANONICAL_MODEL (requer DEEPSEEK_API_KEY). Configure com: hermes model"
fi

if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
  info "Para usar o modelo canônico $CANONICAL_MODEL, defina DEEPSEEK_API_KEY (deepseek.com)."
fi

# ─── last30days skill keys ───────────────────────────────────────────────────

info "Verificando keys para last30days (pesquisa multi-plataforma)..."
if [ -n "${DEEPSEEK_API_KEY:-}" ]; then
  log "DEEPSEEK_API_KEY definida — last30days reasoning ativado"
else
  info "DEEPSEEK_API_KEY não definida (opcional — last30days usará fallback determinístico para planejamento)"
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
