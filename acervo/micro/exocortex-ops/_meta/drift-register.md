---
title: Registro de drift operacional — exocortex-ops
created: 2026-06-05
updated: 2026-06-05
nature: context
kind: drift-register
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
tags: [drift, runtime, setup, ops]
---

# Registro de drift operacional

| ID | Data | Área | Esperado | Observado | Severidade | Status | Próxima ação |
|---|---|---|---|---|---|---|---|
| DRIFT-2026-06-05-001 | 2026-06-05 | Installer | Source contém seed `acervo/micro/exocortex-ops` | Source ainda não contém seed | SEV2 | aberto | Preparar DRAFT de provisionamento |
| DRIFT-2026-06-05-002 | 2026-06-05 | Setup | Setup preserva evolução local de microverso base | Step 3 usa `rsync -a` genérico | SEV1 | aberto | Propor patch com `--ignore-existing` |
| DRIFT-2026-06-05-003 | 2026-06-05 | DocBrain | Docs/skills apontam path funcional | Runtime funcional em `/home/elder/exocortex/tools/docbrain`; docs antigas divergentes | SEV2 | aberto | Corrigir skill/doc em tarefa própria |
| DRIFT-2026-06-05-004 | 2026-06-05 | Modelo | Identidade operacional gpt-5.5 | `hermes profile list` mostra gpt-5.4 | SEV2 | aberto | Auditar config/profile em manutenção separada |
