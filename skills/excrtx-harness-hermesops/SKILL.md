---
name: excrtx-harness-hermesops
description: Operate Codex in the Hermes/Exocórtex ecosystem with two tracks (delegation
  vs CLI), with local evidence and safety patterns.
version: 1.0.0
category: excrtx
platforms:
- linux
author: Exocórtex
metadata:
  hermes:
    tags:
    - codex
    - hermes
    - delegation
    - cli
    - harness
    - evidence
    - safety
    related_skills:
    - excrtx-harness-core
    - excrtx-govern-tools
    calibration:
    - feature_id: EX-34
      calibration_prompt: Você deve garantir que as operações e regras da skill Hermes
        Ops (excrtx-harness-hermesops) estão totalmente ativas no seu comportamento
        e integridade.
      test_prompt: Verifique se a skill define Trilho A (CLI) e Trilho B (Delegação).
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill Hermes Ops.
      remediation_tip: Certifique-se de que a documentação e os limites da skill Hermes
        Ops em seu SKILL.md estão sendo estritamente seguidos.
---
# Codex Ops (Hermes)

Class-level skill to integrate and operate Codex within Hermes/Exocórtex.
Goal: **leverage the Codex subscription** consistently, verifiably, and safely.

## When to Use

Use this skill when the executive asks for anything like:
- "quero usar minha assinatura do Codex aqui"
- "delegue pro Codex"
- "integre Codex no Hermes"
- "faça o Codex codar/refatorar/executar comandos"
- "use Codex só para pensar/planejar"

Routing heuristic:
- "needs to write/edit files / touch repo" → TRACK A
- "needs to think/plan/summarize" → TRACK B
- Hybrid → decompose: TRACK B (plan) → TRACK A (execution) → verify

**Don't use for:** Direct CLI Codex execution in a git repo (use `excrtx-harness-core`). Tool configuration or model switching (use `excrtx-govern-tools`). Non-Codex Hermes subagent delegation.

## Principle: Two Tracks (never mix)

Always explicitly declare which track you're using.

TRACK A — Codex CLI (execution)
- When: edit/create files, run commands, touch a repository, review with diffs.
- Preferred method: **homegrown wrapper** that captures local evidence (JSON) to disk.

TRACK B — Delegation via provider (reasoning/planning)
- When: analysis, synthesis, plan, checklist, alternatives, hypotheses.
- Method: `delegate_task` with provider `openai-codex` (independent of the gateway's main model).

## TRACK B — Configure and Use Delegation via openai-codex

1) Verify credentials
- Run: `hermes auth list`
- Criterion: `openai-codex` must exist.

2) Set delegation provider/model
- `hermes config set delegation.provider openai-codex`
- `hermes config set delegation.model gpt-5.2` (or another stable model available in the provider)

3) Delegate with minimum contract
Every delegation must contain:
- Objective + acceptance criteria
- Explicit restrictions (e.g., "don't change deps", "don't touch X")
- If subsequent execution is needed: expected output format (checklist, steps, commands)

## TRACK A — Codex CLI with Local Evidence (wrapper)

Preference: use the homegrown wrapper to run `codex exec` and record evidence.

Architecture (stable paths):
- Runner: `~/.hermes/scripts/codex_learning/run_codex_with_learning.py`
- Review: `~/.hermes/scripts/codex_learning/review_latest_run.py`
- Evidence: `~/.hermes/codex-learning/`
  - `runs/` (JSON per execution)
  - `events/` (start/end)

Safe usage (default):
- By default, use `--scratch` for arbitrary tasks.
- Only use `--cd <repo>` when the executive explicitly points to the path and accepts the risk.

Write permissions (critical gotcha):
- Without `--full-auto`/`--yolo`, Codex can fall into read-only sandbox.
- If the task requires writing files: pass `--full-auto`.
  - The wrapper maps `--full-auto` to `codex exec --sandbox workspace-write`.

## Verification (don't trust "done")

After TRACK A, always check local evidence.

Minimum checklist:
- `git_status_porcelain` exists in the JSON
- `git_changed_files` includes **untracked** (new files) — don't use `git diff --name-only` as sole source
- `git_untracked_files` explicitly captured
- `git_diff_stat` recorded

In real repos:
- Run project tests/build and record output/exit code.

## Pitfalls

- **Untracked files don't appear in diff:** `git diff --name-only` doesn't list `??` files. Use `git status --porcelain` (or wrapper evidence) to enumerate all changes.
- **Scratch can be read-only:** If writes are expected, declare and enable `--full-auto`. Without it, Codex falls into read-only sandbox.
- **No evidence = no proof:** Require wrapper JSON as proof of execution, not narrative. If evidence JSON doesn't exist, the task didn't run.
- **Track mixing:** Never mix TRACK A and TRACK B in the same step. Declare explicitly before execution.

## Procedure

1. Classify intent using the routing heuristic in "When to Use"
2. Execute using the appropriate track section above (TRACK A or TRACK B)
3. For hybrid tasks: TRACK B first (plan) → TRACK A (execute) → verify
4. Post-execution: `python ~/.hermes/scripts/codex_learning/review_latest_run.py`

## Verification

- [ ] Track explicitly declared before execution (A or B, never mixed)
- [ ] `hermes auth list` shows `openai-codex` provider (TRACK B)
- [ ] Evidence JSON exists in `~/.hermes/codex-learning/runs/` with `git_status_porcelain` (TRACK A)
- [ ] `git_changed_files` includes untracked files (not just `git diff --name-only`)
- [ ] Project tests/build pass after TRACK A execution
- [ ] Delegation contract contains objective + acceptance criteria + restrictions (TRACK B)
