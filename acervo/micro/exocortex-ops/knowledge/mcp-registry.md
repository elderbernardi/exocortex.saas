---
type: knowledge
title: Registro de MCPs
description: '| Nome | Transporte | Tools | Status | Auth | Health check | Modo degradado |'
tags: [mcp, notebooklm, integrations]
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

# Registro de MCPs

| Nome | Transporte | Tools | Status | Auth | Health check | Modo degradado |
|---|---|---|---|---|---|---|
| `notebooklm` | `notebooklm-mcp` | all | enabled | tokens NotebookLM | `hermes mcp list`; `mcp_notebooklm_server_info` quando necessário | registrar fonte local e adiar import/query |

## Política

Adicionar, remover ou reconfigurar MCP exige DRAFT quando muda comportamento futuro, autenticação ou superfície externa.
