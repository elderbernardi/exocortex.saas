---
title: Isolamento de Perfis Hermes
created: 2026-06-05
updated: 2026-06-05
nature: contracts
type: rule
tags: [profiles, isolation, hermes]
sources: [system:profile-policy]
confidence: high
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
