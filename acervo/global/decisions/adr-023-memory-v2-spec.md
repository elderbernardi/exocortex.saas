---
type: decision
title: ADR-023 — Especificação Memória v2 (objetos, tempo, epistemologia, consolidação)
description: Adota a spec Memória v2 — schema v0.2, episódios, entidades, intenções,
  conflito como estado, consolidação.
tags:
- memory
- architecture
- schema
- v2
- spec
timestamp: '2026-07-03'
class: perene
created_at: '2026-07-03T21:30:00Z'
nature: decisions
confidence: high
status: proposed
sources:
- docs/plans/2026-07-03_memory-v2-spec/README.md
---

# ADR-023 — Especificação Memória v2

## Status

**Proposed** — aguarda aprovação do executivo. Fase 0 (reparos de drift) pode executar independentemente.

## Contexto

A reforma de memória de 2026-06 (ADR-019/020/021) acertou o roteamento: Acervo canônico, Hindsight como índice de ponteiros, memória rápida orçada. A pesquisa de estado da arte (2026-07) valida essas apostas. O que falta é um **modelo de verdade no tempo e nas pessoas**: o sistema não representa desde quando um fato vale, com que confiança, o que aconteceu numa reunião, quem é alguém entre domínios, nem o que foi prometido — e trata contradição apenas por deprecação destrutiva. Diagnóstico completo, com dez itens de drift spec/código verificados: `docs/plans/2026-07-03_memory-v2-spec/01-diagnosis.md`.

## Decisão

Adotar a especificação `docs/plans/2026-07-03_memory-v2-spec/` como direção canônica da memória do Exocórtex:

1. **Schema v0.2** — um único eixo `type` (elimina o triplo `type`/`excrtx_type`/`nature`), escalar `status`, validade bitemporal-lite (`observed_at`, `valid_from/until`; git = tempo de transação), camada epistêmica (`epistemic`, `confidence`, `sources`, `extraction`), supersedência estruturada (`supersedes`/`superseded_by`).
2. **Três novos tipos de memória**: `episode` (o que aconteceu), `entity` (quem — com aliases obrigatórios), `intention` (o que foi prometido, com prazo).
3. **Conflito como estado de primeira classe**: verbos supersede/dispute/coexist; objetos `conflict`; banners na recuperação; deprecação reservada para o que nunca foi verdade.
4. **catalog.sqlite derivado** (reconstruível) para filtro por metadados, FTS e degradação graciosa sem Hindsight.
5. **Loop de consolidação** (diário: episódios, entidades, intenções; semanal: auditoria) — git-auditável, nunca rewrite opaco.
6. **Trust gate**: conteúdo de web/email/terceiros nunca vira memória ativa sem aprovação (defesa contra memory poisoning).
7. **Avaliação obrigatória**: harness com perguntas-ouro e contaminação-zero antes de mudanças em skills/schema de memória.

Princípios preservados: *Hindsight aponta. Acervo decide. MEMORY.md só inicializa.* Roadmap em 8 fases com critérios de corte: `12-roadmap.md`.

## Consequências

Positivas: passado e presente distinguíveis pela LLM; memória relacional e prospectiva com casa canônica; contradições viram perguntas de uma linha ao executivo; sistema mensurável. Custos: migração de schema (script idempotente, dry-run), atualização de skills `excrtx-memory-*`, ~15–20 sessões de agente em 8 fases.

## Critérios de aceite

- [ ] Fase 0: `validate_frontmatter.py --dir acervo` limpo; dirs ausentes criados; `groups` unificado.
- [ ] Fase 1: migração v0.2 aplicada; catalog reconstrói de arquivos; `acervoctl doctor` limpo.
- [ ] Fase 3: bateria de perguntas-ouro ≥ alvos de `10-evaluation.md`; contaminação = 0.
- [ ] Fase 4: sessão significativa vira episódio no dia seguinte; digest semanal entregue.
