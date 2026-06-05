---
title: Registro de cron jobs
created: 2026-06-05
updated: 2026-06-05
nature: knowledge
kind: registry
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
tags: [cron, automacao, manutencao]
---

# Registro de cron jobs

Nenhum cron job específico deste microverso foi canonizado neste snapshot.

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
