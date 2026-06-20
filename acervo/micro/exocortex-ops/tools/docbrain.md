---
type: artifact
title: DocBrain Operacional
description: 'Instância funcional atual:'
tags: [docbrain, parser, intake]
timestamp: 2026-06-05
class: volátil
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
excrtx_type: tool
nature: tools
sources: ['conversation:docbrain-check']
confidence: high
created: 2026-06-05
---

# DocBrain operacional

## Estado operacional verificado

Instância funcional atual:

`/home/elder/exocortex/tools/docbrain`

Health check funcional:

`npm run --silent cli -- api health --output json`

## Decisão operacional

O runtime válido para este ambiente é `EXOCORTEX_HOME/tools/docbrain`, com override opcional via `EXOCORTEX_DOCBRAIN_DIR`.
A skill `excrtx-integrate-docbrain` e sua referência de instalação devem apontar para esse default e exigir resolução de workspace antes de qualquer parse.
