---
title: Política de rollback operacional
created: 2026-06-05
updated: 2026-06-05
nature: contracts
kind: rule
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
tags: [rollback, setup, incident]
---

# Política de rollback operacional

## Exigência

Toda mudança operacional sensível precisa declarar rollback antes da aplicação.

## Rollback mínimo

- Arquivos afetados.
- Snapshot ou diff anterior.
- Comandos para restaurar estado.
- Como validar o rollback.
- Riscos de rollback parcial.

## Mudanças que exigem rollback explícito

- Setup e installer.
- Profiles.
- MCPs.
- Providers de memória.
- Cron jobs.
- Skills.
- Gateways.
