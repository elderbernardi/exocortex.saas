---
type: knowledge
title: Registro de profiles Hermes
description: '| Profile | Estado | Modelo reportado | Finalidade operacional | Risco | Observação |'
tags: [hermes, profiles, runtime, isolamento]
timestamp: 2026-06-05
class: volátil
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
nature: knowledge
kind: registry
scope_slug: exocortex-ops
authority: observed
stability: active
lifecycle_state: observed
created: 2026-06-05
---

# Registro de profiles Hermes

## Profiles observados em 2026-06-05

| Profile | Estado | Modelo reportado | Finalidade operacional | Risco | Observação |
|---|---|---|---|---|---|
| `default` | running | `gpt-5.4` no CLI | Interativo principal | médio | Sessão atual informa gpt-5.5 via OpenAI Codex; auditar drift de config. |
| `manut` | stopped | não reportado | Zelador/background | médio | Alterações em profile separado exigem instrução explícita. |

## Regra

O profile ativo não altera skills, plugins, cron ou memories de outro profile sem autorização explícita do executivo.

## Health check

```bash
hermes profile list
```
