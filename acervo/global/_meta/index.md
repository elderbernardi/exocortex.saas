---
schema: acervo/v0.2
type: context
title: Global Index
description: Catálogo de conteúdo universal. Tudo aqui se aplica a TODOS os Microversos.
tags: []
timestamp: 2026-05-27
class: perene
status: active
epistemic: fact
created_at: 2026-05-27T04:03:03Z
last_accessed_at: 2026-05-27T04:03:03Z
nature: _meta
---

# Global Index

> Catálogo de conteúdo universal. Tudo aqui se aplica a TODOS os Microversos.
> Carregado no boot de toda sessão. Consultar antes de carregar páginas.
> Last updated: 2026-06-21 | Total pages: canonical memory package active

## Instruções
<!-- Regras universais — ordenar alfabeticamente -->

## Processos
<!-- Workflows globais — ordenar alfabeticamente -->

## Ferramentas
<!-- Tools disponíveis em todo contexto — ordenar alfabeticamente -->
- [DESIGN.md](DESIGN.md) — Tokens visuais (cores, tipografia, spacing). Carregado sob demanda por `exocortex-design-system`. Formato: Google DESIGN.md.
- [tools/acervo_hindsight_index.py](file:///home/elder/exocortex/acervo/global/tools/acervo_hindsight_index.py) — indexador semântico do Acervo no Hindsight; grava ponteiros, hashes e resumos curtos.
- [tools/acervo-hindsight-indexer-spec.md](tools/acervo-hindsight-indexer-spec.md) — especificação do AcervoIndex.
## Conhecimento
<!-- Compliance, legal, fatos universais — ordenar alfabeticamente -->

## Reflexões
<!-- Lições transversais — ordenar alfabeticamente -->
- [reflections/memory-architecture-brainstorm-2026-06-21.md](reflections/memory-architecture-brainstorm-2026-06-21.md) — síntese do brainstorm da arquitetura Hindsight/Acervo.
## Contratos operacionais
- [contracts/exocortex-hermes-identity-contract.md](contracts/exocortex-hermes-identity-contract.md) — contrato bloqueante de identidade Exocórtex sobre Hermes.
- [contracts/memory-routing-contract.md](contracts/memory-routing-contract.md) — roteamento canônico entre memória rápida, Hindsight, Acervo e session_search.
- [contracts/microverso-directory-structure.md](contracts/microverso-directory-structure.md) — estrutura canônica de diretórios de microverso (14 dirs: 11 natures + 3 infra).
- [contracts/microverso-package-spec.md](contracts/microverso-package-spec.md) — especificação do formato .mvpkg (excrtx/v1) para export/import de microversos.
- [_meta/microversos.yaml](_meta/microversos.yaml) — registro de microversos instalados (append-only, mantido pelo mvinstall).

## Decisões canônicas
- [decisions/adr-019-memory-operating-model.md](decisions/adr-019-memory-operating-model.md) — Hindsight como memória operacional semântica; Acervo como fonte canônica.
- [decisions/adr-020-acervo-hindsight-index.md](decisions/adr-020-acervo-hindsight-index.md) — Hindsight indexa ponteiros do Acervo.
- [decisions/adr-021-memory-fast-layer-budget.md](decisions/adr-021-memory-fast-layer-budget.md) — orçamento da memória rápida.
