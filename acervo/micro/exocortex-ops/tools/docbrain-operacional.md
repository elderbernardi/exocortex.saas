---
schema: acervo/v0.2
type: tool
title: DocBrain Operacional
description: Instância funcional atual do DocBrain atualizada para o repositório canônico elderbernardi/docbrain.
tags: [docbrain, parser, intake]
timestamp: 2026-06-05
class: volátil
status: active
created_at: 2026-06-05T00:00:00Z
created: 2026-06-05
updated: 2026-07-01
nature: tools
excrtx_type: tool
confidence: high
sources: ['conversation:docbrain-check', 'repo:https://github.com/elderbernardi/docbrain.git']
---

# DocBrain operacional

## Estado operacional verificado

Instância funcional atual:

`/home/ubuntu/exocortex/tools/docbrain`

Link de compatibilidade mantido:

`/home/ubuntu/exocortex/docBrain` → `/home/ubuntu/exocortex/tools/docbrain`

Repositório canônico verificado:

`https://github.com/elderbernardi/docbrain.git`

Branch validada:

`master`

Commit validado:

`474873020af25e06589356b8043388a6fbde1767`

Health check funcional:

`npm run --silent cli -- api health --output json`

Validação executada:

- `npm run --silent cli -- api health --output json`
- `npx vitest run --pool=forks`
- `npm run lint`
- `npm run build`

## Decisão operacional

O runtime válido para este ambiente é `EXOCORTEX_HOME/tools/docbrain`, com override opcional via `EXOCORTEX_DOCBRAIN_DIR`.

A skill `excrtx-integrate-docbrain` e sua referência de instalação devem apontar para o repositório `elderbernardi/docbrain`, usar `origin master` e tratar `README.md`, `HARNESS.md`, `schema.md` e `plans/ARCHITECTURE.md` como arquivos canônicos do projeto atual.
