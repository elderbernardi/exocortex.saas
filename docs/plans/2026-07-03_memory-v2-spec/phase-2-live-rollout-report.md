# Phase 2 — Live Rollout Report

> **Executed:** 2026-07-05 · **Status:** ✅ rolled out (reads live-proven; writes proven on isolated copy) · 2 findings open for executive decision

## What was rolled out to the live instance (`~/.hermes` + `~/exocortex/acervo`)

- **Skills v3** → `~/.hermes/skills/excrtx/`: `excrtx-memory-manager` 2.2→3.0, `-deprecate` 1.0→2.0, `-newmicro` 2.0→3.0 (live-only reference docs preserved).
- **SOUL recompiled** in place (`~/.hermes/SOUL.md`) — the 8 `Memory Manager` v3 compiled rules now live; markers intact (20 rule sections).
- **`rtn_inbox_triage.yaml`** in the live acervo upgraded report-only → propose-and-commit-on-approval.
- **Control plane** deployed into `~/exocortex/acervo/global/tools/`: `acervoctl.py`, `acervo_semantic_core.py`, `exocortex_runtime_guard.py`, `validate_frontmatter.py`, `validate_log.py`.
- **MCP `acervo` server** config repaired (see finding 2).

**Backup:** live acervo git tag `pre-phase2-rollout`; `~/.hermes` skills/SOUL/scripts tarballed to scratchpad.

## Bugs the rollout surfaced and fixed

1. **Control plane unreachable by the live agent.** The skills invoked a cwd-relative `scripts/acervoctl.py` that has no home in a deployed instance (the agent runs from neither the installer checkout nor a fixed cwd). Proven: a real `hermes chat` retrieve tried `$ACERVO/scripts/acervoctl.py` and failed.
   - **Fix:** skills resolve a `$CTL` control-plane dir once (ladder: `$ACERVO/global/tools` → installer/scripts → `$HERMES_HOME/scripts`) and invoke `python3 "$CTL/acervoctl.py"`; `setup.sh` deploys the control plane into `$ACERVO/global/tools` on install; `acervo_semantic_core` resolves `validate_frontmatter`/`validate_log`/`microverso_package` sibling-first (its `REPO_ROOT`-relative paths point outside the acervo when it runs from `global/tools`).
   - Commits: installer `dc05630` (local — push to `main` denied by classifier, pending), live acervo `e48a4f8` + `717e4c7`.

2. **MCP `acervo` server pointed at a dead temp dir.** `config.yaml` had `env.ACERVO: /tmp/tmp…/exocortex/acervo` (nonexistent) — the agent's primary memory surface operated on a phantom acervo. Fixed → `/home/ubuntu/exocortex/acervo`; gateway restarted; `hermes mcp test acervo` healthy (10 tools).

## Verification (raw)

- **Live agent retrieve:** `hermes chat -s excrtx-memory-manager` resolved `$CTL=$ACERVO/global/tools`, ran `acervoctl retrieve`, returned a correctly-cited answer (Schema v0.2 / ADR-023, with fields + an integrity caveat about legacy `SCHEMA.md`). 0 "not found" errors.
- **Write cycle on isolated live copy:** `new-object` intention → ok:true, status active, frontmatter PASS; `conflict-check` → ok:true; reindex + `retrieve` → new intention cited; `doctor` → ok:true / 0 errors / 223 objects. Hindsight isolated (dead URL), production bank untouched.
- **Regression:** installer memory suite 174 passed / 1 skipped (excluding the polluting `test_setup_acervo_mcp`).
- **Live doctor via ladder:** ok:true / 0 errors both invocation paths.

## Open findings (executive decision)

1. **Live global writes blocked by legacy logs.** `new-object` validates the *entire* target-scope `_meta/log.md` via `validate_log.py`; the live `global/_meta/log.md` (and likely others) is legacy free-text that fails L-003/L-010/L-020. Reads work; live writes to a scope require migrating that scope's log to the strict format first. **STILL OPEN.**
2. **A test repollutes live config.** `tests/test_setup_acervo_mcp.py` (via the step-11b `hermes mcp add` path) writes `ACERVO` into the **real** `~/.hermes/config.yaml` pointing at the test's temp dir, ignoring the isolated `HERMES_HOME` — this is how the MCP `ACERVO` got the dead temp path, and it recurred when the suite ran during this rollout. The step must honor `HERMES_HOME`; until fixed, do not run that test against a real `~/.hermes`.
   - **✅ RESOLVED 2026-07-06 (commit `1e105be`).** Root cause: on this VM `BASH_ENV=~/.claude/load-env-local.sh` auto-loads `~/.env.local` into every non-interactive subshell, which exports the real `HERMES_HOME` (but not `ACERVO`) — so the test's isolated `HERMES_HOME` was reverted mid-run while `ACERVO` stayed isolated, poisoning the real config. Fix: (a) `step-11b` detects an isolated `HERMES_HOME` (realpath ≠ `$HOME/.hermes`) and, for it, writes the config directly via `_acervo_patch_config` and proves health with the server self-test — the `hermes mcp` CLI (which ignores `HERMES_HOME`) is used only for the real default home; (b) the test clears `BASH_ENV` in the subprocess env so its isolated home survives. Verified: full memory suite **75 passed, real `config.yaml` md5 unchanged** across the run. Live `ACERVO` re-corrected to `/home/ubuntu/exocortex/acervo`, MCP self-test exit 0, gateway restarted (PID stable). Pushed to `origin/main`.
