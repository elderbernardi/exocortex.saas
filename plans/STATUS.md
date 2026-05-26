# Exocórtex.IA — Status Board

> **Last Updated:** 2025-05-25T23:30 (BRT)
> **Updated By:** project-planner

---

## 🔴 Current Focus

**Branch:** PDD (Prompt-Driven Development)
**Phase:** Pre-Execution (Planejamento)
**Blocker:** Nenhum — aguardando aprovação do plano PDD

---

## Branch Status

| Branch | Status | Current Phase | Next Action |
|---|---|---|---|
| **PDD** | 🟡 Planejamento | Pre-P0 | Aprovar plano → clonar Hermes → executar P0 |
| **Code** | ⚪ Não iniciado | — | Depende de validação do PDD na Alpha |

---

## Milestones

| Milestone | Target | Status |
|---|---|---|
| Plano PDD aprovado | Semana 1 | 🟡 Em revisão |
| Hermes clonado e funcional | Semana 1 | ⬜ Pendente |
| P0 (Setup) completo | Semana 1 | ⬜ Pendente |
| P1 (Identity) completo | Semana 2 | ⬜ Pendente |
| P2 (Memory) completo | Semana 2 | ⬜ Pendente |
| P3 (Tools) completo | Semana 3 | ⬜ Pendente |
| P4 (Behavior) completo | Semana 3 | ⬜ Pendente |
| P5 (Validation) completo | Semana 4 | ⬜ Pendente |
| Alpha "O Espelho" shipping | Semana 4 | ⬜ Pendente |

---

## Open Questions

| ID | Question | Owner | Status |
|---|---|---|---|
| Q001 | Docker base image para tenant: usar imagem oficial do Hermes ou build custom? | @elder | ⬜ Aberta |

---

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Hermes API muda upstream | Médio | Versionamento por tag, não por branch `main` |
| Prompt playbook não replicável | Alto | Self-test em todo checkpoint + Meta-Trainer |
| sqlite-vec limites de escala | Baixo (Alpha) | Migração Qdrant planejada para Beta |
