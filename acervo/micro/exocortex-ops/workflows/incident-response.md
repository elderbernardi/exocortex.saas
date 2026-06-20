---
type: artifact
title: Workflow — resposta a incidente operacional
description: 'SEV0: segredo exposto, ação externa sem aprovação, perda de Acervo, alteração indevida em outro profile.'
tags: [incident, sev, seguranca, rollback]
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

# Workflow — resposta a incidente operacional

## Classificação

- SEV0: segredo exposto, ação externa sem aprovação, perda de Acervo, alteração indevida em outro profile.
- SEV1: Hermes não inicia, setup quebra instalação, MCP crítico indisponível, provider com falha séria.
- SEV2: drift que degrada workflow, registry incompleto, path divergente.
- SEV3: index desatualizado, template incompleto, nomenclatura inconsistente.

## Passos

1. Parar mudanças não essenciais.
2. Capturar evidência com tools.
3. Classificar severidade.
4. Gerar relatório de incidente.
5. Preparar rollback em DRAFT quando houver mutação sensível.
6. Executar só após aprovação quando o rollback alterar estado sensível.
7. Registrar decisão ou reflexão após resolver.
