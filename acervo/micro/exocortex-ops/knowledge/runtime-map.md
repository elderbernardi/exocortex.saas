---
schema: acervo/v0.2
type: knowledge
title: Mapa de Runtime
description: Mapa operacional do runtime atual do Exocórtex sobre Hermes neste ambiente.
tags: [runtime, hermes, config, tools]
timestamp: 2026-06-05
class: volátil
status: active
epistemic: fact
created_at: 2026-06-05T18:08:35Z
last_accessed_at: 2026-06-05T18:08:35Z
updated: 2026-07-01
nature: knowledge
excrtx_type: fact
sources: ['command:hermes-tools-list', 'command:hermes-memory-status']
confidence: high
created: 2026-06-05
---

# Mapa de runtime

## Componentes

- Runtime: Hermes Agent.
- Identidade operacional: Exocórtex.IA.
- Acervo Cognitivo: `/home/ubuntu/exocortex/acervo`.
- Alias compatível do Acervo: `/home/ubuntu/.hermes/acervo`.
- Skills Exocórtex: `/home/ubuntu/.hermes/skills/excrtx`.
- Config principal: `/home/ubuntu/.hermes/config.yaml`.

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
