---
type: context
title: Global Log
description: Registro cronológico de operações na camada global. Append-only.
tags: []
timestamp: 2026-05-27
class: perene
created_at: 2026-05-27T04:03:03Z
last_accessed_at: 2026-05-27T04:03:03Z
---

# Global Log

> Registro cronológico de operações na camada global. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: create, update, ingest, archive, lint
> Rotacionar quando exceder 500 entradas: renomear para log-YYYY.md

## [2026-05-26] create | Global layer initialized
- Structure created with SCHEMA.md, index.md, log.md
- Natures: context, knowledge, contracts, workflows, tools, reflections
- Directories: raw/ (articles, documents, assets), _archive/
- [2026-06-01T21:06:19-03:00] Contrato global de identidade Exocórtex sobre Hermes criado em `contracts/exocortex-hermes-identity-contract.md`.
- [2026-06-10] create | Ecossistema Visual — Design System do Exocórtex em `knowledge/ecossistema-visual-design-system.md`
  - Conhecimento promovido após sessão de evolução sobre issue #18 (brandkit generator)
  - Abrange: formato Google DESIGN.md, cascade global→micro, tooling, skills envolvidas, estado atual, path mismatch conhecido
