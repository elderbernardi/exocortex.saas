---
title: Contrato Adapter LLM Wiki para Acervo
created: 2026-05-30
updated: 2026-05-30
nature: instrucoes
kind: contract
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global, dev, ensino, gabinete]
authority: canonical
operational_mode: blocking
stability: stable
sources: [docs/ADR/ADR-006-llm-wiki-adapter-contract.md]
derived_from: [user-confirmation, research/llm-wiki]
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: research/llm-wiki
  assumed_version: "2.1.0"
  coupling: adapter-only
tags: [llm-wiki, acervo, adapter, safety, hermes]
---

# Contrato Adapter LLM Wiki para Acervo

A LLM Wiki nativa é upstream mecânico. O Acervo é fonte canônica.

Toda operação deve seguir:

```text
research/llm-wiki → acervo-llm-wiki-adapter → acervo-manager → Acervo
```

Bloqueios:

- não apontar `WIKI_PATH` para o Acervo inteiro;
- não criar `entities/`, `concepts/`, `comparisons/`, `queries/` no Acervo;
- não escrever em `macro/`;
- não cruzar microversos por wikilink;
- não alterar `raw/` após captura;
- não tratar update upstream como alteração automática do contrato.
