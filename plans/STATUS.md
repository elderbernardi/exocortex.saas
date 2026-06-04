# Exocórtex.IA — Status Board

> **Last Updated:** 2026-06-03T16:30:00-03:00
> **Updated By:** Exocórtex.IA sobre Hermes Agent (consolidação candidate-release)

---

## 🟢 Current Focus

**Branch:** main
**Phase:** Consolidação candidate-release em execução — decisões D000-D007 resolvidas
**Referência:** `docs/ADR/ADR-010-layered-deployment.md`, `docs/ADR/ADR-011-consolidation-decisions.md`
**Progresso:** Infraestrutura (Camada 1) criada — templates v0.4, scripts, setup.sh atualizado

---

## Branch Status

| Branch | Status | Current Phase | Next Action |
|---|---|---|---|
| **PDD v1** | ✅ Concluído (read-only) | P6 (final v1) | Referência histórica — ver `pdd/PLAN.md` |
| **PDD v2** | 🟡 Papel redefinido (checklist) | ADR-010: PDD = validação | Serve como checklist, não como blueprint |
| **main** | 🟢 Ativo | Candidate-release em execução | Completar Fase 3 (Identidade) e Fase 4 (Verificação) |
| **Code** | ⚪ Não iniciado | — | Após candidate-release validado |

---

## Modelo de Deployment (ADR-010)

> Abordagem em 3 camadas, cada uma independente.

| Camada | Responsabilidade | Frequência | Status |
|--------|-----------------|------------|--------|
| **1 — Infraestrutura** | Diretórios, skills, templates, scripts, bundles | Uma vez por instância | 🟢 Criada |
| **2 — Identidade** | SOUL.md, personas, valores, quality skills | Uma vez por instância | 🟡 Em andamento |
| **3 — Evolução** | Hindsight, memória, personalização contínua | Contínua | ⬜ Pós-release |

---

## Decisões Consolidadas (ADR-011)

| ID | Decisão | Resolução |
|----|---------|-----------|
| D000 | Deployment | Camadas (ADR-010) |
| D001 | PDD como checklist | ✅ Aceita |
| D002 | Rotinas/Automações | ✅ Criar _routines/_automations |
| D003 | Personas | ✅ Híbrido SOUL.md + templates + script |
| D004 | Setup-Plan vs PDD | ✅ Resolvido por ADR-010 |
| D005 | Scripts | ✅ 3 críticos agora, 5 pós-release |
| D006 | Memória | ✅ Camada 3 com Hindsight |
| D007 | Backlog | ✅ Adiar pós-release |

---

## Milestones

| Milestone | Target | Status |
|---|---|---|
| Plano PDD v1 aprovado | Semana 1 | ✅ Completo |
| Hermes clonado e funcional | Semana 1 | ✅ Completo |
| PDD v1 completo (P0-P6) | Semana 3 | ✅ Completo |
| PDD v1 → v2 Retrospectiva | Semana 4 | ✅ Completo |
| PDD v2 PLAN + Provisioner | Semana 4 | ✅ Completo |
| Personal Artifact Workspace documentado | Semana 4 | ✅ Completo |
| **Consolidação: inventário + matriz** | Semana 5 | ✅ Completo |
| **Consolidação: decisões D000-D007** | Semana 5 | ✅ Completo |
| **Consolidação: ADRs 010-011** | Semana 5 | ✅ Completo |
| **Consolidação: templates + scripts v0.4** | Semana 5 | ✅ Completo |
| **Consolidação: setup.sh atualizado** | Semana 5 | ✅ Completo |
| Candidate-release verificado (drift audit) | — | 🟡 Em andamento |
| Alpha "O Espelho" shipping | — | ⬜ Pendente |

---

## Open Questions

| ID | Question | Owner | Status |
|---|---|---|---|
| Q001 | Docker vs nativo: o target é ~/exocortex nativo? | @elder | ⬜ Aberta |
| Q002 | Approval-gate transacional: quando implementar? | @elder | ⬜ Aberta (proposta em hermes-setup/decisions/) |
| Q003 | Profile Manutenção: criar `manut` ou sub-modo? | @elder | ⬜ Aberta |
| Q004 | Estúdio criativo: entra no candidate-release? | @elder | ⬜ Aberta |

---

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Hermes API muda upstream | Médio | Versionamento por tag, não por branch `main` |
| Prompt playbook não replicável | Alto | ADR-010: PDD como checklist + Camada 1 setup.sh |
| sqlite-vec limites de escala | Baixo (Alpha) | Migração Qdrant planejada para Beta |
