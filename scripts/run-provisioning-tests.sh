#!/usr/bin/env bash
# =============================================================================
# Exocórtex — Harness de Verificação Pós-Provisionamento
# =============================================================================
# Testa cada feature EX-01 a EX-35 numa instância Hermes recém-provisionada.
#
# Uso:
#   bash scripts/run-provisioning-tests.sh [flags]
#
# Flags:
#   --no-repair   Pula Fase 2 (só diagnóstico, sem Hermes headless)
#   --no-issues   Não cria issues no GitHub para falhas definitivas
#   --no-sync     Não sincroniza reparos para o repositório
#   --skip-api    Marca features com API keys ausentes como "pendente"
#   --fast-fail   Aborta se feature gate falhar
#
# Variáveis de ambiente:
#   HERMES_HOME              Default: ~/.hermes
#   EXOCORTEX_HOME           Default: ~/exocortex
#   ACERVO                   Default: $EXOCORTEX_HOME/acervo
#   EXOCORTEX_HARNESS_MODEL  Model for smoke tests (overrides the default role)
#   EXOCORTEX_DEFAULT_MODEL  Fallback model (papel LLM 'default') for smoke tests
#   EXOCORTEX_REPO_PATH      Path do clone local do repo (para sync)
#   EXOCORTEX_SYNC_ENABLED   Default: 1
#
# Ref: GitHub Issue #21
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Parse flags ---
for arg in "$@"; do
  case "$arg" in
    --no-repair) export NO_REPAIR=1 ;;
    --no-issues) export NO_ISSUES=1 ;;
    --no-sync)   export NO_SYNC=1 ;;
    --no-smoke)  export NO_SMOKE=1 ;;
    --skip-api)  export SKIP_API=1 ;;
    --fast-fail) export FAST_FAIL=1 ;;
    --verbose|-v) export VERBOSE=1 ;;
    --help|-h)
      echo "Uso: bash $0 [--no-repair] [--no-issues] [--no-sync] [--no-smoke] [--skip-api] [--fast-fail] [--verbose]"
      exit 0
      ;;
    *) echo "Flag desconhecida: $arg"; exit 1 ;;
  esac
done

# --- Source helpers e registry ---
source "$SCRIPT_DIR/test-helpers.sh"
source "$SCRIPT_DIR/test-registry.sh"

# --- Banner ---
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   Exocórtex — Verificação Pós-Provisionamento║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo -e "  HERMES_HOME:    ${HERMES_HOME}"
echo -e "  EXOCORTEX_HOME: ${EXOCORTEX_HOME}"
echo -e "  ACERVO:         ${ACERVO}"

# --- Resolve harness model ---
if [ -z "$HARNESS_MODEL" ]; then
  if [ -t 0 ]; then
    echo ""
    echo -e "  ${_YELLOW}Qual modelo usar para smoke tests?${_NC}"
    echo -e "  Enter = default do Hermes (config.yaml)"
    echo -e "  Ou digite o model ID (ex: openai/gpt-5.4, deepseek/deepseek-chat, minimax/minimax-m2.5)"
    echo -en "  ${_BOLD}Model:${_NC} "
    read -r user_model
    if [ -n "$user_model" ]; then
      HARNESS_MODEL="$user_model"
    fi
  else
    # Non-interactive: skip smoke tests if no model resolved
    export NO_SMOKE=1
  fi
fi

if [ -n "$HARNESS_MODEL" ]; then
  echo -e "  Modelo:         ${HARNESS_MODEL}"
else
  echo -e "  Modelo:         ${_YELLOW}(Hermes default)${_NC}"
fi
echo -e "  Repair:         $([ "$NO_REPAIR" = "1" ] && echo "desabilitado" || echo "habilitado")"
echo -e "  Smoke tests:    $([ "${NO_SMOKE:-0}" = "1" ] && echo "desabilitado" || echo "habilitado")"
echo -e "  Issues:         $([ "$NO_ISSUES" = "1" ] && echo "desabilitado" || echo "habilitado")"
echo -e "  Sync:           $([ "$NO_SYNC" = "1" ] && echo "desabilitado" || echo "habilitado")"
echo -e "  Skip API:       $([ "$SKIP_API" = "1" ] && echo "sim" || echo "não")"
echo -e "  Verbose:        $([ "${VERBOSE:-0}" = "1" ] && echo "sim" || echo "não")"
echo ""

# --- Pré-verificações ---
if [ ! -d "$HERMES_HOME" ]; then
  echo -e "${_RED}✗ HERMES_HOME não existe: $HERMES_HOME${_NC}"
  exit 1
fi
if [ ! -d "$SKILLS_DST" ]; then
  echo -e "${_RED}✗ Skills dir não existe: $SKILLS_DST${_NC}"
  exit 1
fi

# Resolve hermes binary path
can_invoke_hermes && echo -e "  Hermes CLI:     ${_GREEN}${HERMES_BIN}${_NC}" || echo -e "  Hermes CLI:     ${_YELLOW}não disponível${_NC}"

# =============================================================================
# FASE 1 — Verificação Determinística (bash puro)
# =============================================================================
echo ""
echo -e "${_BOLD}═══ FASE 1 — Verificação Determinística ═══${_NC}"

FAST_FAIL_TRIGGERED=false

for id in $(seq -f "EX-%02g" 1 35) EX-48 EX-49 EX-50 EX-51 EX-52; do
  if ! run_feature_test "$id"; then
    if [ "$FAST_FAIL" = "1" ]; then
      FAST_FAIL_TRIGGERED=true
      break
    fi
  fi
done

echo ""
echo -e "${_BOLD}═══ Fase 1 completa ═══${_NC}"
echo -e "  Testadas: ${TOTAL_TESTED}  |  Pass: ${TOTAL_PASSED}  |  Fail: ${TOTAL_FAILED}  |  Pending: ${TOTAL_PENDING}"

if $FAST_FAIL_TRIGGERED; then
  echo -e "${_RED}${_BOLD}⛔ Fast-fail acionado. Abortando fases 2 e 3.${_NC}"
  generate_report
  print_summary
  exit 1
fi

# =============================================================================
# FASE 2 — Smoke Tests (Hermes headless verifica features que passaram)
# =============================================================================
if [ "${NO_SMOKE:-0}" != "1" ]; then
  echo ""
  echo -e "${_BOLD}═══ FASE 2 — Smoke Tests via Hermes ═══${_NC}"

  smoke_count=0
  smoke_total=${#SMOKE_PROMPTS_MAP[@]}
  for feature_id in $(echo "${!SMOKE_PROMPTS_MAP[@]}" | tr ' ' '\n' | sort); do
    smoke_count=$((smoke_count + 1))
    _log "  ${_DIM}[$smoke_count/$smoke_total]${_NC}"
    run_smoke_test "$feature_id" "${SMOKE_PROMPTS_MAP[$feature_id]}"
  done

  echo ""
  echo -e "${_BOLD}═══ Fase 2 completa ($smoke_count smoke tests) ═══${_NC}"
else
  echo ""
  echo -e "${_GRAY}Fase 2 (smoke tests) pulada${_NC}"
  if [ -z "$HARNESS_MODEL" ] && [ "${NO_SMOKE:-0}" = "1" ]; then
    TOTAL_SMOKE_SKIPPED=${#SMOKE_PROMPTS_MAP[@]}
    echo -e "${_YELLOW}  ⚠ ${TOTAL_SMOKE_SKIPPED} smoke tests pulados — papel 'default' não configurado (EXOCORTEX_DEFAULT_MODEL)${_NC}"
    echo -e "${_YELLOW}  Para validação completa: configure o papel 'default' (bash setup.sh) ou export EXOCORTEX_HARNESS_MODEL${_NC}"
  else
    echo -e "${_GRAY}  (--no-smoke)${_NC}"
  fi
fi

# =============================================================================
# FASE 2 — Optional Services Smoke
# =============================================================================
# Each enabled optional service runs its own smoke script. Disabled services
# are cleanly skipped. Pass/fail aggregates into the suite error counter.
#
# Toggle names:   EXOCORTEX_ENABLE_HINDSIGHT
#                 EXOCORTEX_ENABLE_HERMES_WEBUI
#                 EXOCORTEX_ENABLE_CONTEXT7
#                 EXOCORTEX_ENABLE_FIRECRAWL
# =============================================================================
if [ "${NO_SMOKE:-0}" != "1" ]; then
  echo ""
  echo -e "${_BOLD}═══ FASE 2 — Optional Services Smoke ═══${_NC}"

  # ── Hindsight ──────────────────────────────────────────────────────────────
  if [ "${EXOCORTEX_ENABLE_HINDSIGHT:-0}" = "1" ]; then
    echo -e "  ${_CYAN}ℹ${_NC} Hindsight: running smoke..."
    _hs_smoke="$SCRIPT_DIR/../provision/hindsight/scripts/smoke.sh"
    if [ -f "$_hs_smoke" ]; then
      if bash "$_hs_smoke"; then
        echo -e "  ${_GREEN}✓${_NC} Hindsight smoke PASS"
      else
        echo -e "  ${_RED}✗${_NC} Hindsight smoke FAIL"
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        DEFINITIVE_FAILS+=("HINDSIGHT_SMOKE")
      fi
    else
      echo -e "  ${_YELLOW}⚠${_NC} Hindsight smoke script not found: $_hs_smoke"
      TOTAL_FAILED=$((TOTAL_FAILED + 1))
      DEFINITIVE_FAILS+=("HINDSIGHT_SMOKE")
    fi
  else
    echo -e "  ${_GRAY}Hindsight: skipped — disabled (EXOCORTEX_ENABLE_HINDSIGHT != 1)${_NC}"
  fi

  # ── Hermes WebUI ───────────────────────────────────────────────────────────
  if [ "${EXOCORTEX_ENABLE_HERMES_WEBUI:-0}" = "1" ]; then
    echo -e "  ${_CYAN}ℹ${_NC} Hermes WebUI: running smoke..."
    _webui_smoke="$SCRIPT_DIR/../provision/hermes-webui/scripts/smoke.sh"
    if [ -f "$_webui_smoke" ]; then
      if bash "$_webui_smoke"; then
        echo -e "  ${_GREEN}✓${_NC} Hermes WebUI smoke PASS"
      else
        echo -e "  ${_RED}✗${_NC} Hermes WebUI smoke FAIL"
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        DEFINITIVE_FAILS+=("HERMES_WEBUI_SMOKE")
      fi
    else
      echo -e "  ${_YELLOW}⚠${_NC} Hermes WebUI smoke script not found: $_webui_smoke"
      TOTAL_FAILED=$((TOTAL_FAILED + 1))
      DEFINITIVE_FAILS+=("HERMES_WEBUI_SMOKE")
    fi
  else
    echo -e "  ${_GRAY}Hermes WebUI: skipped — disabled (EXOCORTEX_ENABLE_HERMES_WEBUI != 1)${_NC}"
  fi

  # ── Context7 ───────────────────────────────────────────────────────────────
  if [ "${EXOCORTEX_ENABLE_CONTEXT7:-0}" = "1" ] || [ -n "${CONTEXT7_API_KEY:-}" ]; then
    echo -e "  ${_CYAN}ℹ${_NC} Context7: running smoke..."
    _ctx7_smoke="$SCRIPT_DIR/../provision/context7/scripts/smoke.sh"
    if [ -f "$_ctx7_smoke" ]; then
      if bash "$_ctx7_smoke"; then
        echo -e "  ${_GREEN}✓${_NC} Context7 smoke PASS"
      else
        echo -e "  ${_RED}✗${_NC} Context7 smoke FAIL"
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        DEFINITIVE_FAILS+=("CONTEXT7_SMOKE")
      fi
    else
      echo -e "  ${_YELLOW}⚠${_NC} Context7 smoke script not found: $_ctx7_smoke"
      TOTAL_FAILED=$((TOTAL_FAILED + 1))
      DEFINITIVE_FAILS+=("CONTEXT7_SMOKE")
    fi
  else
    echo -e "  ${_GRAY}Context7: skipped — disabled (EXOCORTEX_ENABLE_CONTEXT7 != 1 and CONTEXT7_API_KEY unset)${_NC}"
  fi

  # ── Firecrawl ──────────────────────────────────────────────────────────────
  if [ "${EXOCORTEX_ENABLE_FIRECRAWL:-0}" = "1" ]; then
    echo -e "  ${_CYAN}ℹ${_NC} Firecrawl: running smoke..."
    _fc_smoke="$SCRIPT_DIR/../provision/firecrawl/scripts/smoke.sh"
    if [ -f "$_fc_smoke" ]; then
      if bash "$_fc_smoke"; then
        echo -e "  ${_GREEN}✓${_NC} Firecrawl smoke PASS"
      else
        echo -e "  ${_RED}✗${_NC} Firecrawl smoke FAIL"
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        DEFINITIVE_FAILS+=("FIRECRAWL_SMOKE")
      fi
    else
      echo -e "  ${_YELLOW}⚠${_NC} Firecrawl smoke script not found: $_fc_smoke"
      TOTAL_FAILED=$((TOTAL_FAILED + 1))
      DEFINITIVE_FAILS+=("FIRECRAWL_SMOKE")
    fi
  else
    echo -e "  ${_GRAY}Firecrawl: skipped — disabled (EXOCORTEX_ENABLE_FIRECRAWL != 1)${_NC}"
  fi

  echo ""
  echo -e "${_BOLD}═══ Optional Services Smoke completo ═══${_NC}"
else
  echo ""
  echo -e "${_GRAY}Optional Services Smoke pulado (--no-smoke)${_NC}"
fi

# =============================================================================
# FASE 3 — Auto-Repair (Hermes headless conserta features que falharam)
# =============================================================================
if [ "$NO_REPAIR" != "1" ] && [ ${#FAILED_FEATURES[@]} -gt 0 ]; then
  echo ""
  echo -e "${_BOLD}═══ FASE 3 — Auto-Repair via Hermes ═══${_NC}"

  if can_invoke_hermes; then
    echo -e "  Hermes disponível. Modelo: ${HARNESS_MODEL}"
    echo -e "  Features para reparar: ${FAILED_FEATURES[*]}"
    echo ""

    local_fails=("${FAILED_FEATURES[@]}")

    for feature_id in "${local_fails[@]}"; do
      error_desc="Feature $feature_id falhou nos checks determinísticos"
      invoke_hermes_repair "$feature_id" "$error_desc" || true

      for repaired in "${REPAIRED_FEATURES[@]}"; do
        if [ "$repaired" = "$feature_id" ]; then
          run_regression "$feature_id"
          break
        fi
      done
    done
  else
    echo -e "  ${_YELLOW}⚠ Hermes não disponível para auto-repair${_NC}"
    echo -e "    Verifique: hermes no PATH e SOUL.md presente"
    DEFINITIVE_FAILS=("${FAILED_FEATURES[@]}")
  fi
else
  if [ "$NO_REPAIR" = "1" ]; then
    echo ""
    echo -e "${_GRAY}Fase 3 (auto-repair) pulada (--no-repair)${_NC}"
  fi
  DEFINITIVE_FAILS=("${FAILED_FEATURES[@]}")
fi

# =============================================================================
# FASE 4 — Relatório + Issues + Sync
# =============================================================================
echo ""
echo -e "${_BOLD}═══ FASE 4 — Relatório ═══${_NC}"

# Gerar relatório
generate_report

# Criar issues para falhas definitivas
if [ "$NO_ISSUES" != "1" ] && [ ${#DEFINITIVE_FAILS[@]} -gt 0 ]; then
  if can_invoke_hermes; then
    echo ""
    echo -e "  ${_CYAN}Criando issues para ${#DEFINITIVE_FAILS[@]} falha(s) definitiva(s)...${_NC}"
    for fail_id in "${DEFINITIVE_FAILS[@]}"; do
      create_github_issue "$fail_id" || true
    done
  fi
fi

# Sync reparos para o repositório
if [ "$NO_SYNC" != "1" ] && [ ${#REPAIRED_FEATURES[@]} -gt 0 ]; then
  sync_script="$SCRIPT_DIR/sync-repairs-to-repo.sh"
  if [ -x "$sync_script" ]; then
    echo ""
    echo -e "  ${_CYAN}Sincronizando reparos para o repositório...${_NC}"
    bash "$sync_script" || true
  else
    echo -e "  ${_GRAY}Script de sync não encontrado: $sync_script${_NC}"
  fi
fi

# Resumo final
print_summary

# Exit code
if [ ${#DEFINITIVE_FAILS[@]} -gt 0 ]; then
  exit 1
fi
exit 0
