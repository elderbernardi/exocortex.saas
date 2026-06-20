---
type: decision
title: Política Draft-First para mudanças operacionais
description: 'Gerar DRAFT e aguardar aprovação explícita antes de:'
tags: [draft-first, setup, seguranca, governanca]
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

# Política Draft-First para mudanças operacionais

## Ações bloqueadas sem DRAFT

Gerar DRAFT e aguardar aprovação explícita antes de:

- Alterar `setup.sh`, installer ou bootstrap.
- Instalar, remover ou alterar skills.
- Alterar profiles Hermes.
- Alterar MCPs.
- Alterar providers de memória.
- Criar, alterar ou remover cron jobs.
- Configurar gateways.
- Alterar documentos compartilhados ou enviar comunicação externa.
- Executar ação destrutiva ou irreversível.

## DRAFT mínimo

Todo DRAFT operacional contém:

- Objetivo.
- Arquivos afetados.
- Patch ou comandos propostos.
- Impacto e side effects.
- Política de idempotência.
- Rollback.
- Health checks pós-mudança.
- Riscos.
- Critérios de aprovação.

## Aprovação

Só executar após aprovação inequívoca do executivo: `aplique`, `pode aplicar`, `aprovado`, `execute` ou equivalente.
