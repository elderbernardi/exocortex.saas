# Exocórtex.IA — Status Board

> **Last Updated:** 2026-05-27T00:18 (BRT)
> **Updated By:** antigravity (P4 skill creation + provisioning model fix)

---

## 🔴 Current Focus

**Branch:** PDD (Prompt-Driven Development)
**Phase:** Fase P4 (Behavior) — 019-024 concluídos, 025-026 pendentes
**Blocker:** Nenhum — skills P4 criadas, aguardando testes comportamentais em Hermes

---

## Branch Status

| Branch | Status | Current Phase | Next Action |
|---|---|---|---|
| **PDD** | 🟢 Execução | P4 | Testes comportamentais (Prompt 025) + Checkpoint (026) |
| **Code** | ⚪ Não iniciado | — | Depende de validação do PDD na Alpha |

---

## Milestones

| Milestone | Target | Status |
|---|---|---|
| Plano PDD aprovado | Semana 1 | ✅ Completo |
| Hermes clonado e funcional | Semana 1 | ✅ Completo |
| P0 (Setup) completo | Semana 1 | ✅ Completo |
| P1 (Identity) completo | Semana 2 | ✅ Completo |
| P2 (Memory) completo | Semana 2 | ✅ Completo |
| P3 (Tools) completo | Semana 3 | ✅ Completo |
| P4 (Behavior) completo | Semana 3 | 🟡 Em Progresso |
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
| Prompt playbook não replicável | Alto | Self-test em todo checkpoint + Provisioner Agent (dedicado) |
| sqlite-vec limites de escala | Baixo (Alpha) | Migração Qdrant planejada para Beta |
