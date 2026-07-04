---
schema: acervo/v0.2
type: decision
title: ADR-021 — Orçamento e Governança da Memória Rápida
description: Restringe MEMORY.md e USER.md a bootstrap mínimo para reduzir token fixo e evitar duplicação do Acervo/Hindsight.
tags: [memory, token-economy, governance, bootstrap]
timestamp: 2026-06-21
class: perene
created_at: 2026-06-21T16:37:51Z
nature: decisions
excrtx_type: decision
confidence: high
status: active
epistemic: decision
canonical_from: micro/exocortex-dev/decisions/adr-021-memory-fast-layer-budget.md
promoted_at: 2026-06-21T21:50:00Z
scope_slug: global
---

# ADR-021 — Orçamento e Governança da Memória Rápida

## Status

Accepted.

## Contexto

`MEMORY.md` é injetado em todo turno. Quando cresce, vira custo fixo e atrai o agente para responder pela memória rápida em vez de recuperar contexto pelo Hindsight ou consultar o Acervo.

## Decisão

Definir orçamento e critérios rígidos para memória rápida.

| Store | Limite técnico | Alvo operacional | Conteúdo permitido |
|---|---:|---:|---|
| `MEMORY.md` | 2.200 chars | 35%–50% | Invariantes críticos, ponteiros, tool quirks de alta frequência |
| `USER.md` | 1.375 chars | 50%–70% | Preferências duráveis, estilo, limites pessoais |

## O que não entra em `MEMORY.md`

- Diário de tarefa concluída.
- Estado de projeto.
- Decisão longa.
- Plano de execução.
- Dados que pertencem a microverso.
- Conteúdo recuperável por Hindsight.
- Conteúdo canônico do Acervo.

## O que entra em `MEMORY.md`

- Regras de segurança ou governança usadas em quase toda sessão.
- Workaround técnico curto e frequente.
- Ponteiro para fonte canônica quando a ausência dele causa erro operacional.
- Fato que precisa estar disponível antes da primeira ferramenta.

## Política de promoção

Quando uma informação candidata aparecer:

1. Preferência pessoal durável → `USER.md`.
2. Operacional recuperável → `hindsight_retain`.
3. Conhecimento ou decisão canônica → Acervo.
4. Procedimento reutilizável → skill.
5. Literalidade de conversa → `session_search`, sem salvar.

## Critérios de aceite

- [ ] `MEMORY.md` fica abaixo de 50% após migração inicial.
- [ ] Novas memórias rápidas exigem justificativa de “precisa estar no prompt antes da primeira ferramenta”.
- [ ] Hindsight contém os fatos operacionais removidos da memória rápida.
- [ ] Acervo contém decisões e conhecimento removidos da memória rápida.

> Canonicalizado em `global/decisions/adr-021-memory-fast-layer-budget.md` a partir de `micro/exocortex-dev/decisions/adr-021-memory-fast-layer-budget.md` em 2026-06-21T21:50:00Z.

