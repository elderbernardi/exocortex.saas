---
type: decision
title: Política de rollback operacional
description: Toda mudança operacional sensível precisa declarar rollback antes da aplicação.
tags: [rollback, setup, incident]
timestamp: 2026-06-05
class: perene
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
nature: contracts
kind: rule
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
created: 2026-06-05
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
