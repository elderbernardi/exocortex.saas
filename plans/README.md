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
├── pdd/                         ← Prompt-Driven Development Branch
│   ├── PLAN.md                  ← Master plan for PDD branch
│   ├── PLAYBOOK.yaml            ← Executable prompt sequence
│   ├── phases/                  ← One file per phase
│   │   ├── P0_SETUP.md
│   │   ├── P1_IDENTITY.md
│   │   ├── P2_MEMORY.md
│   │   ├── P3_TOOLS.md
│   │   ├── P4_BEHAVIOR.md
│   │   ├── P5_VALIDATION.md
│   │   └── P6_PRODUCTION.md
│   └── artifacts/               ← Templates, SOUL.md seeds, skill files
│       ├── SOUL_SEED.md
│       └── SELF_TEST_SKILL.md
│
└── code/                        ← Code Branch (Plugins, MCP, Infra)
    └── PLAN.md                  ← Master plan for code branch
```

## How to Read This

### For Humans
Start with `STATUS.md` for current progress, then read the relevant branch `PLAN.md`.

### For AI Agents
1. **ALWAYS read `STATUS.md` first** to understand current state
2. **Read `COMMS.md`** for pending messages or instructions from other agents
3. **Read the relevant `PLAN.md`** for the branch you are working on
4. **Check `KNOWLEDGE.md`** before researching something that may already be documented
5. **Update `COMMS.md`** with findings or blockers for other agents

## Conventions

| Convention | Rule |
|---|---|
| **Language** | Plans in Portuguese (user's language). Code comments in English. |
| **Status Tags** | `[ ]` TODO, `[/]` In Progress, `[x]` Done, `[!]` Blocked, `[?]` Needs Clarification |
| **Priority** | `P0` Critical, `P1` High, `P2` Medium, `P3` Low |
| **File Links** | Always use relative paths from `plans/` root |
| **Timestamps** | ISO 8601 (YYYY-MM-DDTHH:MM) in America/Sao_Paulo timezone |
