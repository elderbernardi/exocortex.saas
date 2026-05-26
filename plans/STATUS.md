# Exocórtex.IA — Status Board

> **Last Updated:** 2026-05-26T12:30 (BRT)
> **Updated By:** antigravity (session audit + P1 completion)

---

## 🔴 Current Focus

**Branch:** PDD (Prompt-Driven Development)
**Phase:** Fase P2 (Memory) — pronto para iniciar
**Blocker:** Nenhum — P1 concluída, aguardando início de P2

---

## Branch Status

| Branch | Status | Current Phase | Next Action |
|---|---|---|---|
| **PDD** | 🟢 Execução | P2 | Iniciar Prompt 006 (Memory Architecture) |
| **Code** | ⚪ Não iniciado | — | Depende de validação do PDD na Alpha |

---

## Milestones

| Milestone | Target | Status |
|---|---|---|
| Plano PDD aprovado | Semana 1 | ✅ Completo |
| Hermes clonado e funcional | Semana 1 | ✅ Completo |
| P0 (Setup) completo | Semana 1 | ✅ Completo |
| P1 (Identity) completo | Semana 2 | ✅ Completo |
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
