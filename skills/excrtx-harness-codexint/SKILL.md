---
name: excrtx-harness-codexint
description: Integrate OpenAI Codex (CLI and provider) into Hermes/Exocórtex with
  governance, routing, and verification.
version: 0.2.0
category: excrtx
created_by: agent
context: exocortex
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - harness
    - codexint
    - codex
    - delegation
    related_skills:
    - excrtx-harness-core
    - excrtx-govern-tools
    - excrtx-govern-draftfirst
    calibration:
    - feature_id: EX-32
      calibration_prompt: Você deve garantir que as operações e regras da skill Codex
        Integration (excrtx-harness-codexint) estão totalmente ativas no seu comportamento
        e integridade.
      test_prompt: Verifique se a skill define os dois modos (CLI e provider).
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill Codex Integration.
      remediation_tip: Certifique-se de que a documentação e os limites da skill Codex
        Integration em seu SKILL.md estão sendo estritamente seguidos.
---
# Codex Integration — Hermes/Exocórtex

> Two tracks, one routing policy: Codex CLI (local terminal agent) vs Codex provider (Hermes subagent delegation).

## When to Use

Activate when:
- The executive wants to use their Codex subscription within Hermes
- A task needs delegation to Codex CLI (code/repo work) or Codex provider (general tasks)
- The gateway model changed and you need to verify Codex tracks still work

**Don't use for:** Tasks that don't involve Codex. General Hermes subagent delegation without Codex provider. Model selection or switching (use `excrtx-govern-tools`). Non-code CLI tools.

## Procedure

### 1. Classify the Task (Track Selection)

| Condition | Track | Tool |
|---|---|---|
| File/code changes in a git repo, refactoring, PR review, test execution | **Track A** — Codex CLI | `terminal` with `pty=true` |
| General task (research, synthesis, plan, comparison, checklist) + speed needed | **Track B** — Codex provider | `delegate_task(...)` |
| Hybrid: analysis + implementation + validation | **Both** | Decompose: decide here → implement via CLI → validate here |

### 2. Execute Track A (Codex CLI)

Prerequisites:
- Must be inside a git repo. If scratch work: `mktemp -d && cd $_ && git init`
- Always use `pty=true` when calling via terminal tool

Execution modes:
```bash
# One-shot (small, scoped changes)
codex exec '<prompt>'

# Full-auto (larger changes, sandboxed)
codex exec --full-auto '<prompt>'

# --yolo only with explicit executive approval
```

Prompt contract — always include:
1. **Objective** (1 line)
2. **Context** (paths, versions, constraints)
3. **Acceptance criteria** (what "done" means)
4. **Restrictions** (files/APIs to NOT touch)
5. **Validation commands** (test/lint/build to run)
6. **Required output**: list of changed files, per-file summary, commands + status, risks

### 3. Execute Track B (Hermes Provider Delegation)

Prerequisites:
- Discover model string: `hermes model` (don't guess)
- Configure `delegation.provider` + `delegation.model` to point to `openai-codex`

Prompt contract — always include:
1. **Subagent scope** (what it CAN and CANNOT do)
2. **Output format** (explicit structure)
3. **Sources** (can it use web/file/terminal? State clearly)
4. **Request assumptions list** (separate fact from inference)

### 4. Post-Execution Verification

After Track A (CLI):
```bash
git status      # clean vs dirty
git diff        # inspect changes
# Run tests/lint per stack
```
If failure: request incremental fix from Codex with context (log + diff).

After Track B (delegation):
- Validate output is actionable (not just prose)
- When commands are suggested: execute yourself or generate DRAFT if external action

### 5. Gateway Independence Check

Both tracks must work independently of the gateway's main model:
- Track A is always local (no gateway dependency)
- Track B depends only on `delegation.*` config, not `model.default/provider`

## Pitfalls

- **Git repo required**: Codex CLI refuses outside a git repo. For scratch work: `mktemp -d && cd $_ && git init`.
- **Missing pty=true**: Codex CLI needs interactive terminal. Always set `pty=true`.
- **Guessing model strings**: Don't guess `delegation.model` — discover via `hermes model` then configure.
- **Track confusion**: Main model provider ≠ delegation provider. Track A (CLI) ≠ Track B (provider). Keep them separate.
- **Missing evidence**: Always require Codex CLI to output changed files, commands run, and status. Don't accept "done" without proof.

## Verification

- [ ] Track A: `codex exec` runs inside a git repo and produces `git diff` output
- [ ] Track A: `pty=true` is set when calling via terminal tool
- [ ] Track B: `delegate_task` returns structured output matching the prompt contract
- [ ] Track B: Works regardless of the gateway's main model setting
- [ ] Hybrid: Decomposition follows decide→implement→validate sequence
- [ ] Post-execution: Test/lint commands are run after Track A changes

