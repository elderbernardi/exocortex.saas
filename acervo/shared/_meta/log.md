---
type: context
title: Shared Log
description: Registro cronológico de operações cross-domain. Append-only.
tags: []
timestamp: 2026-05-27
class: perene
created_at: 2026-05-27T04:03:03Z
last_accessed_at: 2026-05-27T04:03:03Z
---

# Shared Log

> Registro cronológico de operações cross-domain. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: create, update, archive

## [2026-05-26] create | Shared layer restructured
- Added SCHEMA.md, index.md, log.md
- Created groups.md with built-in aliases (ALL, CLIENTS, PROJECTS)
- Created cross-refs/ directory

## [2026-07-04] update | groups.md canonizado como fonte única de grupos
- `shared/groups.md` corrigido para 5 microversos ativos (comercial, estudio-criativo, excrtx, exocortex-dev, exocortex-ops); slugs mortos `sales-ai` e `gabinete` removidos; declarado registro canônico único
- `shared/knowledge/groups.md` deprecado (class volátil; superseded por `shared/groups.md`)
- `_meta/index.md` atualizado para apontar para o registro canônico
- `global/_meta/microversos.yaml` populado com backfill dos 5 microversos físicos (Fase 0, memory-v2)
