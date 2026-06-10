---
name: excrtx-harness-codexint
description: "Integrate OpenAI Codex (CLI and provider) into Hermes/Exocórtex with governance, routing, and verification."
version: 0.1.0
created_by: agent
context: exocortex
platforms: [linux]
---

# Codex Integration — Hermes/Exocórtex

Codex here means two distinct things:

1) Codex CLI (local agent via terminal; requires git repo; interactive/PTY)
2) Provider/model openai-codex within Hermes (for subagents via delegation)

This skill defines how to use both without fragile coupling to the gateway's main model.


## When to Use

- The executive wants to "leverage their Codex subscription" within Hermes.
- We need to delegate general tasks to Codex (Hermes subagent) AND use Codex to code (Codex CLI).
- The Hermes gateway may be responding with another LLM via API, but execution/routing must keep working.


## Key Principle (anti-confusion)

- Codex CLI is a local executable. Independent of the Hermes provider/model.
- Delegation provider is Hermes configuration. Independent of the gateway's main model.

In short: two tracks, one routing policy.


## Architecture (Two Tracks)

TRACK A — Codex CLI for repository work
- Called via `terminal` tool with `pty=true`.
- Precondition: must be inside a git repo (Codex refuses outside).
- Modes:
  - One-shot: `codex exec '<prompt>'`
  - Larger changes (prefer): `codex exec --full-auto '<prompt>'` (sandbox; auto-approves workspace changes)
  - Avoid `--yolo` as default (only with explicit executive decision).

TRACK B — Hermes subagent using openai-codex provider (general tasks)
- Configure `delegation.provider` + `delegation.model` to point to openai-codex.
- Execute via `delegate_task(...)` when the task is parallelizable and doesn't require CLI interactivity.


## Routing Policy (Objective Rule)

1) If the task involves file/code changes in repo, refactoring, PR review, or test execution → TRACK A (Codex CLI).
2) If the task is general (research/synthesis/plan/comparison/checklist) and the goal is speed/parallelism → TRACK B (delegate_task with Codex provider).
3) If the task is hybrid → Hermes/Exocórtex decomposes:
   - Analysis/decision here
   - Implementation in Codex CLI
   - Validation here


## Prompt Patterns (Output Contracts)

A) Minimum template for Codex CLI (always request verifiable evidence)

- Objective (1 line)
- Context (paths, versions, constraints)
- Acceptance criteria
- Restrictions (don't touch X; keep API)
- Validation: commands to run (test/lint/build)
- Required output:
  - List of changed files
  - Per-file summary
  - Commands executed + status
  - Risks/limitations

B) Minimum template for delegate_task

- Subagent scope (what it CAN and CANNOT do)
- Output format (explicit structure)
- Sources: if it can use web/file/terminal, state clearly
- Request an "assumptions list" (to separate fact from inference)


## Verification (Post-Execution)

After Codex CLI:
- `git status` (clean vs dirty)
- `git diff` (inspect)
- Run tests/lint per stack
- If failure: request incremental fix from Codex with context (log + diff)

After delegate_task:
- Validate output is actionable
- When commands are suggested: execute yourself (or generate DRAFT if external action)


## Gateway Governance (Main LLM via API)

Goal: operations must not depend on the gateway's main model.

- TRACK A (CLI) is always local and works even if the gateway uses another LLM.
- TRACK B depends only on `delegation.*` being configured; must remain stable when `model.default/provider` of Hermes changes.

Acceptance (smoke tests):
- Run a `codex exec` in a disposable repo and check `git diff`.
- Run a simple `delegate_task` and confirm execution.
- Switch the Hermes main model (gateway/API) and repeat the `delegate_task`.


## Ecosystem/Community (Worth Evaluating)

- Plugin "Hermes Agent Gateway" (Bigsunnyboy/hermes-codex-gateway):
  - Purpose: chat→queue→worktree→runner→verify→artifacts governance
  - Useful when execution should be commanded by chat with guardrails (approve/allow/verify)
- Plugin "Hermes Codex Learning" (New-dev0/hermes-codex-learning):
  - Purpose: instrument Codex sessions and export local artifacts for Hermes to learn
- Harness "Maestro" (ReinaMacCredy/maestro):
  - Purpose: durable local state (spec→task→verify→ship) for multiple agents

See `references/hermes-community-codex.md` for short notes and criteria.


## Pitfalls (Don't Forget)

- Codex CLI requires git repo; for scratch use `mktemp -d && git init`.
- Always use `pty=true` when calling Codex CLI via terminal.
- Don't "guess" `delegation.model` string: discover via `hermes model` then set config.
- Don't confuse: main model provider ≠ delegation provider.


## Evolution (When to Productize)

When the flow is proven:
- Encapsulate in an operational skill (or scripts) with:
  - Automatic worktree creation
  - Codex execution
  - Evidence capture (diff/test)
  - Cleanup
