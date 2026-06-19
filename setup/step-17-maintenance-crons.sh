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

# Verifica se cron já existe antes de criar (idempotente)
create_cron_if_missing() {
  local name="$1"
  local schedule="$2"
  local prompt="$3"

  if hermes cron list 2>/dev/null | grep -q "$name"; then
    log "Cron '$name' já existe — pulando."
  else
    hermes cron create --schedule "$schedule" --name "$name" --prompt "$prompt" 2>/dev/null \
      && log "Cron criado: $name ($schedule)" \
      || warn "Falha ao criar cron '$name' — configure manualmente."
  fi
}

create_cron_if_missing "maintenance-weekly" "0 3 * * 0" \
  "Execute tarefas de manutenção completa do perfil manut. Persona: síndico. Use a skill excrtx-harness-maintenance (manutenção geral) e a skill excrtx-memory-syndic (lifecycle do Acervo: scan → quarentena → purge). Para o syndic: (1) varre arquivos voláteis com last_accessed_at > 90 dias e deprecated_at > 180 dias, (2) move candidatos para .quarantine/ via excrtx-memory-quarantine, (3) purga arquivos com quarantine_expires_at vencido, (4) registra em log.md e .purge_log. Envie o relatório consolidado no formato padronizado."

create_cron_if_missing "inbox-triage" "30 3 * * 1" \
  "Execute triagem de inbox com rotina rtn_inbox_triage. Persona: arquivista. Liste itens no inbox (raw/) com >7 dias sem promoção. Classifique e recomende ações ao executivo. NÃO mova itens. Envie relatório padronizado."

create_cron_if_missing "artifact-audit" "0 4 1,15 * *" \
  "Execute auditoria de artefatos com rotina rtn_artifact_quality_audit. Persona: auditor. Verifique artefatos sem receipt/hash válido. Cheque manifests YAML. Identifique artefatos órfãos. Envie relatório padronizado."

create_cron_if_missing "publication-check" "30 4 * * *" \
  "Execute verificação de publicações pendentes com rotina rtn_ready_artifact_publication. Persona: operador. Identifique artefatos com status ready/approved ainda não publicados. Envie relatório padronizado."

log "Cron jobs de manutenção configurados (03h–05h)."
