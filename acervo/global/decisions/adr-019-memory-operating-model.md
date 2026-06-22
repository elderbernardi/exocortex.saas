---
type: decision
title: ADR-019 — Modelo Operacional de Memória do Exocórtex
description: Define Hindsight como memória operacional semântica, Acervo como fonte
  canônica e memória rápida como bootstrap mínimo.
tags:
- memory
- hindsight
- acervo
- architecture
- token-economy
timestamp: '2026-06-21'
class: perene
created_at: '2026-06-21T16:37:51Z'
nature: decisions
excrtx_type: decision
confidence: high
status: accepted
canonical_from: micro/exocortex-dev/decisions/adr-019-memory-operating-model.md
promoted_at: '2026-06-21T21:50:00Z'
scope_slug: global
---

# ADR-019 — Modelo Operacional de Memória do Exocórtex

## Status

Accepted.

## Contexto

O Exocórtex opera com quatro superfícies de memória:

1. `MEMORY.md` / `USER.md` — memória rápida injetada no prompt.
2. Hindsight — memória semântica operacional, com `retain`, `recall` e `reflect`.
3. `session_search` — busca literal em transcrições.
4. Acervo Cognitivo — contexto, conhecimento, decisões, contratos e reflexões por microverso.

A memória rápida está sendo usada como repositório primário. Isso aumenta token fixo, reduz economia e faz o agente responder pelo que já está no prompt, em vez de recuperar contexto sob demanda.

## Decisão

Adotar o seguinte modelo operacional:

| Camada | Papel | Autoridade |
|---|---|---|
| `SOUL.md` | Constituição e regras de comportamento | Máxima |
| `USER.md` | Preferências duráveis do executivo | Alta |
| `MEMORY.md` | Bootstrap mínimo e invariantes críticos | Alta, mas restrita |
| Hindsight | Memória operacional semântica sob demanda | Recuperação e síntese |
| Acervo | Fonte canônica estruturada | Verdade documental |
| `session_search` | Histórico literal | Evidência textual |

A regra principal passa a ser:

> Se o pedido depende de passado, estado, decisão, contexto multi-sessão ou conhecimento não presente no turno atual, o agente deve chamar `hindsight_recall` antes de responder.

## Consequências

### Positivas

- Reduz token fixo em sessões futuras.
- Diminui dependência de `MEMORY.md`.
- Melhora recall semântico entre sessões.
- Mantém decisões e conhecimento no Acervo, com lifecycle e auditabilidade.
- Dá a agentes menores uma regra simples: Hindsight localiza; Acervo decide.

### Custos

- Algumas respostas passam a exigir uma chamada de ferramenta.
- O agente precisa seguir o contrato de recuperação.
- O índice semântico do Acervo precisa de manutenção.

## Regras operacionais

1. `MEMORY.md` não deve guardar diário de tarefas, decisões longas ou estado de projeto.
2. Hindsight guarda fatos operacionais, ponteiros e sínteses recuperáveis.
3. Acervo guarda conhecimento canônico, contexto de domínio e decisões aprovadas.
4. `session_search` entra quando a pergunta exige texto literal ou auditoria de conversa.
5. Hindsight nunca vence o Acervo em conflito; ele aponta, não decide.

## Critérios de aceite

- [ ] `MEMORY.md` fica abaixo de 50% de uso após consolidação.
- [ ] Perguntas sobre estado passado acionam `hindsight_recall`.
- [ ] Decisões canônicas são lidas do Acervo antes da resposta final.
- [ ] Agentes menores conseguem executar tarefas usando apenas esta ADR e o plano de execução.

> Canonicalizado em `global/decisions/adr-019-memory-operating-model.md` a partir de `micro/exocortex-dev/decisions/adr-019-memory-operating-model.md` em 2026-06-21T21:50:00Z.

