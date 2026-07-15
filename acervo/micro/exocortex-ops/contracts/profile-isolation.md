---
schema: acervo/v0.2
type: contract
title: Isolamento de Perfis Hermes
description: Perfis Hermes possuem skills, plugins, cron e memória próprios.
tags: [profiles, isolation, hermes]
timestamp: 2026-06-05
class: perene
status: active
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
excrtx_type: rule
nature: contracts
sources: ['system:profile-policy']
confidence: high
created: 2026-06-05
---

# Isolamento de perfis Hermes

Perfis Hermes possuem skills, plugins, cron e memória próprios.

## Regra

- O profile ativo governa as alterações locais.
- Alterar `~/.hermes/profiles/<name>/` exige pedido explícito quando não for o profile ativo.
- Diagnóstico pode ler paths de outros profiles quando necessário, mas escrita cross-profile exige autorização clara.

## Aplicação

Ao auditar setup ou manutenção, separar:

- estado do profile ativo;
- estado global em `~/.hermes`;
- estado de profiles nomeados.
