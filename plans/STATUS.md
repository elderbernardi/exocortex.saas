# Exocórtex.IA — Status Board

> **Last Updated:** 2026-05-30T15:03 (BRT)
> **Updated By:** Exocórtex (Personal Artifact Workspace docs)

---

## 🔴 Current Focus

**Branch:** PDD v2 (Prompt-Driven Development)
**Phase:** PDD v2 — Provisioner pronto, aguardando execução em instância limpa
**Blocker:** Nenhum
**Referência:** `pdd_v2/PLAN.md` (plano ativo), `pdd_v2/RETROSPECTIVE.md` (análise de drift v1 → v2), `pdd_v2/ARTIFACT_WORKSPACE.md` (addendum pós-graduação para artefatos finais)

---

## Branch Status

| Branch | Status | Current Phase | Next Action |
|---|---|---|---|
| **PDD v1** | ✅ Concluído (read-only) | P6 (final v1) | Referência histórica — ver `pdd/PLAN.md` |
| **PDD v2** | 🟢 Ativo | Provisioner pronto | Executar PDD v2 em instância limpa (Docker ou local) |
| **Code** | ⚪ Não iniciado | — | Depende de validação do PDD v2 na Alpha |

---

## Fases PDD v2

> Estrutura reduzida: 6 fases (P0-P5, era P0-P6 no v1), 27 prompts (era 31).
> Drift audit obrigatório em todas as fases. Quality skills desde P1.

| Fase | Nome | Prompts | Gate | Descrição |
|------|------|---------|------|-----------|
| **P0** | Foundation | 0 (manual) | artifacts + setup.sh | Pré-requisitos, agent_protocol, golden image semente |
| **P1** | Identity | 001–005 | self-test ≥ 2/5 | SOUL.md, quality skills (stop-slop + taste-skill) |
| **P2** | Memory | 006–012 | self-test ≥ 3/5 | Acervo 4 camadas, acervo-manager unificado |
| **P3** | Behavior | 013–021 | self-test ≥ 4/5 | Skills de negócio, bundle, profiles (sem MCPs) |
| **P4** | Validation | 022–026 | self-test = 5/5 | Smoke tests, quality gate, drift audit final |
| **P5** | Production | 027 | GRADUATION | Golden image final, estado PRODUCTION |

---

## Milestones

| Milestone | Target | Status |
|---|---|---|
| Plano PDD v1 aprovado | Semana 1 | ✅ Completo |
| Hermes clonado e funcional | Semana 1 | ✅ Completo |
| PDD v1 P0 (Setup) completo | Semana 1 | ✅ Completo |
| PDD v1 P1 (Identity) completo | Semana 2 | ✅ Completo |
| PDD v1 P2 (Memory) completo | Semana 2 | ✅ Completo |
| PDD v1 P3 (Tools) completo | Semana 3 | ✅ Completo |
| PDD v1 P4 (Behavior) completo | Semana 3 | ✅ Completo |
| PDD v1 → v2 Retrospectiva | Semana 4 | ✅ Completo |
| PDD v2 PLAN + Provisioner | Semana 4 | ✅ Completo |
| Personal Artifact Workspace documentado | Semana 4 | ✅ Completo |
| PDD v2 execução em instância limpa | — | ⬜ Pendente |
| Alpha "O Espelho" shipping | — | ⬜ Pendente |

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
| Prompt playbook não replicável | Alto | Self-test em todo checkpoint + Provisioner Agent (dedicado) + Drift Audit v2 |
| sqlite-vec limites de escala | Baixo (Alpha) | Migração Qdrant planejada para Beta |
