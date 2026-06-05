---
title: Matriz de versões operacionais
created: 2026-06-05
updated: 2026-06-05
nature: knowledge
kind: registry
scope_slug: exocortex-ops
authority: observed
stability: active
lifecycle_state: observed
tags: [versions, hermes, runtime]
---

# Matriz de versões operacionais

| Componente | Versão/estado observado | Comando/fonte | Última verificação |
|---|---|---|---|
| Hermes Agent | `v0.15.1 (2026.5.29)` | `hermes --version` | 2026-06-05 |
| Profile default | `running`, modelo CLI `gpt-5.4` | `hermes profile list` | 2026-06-05 |
| Sessão atual | modelo operacional `gpt-5.5` | metadado do runtime da sessão | 2026-06-05 |
| MCP NotebookLM | enabled | `hermes mcp list` | 2026-06-05 |
| Memory provider | built-in active, external none | `hermes memory status` | 2026-06-05 |

## Regra

Nunca responder sobre versões, profile ativo, providers ou MCPs sem verificar o runtime com ferramenta.
