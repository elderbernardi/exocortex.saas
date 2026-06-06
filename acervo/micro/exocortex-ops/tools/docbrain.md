---
title: DocBrain Operacional
created: 2026-06-05
updated: 2026-06-05
nature: tools
type: tool
tags: [docbrain, parser, intake]
sources: [conversation:docbrain-check]
confidence: high
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
