---
schema: acervo/v0.2
type: knowledge
title: Registro de cron jobs
description: Registro de cron jobs canônicos do microverso, incluindo a reconciliação diária do AcervoIndex.
tags: [cron, automacao, manutencao]
timestamp: 2026-06-05
class: volátil
status: active
epistemic: fact
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-21T00:00:00Z
updated: 2026-06-21
nature: knowledge
kind: registry
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
created: 2026-06-05
---

# Registro de cron jobs

## Crons canônicos

### acervo-index-reconcile (ADR-020)

| Campo | Valor |
|---|---|
| job_id | Atribuído na ativação (`hermes cron list` após `scripts/activate-maintenance-crons.sh`) |
| schedule | `0 5 * * *` (diário 05:00 GMT-3) |
| script | `python "$ACERVO/global/tools/acervo_hindsight_index.py" scan --all` + `report` |
| profile/workdir | perfil `manut` (persona síndico), workdir = Acervo |
| side effects | Indexa ponteiros do Acervo no Hindsight (rede → localhost:8888); escreve manifesto `global/tools/state/acervo_hindsight_index.json`; envia relatório ao home channel. **Não apaga** entradas Hindsight. |
| approval | Reforma Memory Excellence (Fases 6–7); ver `workflows/memory-excellence-execution-plan.md` |
| rollback | `hermes cron delete acervo-index-reconcile` (ou pausar via `hermes cron`); a indexação é idempotente e não-destrutiva |

## Regra

Todo cron recorrente deve registrar:

| Campo | Exigência |
|---|---|
| job_id | ID real retornado por `cronjob list` |
| schedule | Cron expression ou intervalo |
| prompt/script | Conteúdo completo ou path |
| profile/workdir | Escopo de execução |
| side effects | Envio, escrita, rede, alteração de estado |
| approval | Link ou referência ao DRAFT aprovado |
| rollback | Como pausar/remover |

Cron jobs não podem criar outros cron jobs em execução autônoma.
