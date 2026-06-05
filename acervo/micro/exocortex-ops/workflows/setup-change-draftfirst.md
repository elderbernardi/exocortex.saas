---
title: Alteração de Setup com Draft-First
created: 2026-06-05
updated: 2026-06-05
nature: workflows
type: workflow
tags: [setup, draft-first, reproducibility]
sources: [skill:excrtx-memory-mvsetup]
confidence: high
---

# Alteração de setup com Draft-First

## Quando usar

Qualquer alteração que mude comportamento de instalações futuras ou runtime compartilhado.

## Fluxo

1. Gerar DRAFT de patch.
2. Explicar impacto, idempotência e validação planejada.
3. Aguardar aprovação explícita.
4. Aplicar patch apenas após aprovação.
5. Validar sintaxe e execução isolada quando aplicável.
6. Registrar decisão e log.

## Nunca fazer

- Editar `setup.sh` diretamente sem DRAFT.
- Instalar dependência para “testar rapidinho” sem aprovação.
- Sobrescrever arquivos semânticos existentes em setup idempotente.
