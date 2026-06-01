---
title: Decisão — Estúdio Criativo como Microverso Base
created: 2026-06-01
updated: 2026-06-01
nature: conhecimento
kind: decision
scope_mode: micro
scope_slug: hermes-setup
applies_to: [estudio-criativo]
authority: canonical
operational_mode: read_only
stability: active
sources: [micro/estudio-criativo/decisions/create-estudio-criativo.md]
derived_from: []
confidence: high
promotion_policy: none
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
tags: [setup, microverso, creative-studio]
---

# Decisão

Incluir `estudio-criativo` como microverso base do setup replicável do Exocórtex.

## Motivo

O Exocórtex precisa de uma capacidade criativa inicial, adaptável ao usuário, capaz de atuar em tarefas próprias e apoiar tarefas mistas com outros microversos. Essa capacidade deve nascer como domínio estruturado do Acervo, não como skill isolada nem como contexto pessoal.

## Critérios

- Criar `micro/estudio-criativo/` com Ontologia Multifocal v2.
- Manter o Estúdio genérico e adaptável ao usuário.
- Documentar atuação própria e apoio misto entre microversos.
- Permitir uso de ferramentas e skills criativas consolidadas, com IA e sem IA.
- Instalações que modifiquem ambiente exigem aprovação explícita.
- Evitar poluição com contexto de um usuário, instituição ou projeto específico.

## Consequência para setup

O setup replicável deve provisionar ou preservar o microverso `estudio-criativo` como capacidade criativa base, junto dos demais microversos essenciais.
