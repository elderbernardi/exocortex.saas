---
schema: acervo/v0.2
type: workflow
title: Workflow — Ingestão de Conhecimento de Referência
description: Transformar obras e referências em conhecimento acionável para criação.
tags: [workflow, knowledge, ingestion]
timestamp: 2026-06-01
class: volátil
status: active
created_at: 2026-06-01T00:00:00Z
last_accessed_at: 2026-06-01T00:00:00Z
updated: 2026-06-01
nature: workflows
kind: workflow
scope_mode: micro
scope_slug: estudio-criativo
applies_to: []
authority: canonical
operational_mode: executable
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

# Objetivo

Transformar obras e referências em conhecimento acionável para criação.

# Entrada

Uma referência por ciclo: livro, artigo, vídeo, campanha, aula, entrevista ou case.

# Processo

1. Registrar a referência no backlog em `knowledge/reference-corpus.md`.
2. Se NotebookLM estiver disponível e autenticado, usar NLM como etapa de leitura assistida para extrair passagens, conceitos e perguntas de estudo.
3. Produzir ficha em `templates/learning-card.md`.
4. Extrair princípios, padrões e anti-padrões.
5. Converter aplicação prática para uma tarefa criativa simulada.
6. Classificar maturidade: bruto, testado ou incorporado.
7. Promover para workflow/template/skill apenas após uso real.

# Saída mínima

- 5 princípios reutilizáveis;
- 3 anti-padrões;
- 1 aplicação concreta em tarefa do Estúdio;
- decisão de promoção ou retenção.
