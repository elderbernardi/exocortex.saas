# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What This Repository Is

`exocortex.saas` is a **configuration and skill package** for the Hermes Agent runtime — not a traditional application. It packages custom behavioral skills, agent profiles, memory structures, and provisioning scripts that together form the **Exocórtex.IA** cognitive extension system.

The key distinction: Hermes is the runtime (CLI, memory, tool execution); Exocórtex is the identity, method, and behavior compiled on top of it.

---

## Working Discipline

Behavioral guidelines for changing code here. They bias toward caution over speed; for trivial tasks, use judgment.

### 1. Think before coding

Don't assume. Don't hide confusion. Surface tradeoffs.

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If something is unclear, stop, name what's confusing, and ask.

This mirrors the **Evolução** vector: when the path is ambiguous, ask before concluding rather than fabricating a direction.

### 2. Simplicity in code, fidelity in reasoning

Write the minimum code that solves the problem. Nothing speculative — no unrequested abstractions, configurability, or error handling for impossible scenarios. If 200 lines could be 50, rewrite it. Ask: "Would a senior engineer call this overcomplicated?"

**Important distinction** — this applies to *code and prompts*, not to *analysis*. SOUL_SEED.md's rule "nunca simplificar sem justificativa" governs reasoning and communication: never drop nuance to look clearer. Keep skill prompts compact (D5: Economy rewards this), but preserve the complexity of the actual problem when explaining it.

### 3. Surgical changes

Touch only what you must. Clean up only your own mess.

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor what isn't broken. Match existing skill conventions even if you'd do it differently.
- Remove imports/variables your changes orphaned; leave pre-existing dead code unless asked.
- Every changed line should trace directly to the request.

**Repo-specific:** the Hermes runtime config files (`SOUL_SEED.md`, `FEATURES.md`, `skills/`, `profiles/`, `install.sh`, `setup.sh`, `acervo/`) follow Hermes conventions and must **not** be reshaped to fit external/monorepo style — see `HARNESS.md`. Note that `SOUL_SEED.md` is partly generated: edit skills' `compiled_rules:` and regenerate via `compile_soul.py` rather than hand-editing the compiled block.

### 4. Goal-driven execution

Define success criteria, then loop until verified.

- "Add a skill" → "D1 structural check passes, then full `skill_judge` verdict is PASS"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- For multi-step work, state a brief plan with a `verify:` check per step.

This is the code-level form of **EX-49**: never claim something works without printing the verification command's raw output as proof.

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

### Frontmatter Validation & Migration

```bash
# Validate a single Acervo file or an entire directory tree
python3 scripts/validate_frontmatter.py <path>
# Exit 0 = pass (WARN allowed); Exit 1 = one or more ERROR rules failed

# One-time migration of legacy frontmatter to the OKF v0.1 superset schema
# (adds type, timestamp, class, created_at; renames old type → excrtx_type)
python3 scripts/migrate_frontmatter.py <path>
```

The schema is documented in `docs/plans/2026-06-19_acervo-lifecycle-okf/SCHEMA.md` (canonical reference) and `docs/plans/2026-06-19_acervo-lifecycle-okf/schema-spec.md` (detailed spec with migration derivation rules). Decision: ADR-013.

A full v2 redesign of the memory system (schema v0.2, episodes/entities/intentions, conflict-as-state, consolidation loop) is specified in `docs/plans/2026-07-03_memory-v2-spec/` — status: proposed (ADR-023).

### Skill Quality Audits

```bash
# D1 structural check only (no LLM keys required)
python3 scripts/skill_judge.py --skill excrtx-<name> --d1-only

# Full 5-dimension quality sweep — uses the central 'default' LLM role
# (EXOCORTEX_DEFAULT_PROVIDER/MODEL/API_KEY/BASE_URL, resolved by
# scripts/lib/llm_roles.py). Configure it via `bash setup.sh` or the .env.local.
# `--model` overrides just the model; `--list-models` lists the default role
# provider's models.
python3 scripts/skill_judge.py --skill excrtx-<name>
python3 scripts/skill_judge.py --skill excrtx-<name> --model <model-id>
```

The 3 LLM roles (**default** / **vision** / **auxiliar**) are the single source of
truth for every LLM call in this repo. `default` is always used; `vision` and
`auxiliar` inherit `default` field-by-field when unset. The provider catalog lives
in `setup/providers.json`; the resolvers are `scripts/lib/llm_roles.py` (Python) and
`setup/lib/llm-roles.sh` (shell). Legacy keys (`OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`,
`DOCBRAIN_LLM_API_KEY`, …) are migrated once into the roles by
`scripts/migrate-env-roles.py` (run automatically by `setup.sh`).

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

### Memory Lifecycle Skills

The Acervo's autonomous lifecycle is implemented by three skills that work with `excrtx-memory-manager`:

| Skill | Role | Trigger |
|-------|------|---------|
| `excrtx-memory-deprecate` | Semantic revision on insert — detects contradictions between a new memory and existing ones, deprecates superseded `volátil` files automatically, flags ambiguous overlaps for review | Called by `excrtx-memory-manager` WRITE before commit (ADR-016) |
| `excrtx-memory-quarantine` | Moves stale/deprecated files to `.quarantine/`, sets quarantine frontmatter fields, logs the movement | Called by the syndic or executive |
| `excrtx-memory-syndic` | Autonomous scan → quarantine → purge cycle. Runs under the `manut` profile on a schedule (ADR-018) | Cron-triggered |

`excrtx-memory-manager` orchestrates: WRITE calls `excrtx-memory-deprecate` before commit; SEARCH skips `deprecated: true` files and `.quarantine/` entirely; READ updates `last_accessed_at`.

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
  .quarantine/   # Stale/deprecated files awaiting purge (30-day window; ADR-015)
                 #   NOT part of active memory — search skips this entirely
  _inbox/        # Multi-channel intake queue
  _artifacts/    # Durable produced documents
  _tasks/        # Active task boards
  _routines/     # Scheduled automation configs
  _automations/  # Background automation definitions
```

### Frontmatter Schema (OKF v0.1 Aligned)

Every Acervo markdown file carries YAML frontmatter conforming to a **superset of the Open Knowledge Format (OKF v0.1)**. Two mandatory tiers plus conditional lifecycle fields:

- **OKF Canonical** (mandatory): `type`, `title`, `description`, `tags`, `timestamp`
- **Acervo Extension** (lifecycle): `class` (`perene` | `volátil`), `created_at`, `last_accessed_at`, `promoted_at`
- **Conditional**: deprecation (`deprecated`, `deprecated_at`, `deprecated_reason`) and quarantine (`quarantined_at`, `quarantine_reason`, `quarantine_expires_at`)

**Canonical reference:** `docs/plans/2026-06-19_acervo-lifecycle-okf/SCHEMA.md`

**`type` vs `excrtx_type` vs `nature`** — three orthogonal classification fields:
- `type` — OKF concept type (`decision`, `memory`, `reflection`, `context`, `knowledge`, `artifact`). Mandatory, interoperable.
- `excrtx_type` — legacy Acervo type (`fact`, `rule`, `workflow`, `tool`, ...), preserved from pre-migration. The old `type` was renamed to `excrtx_type` during migration to avoid collision with the OKF `type` field.
- `nature` — directory routing key used by `excrtx-memory-manager` (e.g. `knowledge`, `contracts`, `workflows`). Coexists with `type`.

### Memory Lifecycle: Deprecation, Quarantine, Syndic

The Acervo has an autonomous lifecycle governed by the `class` frontmatter field:

- **`perene`** — permanent truth (decisions, architecture, identity). Never auto-deprecated or quarantined.
- **`volátil`** — transient state (configs, prices, defaults). Candidate for deprecation when superseded; candidate for quarantine when stale.

Lifecycle flow: `SCAN → QUARANTINE → PURGE` (ADR-015). No file is deleted directly.

- **Deprecation (ADR-014):** when a new memory contradicts an existing `volátil` one, the old is marked `deprecated: true` (not deleted). Triggered by the semantic revision hook (ADR-016) — `excrtx-memory-manager` calls `excrtx-memory-deprecate` before committing a WRITE.
- **Quarantine (ADR-015):** the syndic (ADR-018, autonomous, runs under `manut`) moves stale files (`last_accessed_at` > 90 days) or long-deprecated files (`deprecated_at` > 180 days) to `.quarantine/`. Files gain `quarantined_at`, `quarantine_reason`, `quarantine_expires_at` (30-day purge window).
- **Purge:** after 30 days without restore, the file is permanently deleted. Irreversible.
- **Restore:** executive can restore a quarantined file within the 30-day window.

Each container (`micro/{slug}/`, `global/`, `shared/`) has an append-only `_meta/log.md` recording lifecycle events (`CREATED`, `UPDATED`, `DEPRECATED`, `PROMOTED`, `QUARANTINED`, `PURGED`, `RESTORED`). See `log-convention.md`.

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
