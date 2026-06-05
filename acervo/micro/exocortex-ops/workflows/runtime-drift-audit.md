---
title: Auditoria de Drift Runtime vs Contrato
created: 2026-06-05
updated: 2026-06-05
nature: workflows
type: workflow
tags: [drift, audit, runtime, skills]
sources: [conversation:docbrain-check]
confidence: high
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
