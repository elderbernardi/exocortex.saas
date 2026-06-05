---
title: Registro de MCPs
created: 2026-06-05
updated: 2026-06-05
nature: knowledge
kind: registry
scope_slug: exocortex-ops
authority: observed
stability: active
lifecycle_state: observed
tags: [mcp, notebooklm, integrations]
---

# Registro de MCPs

| Nome | Transporte | Tools | Status | Auth | Health check | Modo degradado |
|---|---|---|---|---|---|---|
| `notebooklm` | `notebooklm-mcp` | all | enabled | tokens NotebookLM | `hermes mcp list`; `mcp_notebooklm_server_info` quando necessário | registrar fonte local e adiar import/query |

## Política

Adicionar, remover ou reconfigurar MCP exige DRAFT quando muda comportamento futuro, autenticação ou superfície externa.
