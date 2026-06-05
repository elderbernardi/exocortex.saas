---
title: Self-Check do Exocórtex
created: 2026-06-05
updated: 2026-06-05
nature: workflows
type: workflow
tags: [self-check, diagnostics, maintenance]
sources: [skill:excrtx-assess-selftest]
confidence: high
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
