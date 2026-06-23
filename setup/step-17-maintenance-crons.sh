#!/usr/bin/env bash
# =============================================================================
# Step 17: Ativar cron jobs de manutenção do síndico
# =============================================================================
# Agenda rotinas automáticas de zeladoria entre 03h–05h GMT-3.
# Usa hermes cron nativo — não cria crontab do sistema.
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

info "Configurando cron jobs de manutenção (síndico)..."

if ! command -v hermes &>/dev/null; then
  warn "Hermes CLI não encontrado — cron jobs de manutenção não ativados."
  warn "Execute manualmente: bash scripts/activate-maintenance-crons.sh"
  return 0 2>/dev/null || exit 0
fi

# Verifica se cron já existe antes de criar (idempotente).
# Args posicionais: name, schedule, prompt. Quaisquer args extras ("$@" após
# `shift 3`) são repassados verbatim ao `hermes cron create` — ex.: flags --skill.
create_cron_if_missing() {
  local name="$1"
  local schedule="$2"
  local prompt="$3"
  shift 3

  if hermes cron list 2>/dev/null | grep -q "$name"; then
    log "Cron '$name' já existe — pulando."
  else
    # `schedule` e `prompt` são posicionais no `hermes cron create` (não há
    # flags --schedule/--prompt). Flags extras ("$@") vêm antes dos posicionais.
    # Captura stderr para diagnóstico real.
    local err
    if err=$(hermes cron create --name "$name" "$@" "$schedule" "$prompt" 2>&1); then
      log "Cron criado: $name ($schedule)"
    else
      warn "Falha ao criar cron '$name': ${err##*$'\n'}"
      CRON_FAILURES=$((CRON_FAILURES + 1))
    fi
  fi
}

CRON_FAILURES=0

# O 'maintenance-weekly' cobre o ciclo do síndico (scan → quarentena → purge) +
# manutenção geral, anexando as skills via --skill (mais confiável que apenas
# mencioná-las no prompt). Se o cron legado 'Acervo Syndic' (mesmo horário, mesma
# skill de síndico, criado pelo plano 09-syndic-cron.md) já existir nesta máquina,
# NÃO cria o maintenance-weekly — evita zeladoria dupla no domingo 03h.
if hermes cron list 2>/dev/null | grep -q "Acervo Syndic"; then
  log "Cron de síndico legado 'Acervo Syndic' já existe — pulando 'maintenance-weekly' (evita duplicação)."
else
  create_cron_if_missing "maintenance-weekly" "0 3 * * 0" \
    "Execute tarefas de manutenção completa do perfil manut. Persona: síndico. Use a skill excrtx-harness-maintenance (manutenção geral) e a skill excrtx-memory-syndic (lifecycle do Acervo: scan → quarentena → purge). Para o syndic: (1) varre arquivos voláteis com last_accessed_at > 90 dias e deprecated_at > 180 dias, (2) move candidatos para .quarantine/ via excrtx-memory-quarantine, (3) purga arquivos com quarantine_expires_at vencido, (4) registra em log.md e .purge_log. Envie o relatório consolidado no formato padronizado." \
    --skill excrtx-harness-maintenance --skill excrtx-memory-syndic
fi

create_cron_if_missing "inbox-triage" "30 3 * * 1" \
  "Execute triagem de inbox com rotina rtn_inbox_triage. Persona: arquivista. Liste itens no inbox (raw/) com >7 dias sem promoção. Classifique e recomende ações ao executivo. NÃO mova itens. Envie relatório padronizado."

create_cron_if_missing "artifact-audit" "0 4 1,15 * *" \
  "Execute auditoria de artefatos com rotina rtn_artifact_quality_audit. Persona: auditor. Verifique artefatos sem receipt/hash válido. Cheque manifests YAML. Identifique artefatos órfãos. Envie relatório padronizado."

create_cron_if_missing "publication-check" "30 4 * * *" \
  "Execute verificação de publicações pendentes com rotina rtn_ready_artifact_publication. Persona: operador. Identifique artefatos com status ready/approved ainda não publicados. Envie relatório padronizado."

create_cron_if_missing "acervo-index-reconcile" "0 5 * * *" \
  "Execute a reconciliação diária do AcervoIndex (ADR-020). Persona: síndico. Rode 'python \"\$ACERVO/global/tools/acervo_hindsight_index.py\" scan --all' e depois 'report'. Entregue ao home channel um relatório compacto com: novos indexados, alterados, órfãos (orphaned_manifest_entries), ignorados por lifecycle e erros. NÃO apague entradas Hindsight nesta versão — apenas reporte órfãos."

if [ "$CRON_FAILURES" -eq 0 ]; then
  log "Cron jobs de manutenção configurados (03h–05h)."
else
  warn "$CRON_FAILURES cron(s) de manutenção NÃO foram criados — o síndico autônomo (ADR-018) não rodará."
  warn "Configure manualmente: bash scripts/activate-maintenance-crons.sh"
fi
