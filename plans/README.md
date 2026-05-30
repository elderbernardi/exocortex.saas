# Exocórtex.IA — Plans Directory

> **PURPOSE:** This directory is the Source of Truth for all development plans, inter-agent communication, and accumulated knowledge for the Exocórtex.IA project.

## Directory Structure

```
plans/
├── README.md                    ← You are here
├── STATUS.md                    ← Global project status board
├── DECISIONS.md                 ← Architectural Decision Records (ADRs)
├── KNOWLEDGE.md                 ← Accumulated discoveries and learnings
├── COMMS.md                     ← Inter-agent message board
│
├── pdd_v2/                      ← PDD v2 (PLANO ATIVO)
│   ├── PLAN.md                  ← Master plan for PDD v2
│   ├── PLAYBOOK.yaml            ← Executable prompt sequence (27 prompts)
│   ├── RETROSPECTIVE.md         ← Análise de drift v1 → v2
│   ├── DOCKER_TEST.md           ← Ambiente de teste Docker isolado
│   ├── STYLE_SET_CHANGELOG.md   ← Changelog do design system visual
│   ├── ARTIFACT_WORKSPACE.md    ← Addendum: publicação de artefatos finais no Drive via Acervo
│   ├── phases/                  ← One file per phase (P0-P5)
│   │   ├── P0_FOUNDATION.md
│   │   ├── P1_IDENTITY.md
│   │   ├── P2_MEMORY.md
│   │   ├── P3_BEHAVIOR.md
│   │   ├── P4_VALIDATION.md
│   │   └── P5_PRODUCTION.md
│   ├── artifacts/               ← Golden image autocontida
│   │   ├── setup.sh             ← Script de provisioning
│   │   ├── SOUL_SEED.md         ← Template de identidade
│   │   ├── BACKLOG_TEMPLATE.md  ← Template de integrações futuras
│   │   ├── skills/              ← 15 skills (espelho de ~/.hermes/skills/)
│   │   ├── acervo/              ← 4 camadas (macro/global/micro/shared)
│   │   ├── profiles/            ← exec/ e evol/
│   │   └── skill-bundles/       ← exocortex-alpha.yaml
│   ├── provisioner/             ← Pacote de automação de instalação
│   │   ├── RUNBOOK.md           ← Documento executável (agente lê isto)
│   │   ├── README.md            ← Instruções do provisioner
│   │   ├── lib/                 ← Scripts: detect, verify, drift audit
│   │   ├── prompts/             ← 27 prompts atomizados por fase
│   │   ├── docker/              ← Compose + entrypoint
│   │   └── state/               ← Controle de idempotência (P{N}.done)
│   ├── dist/                    ← Pacote distribuível (tar.gz)
│   └── logs/                    ← Session logs por fase
│
├── pdd/                         ← PDD v1 (READ-ONLY, referência histórica)
│   ├── PLAN.md                  ← Plano original (31 prompts, 7 fases P0-P6)
│   ├── PLAYBOOK.yaml            ← Playbook v1.1.0
│   ├── BACKLOG_INTEGRATIONS.md  ← MCPs diferidos
│   ├── phases/                  ← Fases v1 (P0_SETUP → P6_PRODUCTION)
│   ├── artifacts/               ← SOUL_SEED.md, SELF_TEST_SKILL.md
│   └── logs/                    ← Session logs v1
│
└── code/                        ← Code Branch (Plugins, MCP, Infra)
    └── PLAN.md                  ← Master plan for code branch
```

## How to Read This

### For Humans
Start with `STATUS.md` for current progress, then read `pdd_v2/PLAN.md` (plano ativo).

### For AI Agents
1. **ALWAYS read `STATUS.md` first** to understand current state
2. **Read `COMMS.md`** for pending messages or instructions from other agents
3. **Read `pdd_v2/PLAN.md`** for the active PDD plan (v1 is read-only history)
4. **Check `KNOWLEDGE.md`** before researching something that may already be documented
5. **For artifact publication:** read `pdd_v2/ARTIFACT_WORKSPACE.md` and the microverso `hermes-setup`
6. **Update `COMMS.md`** with findings or blockers for other agents
7. **If provisioning:** Read `pdd_v2/provisioner/RUNBOOK.md`

> **⚠️ PDD v1 (`pdd/`) is frozen.** All active work uses `pdd_v2/`. See `pdd_v2/RETROSPECTIVE.md` for the rationale.

## Conventions

| Convention | Rule |
|---|---|
| **Language** | Plans in Portuguese (user's language). Code comments in English. |
| **Status Tags** | `[ ]` TODO, `[/]` In Progress, `[x]` Done, `[!]` Blocked, `[?]` Needs Clarification |
| **Priority** | `P0` Critical, `P1` High, `P2` Medium, `P3` Low |
| **File Links** | Always use relative paths from `plans/` root |
| **Timestamps** | ISO 8601 (YYYY-MM-DDTHH:MM) in America/Sao_Paulo timezone |
