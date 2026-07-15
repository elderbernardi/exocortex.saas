---
schema: acervo/v0.2
type: workflow
title: Self-Check do Exocórtex
description: 'Pedido explícito: “self-check”, “status”, “diagnóstico”.'
tags: [self-check, diagnostics, maintenance]
timestamp: 2026-06-05
class: volátil
status: active
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
excrtx_type: workflow
nature: workflows
sources: ['skill:excrtx-assess-selftest']
confidence: high
created: 2026-06-05
---

# Self-check

## Quando usar

- Pedido explícito: “self-check”, “status”, “diagnóstico”.
- Antes de mudanças estruturais no setup.
- Após drift relevante entre skill, docs e runtime.

## Procedimento mínimo

1. Verificar SOUL.md e Macroverso.
2. Verificar MEMORY/log auditável quando existir.
3. Verificar skills Exocórtex essenciais.
4. Verificar toolsets e MCPs com comando real.
5. Verificar comportamento por amostragem quando solicitado.

## Saída

Relatório curto com OK/falhas, evidência e próximo passo.
