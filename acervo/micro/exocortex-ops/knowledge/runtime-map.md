---
title: Mapa de Runtime
created: 2026-06-05
updated: 2026-06-05
nature: knowledge
type: fact
tags: [runtime, hermes, config, tools]
sources: [command:hermes-tools-list, command:hermes-memory-status]
confidence: high
---

# Mapa de runtime

## Componentes

- Runtime: Hermes Agent.
- Identidade operacional: Exocórtex.IA.
- Acervo Cognitivo: `/home/elder/.hermes/acervo`.
- Skills Exocórtex: `/home/elder/.hermes/skills/exocortex`.
- Config principal: `/home/elder/.hermes/config.yaml`.

## Toolsets observados como habilitados

- web
- browser
- terminal
- file
- code_execution
- vision
- image_gen
- x_search
- moa
- tts
- skills
- todo
- memory
- session_search
- clarify
- delegation
- cronjob
- messaging

## MCPs observados

- notebooklm: configurado e com tools habilitadas.

## Regra

Antes de declarar estado operacional, verificar com ferramenta. Não responder de memória sobre runtime, paths, providers, tools ou data.
