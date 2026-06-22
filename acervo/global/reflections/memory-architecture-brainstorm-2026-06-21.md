---
type: reflection
title: Reflexão — Memória operacional, Acervo e Hindsight
description: Síntese do brainstorm que levou à arquitetura de Hindsight como índice
  semântico e Acervo como fonte canônica.
tags:
- memory
- reflection
- hindsight
- acervo
- architecture
timestamp: '2026-06-21'
class: volátil
created_at: '2026-06-21T16:37:51Z'
nature: reflections
excrtx_type: lesson
confidence: high
canonical_from: micro/exocortex-dev/reflections/memory-architecture-brainstorm-2026-06-21.md
promoted_at: '2026-06-21T21:50:00Z'
scope_slug: global
---

# Reflexão — Memória operacional, Acervo e Hindsight

## Problema observado

O agente continuava usando pouco o Hindsight mesmo com o provider ativo. A causa identificada foi comportamental: a memória rápida fica sempre no prompt, então o modelo tende a responder por ela antes de buscar contexto.

## Insight central

A memória excelente não exige mais memória rápida. Exige melhor roteamento.

O desenho correto separa:

- memória rápida para bootstrap mínimo;
- Hindsight para recuperação semântica;
- Acervo para verdade canônica;
- session_search para literalidade;
- skills para procedimentos.

## Decisão emergente

Hindsight deve acessar o Acervo como índice semântico e roteador. Ele guarda ponteiros, resumos, tags, hash e lifecycle. O Acervo continua guardando o conteúdo integral e canônico.

## Risco principal

Se o Hindsight receber cópias integrais do Acervo, o sistema cria uma fonte paralela e stale. Isso enfraquece lifecycle, deprecação, quarentena e isolamento por microverso.

## Princípio final

Hindsight aponta. Acervo decide. `MEMORY.md` só inicializa.

> Canonicalizado em `global/reflections/memory-architecture-brainstorm-2026-06-21.md` a partir de `micro/exocortex-dev/reflections/memory-architecture-brainstorm-2026-06-21.md` em 2026-06-21T21:50:00Z.

