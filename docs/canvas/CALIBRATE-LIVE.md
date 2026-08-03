# canvas-calibrate --live — Owner-Gated Isolated Smoke Runbook

> **INVARIANT (hard):** prod `:8787` and the real acervo (`~/exocortex/acervo`) are NEVER
> touched by this smoke.  Every write happens in a temp directory that is deleted on exit.
> Verify the prod server PID before and after the run if you want extra assurance.

## When to run

Run `--live` when you want to verify that the live DeepSeek model, governed by the
current `SOUL_SEED.md` conduct blocks, correctly:

1. Classifies canonical phrases into the right vetores (**enquadrador 3/3**).
2. Writes its fable-loop trail to `conduct.jsonl` (not narrated prose) and produces a
   Draft-First AUTH Sala card (**condução check**).
3. Produces a reply free of PT-BR phase narration (**anti-narration empty**).

This is the EX-49 live-tier evidence gate.  Run it after any calibration of
`excrtx-conduct-loop`, `excrtx-conduct-bounds`, or `SOUL_SEED.md`.

---

## Prerequisites

| Requirement | Check |
|---|---|
| `DEEPSEEK_API_KEY` in env | `echo $DEEPSEEK_API_KEY \| wc -c` — must be > 1 |
| `~/.hermes/config.yaml` exists | provisioned via `bash setup.sh` |
| `~/.hermes/hermes-agent/venv/bin/python` exists | hermes-agent venv provisioned |
| `~/.hermes/hermes-webui/` exists | step-10b provisioned |
| Port `:8794` is free | `ss -tlnp \| grep 8794` → should be empty |

---

## Sourcing DEEPSEEK_API_KEY

The key lives in `databrain/.env` (relative to the umbrella repo root).

```bash
# Source the key — MASK it in any logs or terminal history
export DEEPSEEK_API_KEY="$(grep '^DEEPSEEK_API_KEY=' /path/to/projetob/databrain/.env | cut -d= -f2-)"
# Verify it is set (print length only — NEVER print the value)
echo "Key length: ${#DEEPSEEK_API_KEY}"
```

> The key is NEVER printed, echoed, or written to any file by `canvas_calibrate.py`.
> Do not copy the key into shell history if you can avoid it (`read -s` form below).

Alternatively, enter it interactively without shell history:

```bash
read -rs DEEPSEEK_API_KEY && export DEEPSEEK_API_KEY
```

---

## Running the smoke

```bash
# From the exocortex.saas repo root (or the f5/canvas-slice-a worktree):
cd /path/to/exocortex.saas

python3 scripts/canvas_calibrate.py --live
```

The script:
1. Checks `DEEPSEEK_API_KEY` — exits 2 with a clean message if absent (no traceback).
2. Creates a temp directory with an isolated `HERMES_HOME` + `ACERVO` scaffold.
3. Copies `~/.hermes/config.yaml` into the isolated home and applies DeepSeek overrides
   (see "Isolated env overrides" below).
4. Starts the hermes-webui fork on port `:8794` using the hermes-agent venv
   (sets `HERMES_WEBUI_PORT=8794` + `HERMES_WEBUI_HOST=127.0.0.1` — the fork reads
   `HERMES_WEBUI_PORT`, not bare `PORT`; prod `:8787` is NEVER touched).
5. Drives the enquadrador check (3 canonical phrases) and the conduction check (1 real session).
6. Terminates the server and deletes the temp directory.
7. Prints the EX-49 evidence report and exits 0 (PASS) or 3 (FAIL).

---

## Isolated env overrides

The isolated `HERMES_HOME/config.yaml` receives these overrides (applied by `_apply_yaml_overrides`):

| Key | Value |
|---|---|
| `model.provider` | `deepseek` |
| `model.default` | `deepseek-v4-pro` |
| `model.base_url` | `https://api.deepseek.com/v1` |
| `model.api_mode` | `openai_chat_completions` |
| `context_file_max_chars` | `40000` |

These match the C0/F3 isolated-smoke recipe (see `docs/sala/F3-GATE-PROOF.md`).
The `context_file_max_chars: 40000` pin avoids SOUL truncation at the 128K cap.

---

## Canonical phrases and expected vetores

| # | Phrase | Expected vetor |
|---|---|---|
| 1 | "Faça o ofício de renegociação com o Cliente Alfa até sexta." | `execucao` (produzir) |
| 2 | "Estou pensando sobre como reposicionar a linha premium." | `evolucao` (explorar) |
| 3 | "Revise as pendências e limpe o que estiver obsoleto." | `manutencao` (revisar) |

**PASS criterion (enquadrador):** all 3 vetores correct, `gaps` not fabricated. All 3
canonical phrases are self-contained (they carry no implicit blocking prerequisite), so a
non-empty `gaps` list on ANY of them means the model hallucinated prerequisites → that phrase
FAILs. Expected `gaps`: empty list or `null`.

---

## Conduction check — what PASS looks like

The script launches one real session with an execução phrase that forces a Draft-First
external-action (e-mail send scenario):

> "Redigir e enviar o e-mail de cobrança para o Cliente Alfa até sexta.
>  Não enviar sem aprovação explícita."

**PASS requires ALL of the following:**

| Criterion | How verified |
|---|---|
| `conduct.jsonl` written (not narrated) | `n_events > 0` on the isolated acervo path |
| ≥1 Draft-First AUTH Sala card | at least one `sala_draft` event with `requires_auth: true` in `/api/canvas/sala/state` |
| Anti-narration empty | `check_anti_narration.check_narration(agent_messages)` returns `[]` on the real reply |

**Known caveat (C0 smoke-isolation artifact):** the hermes-agent MCP server may write
`conduct.jsonl` to the REAL acervo path (`~/exocortex/acervo/_tasks/<id>/`) instead of the
isolated `$ACERVO` — because the acervo MCP server still resolves the real path at runtime.
In production (single acervo) this is correct.  In the smoke it may cause `n_events = 0` on
the isolated path; the script falls back to counting `sala_events` from the SSE state.
If you see `n_events = 0` but Sala cards ARE present, the agent wrote to the real acervo —
**clean it up** with `rm -rf ~/exocortex/acervo/_tasks/<task_id>` after the smoke.

---

## Expected output (PASS)

```
══════════════════════════════════════════════════════════
  canvas-calibrate — Live Tier (EX-49 / owner-gated)
══════════════════════════════════════════════════════════
  ✅ Enquadrador: 3/3
       enquadrador 3/3: PASS[execucao] ... | PASS[evolucao] ... | PASS[manutencao] ...
  ✅ Condução: conduction PASS: session=... n_events=9 draft_auth=1 anti_narration=[]
──────────────────────────────────────────────────────────
  Verdict: ✅ PASS
══════════════════════════════════════════════════════════
```

Exit code `0` = PASS.  Exit code `3` = smoke ran but FAIL.  Exit code `2` = key absent.

---

## Fail paths and troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `exit=2`, "DEEPSEEK_API_KEY ausente" | Key not set | `export DEEPSEEK_API_KEY=...` |
| `exit=1`, "config.yaml not found" | exocortex not provisioned | Run `bash setup.sh` first |
| Server timeout (15s) | Port conflict or fork not provisioned | Check `:8794` free; run step-10b |
| enquadrador `FAIL[evolucao]` — wrong vetor | Enquadrador calibration drift | Re-run `--refresh`, check skill D1, re-calibrate |
| `n_events=0` + no sala cards | conduct.jsonl not written (C0 gap regressed) | Re-run `--refresh`; verify `## Conduct Loop` in SOUL |
| `n_events=0` + sala cards present | Real-acervo write (caveat) — see above | Clean real acervo; acceptable smoke-isolation artifact |
| Anti-narration hits | Model narrating the method | Re-calibrate `excrtx-conduct-loop` `compiled_rules`; re-compile SOUL |

---

## Post-run cleanup checklist

1. Verify prod server still running: `curl -s http://127.0.0.1:8787/health | python3 -m json.tool`
   (The fork's health route is `/health` — not `/api/health`.  The isolated smoke uses `:8794` via `HERMES_WEBUI_PORT`; prod is `:8787`.  These must never overlap.)
2. If conduct.jsonl leaked to real acervo (caveat above): `rm -rf ~/exocortex/acervo/_tasks/<task_id>`
3. Temp dir is deleted automatically by the script even on error.
4. Do NOT commit the `DEEPSEEK_API_KEY` value anywhere.

---

## Fail-clean guard (keyless verify)

To confirm the guard works without a live key:

```bash
env -u DEEPSEEK_API_KEY python3 scripts/canvas_calibrate.py --live
# Expected: exit=2, message contains "owner-gated: DEEPSEEK_API_KEY ausente", NO traceback
echo "exit=$?"
```

This is the ONLY automated verification run in CI/keyless tier.  The full live run is
owner-gated and is NOT run in CI.
