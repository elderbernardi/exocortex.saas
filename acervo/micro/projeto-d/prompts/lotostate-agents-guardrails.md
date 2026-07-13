---
title: "LotoState by ALEQIA — Prompt Base para Agentes"
type: knowledge
description: "Prompt operacional base para agentes de programação atuando no LotoState"
class: volátil
timestamp: "2026-07-05"
created_at: "2026-07-05T19:56:31Z"
created: "2026-07-05"
updated: "2026-07-05"
nature: prompts
excrtx_type: rule
tags: [projeto-d, lotostate, aleqia, prompts, agents, coding]
confidence: high
sources:
  - /home/elder/.hermes/cache/documents/doc_c15191a2021b_PRD_LotoState_by_ALEQIA.md
---

# LotoState by ALEQIA — Prompt Base para Agentes

Use este prompt como base quando um agente de programação for atuar no repositório do LotoState.

## Contexto

Este repositório implementa o LotoState by ALEQIA, produto mobile/web para análise estatística, monitoramento e gestão de apostas lotéricas. A especificação é a fonte de verdade.

Antes de alterar código, ler:
- `specs/PRD.md`
- `specs/DOMAIN.md`
- `specs/API_SPEC.md`
- `specs/TEST_PLAN.md`

## Regras críticas

- não expor fórmulas internas do ALEQIA D no frontend
- não enviar número, score ou histórico de dezena bloqueada
- não prometer ganho, prêmio ou previsão garantida
- não enviar WhatsApp sem consentimento ativo
- não armazenar CPF ou cartão em texto puro
- usar centavos para valores monetários
- incluir testes para regras de plano, jogo e carteira

## Fluxo de trabalho mínimo

1. identificar o requisito-fonte por ID
2. listar arquivos prováveis da mudança
3. implementar a menor mudança coesa possível
4. rodar testes, lint e typecheck
5. atualizar specs se o contrato mudou
6. registrar riscos e decisões no PR

## Checklist de revisão do diff

- o backend continua como autoridade de entitlement?
- payloads bloqueados seguem sem número ou score?
- copy pública evita linguagem proibida?
- cálculos financeiros usam centavos?
- webhooks de pagamento seguem idempotentes?
- logs evitam dados sensíveis?
- analytics do requisito foram implementados quando aplicável?

## Comandos esperados

- backend: `pytest`, `ruff`, `mypy`
- web/mobile: `pnpm test`, `pnpm lint`, `pnpm typecheck`
- E2E: `pnpm e2e`
