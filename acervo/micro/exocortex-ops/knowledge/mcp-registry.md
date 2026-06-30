---
type: knowledge
title: Registro de MCPs
description: '| Nome | Transporte | Tools | Status | Auth | Health check | Modo degradado |'
tags: [mcp, notebooklm, acervo, integrations]
timestamp: 2026-06-05
class: volátil
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-28T00:00:00Z
updated: 2026-06-28
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
| `acervo` | `python3 scripts/acervo_mcp_server.py` | 10 semantic tools (`list`, `search`, `read`, `prepare`, `commit`, `create`, `update`, `validate`, `export`) | enabled | local filesystem only | `python3 scripts/acervo_mcp_server.py --self-test --acervo-root "$ACERVO"`; `hermes mcp test acervo`; `hermes mcp list` | usar `python3 scripts/acervoctl.py` e acesso direto a arquivos para humano/infra/manutenção até o MCP voltar |

## Política

- Adicionar, remover ou reconfigurar MCP exige DRAFT quando muda comportamento futuro, autenticação ou superfície externa.
- Para o MCP `acervo`, a regra operacional é: **agente em superfície Hermes** → MCP; **script/teste/adaptador local** → `python3 scripts/acervoctl.py`; **humano/infra/manutenção corretiva** → acesso direto a arquivo continua válido.
- Se `hermes mcp test acervo` falhar, o sistema entra em modo degradado explícito: usar `acervoctl` e filesystem, nunca inventar uma segunda semântica paralela.
