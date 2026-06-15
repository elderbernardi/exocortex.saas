# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What This Repository Is

`exocortex.saas` is a **configuration and skill package** for the Hermes Agent runtime — not a traditional application. It packages custom behavioral skills, agent profiles, memory structures, and provisioning scripts that together form the **Exocórtex.IA** cognitive extension system.

The key distinction: Hermes is the runtime (CLI, memory, tool execution); Exocórtex is the identity, method, and behavior compiled on top of it.

---

## Common Commands

### Running the Agent

```bash
hermes                  # interactive session (exec + evol profile)
hermes -p manut         # maintenance profile (background housekeeping)
```

### After Modifying Any Skill

```bash
# Always run after editing a skill's compiled_rules: block
python3 scripts/compile_soul.py
```

### Skill Quality Audits

```bash
# D1 structural check only (no LLM keys required)
python3 scripts/skill_judge.py --skill excrtx-<name> --d1-only

# Full 5-dimension quality sweep (requires OPENROUTER_API_KEY or DEEPSEEK_API_KEY)
python3 scripts/skill_judge.py --skill excrtx-<name>
```

Verdict must be `PASS` before merging. `REWRITE` blocks the merge.

### Tests

```bash
# Python unit tests (requires pytest installed in active env)
python3 -m pytest tests/

# Dogfood scenario catalog validation (no LLM required)
bash scripts/test-registry.sh dogfood-catalog

# Dogfood P0/P1 features in safe mode
bash scripts/test-registry.sh dogfood-p0

# Full provisioning feature verification
bash scripts/run-provisioning-tests.sh
```

### Behavioral Calibration

```bash
bash scripts/calibrate-hermes.sh
```

### Environment Validation

```bash
bash scripts/validate-environment.sh            # human-readable report
bash scripts/validate-environment.sh --json     # JSON output for CI
bash scripts/validate-environment.sh --install  # attempt to install missing deps
```

### Provisioning

```bash
bash setup.sh                # interactive (npm-init style)
bash setup.sh --yes          # accept all defaults (CI/CD)
bash setup.sh --calibrate    # run cognitive calibration after install
```

---

## Architecture

### The Three Concentric Layers

1. **Macroverso** (`acervo/macro/SOUL.md`) — Executive "Constitution." Identity, values, tone, non-negotiables. Populated by the onboarding skill; governs everything. Changes rarely.
2. **Microversos** (`acervo/micro/<slug>/`) — Self-contained semantic domains (clients, projects, disciplines). Each has its own knowledge, context, decisions, workflows, and sharing constraints.
3. **Tarefa** — The active operational room. Short-lived. Anchored to a primary Microverso. A Microverso is never a room (EX-06).

### The Three Operational Vectors

Each input is silently classified by `excrtx-behavior-vetor` (EX-05) before any response:

| Vector | Posture | Trigger signals |
|---|---|---|
| **Execução (DO)** | Specialist agent, deliver artifact | Action verbs, deadlines, "faça X" |
| **Evolução (THINK)** | Socratic guide, ask before concluding | "estou pensando sobre...", open questions |
| **Manutenção (CLEAN)** | Housekeeper, verify/audit/clean | "revise pendências", cron-triggered |

Ambiguous inputs get a clarifying question, never an assumption.

### Skills System

All custom skills live in `skills/excrtx-*/SKILL.md`. Each must have:

**YAML Frontmatter:**
```yaml
---
name: excrtx-domain-action    # kebab-case, excrtx- prefix
description: English summary  # English required for searchability
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, ...]
    related_skills: [...]
compiled_rules: |             # injected into SOUL_SEED.md at compile time
  - Rule one...
  - Rule two...
---
```

**Required body sections:** `## When to Use`, `## Procedure`, `## Pitfalls`, `## Verification`

After editing `compiled_rules:`, always run `python3 scripts/compile_soul.py` to inject them into `SOUL_SEED.md`.

### Skill vs. MCP Decision (ADR-006)

- **Custom skill** (`skills/excrtx-*`): for behavioral governance, prompt-driven workflows, local scripting, no background daemons
- **MCP server** (`hermes mcp add`): for SaaS/third-party APIs, stateful services, structured data sources, OAuth-managed integrations

### Acervo Memory Structure

```
acervo/
  macro/         # Macroverso — executive constitution (SOUL.md)
  micro/<slug>/  # Microversos — semantic domains
    _meta/
    context/
    knowledge/
    decisions/
    workflows/
    contracts/
  global/        # System-wide shared knowledge (WELCOME.md, etc.)
  shared/        # Cross-microverso references allowed by sharing constraints
  _inbox/        # Multi-channel intake queue
  _artifacts/    # Durable produced documents
  _tasks/        # Active task boards
  _routines/     # Scheduled automation configs
  _automations/  # Background automation definitions
```

### Profiles and Bundles

- `profiles/chat/` — default interactive session (exec + evol)
- `profiles/manut/` — maintenance housekeeping session
- `skill-bundles/exocortex-alpha.yaml` — primary bundle loading all 40+ excrtx skills

### Execution Tracks (EX-34)

- **Trilho A** (Execution): direct tool calls, local script execution, compilation, staging validation — terminates with empirical verification (EX-49)
- **Trilho B** (Reasoning/Delegation): research, multi-agent orchestration, planning — uses parallel worker dispatch

---

## Key Governance Rules

### Draft-First Protocol (EX-08)

**Internal actions** (execute directly, no draft needed): `git commit`, `git add`, file edits, running tests/lint, read-only operations.

**External actions** (mandatory DRAFT before execution): `git push`, deploy, email, calendar events, shared document edits, Telegram messages to third parties, any communication on behalf of the executive.

Draft flow: generate payload → present as `📋 DRAFT` → halt → wait for explicit approval → execute.

### Accuracy Verification (EX-49)

Never claim an action succeeded without running an empirical verification command and printing its raw output as proof.

### Communication Language

All user-facing communication defaults to **PT-BR (Brazilian Portuguese)**. Technical names, commands, code, log output, and tool results may remain in their original language.

---

## Quality Evaluation Dimensions (skill_judge.py)

| Dimension | Method | Criteria |
|---|---|---|
| D1: Structural | Deterministic | Name format, YAML compliance, English description, required sections |
| D2: Clarity | LLM judge | Readability, absence of ambiguity |
| D3: Alignment | LLM judge | Consistency with SOUL_SEED.md behavioral contract |
| D4: Fitness | LLM judge | API edge case handling, input validation |
| D5: Economy | LLM judge | Prompt compactness, no bloat |

---

## Developer Reference

The primary developer documentation lives in the `exocortex-dev` Microverso:

- `acervo/micro/exocortex-dev/knowledge/architecture.md` — system architecture and Trilho A/B
- `acervo/micro/exocortex-dev/contracts/development-standards.md` — coding conventions and skill specs
- `acervo/micro/exocortex-dev/decisions/skill-vs-mcp-selection.md` — ADR-006
- `acervo/micro/exocortex-dev/workflows/create-custom-skill.md` — SOP-001: skill scaffolding
- `acervo/micro/exocortex-dev/workflows/run-preflight-checks.md` — SOP-002: preflight checks
