---
type: decision
title: Governança de Ferramentas e Skills Criativas
description: O Estúdio pode usar ferramentas e skills consolidadas para criação com IA e sem IA, desde que respeite aprovação, esc...
tags: [contract, tools, skills]
timestamp: 2026-06-01
class: perene
created_at: 2026-06-01T00:00:00Z
last_accessed_at: 2026-06-01T00:00:00Z
updated: 2026-06-01
nature: contracts
kind: contract
scope_mode: micro
scope_slug: estudio-criativo
applies_to: []
authority: canonical
operational_mode: blocking
stability: active
sources: []
derived_from: []
confidence: high
promotion_policy: none
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
created: 2026-06-01
---

# Governança de ferramentas e skills

O Estúdio pode usar ferramentas e skills consolidadas para criação com IA e sem IA, desde que respeite aprovação, escopo e reversibilidade.

## Uso permitido

- carregar skills existentes quando relevantes;
- usar ferramentas já disponíveis no ambiente;
- propor instalação de ferramenta quando houver ganho claro;
- documentar stack validada em `tools/`;
- transformar workflows recorrentes em skills.

## Limites

- Não instalar ferramentas sem aprovação explícita quando a instalação modifica o ambiente.
- Não tratar geração por IA como entrega final sem curadoria humana.
- Não publicar, enviar ou modificar artefatos externos sem Draft-First.
- Não criar dependência de ferramenta sem registrar alternativa ou fallback.

## Critério de consolidação

Uma ferramenta entra no stack do Estúdio quando: resolve tarefa recorrente, tem qualidade verificável, é operável pelo Hermes/Exocórtex e pode ser documentada de forma reprodutível.
