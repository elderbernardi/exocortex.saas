---
type: artifact
title: Auditoria de Drift Runtime vs Contrato
description: Detectar divergência entre skill, documentação, configuração e runtime real.
tags: [drift, audit, runtime, skills]
timestamp: 2026-06-05
class: volátil
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
excrtx_type: workflow
nature: workflows
sources: ['conversation:docbrain-check']
confidence: high
created: 2026-06-05
---

# Auditoria de drift

## Objetivo

Detectar divergência entre skill, documentação, configuração e runtime real.

## Procedimento

1. Identificar o contrato declarado: skill, README, config ou índice do acervo.
2. Verificar runtime real com comando ou leitura de arquivo.
3. Classificar drift:
   - path incorreto;
   - comando obsoleto;
   - provider inativo;
   - credential reminder stale;
   - documentação incompleta.
4. Operar apenas sobre o estado verificado.
5. Propor correção da fonte canônica.

## Regra

Se a correção afetar setup executável, provider, MCP, cron ou instalação: DRAFT primeiro.
