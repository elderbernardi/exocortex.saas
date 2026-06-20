---
type: artifact
title: Workflow — validação pós-mudança operacional
description: 1. Rodar health check específico da área alterada.
tags: [validacao, setup, rollback]
timestamp: 2026-06-05
class: volátil
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
nature: workflows
kind: workflow
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
created: 2026-06-05
---

# Workflow — validação pós-mudança operacional

## Passos

1. Rodar health check específico da área alterada.
2. Rodar `bash -n` quando houver shell script.
3. Comparar estado esperado e observado.
4. Atualizar registry afetado.
5. Registrar log no microverso.
6. Criar snapshot `after` se a mudança alterou setup, profile, MCP, provider, cron ou skill.
7. Se falhar, acionar rollback ou registrar incidente.

## Critérios

- GREEN: mudança validada.
- YELLOW: operação possível com drift conhecido.
- RED: bloquear novas mudanças e preparar rollback.
