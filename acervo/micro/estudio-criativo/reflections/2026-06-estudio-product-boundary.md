---
type: reflection
title: Caso Real — Fronteira Operacional com Produto
description: O Estúdio já operava como capacidade transversal, mas ainda faltava uma fronteira explícita com Produto. Sem esse con...
tags: [reflection, case, receipt, boundary, product]
timestamp: 2026-06-14
class: perene
created_at: 2026-06-14T00:00:00Z
last_accessed_at: 2026-06-14T00:00:00Z
updated: 2026-06-14
nature: reflections
kind: case
scope_mode: micro
scope_slug: estudio-criativo
applies_to: []
authority: canonical
operational_mode: read_only
stability: active
sources: [issue, commit e2b353d, acervo/micro/estudio-criativo/contracts/boundary-with-product.md]
derived_from: []
confidence: high
promotion_policy: none
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
created: 2026-06-14
---

# Caso real — fronteira operacional com Produto

## Contexto

O Estúdio já operava como capacidade transversal, mas ainda faltava uma fronteira explícita com Produto. Sem esse contrato, narrativa, proposta de valor, conceito e artefatos de validação podiam virar território borrado.

## Objetivo

Definir autoridade de Produto, autoridade do Estúdio, zonas compartilhadas e handoffs mínimos.

## Artefato produzido

- `contracts/boundary-with-product.md`
- ajuste do índice
- ajuste de `context/current-state.md`

## O que funcionou

- formular a fronteira como contrato operacional curto
- diferenciar quem decide o que vale existir de quem decide como ganha forma percebida
- manter explícita a regra: método fica no Estúdio, contexto e hipótese ficam no microverso atendido

## O que exigiu ajuste

- resistir à leitura que reduz Estúdio a apoio visual
- resistir à leitura que dilui Produto em narrativa solta
- transformar colaboração em handoff descritível, não em slogan de cooperação

## O que virou método

- triângulo canônico em paridade: Produto, Estúdio e Engenharia
- Produto decide hipótese, problema, escopo, prioridade e validação
- Estúdio decide forma percebida, narrativa, tangibilização e crítica criativa
- Engenharia decide viabilidade, implementação, testes e operação real

## Receipts verificáveis

- issue: `#62`
- commit: `e2b353d711f89d489f7638b66152a554d81f7121`
- mensagem: `docs: formalizar fronteira entre estudio e produto`
- diff principal: `contracts/boundary-with-product.md`, `_meta/index.md`, `context/current-state.md`

## Destino do aprendizado

- método estrutural do Estúdio
- referência para futura fronteira equivalente com Engenharia
