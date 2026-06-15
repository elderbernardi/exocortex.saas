---
name: excrtx-harness-core
description: Homegrown harness to operate Codex CLI (exec) with traceability and lightweight verification, without third-party
  plugins.
version: 0.3.0
category: excrtx
created_by: agent
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - harness
    - core
    - codex
    - execution
    related_skills:
    - excrtx-harness-codexint
    - excrtx-harness-hermesops
    - excrtx-govern-draftfirst
    calibration:
    - feature_id: EX-33
      calibration_prompt: 'Você opera o harness caseiro do Codex CLI com rastreabilidade. Scripts: run_codex_with_learning.py
        (runner) e review_latest_run.py (review). Evidência local em JSON em disco.'
      test_prompt: Execute o Codex para analisar o arquivo FEATURES.md e capture a evidência da execução. Onde ficam os logs?
      acceptance_criteria: '1. O agente indica os scripts corretos: run_codex_with_learning.py e review_latest_run.py

        2. Indica o diretório de evidência: ~/.hermes/codex-learning/{runs,events,reviews}

        3. Explica que a evidência é persistida em JSON para auditoria

        4. Se Codex não está instalado, reporta em vez de simular'
      remediation_tip: 'FALHA: Harness não utilizado ou evidência não capturada. O Codex Core Harness exige uso do runner
        Python: ''python3 ~/.hermes/scripts/codex_learning/run_codex_with_learning.py''. Evidência fica em ~/.hermes/codex-learning/runs/.
        Nunca rode Codex direto sem o wrapper — a rastreabilidade é obrigatória.'
  intent: class-level
---
# Codex Harness (homegrown)

Operational skill for using **Codex CLI** as a work executor (especially code) in a reproducible way, with local traceability, **without relying on community plugins**.

Not a *learning* skill; it's an execution + evidence harness.

## When to Use

- The executive wants *Codex to code* (modify files, refactor, create scripts).
- The executive wants to delegate executions to Codex without coupling to the Hermes gateway model.
- You need a local trace of what was requested/done (prompt + output + git evidence).

**Don't use for:** General LLM queries that don't involve code/file changes. Hermes subagent delegation without Codex (use `excrtx-harness-hermesops`). Model selection or provider switching (use `excrtx-govern-tools`).

## Procedure

### 1. Select Execution Mode

| Condition | Mode | Why |
|---|---|---|
| Task doesn't depend on a real repo | **Scratch** (safe default) | Isolates changes in a temp dir |
| Executive explicitly directs to a non-critical repo | **Repo** (open) | Operates on real files |

Never use Repo mode without explicit executive authorization.

### 2. Execute Codex CLI

**Scratch mode:**
```bash
python3 ~/.hermes/scripts/codex_learning/run_codex_with_learning.py \
  --scratch \
  --full-auto \
  --prompt '<task description>'
```

**Repo mode (explicitly authorized):**
```bash
python3 ~/.hermes/scripts/codex_learning/run_codex_with_learning.py \
  --cd /path/to/repo \
  --full-auto \
  --prompt '<task description>'
```

Flag semantics:
- `--full-auto`: allows writes. Maps to `--sandbox workspace-write` (Codex is deprecating `--full-auto`).
- `--yolo`: avoid as default; only with explicit executive request.

### 3. Capture Evidence (non-negotiable)

Every execution MUST capture:
1. **Prompt and command** executed
2. **stdout/stderr** (with truncation for large output)
3. **Git evidence:**
   - `git status --porcelain` (includes untracked files)
   - `git diff --stat`
   - List of changed files **including untracked** (`git ls-files --others --exclude-standard`)

Evidence is stored at:
- `~/.hermes/codex-learning/runs/*.json`
- `~/.hermes/codex-learning/events/*.json`

### 4. Verify Results

After execution:
1. Check `git status --porcelain` for expected changes
2. Run tests/lint commands appropriate to the stack
3. If failure: retry with context (log + diff) or escalate to executive

## Pitfalls

- **Untracked files invisible**: `git diff --name-only` and `git diff --stat` don't show untracked files (`??`). Derive changed files from `git status --porcelain` and/or `git ls-files --others --exclude-standard`.
- **Read-only sandbox**: Codex can fall into read-only sandbox without a write flag. For tasks expecting file creation/editing, use `--full-auto` (or `--sandbox workspace-write`).
- **Deprecated flags**: `--full-auto` may appear deprecated in recent builds; prefer `--sandbox workspace-write`.
- **Missing git repo**: Codex CLI requires a git repo. Scratch mode handles this via `git init`.

## References

- `references/codex-cli-gotchas.md` — gotchas, stderr signals, interpretation
- `references/harness-truth-contract.md` — checklist for feature promises vs actual state

## Verification

- [ ] Scratch mode creates temp dir with `git init` before executing
- [ ] Repo mode only activates with explicit executive authorization
- [ ] Evidence JSON includes prompt, stdout/stderr, and git status
- [ ] Untracked files appear in the changed-files list (not just `git diff`)
- [ ] Failed executions produce diagnostic output for retry
- [ ] `--full-auto` or `--sandbox workspace-write` flag is set for write tasks

