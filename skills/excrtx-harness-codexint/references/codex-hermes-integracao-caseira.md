---
title: "Codex × Hermes: homegrown integration (two tracks)"
created: "2026-05-29"
updated: "2026-05-29"
tags: [codex, hermes, delegation, harness, evidence]
confidence: high
---

Context

Goal: integrate Codex into Hermes in a homegrown way, without depending on third-party plugins, with clear separation between:

Track A — Codex CLI (local execution / file modification)

- Use when the task involves: creating/editing files, refactoring, running commands, working in a repo, generating patches, executing tests.
- Prefer local wrapper/harness (below) to standardize logging and evidence.
- Safe default: run in scratch (temporary repo) when the task is "arbitrary" or without clear scope.

Track B — Delegation provider openai-codex (general tasks)

- Use when the task involves: planning, analyzing, synthesizing, writing checklists, generating hypotheses.
- Implement via delegate_task with delegation.provider=openai-codex and fixed delegation.model.
- Maintains independence from the gateway's main model (which may be another provider).

Integration Checklist (Hermes)

1) Credentials
- `hermes auth list` must show `openai-codex`.

2) Delegation config (Track B)
- `hermes config set delegation.provider openai-codex`
- `hermes config set delegation.model gpt-5.2` (or another listed in local cache)
- Verify in `~/.hermes/config.yaml`.

Codex CLI Harness (Track A)

Local artifacts (standard):
- Runner: `~/.hermes/scripts/codex_learning/run_codex_with_learning.py`
- Reviewer: `~/.hermes/scripts/codex_learning/review_latest_run.py`
- Runs: `~/.hermes/codex-learning/runs/*.json`
- Events: `~/.hermes/codex-learning/events/*.json`

Important Semantics

- Codex can fall into read-only sandbox if not explicitly configured for writes.
- In wrapper: use `--full-auto` to map to write sandbox (`workspace-write`).
- Codex CLI typically requires being inside a git repo; the wrapper ensures `git init` + initial commit.

Evidence (don't trust "done")

Key learning: `git diff --name-only` / `--stat` doesn't include untracked (`??`). For correct evidence, rely on:
- `git status --porcelain` (includes `??`)
- `git ls-files --others --exclude-standard` (lists untracked)

Prompt Contract (when sending task to Codex CLI)

Always make explicit:
- Goal + acceptance criteria
- Constraints (don't touch X, don't change deps, etc.)
- Expected evidence: changed/created files + commands run + relevant stdout + exit code.

Routing Heuristic

- "Needs to write/edit file, run tests, work in repo" → Track A (Codex CLI)
- "Needs to analyze/plan/synthesize" → Track B (delegate_task)
- Hybrid → decompose: Track B (analysis) → Track A (execution) → Hermes validates and summarizes evidence.
