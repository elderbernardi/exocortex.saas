# Exocórtex.IA — Agent Communication Board

> **PURPOSE:** Structured message passing between AI agents across sessions.
> Any agent starting work MUST read this file first and check for pending messages.
> After completing work, agents MUST leave a summary here.

---

## Protocol

1. **Read all `PENDING` messages** before starting any work
2. **Mark messages as `READ`** after processing them
3. **Post new messages** at the bottom of the Inbox section
4. **Archive processed messages** by moving them to the Archive section

### Message Format

```markdown
### MSG-{NNN} | {timestamp}
- **From:** {agent-name}
- **To:** {target-agent | ALL}
- **Priority:** P0 | P1 | P2 | P3
- **Status:** PENDING | READ | RESOLVED
- **Subject:** {brief description}
- **Body:** {detailed message}
- **Action Required:** {what the recipient should do}
```

---

## Inbox

### MSG-002 | 2026-05-30T11:20
- **From:** antigravity
- **To:** ALL
- **Priority:** P0
- **Status:** PENDING
- **Subject:** PDD v2 é agora o plano ativo — v1 é read-only
- **Body:** O PDD v2 (`pdd_v2/PLAN.md`) substitui o v1 como plano ativo. Principais mudanças: 6 fases (P0-P5, era P0-P6), 27 prompts (era 31), drift audit em todas as fases, quality skills desde P1, MCPs movidos para BACKLOG. O provisioner (`pdd_v2/provisioner/`) é um pacote auto-contido para instalação automatizada. A retrospectiva completa está em `pdd_v2/RETROSPECTIVE.md`.
- **Action Required:** Próximo agente que for executar deve: (1) ler `pdd_v2/PLAN.md`, (2) verificar `STATUS.md`, (3) para provisioning: ler `pdd_v2/provisioner/RUNBOOK.md`. **Não use mais referências a `pdd/` como plano ativo.**

---

## Archive

### MSG-001 | 2025-05-25T23:30
- **From:** project-planner
- **To:** ALL
- **Priority:** P0
- **Status:** RESOLVED
- **Subject:** Plano PDD v1 criado — estrutura de plans/ inicializada
- **Body:** Criei a estrutura completa do plano PDD em `plans/pdd/`. Inclui 7 fases detalhadas (P0-P6), playbook YAML, e artefatos-semente (SOUL_SEED.md, SELF_TEST_SKILL.md). O plano é projetado para ser legível e executável por qualquer agente, incluindo agentes menos poderosos.
- **Action Required:** ~~Próximo agente que for executar deve: (1) ler `pdd/PLAN.md`, (2) verificar `STATUS.md`, (3) começar por P0_SETUP.md.~~ **Superseded by MSG-002.** Use `pdd_v2/PLAN.md` como referência ativa.
