---
schema: acervo/v0.2
type: contract
title: Contrato de Roteamento de Memória do Exocórtex
description: Regras executáveis para escolher entre MEMORY.md, USER.md, Hindsight, Acervo, session_search e skills.
tags: [memory, routing, contract, hindsight, acervo]
timestamp: 2026-06-21
class: perene
status: active
created_at: 2026-06-21T16:37:51Z
nature: contracts
excrtx_type: rule
confidence: high
canonical_from: micro/exocortex-dev/contracts/memory-routing-contract.md
promoted_at: 2026-06-21T21:50:00Z
scope_slug: global
---

# Contrato de Roteamento de Memória do Exocórtex

## Regra de recuperação

Antes de responder, classifique a necessidade de contexto:

| Pergunta/tarefa | Primeira ação |
|---|---|
| Passado, estado, decisão, “onde paramos”, contexto multi-sessão | `hindsight_recall` |
| Síntese de várias memórias | `hindsight_reflect` |
| Decisão ou conhecimento canônico | `hindsight_recall` → ler Acervo |
| Conversa exata, frase literal, auditoria de sessão | `session_search` |
| Preferência pessoal já injetada | usar `USER.md` |
| Procedimento recorrente | carregar skill |

## Regra de retenção

| Informação nova | Destino |
|---|---|
| Preferência durável do executivo | `USER.md` |
| Fato operacional útil | Hindsight |
| Decisão validada | Acervo `decisions/` |
| Conhecimento curado | Acervo `knowledge/` |
| Contexto de domínio | Acervo `context/` |
| Reflexão pós-evento | Acervo `reflections/` |
| Procedimento reutilizável | skill |
| Transcript literal | não salvar; usar `session_search` |

## Regra de autoridade

1. SOUL e instruções do sistema vencem tudo.
2. Contratos do Acervo vencem Hindsight.
3. Decisões do Acervo vencem observações do Hindsight.
4. Hindsight vence memória rápida para contexto operacional que não precisa estar sempre no prompt.
5. `session_search` vence quando a disputa é sobre texto literal.

## Regra de resposta

Quando a resposta depender de recuperação, declarar a origem de forma curta:

- `Hindsight recuperou...`
- `Acervo confirma em micro/...`
- `session_search localizou a conversa...`

Não expor detalhes internos quando a resposta for para público externo; usar a origem apenas para governança interna com o executivo.

> Canonicalizado em `global/contracts/memory-routing-contract.md` a partir de `micro/exocortex-dev/contracts/memory-routing-contract.md` em 2026-06-21T21:50:00Z.

