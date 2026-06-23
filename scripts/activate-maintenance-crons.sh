#!/usr/bin/env bash
# =============================================================================
# Ativar cron jobs de manutenção do síndico
# Horários: 03h–05h GMT-3 (madrugada, sem impacto no executivo)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[síndico]${NC} $1"; }
ok()    { echo -e "${GREEN}[✅]${NC} $1"; }
warn()  { echo -e "${YELLOW}[⚠️]${NC} $1"; }

# -----------------------------------------------------------------------------
# Verificar se hermes está disponível
# -----------------------------------------------------------------------------
if ! command -v hermes &>/dev/null; then
  warn "Comando 'hermes' não encontrado no PATH."
  warn "Certifique-se de que o Hermes Agent está instalado e acessível."
  exit 1
fi

echo ""
info "Configurando cron jobs de manutenção (03h–05h GMT-3)"
echo ""

# -----------------------------------------------------------------------------
# 1. Manutenção semanal — Domingos 03:00
# -----------------------------------------------------------------------------
info "Criando: maintenance-weekly (dom 03:00)"
hermes cron create \
  --name "maintenance-weekly" \
  "0 3 * * 0" \
  "Execute tarefas de manutenção completa do perfil manut. Persona: síndico. Use a skill excrtx-harness-maintenance. Execute todos os 6 passos do Procedure: pré-requisitos, varredura de saúde, revisão de pendências, auditoria de artefatos, triagem de inbox, relatório final. Envie o relatório no formato padronizado."
ok "maintenance-weekly → dom 03:00"

# -----------------------------------------------------------------------------
# 2. Triagem de inbox — Segundas 03:30
# -----------------------------------------------------------------------------
info "Criando: inbox-triage (seg 03:30)"
hermes cron create \
  --name "inbox-triage" \
  "30 3 * * 1" \
  "Execute triagem de inbox com rotina rtn_inbox_triage. Persona: arquivista. Liste itens no inbox (raw/) com >7 dias sem promoção. Classifique cada item como: promover para knowledge/context, arquivar, ou manter. NÃO mova itens — apenas recomende ações ao executivo. Envie relatório padronizado."
ok "inbox-triage → seg 03:30"

# -----------------------------------------------------------------------------
# 3. Auditoria de artefatos — 1º e 15º de cada mês 04:00
# -----------------------------------------------------------------------------
info "Criando: artifact-audit (1º e 15º 04:00)"
hermes cron create \
  --name "artifact-audit" \
  "0 4 1,15 * *" \
  "Execute auditoria de artefatos com rotina rtn_artifact_quality_audit. Persona: auditor. Verifique artefatos sem receipt/hash válido. Cheque manifests YAML. Identifique artefatos órfãos sem referência em index.md. Valide links em documentos canônicos. Envie relatório padronizado."
ok "artifact-audit → dias 1 e 15, 04:00"

# -----------------------------------------------------------------------------
# 4. Check de publicação — Diário 04:30
# -----------------------------------------------------------------------------
info "Criando: publication-check (diário 04:30)"
hermes cron create \
  --name "publication-check" \
  "30 4 * * *" \
  "Execute verificação de publicações pendentes com rotina rtn_ready_artifact_publication. Persona: operador. Identifique artefatos com status ready/approved ainda não publicados. Verifique se passaram pelos quality gates. Liste para o executivo com recomendação de canal. Envie relatório padronizado."
ok "publication-check → diário 04:30"

# -----------------------------------------------------------------------------
# 5. Reconciliação AcervoIndex — Diário 05:00 (ADR-020)
# -----------------------------------------------------------------------------
info "Criando: acervo-index-reconcile (diário 05:00)"
hermes cron create \
  --name "acervo-index-reconcile" \
  "0 5 * * *" \
  "Execute a reconciliação diária do AcervoIndex (ADR-020). Persona: síndico. Rode 'python \"\$ACERVO/global/tools/acervo_hindsight_index.py\" scan --all' e depois 'python \"\$ACERVO/global/tools/acervo_hindsight_index.py\" report'. Entregue ao home channel um relatório compacto com: novos indexados, alterados, órfãos (orphaned_manifest_entries), ignorados por lifecycle e erros. NÃO apague entradas Hindsight nesta versão — apenas reporte órfãos. Se o scan retornar erros, liste os arquivos afetados."
ok "acervo-index-reconcile → diário 05:00"

# -----------------------------------------------------------------------------
# Resumo
# -----------------------------------------------------------------------------
echo ""
info "═══════════════════════════════════════════════════"
info "  Cron jobs do síndico ativados"
info "═══════════════════════════════════════════════════"
echo ""
echo "  ┌────────────────────────┬───────────────┬────────────┐"
echo "  │ Job                    │ Horário       │ Frequência │"
echo "  ├────────────────────────┼───────────────┼────────────┤"
echo "  │ maintenance-weekly     │ dom 03:00     │ semanal    │"
echo "  │ inbox-triage           │ seg 03:30     │ semanal    │"
echo "  │ artifact-audit         │ 1º/15º 04:00  │ quinzenal  │"
echo "  │ publication-check      │ 04:30         │ diário     │"
echo "  │ acervo-index-reconcile │ 05:00         │ diário     │"
echo "  └────────────────────────┴───────────────┴────────────┘"
echo ""
info "Timezone: GMT-3 (horário local do sistema)"
info "Verifique com: hermes cron list"
echo ""
