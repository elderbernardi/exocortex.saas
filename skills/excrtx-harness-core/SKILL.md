---
name: excrtx-harness-core
description: "Homegrown harness to operate Codex CLI (exec) with traceability and lightweight verification, without third-party plugins."
version: 0.2.0
created_by: agent
platforms: [linux]
metadata:
  intent: class-level
---

# Codex Harness (homegrown)

Operational skill for using **Codex CLI** as a work executor (especially code) in a reproducible way, with local traceability, **without relying on community plugins**.

Not a *learning* skill; it's an execution + evidence harness.

## When to Use

- The executive wants *Codex to code* (modify files, refactor, create scripts).
- The executive wants to delegate executions to Codex without coupling to the Hermes gateway model.
- You need a local trace of what was requested/done (prompt + output + git evidence).

## Artifacts (local)

Recommended pattern: use the wrapper at `~/.hermes/scripts/codex_learning/` which records to:

- `~/.hermes/codex-learning/runs/*.json`
- `~/.hermes/codex-learning/events/*.json`

## Modes

### 1) Scratch (safe default)

Use when the task doesn't depend on a real repo.

- Creates temporary directory
- Initializes git
- Runs Codex
- Captures evidence

Example:

```bash
python3 ~/.hermes/scripts/codex_learning/run_codex_with_learning.py \
  --scratch \
  --full-auto \
  --prompt 'Create hello.py that prints "hello" and run python3 hello.py.'
```

### 2) Non-critical repo (open)

Use only when explicitly directed and the repo is non-critical.

```bash
python3 ~/.hermes/scripts/codex_learning/run_codex_with_learning.py \
  --cd /path/to/repo \
  --full-auto \
  --prompt '...'
```

## Flags and Semantics

- `--full-auto`: allows writes. Internally, **maps to** `--sandbox workspace-write` (Codex is deprecating `--full-auto`).
- `--yolo`: avoid as default; only when the executive explicitly requests it.

## Evidence: What to Capture (non-negotiable)

1) Prompt and command executed.
2) stdout/stderr (with truncation).
3) Git evidence:
   - `git status --porcelain`
   - `git_diff_stat`
   - List of changed files **including untracked** (important).

## Pitfalls (learned in production)

- `git diff --name-only` and `git diff --stat` **don't show untracked files** (`??`). To measure "changed files" correctly, derive from `git status --porcelain` and/or `git ls-files --others --exclude-standard`.
- Codex can fall into read-only sandbox without a write flag. For tasks expecting file creation/editing, use `--full-auto` (or equivalent `--sandbox workspace-write`).
- `--full-auto` may appear as deprecated in recent builds; prefer `--sandbox workspace-write`.

## References

- `references/codex-cli-gotchas.md` (gotchas + stderr signals + how to interpret)
- `references/harness-truth-contract.md` (checklist to align feature promises, actual files, `setup.sh`, `HERMES_HOME` and dogfood before declaring PASS)
