# Exocórtex.IA — Plano Code Branch

> **Branch:** Code — Plugins, MCP Servers, Infrastructure
> **Status:** ⚪ Não Iniciado (depende da validação PDD Alpha)
> **Owner:** @elder

---

## Quando Ativar

Esta branch é ativada quando o PDD Branch atinge seus limites — quando funcionalidades necessárias não podem ser implementadas apenas com prompts e skills.

**Triggers de ativação:**
- Multi-tenant control plane (Docker orchestration)
- HITL Cockpit web (approval UI)
- Custom MCP servers (Python code)
- Performance/scale requirements

---

## Epics (Referência do Implementation Plan)

| Epic | Escopo | Depende de PDD |
|---|---|---|
| E3 — Draft-First HITL Plugin | Approval API + Queue | P4 (skill como MVP) |
| E4 — Multi-Tenant Control Plane | Provisioner Agent + Intake Control Plane + Registry | P6 (golden image) |
| E5 — External Integration MCPs | Google Workspace, Corp Insights | P3 (tool governance) |
| E6 — Cognitive Studio & HITL Cockpit | Next.js Web UI | E3 + E4 |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Custom Plugins | Python (Hermes plugin API) |
| MCP Servers | Python (`mcp` SDK) |
| Control Plane | FastAPI + SQLite/Postgres |
| Web UI | Next.js 15 |
| Containerization | Docker Compose → Kubernetes |

---

## Detalhamento

Seed já implementada no projeto: `apps/intake_control_plane/` fornece um control plane local mínimo, contrato do `IntakeEnvelope` e dropzone demo. Na transição para Code Branch, esse seed pode ser migrado para FastAPI + persistência sem quebrar o contrato externo.

Ver `../pdd/PLAN.md` para o plano ativo atual.
