# F3 — Sala viva conduzida — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Charter:** `F3-CHARTER.md`. **ADRs consumed:** ADR-CT-04 (job+poll), ADR-CT-05 (vanilla), ADR-CT-06 (canvas v0.5). **New ADR produced here:** ADR-CT-07 (port conduct skills). **Design provenance:** multiagent design workflow 2026-07-25 (6 readers → 3 architectures → synthesis → adversarial critique, verdict *needs-revision*/7 must-fix — all folded in below). **Owner decisions (locked 2026-07-25):** OD-1 = conduct.jsonl trail + journal-tail backstop; OD-2 = 2 skills; OD-3 = kanban display projection only; OD-4 = `SALA_ENABLE` default off.

**Goal:** The launched Hermes session updates the canvas live — artifacts/clarify/kanban/traces/Draft-First all become verifiable Cockpit cards — conducted by the fable-method loop, with HITL restricted to the 3 sanctioned classes and mechanical bounds, and the loop phases visible discreetly but **never narrated** in the agent output.

**Architecture:** A **pure observe-and-translate** layer bolted onto the proven F2 Curador seams; the launched Hermes session runtime is **never touched**. One new forward prefix `/api/canvas/sala/` (2 lines each way in `canvas_tarefas.py`, `routes.py` untouched). Two new backend files: `api/canvas_sala.py` (impure shell — a non-closing `SALA_ROOMS` cloned from `CURADOR_ROOMS`, the per-session observer daemon, the clarify/approval bridges) and `api/sala_reducer.py` (a **pure, IO-free** `SalaState.ingest(frame) -> [(event, payload)]` holding the phase state machine, the 3 bound counters, and the authority-order resolution — the hermetic TDD seam). For v1 the observer's **single durable source is the agent-written `_tasks/<task_id>/conduct.jsonl`** (phases/traces/bounds/artifacts/next-moves/drafts — all agent-DECLARED, so anti-narration is structural) plus the two multi-subscriber HITL registries it subscribes (`clarify.sse_subscribe`, `route_approvals._approval_sse_subscribe`). It **mints no blocking primitive of its own**, so "interrupts only in the 3 classes" is *structural*. *(A `run_journal.read_session_run_events` artifact backstop — catching artifacts the agent forgets to declare — is **deferred to F5**: the review found its dict-return/`payload`-nested/`run_id:seq`-cursor shape needs a bootstrap redesign, and OD-1 already makes conduct.jsonl authoritative, so v1 relies on the conduct trail alone.)* The conducting method lives in two new `excrtx-conduct-*` skills whose `compiled_rules` reach the launched session through its profile SOUL (embed-in-brief is structurally incapable — the brief is user-turn content, gone after turn 1).

**Tech Stack:** Python 3.12 stdlib only (threading, queue, json, subprocess, pathlib, yaml — already a dep); vanilla ES5-ish IIFE JS (no deps, no build); Exocortex skills (`SKILL.md` frontmatter + `compiled_rules:` → `compile_soul.py`). Tests: `pytest` (fork), `skill_judge.py --d1-only` + `compile_soul.py --validate-compiled-rules` (skills, keyless), Playwright for the island.

---

## Global Constraints

> Copied verbatim from `00-INDEX.md` §"Contrato de execução para agentes" (binding — every task implicitly includes this section). Violation = **stop and report, never improvise**.

1. **Execute apenas a fase que tem PLANO detalhado.** Charter não é plano — não implemente a partir de charter.
2. **Escopo é fechado**: toque somente os arquivos listados na tarefa. Precisar de um arquivo fora da lista = surpresa → **pare e reporte**, nunca expanda em silêncio.
3. **Nunca toque** (zona quente de rebase / fora do escopo do programa): `hermes-webui/static/{ui,messages,sessions,panels,boot}.js`, `static/style.css`, `static/index.html`, e `api/routes.py` além dos hooks explicitamente indicados no plano (máx. 8 linhas novas ao todo). **F1b já esgotou esse teto de 8 linhas — logo F3 adiciona ZERO linhas a `routes.py`** (endpoints entram por forward em `canvas_tarefas.py`).
4. **Zero dependências novas** (pip/npm), **zero build step**, strings de UI em **PT-BR**.

> **Emenda do owner (2026-07-26) — regras 3 e 4 relaxadas para F3.** O invariante real é **não perturbar o upstream nesquena de um jeito que quebre o rebase**, não os números literais.
> - **Regra 3 (routes.py):** o teto "8 linhas" **não é essencial** e fica dispensado. A **proibição da zona quente** (`static/{ui,messages,sessions,panels,boot}.js`, `style.css`, `index.html`) PERMANECE — esses são o verdadeiro hot-zone de rebase. Para `routes.py`, minimizar churn continua sendo a meta, mas sem quota rígida. **Ponderação: F3 continua a adicionar 0 linhas a `routes.py`** — o forward-dispatch em `canvas_tarefas.py` (padrão F2) é o design mais limpo mesmo sem o teto; um hook dedicado em `routes.py` seria mais churn sem ganho. Nenhuma tarefa muda.
> - **Regra 4 (deps):** "zero deps" fica relaxado — uma dependência nova é aceitável **se não exigir build step e não tocar o tooling de frontend do upstream**. **"zero build step" PERMANECE** (um dep npm/JS forçaria build = churn de tooling upstream = proibido); um dep **Python** pequeno e autocontido seria aceitável se genuinamente necessário. **Ponderação: F3 não precisa de dep novo** — backend é stdlib + PyYAML (já presente), a ilha é vanilla JS; `watchdog` (FS events vs poll do `conduct.jsonl`) e Preact (ilha) foram considerados e rejeitados (poll 1s basta / ADR-CT-04; vanilla abaixo do gatilho ADR-CT-05; Preact exige build). A liberdade fica registrada mas **não usada** na v1. *(A emenda equivalente no `00-INDEX.md` fica a critério do owner — mantida F3-escopo por ora.)*
5. **Prova bruta por tarefa (EX-49)**: toda tarefa termina com o output real do comando de verificação. Sem output, a tarefa não está concluída — não marque.
6. **Bounds (fable-method)**: 3 ciclos falha-conserto na mesma verificação → pare, registre o que tentou, a saída real e sua hipótese, e devolva. 2 buscas sem informação nova → pare de buscar e registre a lacuna.
7. **Segredos nunca** aparecem em logs, commits ou relatórios (chaves mascaradas).
8. **`.quarantine/` não existe para você** — nunca ler, listar ou escrever.
9. Commits pequenos e frequentes na branch **`collab/canvas-f3`** do repo indicado pela tarefa; mensagens em inglês, prefixo convencional (`feat:`, `test:`, `docs:`); **nunca** `git push` sem instrução explícita da tarefa.
10. Ações externas (push, comentário em issue, deploy) só quando a tarefa manda — e o relatório final da fase cita cada uma.

### F3-specific binding constraints (from the adversarial critique — do not weaken)

- **C-A (three-repo COLLAB + shared-checkout hazard).** The owner runs parallel agent sessions on the **same** checkouts (incident 2026-07-24 required worktree+cherry-pick recovery). F3 touches **three independent repos**: `hermes-webui` (fork), `exocortex.saas` (skills+ADR), and the umbrella `projetob` (contract+change-record). For **each** repo: work in an **isolated `git worktree`** under scratchpad, branch **`collab/canvas-f3`** cut from that repo's integration tip (fork = `exocortex/stable@14d880b6`; **do NOT reuse the stale `collab/canvas-tarefas`**). Verify the branch **in the same compound command as every commit** (`git -C <wt> branch --show-current && git -C <wt> add <explicit paths> && git -C <wt> commit …`). **Never `git add -A/-u/.`** — explicit paths only. Never disturb sibling checkouts' uncommitted WIP.
- **C-B (mint no blocking primitive).** F3 code must **never** call `clarify.submit_pending` / `register_gateway_notify` / any approval-raising API. The only blocking HITL is the **live agent self-invoking** clarify/approval under skill governance; F3 only **observes** via `clarify.sse_subscribe` and `route_approvals._approval_sse_subscribe` (both multi-subscriber). A test asserts F3 registers **no** `register_gateway_notify`.
- **C-C (honest bound framing).** The bound-interrupt "sticky, long-timeout" property is **behavioral + watchdog**, not structural — `clarify._with_timeout_metadata` always sets `expires_at`, so auto-proceed eventually fires. Never claim structural non-weakening; the guarantee is: skill forbids "best-judgement" on a bound timeout + fork watchdog re-surfaces + human escalation.
- **C-D (E9 reconciliation).** "E9" in the charter is the **canvas-SSE event taxonomy of the `exocortex-hermes-webui` contract** (§d + Curador §f). `sala_*` events live in a **new §(g)** mirroring the Curador §(f) precedent — they are **NOT** AG-UI gateway events (those govern sales-AI `/api/agente/run` in `AGUI_GATEWAY.md`, a different surface). State this in the change record.
- **C-E (SOUL propagation is necessary-but-not-sufficient — resolved by the T0 trace).** The launched session's persona is `run_agent.load_soul_md()` reading **`$HERMES_HOME/SOUL.md`** as identity slot #1 (`personality=None`; `config.yaml agent.personalities` is dead for launched sessions). `compile_soul.py` writes the repo **`SOUL_SEED.md`** (between `COMPILED_RULES` markers; `excrtx-conduct-loop` → `## Conduct Loop`), and the runtime `$HERMES_HOME/SOUL.md` is a **verbatim copy** installed by `setup.sh` **step-07** (which overwrites the in-place compile). So the mandatory chain is **skill `compiled_rules` → `compile_soul.py` → `SOUL_SEED.md` → (step-07 `cp`) → `$HERMES_HOME/SOUL.md` → `load_soul_md()`**. Forcing a `profile=` at launch is **a no-op in the isolated smoke** (default profile already maps to `$HERMES_HOME`) and only load-bearing in multi-profile prod → **F3 does not force a profile**; conduct scoping to launched-only sessions defers to F5. Governance is provable **offline (no LLM key)** via `run_agent.load_soul_md()` and `agent._build_system_prompt()` (both pure file-assembly). See T15/T16.

---

## File Structure

### Repo A — `hermes-webui` (fork), branch `collab/canvas-f3` off `exocortex/stable@14d880b6`

| Path | Action | Responsibility |
|---|---|---|
| `api/sala_reducer.py` | **create** | Pure IO-free `SalaState`: normalized-frame → `[(event, payload)]`; phase state machine; 3 bound counters; authority-order resolution. No imports beyond stdlib. **The hermetic TDD seam.** |
| `api/canvas_sala.py` | **create** | Impure shell: `SALA_ROOMS`+`_room`/`_emit`/non-closing `_stream_events` (cloned from Curador); `LAUNCHED` reverse index + `register_launch`/`resolve`; the per-session **observer daemon** (poll conduct.jsonl → reducer → emit, + primed clarify/approval bridges); `handle_sala_get/post`. `SALA_ENABLE`-gated. |
| `api/canvas_tarefas.py` | **modify** | (1) 2-line forward to `handle_sala_get/post` in `handle_canvas_get`/`handle_canvas_post`; (2) in `_handle_launch`: register the `session_id→canvas_id` link + write `_tasks/<canvas_id>/launch.yaml`; (3) add `"/authorization/*"` to `_WHITELIST_RAW`. **No profile-forcing** — the SOUL trace showed the launched default-profile session already loads `$HERMES_HOME/SOUL.md`, so the conduct rules reach it via SOUL propagation, not a `_new_session` change (vetor→profile scoping defers to F5). |
| `static/canvas-sala.js` | **create** | IIFE island cloned from `canvas-curador.js`: own `#cvt-sala-zone`, own `EventSource` on `/api/canvas/sala/stream`, one renderer per `sala_*` event, accept via `window.CVT.acceptOps`, HITL answers via `/api/clarify/respond`+`/api/approval/respond`, AUTH-words captured in-island → `/api/canvas/patch`. PT-BR. |
| `static/canvas-tarefas.css` | **modify** | Append `.cvt-sala-*` rules (append-only; matches existing dark palette). |
| `static/canvas-dev.html` | **modify** | Add `<script src="/static/canvas-sala.js"></script>` after `canvas-curador.js`. |
| `static/canvas-tarefas.js` | **modify** | **One guarded line** (T12): `try { if (window.CanvasSala) window.CanvasSala.onCockpitOpen(cid); } catch (_) {}` beside the existing Curador handoff. NOT the hot zone. |
| `EXCRTX_MODIFICATIONS.md` | **modify** | Add **MOD-014** cataloguing the Sala layer. |
| `tests/test_sala_reducer.py` | **create** | Pure-reducer unit tests (frames→events, counters, authority order, dedup). |
| `tests/test_canvas_sala.py` | **create** | Room/stream replay; observer one-cycle w/ injected journal+conduct reader; clarify/approval bridge; **no `register_gateway_notify`** assertion; forward fall-through. |
| `tests/test_sala_launch_link.py` | **create** | `session_id↔canvas_id` link + `launch.yaml` glob-rebuild after simulated restart. |
| `tests/test_sala_whitelist.py` | **create** | `/authorization/*` editable; newline-injection rejected; `/patch` adds the object. |
| `tests/test_sala_island.py` (or Playwright script) | **create** | Island renders each `sala_*` card on `canvas-dev.html`; accept routes ops; `esc` escaping; phase chip present & never a chat bubble. |

### Repo B — `exocortex.saas`, branch `collab/canvas-f3` off `main` (integration tip)

| Path | Action | Responsibility |
|---|---|---|
| `skills/excrtx-conduct-loop/SKILL.md` | **create** | 7 loop phases + anti-narration + no-weaken-the-gate. `compiled_rules:` + new EX-ID + dogfood scenario. |
| `skills/excrtx-conduct-bounds/SKILL.md` | **create** | 3 bounds (3-verify-fail / 2-empty-search / surprise) + authority order executivo>spec>tests>código + HITL-3-classes + the `conduct.jsonl` write protocol. `compiled_rules:` + new EX-ID + dogfood. |
| `SOUL_SEED.md` | **modify (generated)** | Regenerated by `compile_soul.py` — **do not hand-edit** the compiled block. |
| `$HERMES_HOME/SOUL.md` (runtime, isolated for smoke) | **propagate** | Receives `SOUL_SEED.md` **verbatim** via `setup.sh` step-07 (or `cp SOUL_SEED.md $HERMES_HOME/SOUL.md`). Mandatory 2nd hop — `compile_soul → SOUL_SEED.md` alone does NOT reach the launched session (SOUL trace). |
| `docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-07-port-conduct-skills.md` | **create** | Records CREATE-2-skills (vs embed) + corrected SOUL-propagation evidence (persona=`load_soul_md($HERMES_HOME/SOUL.md)`, step-07 copy, profile-force is a no-op in isolated mode). |
| `docs/plans/2026-07-23_canvas-tarefas/F3-PLANO.md` | *(this file)* | The plan. |

### Repo C — umbrella `projetob`, branch `collab/canvas-f3` off `master`

| Path | Action | Responsibility |
|---|---|---|
| `.harness/contracts/exocortex-hermes-webui.md` | **modify** | Add **§(g) Sala viva** (10 `sala_*` events + `/authorization/*` whitelist note + `launch.yaml`/`conduct.jsonl` conventions); bump version; reconcile "E9". |
| `.harness/changes/2026-07-25_COLLAB_canvas-f3-sala-viva.md` | **create** | COLLAB change record (three-repo scope, additive-SSE rationale, MOD-014, ADR-CT-07). |

---

## Shared Interface Contract (locked — every task honors these exact names/types)

### The 10 additive `sala_*` SSE events (contract §(g), stable names)

Each event is `event: <name>` + `data: <json payload>` over the non-closing `SALA_ROOMS[cid]` log (cursor-replayable, `since=N`). Payloads:

| Event | Payload | Emits when | `ops` (accept applies via `/api/canvas/patch`) |
|---|---|---|---|
| `sala_phase` | `{canvas_id, phase, seq}` | conduct.jsonl phase line | none (UI-only chip; **never** a token) |
| `sala_artifact` | `{canvas_id, title, type, path, tool, ops}` | file-producing `tool_complete` in journal | `[{op:add, path:/artifacts/expected/-, value:{title,path,type}}]` |
| `sala_gap` | `{canvas_id, source, clarify_id, session_id, question, choices_offered, ops}` | observed clarify **or** 2nd empty-search | `[{op:add, path:/gaps/-, value:question}]` |
| `sala_kanban` | `{canvas_id, task_id, column}` | phase→column projection | none (display only; no board write) |
| `sala_next_move` | `{canvas_id, text, ops}` | conduct/agent next-move signal | `[{op:add, path:/next_moves/-, value:text}]` |
| `sala_trace` | `{canvas_id, kind, title, evidence:{event_id?,path?,tool?}, verifiable:true, ops?}` | conduct.jsonl trace line (intent/twins/pending) | optional `[{op:add, path:/assumptions/-|/scope/-, value:title}]` |
| `sala_draft` | `{canvas_id, session_id, action, draft_text, approval_id, requires_auth:true}` | agent declares an external action (conduct `{"t":"draft"}`) **or** a runtime tool-permission gate fires (`approval_id` set) | none (the halt is the agent's own EX-08 turn-end / the runtime gate) |
| `sala_auth` | `{canvas_id, action, words, ops}` | human approves a `sala_draft`, typing verbatim words in-island | `[{op:add, path:/authorization/-, value:{action, words, at}}]` |
| `sala_interrupt` | `{canvas_id, klass, clarify_id?, session_id, tried, output, hypothesis, ops}` | 3rd verify-fail (observed clarify or watchdog) | `[{op:add, path:/gaps/-, value:hypothesis}]` |
| `sala_finding` | `{canvas_id, subject, code, check, spec, authority:["executivo","spec","tests","codigo"], resolution}` | surprise (code×check×spec disagree) | none (non-blocking) |

> `klass` avoids the Python keyword `class`. Field `type` in `sala_artifact` is the artifact kind (a plain string), not a Python type.

### `api/sala_reducer.py` — pure core (locked signatures)

```python
class SalaState:
    def __init__(self, canvas_id: str, task_id: str) -> None: ...
    def ingest(self, frame: dict) -> list[tuple[str, dict]]:
        """Take ONE normalized frame, return the list of (event_name, payload)
        to emit. Pure: no IO, no threads, no clock. Deterministic given frames."""
```

**Normalized frame taxonomy** (the observer produces these from conduct.jsonl + the two HITL queues; the reducer only sees these):

| `frame["kind"]` | source → other keys | reducer action |
|---|---|---|
| `"phase"` | conduct → `phase` (exact token, see below), `seq` | emit `sala_phase` + `sala_kanban` (via `PHASE_TO_COLUMN`) |
| `"artifact"` | conduct → `title, atype, path, tool` | emit `sala_artifact` |
| `"next_move"` | conduct → `text` | emit `sala_next_move` |
| `"trace"` | conduct → `trace_kind` (`intent\|twins\|pending`), `title`, `evidence` | emit `sala_trace` |
| `"verify"` | conduct → `subject, ok` (bool) | bump per-subject fail counter; on 3rd consecutive fail → emit `sala_interrupt` (klass=`verify_fail`) |
| `"search"` | conduct → `query_sig, empty` (bool) | bump empty counter (reuse `_bump_empty`/`_sig` shape); on 2nd → emit `sala_gap` (`source="empty_search"`) |
| `"surprise"` | conduct → `subject, code, check, spec` | emit `sala_finding` w/ `authority=["executivo","spec","tests","codigo"]` |
| `"clarify"` | clarify queue → `clarify_id, session_id, question, choices_offered` (+ `bound_interrupt?`) | emit `sala_gap` (`source="clarify"`) or `sala_interrupt` |
| `"approval"` | **two sources** → `session_id, action, draft_text, approval_id?` | emit `sala_draft`. Producers: (1) conduct `{"t":"draft"}` = the conducting agent's own EX-08 Draft-First declaration (`approval_id=None`); (2) `route_approvals._approval_sse_subscribe` = a genuine runtime **tool-permission** gate (real `approval_id`). |

**Exact phase tokens** (the skill MUST emit these verbatim — no spaces): `classify` · `define_done` · `evidence` · `decide` · `act` · `verify` · `report`.

`PHASE_TO_COLUMN = {"classify":"triage","define_done":"todo","evidence":"ready","decide":"ready","act":"running","verify":"running","report":"done"}`; a bound-trigger sets column `"blocked"`.

### `api/canvas_sala.py` — shell (locked public surface)

```python
SALA_ROOMS: dict[str, dict]                     # keyed by canvas_id
def register_launch(session_id: str, canvas_id: str, task_id: str) -> None
def resolve(session_id: str) -> dict | None     # -> {"canvas_id","task_id"} | None
def start_observer(session_id: str) -> None      # idempotent; no-op unless SALA_ENABLE=1
def handle_sala_get(handler, parsed) -> bool     # /api/canvas/sala/{stream,state}
def handle_sala_post(handler, path, body) -> bool  # /api/canvas/sala/observe
```

Seams (test-only): `SALA_ENABLE` (env gate, default off), the module dict `_INJECTED = {"conduct": callable|None}` (tests inject a fake conduct reader; the journal reader is deferred to F5), `SALA_POLL_INTERVAL` (env, default 1.0s).

### `_handle_launch` additive changes (canvas_tarefas.py)

At the existing `_emit(cid, "canvas_launched", …)` point: late-import `api.canvas_sala`, call `register_launch(session.session_id, cid, task_id)`, write `_tasks/<cid>/launch.yaml = {session_id, task_id, launched_at}`, and (SALA_ENABLE) `start_observer(session.session_id)`. Cold-start rebuild of `LAUNCHED` globs `_tasks/canvas_*/launch.yaml` (mirrors `_list_canvases`).

### `conduct.jsonl` line schema (agent-written, fork-read; documented in §(g))

Append-only JSONL at `_tasks/<task_id>/conduct.jsonl`; one object per line, appended by the live agent under `excrtx-conduct-*` governance. **Append mechanism** (the fork has no append-tool; `write_file` replaces): the skill instructs the agent to append via the shell tool — `printf '%s\n' '<json-line>' >> "$ACERVO/_tasks/<task_id>/conduct.jsonl"` (documented in `excrtx-conduct-loop`). Lines (phase token exact — no spaces):
```json
{"t": "phase",    "phase": "act", "seq": 4}
{"t": "trace",    "kind": "intent", "title": "...", "evidence": {"event_id": "..."}}
{"t": "artifact", "title": "...", "atype": "markdown", "path": "...", "tool": "write_file"}
{"t": "verify",   "subject": "test_x", "ok": false}
{"t": "search",   "query_sig": "...", "empty": true}
{"t": "surprise", "subject": "...", "code": "...", "check": "...", "spec": "..."}
{"t": "next_move","text": "..."}
{"t": "draft",    "action": "git push", "draft_text": "..."}
```
`_frame_from_conduct` maps `t`→frame `kind` (`t:"draft"`→`kind:"approval"`; all others `t:X`→`kind:X`; `t:"trace"` renames `kind`→`trace_kind`). **Everything here is agent-DECLARED via a tool write (not assistant text) → structurally out-of-band → anti-narration by construction** (OD-1). *(The `run_journal` artifact backstop — for artifacts the agent forgets to declare — is deferred to F5; see the Deferred section.)*

---

## Task Index

- **T1** — COLLAB scaffold (contract §(g) + change record + MOD-014) *(umbrella + fork docs)*
- **T2** — `/authorization/*` whitelist *(fork)*
- **T3** — `session_id↔canvas_id` linkage + `launch.yaml` *(fork)*
- **T4** — pure reducer: phase/artifact/next_move/trace frames *(fork)*
- **T5** — pure reducer: the 3 bounds + authority order *(fork)*
- **T6** — `SALA_ROOMS` room + non-closing stream + `/api/canvas/sala/state` *(fork)*
- **T7** — forward wiring `/api/canvas/sala/` *(fork)*
- **T8** — observer daemon (fingerprint→journal+conduct→reducer→emit) *(fork)*
- **T9** — clarify→gap bridge *(fork)*
- **T10** — bound-interrupt surfacing (observed clarify + watchdog) *(fork)*
- **T11** — Draft-First → `sala_draft`/`sala_auth` (approval observe + verbatim AUTH) *(fork)*
- **T12** — island `canvas-sala.js` + CSS + `canvas-dev.html` *(fork)*
- **T13** — `excrtx-conduct-loop` skill *(exocortex)* — filled after T0 SOUL trace
- **T14** — `excrtx-conduct-bounds` skill *(exocortex)* — filled after T0 SOUL trace
- **T15** — vetor→profile at launch so the persona carries the rules *(fork+exocortex)* — filled after T0 SOUL trace
- **T16** — exit-gate: real task, EX-49 raw proof, anti-narration guard *(all)* — filled after T0 SOUL trace

---

### Task 1: COLLAB scaffold — contract §(g) + change record + MOD-014

**Files:**
- Modify: `projetob/.harness/contracts/exocortex-hermes-webui.md` (add §(g); bump version header)
- Create: `projetob/.harness/changes/2026-07-25_COLLAB_canvas-f3-sala-viva.md`
- Modify: `hermes-webui/EXCRTX_MODIFICATIONS.md` (add MOD-014)

**Interfaces:**
- Produces: the canonical names every later task references — the 10 `sala_*` event names + payloads (§ Shared Interface Contract above), the `/authorization/*` whitelist entry, and the `launch.yaml` / `conduct.jsonl` task-dir conventions. No code depends on T1 at import time; it is the governance record that makes the additive SSE surface legitimate (contract change-rule).

- [ ] **Step 1: Write the failing check (contract completeness)**

Create `hermes-webui/tests/test_contract_g_names.py` (a lint that the contract lists every event this branch emits — keeps code and contract in lock-step). **M10:** the umbrella is an independent repo in its own worktree, NOT a sibling of the fork — so resolve its path from an env var and `skip` cleanly when absent (the fork suite must not hard-fail in a fork-only/CI checkout):

```python
import os, pathlib, pytest

def _contract_path():
    root = os.environ.get("UMBRELLA_ROOT")
    if not root:
        pytest.skip("UMBRELLA_ROOT not set (umbrella worktree path); run from the F3 harness")
    p = pathlib.Path(root) / ".harness" / "contracts" / "exocortex-hermes-webui.md"
    if not p.is_file():
        pytest.skip(f"contract not found at {p}")
    return p

SALA_EVENTS = ["sala_phase","sala_artifact","sala_gap","sala_kanban","sala_next_move",
               "sala_trace","sala_draft","sala_auth","sala_interrupt","sala_finding"]

def test_contract_declares_every_sala_event():
    text = _contract_path().read_text(encoding="utf-8")
    assert "### (g)" in text, "contract must define section (g)"
    missing = [e for e in SALA_EVENTS if e not in text]
    assert not missing, f"contract §(g) missing events: {missing}"
    # M8 / C-D: assert distinctive reconciliation markers written by THIS branch,
    # not substrings ('AG-UI', 'não') that already exist in the pre-(g) contract.
    assert "E9" in text and "AGUI_GATEWAY" in text, "contract §(g) must reconcile 'E9' vs the AGUI_GATEWAY surface"
```

> Run it with `UMBRELLA_ROOT=<umbrella-worktree>` in the SDD harness; it skips (not fails) elsewhere.

- [ ] **Step 2: Run it to verify it fails**

Run: `cd <fork-worktree> && .venv/bin/python -m pytest tests/test_contract_g_names.py -q`
Expected: FAIL (`### (g)` absent).

- [ ] **Step 3: Add §(g) to the contract**

Append to `exocortex-hermes-webui.md` (after §(f)), and bump the version header to `v1.2 — F3 Sala viva (subseção (g), agente-observador in-process, collab/canvas-f3)`:

```markdown
### (g) Sala viva (fork; MOD-014, F3) — camada observadora in-process

**"E9" reconciliado:** os eventos abaixo pertencem à **taxonomia SSE do canvas deste contrato** (§(d) + Curador §(f)); **NÃO** são eventos do gateway AG-UI (`AGUI_GATEWAY.md`, que governa `sales-AI /api/agente/run`, superfície diferente). A "E9 taxonomy" citada no F3-CHARTER resolve para esta seção.

**Endpoints** (forward em `api/canvas_tarefas.py`; `routes.py` INTOCADO):
| Método/rota | Request → Response |
|---|---|
| `GET /api/canvas/sala/stream?canvas_id=&since=N` | SSE re-anexável (log próprio `SALA_ROOMS`, replay por cursor; não fecha em terminal) |
| `GET /api/canvas/sala/state?canvas_id=` | → `{phase, columns, n_events}` (poll de fallback) |
| `POST /api/canvas/sala/observe` | `{canvas_id}` → `{ok}` (inicia idempotente o observador; no-op sem `SALA_ENABLE=1`) |

**Eventos SSE** (log próprio `SALA_ROOMS[cid]["events"]`, aditivos; nomes estáveis):
`sala_phase {canvas_id,phase,seq}` · `sala_artifact {canvas_id,title,type,path,tool,ops}` · `sala_gap {canvas_id,source,clarify_id,session_id,question,choices_offered,ops}` · `sala_kanban {canvas_id,task_id,column}` · `sala_next_move {canvas_id,text,ops}` · `sala_trace {canvas_id,kind,title,evidence,verifiable,ops?}` · `sala_draft {canvas_id,session_id,action,draft_text,approval_id,requires_auth}` · `sala_auth {canvas_id,action,words,ops}` · `sala_interrupt {canvas_id,klass,clarify_id?,session_id,tried,output,hypothesis,ops}` · `sala_finding {canvas_id,subject,code,check,spec,authority,resolution}`. `ops` = JSON-Patch RFC 6902 que "aceitar" aplica via `POST /api/canvas/patch`.

**Whitelist (espelho do fork):** `_WHITELIST_RAW` ganha `/authorization/*` — `authorization[]` já é canônico (`_MINIMAL`, ADR-CT-06 §5); só faltava ser editável. Núcleo (`canvas_schema.py`/`_CORE_TO_DOC`) intocado. **Nenhuma mudança de schema no exocortex** (aditivo puro do lado do fork).

**Convenções de task-dir** (aditivas, como o `links.yaml` do F1b):
- `_tasks/<canvas_id>/launch.yaml` = `{session_id, task_id, launched_at}` — linkagem durável session↔canvas.
- `_tasks/<task_id>/conduct.jsonl` = trilha append-only escrita pelo AGENTE VIVO (sob skills `excrtx-conduct-*`); o fork só LÊ. Linhas: `{t:phase|trace|artifact|verify|search|surprise|next_move|draft, …}` (tokens de fase exatos: `classify|define_done|evidence|decide|act|verify|report`). Append via shell (`printf … >> conduct.jsonl`; o fork não tem tool de append). É o canal out-of-band que torna tudo isso **não-narração por construção**. O backstop de artefatos via `run_journal` fica para F5.

**Guardrails**: a camada Sala **não cunha primitiva bloqueante** — só observa `clarify.sse_subscribe` e `route_approvals._approval_sse_subscribe` (ambos multi-subscriber); o único bloqueio HITL é o agente vivo auto-invocando clarify/approval (ou terminando o turno em Draft-First, EX-08). Logo "interrupções só nas 3 classes" é **estrutural**. O "sticky/long-timeout" do bound-interrupt é **comportamental+watchdog** (o `expires_at` sempre existe), não estrutural.
```

Also, in the same Step 3, **update the contract change-rule enumeration** (M9): edit the existing line `Rename/remoção/mudança de tipo de qualquer superfície (a)–(f) → breaking` to read **(a)–(g)** so the new Sala surface is enumerated as breaking-protected (the F2 precedent updated this when adding (f)).

- [ ] **Step 4: Create the COLLAB change record**

Create `projetob/.harness/changes/2026-07-25_COLLAB_canvas-f3-sala-viva.md` following `CHANGE_LOG_PROTOCOL.md`: mode COLLAB; three-repo scope (fork code + exocortex skills/ADR-CT-07 + umbrella contract); additive-SSE rationale; names the fork-mirror file touched (`_WHITELIST_RAW` in `canvas_tarefas.py`); notes **no exocortex schema change** (authorization[] already canonical); MOD-014; the E9/AG-UI reconciliation.

- [ ] **Step 5: Add MOD-014 to the fork catalog**

Append to `hermes-webui/EXCRTX_MODIFICATIONS.md` a `[MOD-014]` entry: "F3 Sala viva — observe-and-translate layer (`api/canvas_sala.py` + `api/sala_reducer.py`), forward `/api/canvas/sala/`, `static/canvas-sala.js`, `/authorization/*` whitelist; observes conduct.jsonl + clarify/approval registries; mints no blocking primitive (run_journal artifact backstop = F5)."

- [ ] **Step 6: Run the check to verify it passes**

Run: `cd <fork-worktree> && .venv/bin/python -m pytest tests/test_contract_g_names.py -q`
Expected: PASS.

- [ ] **Step 7: Commit (each repo separately, explicit paths, verify branch)**

```bash
# umbrella
git -C <umbrella-wt> branch --show-current && \
git -C <umbrella-wt> add .harness/contracts/exocortex-hermes-webui.md .harness/changes/2026-07-25_COLLAB_canvas-f3-sala-viva.md && \
git -C <umbrella-wt> commit -m "docs(contract): exocortex<->hermes-webui §(g) Sala viva + COLLAB record (F3)"
# fork
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add EXCRTX_MODIFICATIONS.md tests/test_contract_g_names.py && \
git -C <fork-wt> commit -m "docs(mod): MOD-014 Sala viva + contract §(g) name lint"
```
Expected: each commit prints `[collab/canvas-f3 <sha>]` — confirm the branch in the printed line (C-A).

---

### Task 2: `/authorization/*` whitelist

**Files:**
- Modify: `hermes-webui/api/canvas_tarefas.py:31-37` (`_WHITELIST_RAW`)
- Test: `hermes-webui/tests/test_sala_whitelist.py`

**Interfaces:**
- Consumes: `canvas_store.apply_patch`, `canvas_tarefas._path_editavel` (existing).
- Produces: `/authorization/-` becomes an accepted patch path (T11 `sala_auth` accept + T12 island rely on it). `authorization[]` already exists in `_MINIMAL` (canvas_store.py:33) and in the harness template (ADR-CT-06 §5).

- [ ] **Step 1: Write the failing test**

Create `tests/test_sala_whitelist.py`:

```python
from api import canvas_tarefas as ct

def test_authorization_pointer_is_editable():
    assert ct._path_editavel("/authorization/-") is True
    assert ct._path_editavel("/authorization/0") is True

def test_non_whitelisted_still_rejected():
    assert ct._path_editavel("/personas/evaluators/-") is False
```

> **I3 (review):** do NOT assert `/authorization/-\n` is rejected. A wildcard whitelist entry compiles to `^/authorization/[^/]+$`, and `[^/]` matches `\n`, so `fullmatch` would return **True** — the newline guard only holds for *literal* entries like `/focus` (`^/focus$`). This is identical to every existing wildcard pointer (`/gaps/*`, `/next_moves/*`, …); tightening it (`[^/]`→`[^/\n]` in `_whitelist_regex`) would change ALL wildcards and is **outside T2's scope → raise as a surprise, do not do silently**.

- [ ] **Step 2: Run it to verify it fails**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_whitelist.py -q`
Expected: FAIL — `/authorization/-` not yet whitelisted (`_path_editavel` returns False).

- [ ] **Step 3: Add the one whitelist entry**

In `api/canvas_tarefas.py`, extend `_WHITELIST_RAW` (the tuple at :31-37) with `"/authorization/*"`:

```python
    "/personas/suggested/*", "/acervo_aplicado/*",
    "/authorization/*",
)
```

- [ ] **Step 4: Run it to verify it passes**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_whitelist.py -q`
Expected: PASS (3 tests).

- [ ] **Step 5: Add the round-trip patch test (guards the `authorization` key exists)**

Append to `tests/test_sala_whitelist.py` — proves an actual `/patch` add lands, catching the case where a loaded doc lacks the `authorization` list:

```python
import copy
from api import canvas_store

def test_patch_adds_authorization_item(tmp_path, monkeypatch):
    monkeypatch.setenv("ACERVO", str(tmp_path))
    (tmp_path / "_tasks").mkdir()
    cid, canvas = canvas_store.create_draft("autorizar envio de ofício")
    # a launched-session doc must carry an authorization list (harness template does;
    # _MINIMAL fallback does). Assert the add applies and re-validates.
    ops = [{"op": "add", "path": "/authorization/-",
            "value": {"action": "git push", "words": "pode dar push", "at": "2026-07-25T20:00:00Z"}}]
    canvas2 = canvas_store.apply_patch(copy.deepcopy(canvas), ops)
    assert canvas2["authorization"][-1]["words"] == "pode dar push"
```

- [ ] **Step 6: Run it**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_whitelist.py -q`
Expected: PASS (4 tests). If the template lacks `authorization`, this fails loudly → the implementer confirms the F1a harness template carries `authorization: []` (it must, per ADR-CT-06 §5) and, if not, files a surprise (scope constraint 2) rather than editing the template silently.

- [ ] **Step 7: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add api/canvas_tarefas.py tests/test_sala_whitelist.py && \
git -C <fork-wt> commit -m "feat(canvas): whitelist /authorization/* for patch (F3 sala_auth)"
```

---

### Task 3: `session_id ↔ canvas_id` linkage + `launch.yaml`

**Files:**
- Create: `hermes-webui/api/canvas_sala.py` (only the `LAUNCHED` index + `register_launch`/`resolve`/`_rebuild_launched` in this task; the room/observer arrive in T6/T8)
- Modify: `hermes-webui/api/canvas_tarefas.py` — `_handle_launch` (write `launch.yaml` + `register_launch`)
- Test: `hermes-webui/tests/test_sala_launch_link.py`

**Interfaces:**
- Produces: `canvas_sala.register_launch(session_id, canvas_id, task_id) -> None`, `canvas_sala.resolve(session_id) -> {"canvas_id","task_id"} | None`, `canvas_sala._rebuild_launched() -> None` (cold-start glob). T8 observer calls `resolve` to route journal frames to the right room; T6/T8 add more to this module.
- Consumes: `canvas_store.tasks_dir()`, the existing `_handle_launch` `_emit(cid,"canvas_launched",…)` point (canvas_tarefas.py:269).

- [ ] **Step 1: Write the failing test**

Create `tests/test_sala_launch_link.py`:

```python
import yaml
from pathlib import Path
from api import canvas_sala

def test_register_and_resolve(monkeypatch, tmp_path):
    monkeypatch.setenv("ACERVO", str(tmp_path))
    (tmp_path / "_tasks" / "canvas_20260725_120000_x_00100").mkdir(parents=True)
    canvas_sala._LAUNCHED.clear()
    canvas_sala.register_launch("sess-1", "canvas_20260725_120000_x_00100", "task_abc")
    assert canvas_sala.resolve("sess-1") == {"canvas_id": "canvas_20260725_120000_x_00100", "task_id": "task_abc"}
    assert canvas_sala.resolve("nope") is None
    # durable sidecar written under the canvas dir
    lp = tmp_path / "_tasks" / "canvas_20260725_120000_x_00100" / "launch.yaml"
    assert yaml.safe_load(lp.read_text())["session_id"] == "sess-1"

def test_rebuild_after_restart(monkeypatch, tmp_path):
    monkeypatch.setenv("ACERVO", str(tmp_path))
    d = tmp_path / "_tasks" / "canvas_20260725_120000_y_00200"
    d.mkdir(parents=True)
    (d / "launch.yaml").write_text(yaml.safe_dump(
        {"session_id": "sess-2", "task_id": "task_y", "launched_at": "t"}))
    canvas_sala._LAUNCHED.clear()            # simulate server restart (memory lost)
    canvas_sala._rebuild_launched()
    assert canvas_sala.resolve("sess-2") == {"canvas_id": "canvas_20260725_120000_y_00200", "task_id": "task_y"}
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_launch_link.py -q`
Expected: FAIL — `api.canvas_sala` does not exist.

- [ ] **Step 3: Create `api/canvas_sala.py` with the linkage core**

```python
"""EXCRTX MOD-014 (F3) — Sala viva: observe-and-translate layer.

Camada in-process que reflete a sessão lançada no canvas. NUNCA cunha
primitiva bloqueante (só observa clarify/approval multi-subscriber);
NUNCA escreve no runtime da sessão. Gate SALA_ENABLE (default off).
Este arquivo cresce por tarefa: T3=linkagem, T6=sala+stream, T8=observador."""
from __future__ import annotations

import threading
import time
import yaml

from api import canvas_store

_LAUNCHED: dict[str, dict] = {}          # session_id -> {"canvas_id","task_id"}
_LAUNCHED_LOCK = threading.Lock()


def register_launch(session_id: str, canvas_id: str, task_id: str) -> None:
    """Grava a linkagem em memória E num sidecar durável canvas-keyed
    (_tasks/<canvas_id>/launch.yaml), para sobreviver a restart do servidor."""
    with _LAUNCHED_LOCK:
        _LAUNCHED[session_id] = {"canvas_id": canvas_id, "task_id": task_id}
    d = canvas_store.tasks_dir() / canvas_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "launch.yaml").write_text(
        yaml.safe_dump({"session_id": session_id, "task_id": task_id,
                        "launched_at": time.strftime("%Y-%m-%dT%H:%M:%S")},
                       allow_unicode=True, sort_keys=False),
        encoding="utf-8")


def resolve(session_id: str) -> dict | None:
    with _LAUNCHED_LOCK:
        v = _LAUNCHED.get(session_id)
        return dict(v) if v else None


def _rebuild_launched() -> None:
    """Cold-start: reconstrói _LAUNCHED varrendo os sidecars em disco
    (mesmo padrão de _list_canvases)."""
    for p in canvas_store.tasks_dir().glob("canvas_*/launch.yaml"):
        try:
            doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        sid = doc.get("session_id")
        if sid:
            with _LAUNCHED_LOCK:
                _LAUNCHED[sid] = {"canvas_id": p.parent.name, "task_id": doc.get("task_id")}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_launch_link.py -q`
Expected: PASS (2 tests).

- [ ] **Step 5: Wire `register_launch` into `_handle_launch`**

In `api/canvas_tarefas.py`, at the `_emit(cid, "canvas_launched", …)` line (:269), add immediately after it (late import to keep boot cheap, like the Curador forward):

```python
    _emit(cid, "canvas_launched", {"task_id": task_id, "session_id": session.session_id})
    from api import canvas_sala
    canvas_sala.register_launch(session.session_id, cid, task_id)
```

- [ ] **Step 6: Add the wiring test (launch populates the link)**

Append to `tests/test_sala_launch_link.py` — reuses the F1b `_handle_launch` test seams (`_new_session`/`_register_task` are monkeypatchable):

```python
def test_handle_launch_registers_link(monkeypatch, tmp_path):
    monkeypatch.setenv("ACERVO", str(tmp_path))
    from api import canvas_tarefas as ct, canvas_store, canvas_sala
    cid, _ = canvas_store.create_draft("preparar ofício")
    # minimal valid doc so compile_brief passes (vetor != ambiguo)
    doc = canvas_store.load_canvas(cid); doc["vetor"] = "execucao"; doc["focus"] = "preparar ofício de renegociação"
    canvas_store.save_canvas(cid, doc)
    monkeypatch.setattr(ct, "_register_task", lambda *a, **k: "task_L")
    monkeypatch.setattr(ct, "_new_session", lambda: type("S", (), {"session_id": "sess-L"})())
    monkeypatch.setattr(ct, "_stage_file", lambda sid, p: {"name": p.name, "path": str(p), "size": 1, "mime": "text/markdown", "is_image": False})
    canvas_sala._LAUNCHED.clear()
    captured = {}
    class H:  # fake handler capturing the JSON body
        def send_response(self, *a): pass
        def send_header(self, *a): pass
        def end_headers(self): pass
        class wfile:
            @staticmethod
            def write(b): captured["body"] = b
    ct._handle_launch(H(), {"canvas_id": cid})
    assert canvas_sala.resolve("sess-L") == {"canvas_id": cid, "task_id": "task_L"}
```

- [ ] **Step 7: Run it**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_launch_link.py -q`
Expected: PASS (3 tests).

- [ ] **Step 8: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add api/canvas_sala.py api/canvas_tarefas.py tests/test_sala_launch_link.py && \
git -C <fork-wt> commit -m "feat(sala): session<->canvas linkage + durable launch.yaml (F3 T3)"
```

---

### Task 4: pure reducer — phase / artifact / next_move / trace frames

**Files:**
- Create: `hermes-webui/api/sala_reducer.py`
- Test: `hermes-webui/tests/test_sala_reducer.py`

**Interfaces:**
- Produces: `SalaState(canvas_id, task_id)` with `.ingest(frame) -> list[(event, payload)]` and module const `PHASE_TO_COLUMN`. T5 extends the SAME class with bound frames. T8 observer calls `.ingest` per normalized frame and `_emit`s each returned tuple.

- [ ] **Step 1: Write the failing test**

Create `tests/test_sala_reducer.py`:

```python
from api.sala_reducer import SalaState, PHASE_TO_COLUMN

def _st(): return SalaState("canvas_x", "task_x")

def test_phase_frame_emits_phase_and_kanban():
    out = _st().ingest({"kind": "phase", "phase": "act", "seq": 4})
    names = [n for n, _ in out]
    assert names == ["sala_phase", "sala_kanban"]
    phase_p = out[0][1]; kanban_p = out[1][1]
    assert phase_p == {"canvas_id": "canvas_x", "phase": "act", "seq": 4}
    assert kanban_p == {"canvas_id": "canvas_x", "task_id": "task_x", "column": PHASE_TO_COLUMN["act"]}

def test_artifact_frame_emits_sala_artifact_with_ops():
    out = _st().ingest({"kind": "artifact", "title": "Ofício v1", "atype": "markdown",
                        "path": "/x/oficio.md", "tool": "write_file"})
    assert len(out) == 1 and out[0][0] == "sala_artifact"
    p = out[0][1]
    assert p["ops"] == [{"op": "add", "path": "/artifacts/expected/-",
                         "value": {"title": "Ofício v1", "path": "/x/oficio.md", "type": "markdown"}}]

def test_next_move_frame():
    out = _st().ingest({"kind": "next_move", "text": "validar com o jurídico"})
    assert out == [("sala_next_move", {"canvas_id": "canvas_x", "text": "validar com o jurídico",
                    "ops": [{"op": "add", "path": "/next_moves/-", "value": "validar com o jurídico"}]})]

def test_trace_frame_intent():
    out = _st().ingest({"kind": "trace", "trace_kind": "intent", "title": "Renegociar prazo",
                        "evidence": {"event_id": "run1:3"}})
    assert out[0][0] == "sala_trace"
    p = out[0][1]
    assert p["kind"] == "intent" and p["verifiable"] is True and p["evidence"] == {"event_id": "run1:3"}
    assert p["ops"] == [{"op": "add", "path": "/assumptions/-", "value": "Renegociar prazo"}]

def test_unknown_frame_is_ignored():
    assert _st().ingest({"kind": "wat"}) == []
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_reducer.py -q`
Expected: FAIL — module missing.

- [ ] **Step 3: Implement the reducer (frames handled in this task)**

```python
"""EXCRTX MOD-014 (F3) — Sala reducer: núcleo PURO (sem IO/threads/relógio).

Recebe UM frame normalizado (produzido pelo observador a partir do
conduct.jsonl e das filas HITL clarify/approval) e devolve a lista de (evento, payload) a emitir.
Determinístico: mesma sequência de frames -> mesma sequência de eventos.
É a costura de teste hermética do F3 (fakes entram, lista exata sai)."""
from __future__ import annotations

PHASE_TO_COLUMN = {
    "classify": "triage", "define_done": "todo", "evidence": "ready",
    "decide": "ready", "act": "running", "verify": "running", "report": "done",
}

TRACE_OP_PATH = {"intent": "/assumptions/-", "twins": "/scope/-", "pending": "/assumptions/-"}


class SalaState:
    def __init__(self, canvas_id: str, task_id: str) -> None:
        self.cid = canvas_id
        self.task_id = task_id
        # bound counters (T5)
        self._verify_fails: dict[str, int] = {}
        self._empty = 0
        self._last_sig: str | None = None
        self._has_baseline = False

    def ingest(self, frame: dict) -> list[tuple[str, dict]]:
        kind = frame.get("kind")
        handler = getattr(self, f"_on_{kind}", None)
        if handler is None:
            return []
        return handler(frame)

    # ── D4 / D1 ───────────────────────────────────────────────────────────
    def _on_phase(self, f: dict) -> list[tuple[str, dict]]:
        phase = f.get("phase")
        column = PHASE_TO_COLUMN.get(phase, "triage")
        return [
            ("sala_phase", {"canvas_id": self.cid, "phase": phase, "seq": f.get("seq")}),
            ("sala_kanban", {"canvas_id": self.cid, "task_id": self.task_id, "column": column}),
        ]

    def _on_artifact(self, f: dict) -> list[tuple[str, dict]]:
        value = {"title": f.get("title"), "path": f.get("path"), "type": f.get("atype")}
        return [("sala_artifact", {
            "canvas_id": self.cid, "title": f.get("title"), "type": f.get("atype"),
            "path": f.get("path"), "tool": f.get("tool"),
            "ops": [{"op": "add", "path": "/artifacts/expected/-", "value": value}]})]

    def _on_next_move(self, f: dict) -> list[tuple[str, dict]]:
        text = f.get("text")
        return [("sala_next_move", {
            "canvas_id": self.cid, "text": text,
            "ops": [{"op": "add", "path": "/next_moves/-", "value": text}]})]

    def _on_trace(self, f: dict) -> list[tuple[str, dict]]:
        tk = f.get("trace_kind")
        payload = {"canvas_id": self.cid, "kind": tk, "title": f.get("title"),
                   "evidence": f.get("evidence") or {}, "verifiable": True}
        path = TRACE_OP_PATH.get(tk)
        if path:
            payload["ops"] = [{"op": "add", "path": path, "value": f.get("title")}]
        return [("sala_trace", payload)]
```

- [ ] **Step 4: Run it to verify it passes**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_reducer.py -q`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add api/sala_reducer.py tests/test_sala_reducer.py && \
git -C <fork-wt> commit -m "feat(sala): pure reducer for phase/artifact/next_move/trace (F3 T4)"
```

---

### Task 5: pure reducer — the 3 bounds + authority order

**Files:**
- Modify: `hermes-webui/api/sala_reducer.py` (add `_on_verify`, `_on_search`, `_on_surprise`)
- Test: `hermes-webui/tests/test_sala_reducer.py` (append)

**Interfaces:**
- Consumes: `SalaState` from T4.
- Produces: bound behavior — `sala_interrupt` on 3rd consecutive verify-fail per subject; `sala_gap`(source=`empty_search`) on 2nd empty; `sala_finding` on surprise with fixed authority order. Mirrors the F2 Curador `_bump_empty`/`_sig`/threshold shape (canvas_curador.py:356-376).

- [ ] **Step 1: Write the failing test (append to `tests/test_sala_reducer.py`)**

```python
def test_verify_fail_interrupts_on_third_consecutive():
    st = _st()
    assert st.ingest({"kind": "verify", "subject": "test_a", "ok": False}) == []
    assert st.ingest({"kind": "verify", "subject": "test_a", "ok": False}) == []
    out = st.ingest({"kind": "verify", "subject": "test_a", "ok": False})
    assert out[0][0] == "sala_interrupt"
    p = out[0][1]
    assert p["klass"] == "verify_fail" and p["ops"] == [{"op": "add", "path": "/gaps/-", "value": p["hypothesis"]}]

def test_verify_success_resets_counter():
    st = _st()
    st.ingest({"kind": "verify", "subject": "test_a", "ok": False})
    st.ingest({"kind": "verify", "subject": "test_a", "ok": True})   # reset
    st.ingest({"kind": "verify", "subject": "test_a", "ok": False})
    out = st.ingest({"kind": "verify", "subject": "test_a", "ok": False})
    assert out == []   # only 2 fails since reset

def test_verify_fail_per_subject_isolated():
    st = _st()
    for _ in range(2): st.ingest({"kind": "verify", "subject": "a", "ok": False})
    assert st.ingest({"kind": "verify", "subject": "b", "ok": False}) == []  # b independent

def test_empty_search_gap_on_second():
    st = _st()
    assert st.ingest({"kind": "search", "query_sig": "sig1", "empty": True}) == []
    out = st.ingest({"kind": "search", "query_sig": "sig2", "empty": True})
    assert out[0][0] == "sala_gap" and out[0][1]["source"] == "empty_search"

def test_identical_signature_counts_as_empty():
    st = _st()
    st.ingest({"kind": "search", "query_sig": "same", "empty": False})   # baseline
    out = st.ingest({"kind": "search", "query_sig": "same", "empty": False})  # repeat -> empty#1... need 2
    # first repeat is empty#1 (dup of baseline), second repeat triggers gap
    out2 = st.ingest({"kind": "search", "query_sig": "same", "empty": False})
    assert out2[0][0] == "sala_gap"

def test_surprise_emits_finding_with_authority_order():
    out = _st().ingest({"kind": "surprise", "subject": "prazo", "code": "30d", "check": "45d", "spec": "60d"})
    assert out[0][0] == "sala_finding"
    assert out[0][1]["authority"] == ["executivo", "spec", "tests", "codigo"]
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_reducer.py -q`
Expected: FAIL — `_on_verify`/`_on_search`/`_on_surprise` missing (frames ignored → `[]`).

- [ ] **Step 3: Implement the bound handlers (append to `SalaState`)**

```python
    # ── D3 bounds (mirror F2 Curador _bump_empty/_sig shape) ───────────────
    def _on_verify(self, f: dict) -> list[tuple[str, dict]]:
        subj = f.get("subject") or ""
        if f.get("ok"):
            self._verify_fails[subj] = 0            # success resets the streak
            return []
        n = self._verify_fails.get(subj, 0) + 1
        self._verify_fails[subj] = n
        if n < 3:
            return []
        hypothesis = f.get("hypothesis") or (
            f"'{subj}' falhou {n}x seguidas — provável causa a investigar")
        return [("sala_interrupt", {
            "canvas_id": self.cid, "klass": "verify_fail",
            "clarify_id": f.get("clarify_id"), "session_id": f.get("session_id"),
            "tried": f.get("tried"), "output": f.get("output"), "hypothesis": hypothesis,
            "ops": [{"op": "add", "path": "/gaps/-", "value": hypothesis}]})]

    def _on_search(self, f: dict) -> list[tuple[str, dict]]:
        sig = f.get("query_sig") or ""
        empty = bool(f.get("empty")) or (sig == self._last_sig) or (not self._has_baseline)
        self._last_sig = sig
        self._has_baseline = True
        if not empty:
            return []
        self._empty += 1
        if self._empty < 2:
            return []
        q = f.get("query") or sig or "busca"
        reason = f"Sala não encontrou informação nova para '{q}' após 2 buscas"
        return [("sala_gap", {"canvas_id": self.cid, "source": "empty_search",
                              "question": reason,
                              "ops": [{"op": "add", "path": "/gaps/-", "value": reason}]})]

    def _on_surprise(self, f: dict) -> list[tuple[str, dict]]:
        return [("sala_finding", {
            "canvas_id": self.cid, "subject": f.get("subject"),
            "code": f.get("code"), "check": f.get("check"), "spec": f.get("spec"),
            "authority": ["executivo", "spec", "tests", "codigo"],
            "resolution": f.get("resolution")})]
```

> Bound semantics honor C-C: the reducer only *emits a card*; it never blocks. The genuine halt is the live agent self-invoking clarify (observed via T9/T10). `_on_verify` counts **consecutive** fails per subject (a success resets), matching "3 fix-fail cycles on the SAME verification" (constraint 6).

- [ ] **Step 4: Run to verify it passes**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_reducer.py -q`
Expected: PASS (11 tests total).

- [ ] **Step 5: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add api/sala_reducer.py tests/test_sala_reducer.py && \
git -C <fork-wt> commit -m "feat(sala): reducer bounds (3-verify-fail/2-empty/surprise) + authority order (F3 T5)"
```

---

### Task 6: `SALA_ROOMS` room + non-closing stream + `/api/canvas/sala/state`

**Files:**
- Modify: `hermes-webui/api/canvas_sala.py` (add `SALA_ROOMS`, `_room`, `_emit`, `_stream_events`, `_project`, `handle_sala_get` for stream/state)
- Test: `hermes-webui/tests/test_canvas_sala.py`

**Interfaces:**
- Produces: `SALA_ROOMS`, `_room(cid)`, `_emit(cid, name, payload)`, `_project(room) -> {"phase","columns","n_events"}`, and `handle_sala_get(handler, parsed)` handling `/api/canvas/sala/stream` + `/api/canvas/sala/state`. T7 forwards to `handle_sala_get`; T8 observer calls `_emit`.
- Consumes: nothing new (cloned from the F2 Curador room, `canvas_curador.py:35-73` + `210-235`).

- [ ] **Step 1: Write the failing test**

Create `tests/test_canvas_sala.py`:

```python
from api import canvas_sala

def test_emit_appends_and_project_derives_phase_and_columns():
    canvas_sala.SALA_ROOMS.clear()
    canvas_sala._emit("cid1", "sala_phase", {"canvas_id": "cid1", "phase": "act", "seq": 1})
    canvas_sala._emit("cid1", "sala_kanban", {"canvas_id": "cid1", "task_id": "t1", "column": "running"})
    proj = canvas_sala._project(canvas_sala._room("cid1"))
    assert proj == {"phase": "act", "columns": {"t1": "running"}, "n_events": 2}

def test_emit_to_missing_room_creates_it():
    canvas_sala.SALA_ROOMS.clear()
    canvas_sala._emit("cid2", "sala_next_move", {"canvas_id": "cid2", "text": "x"})
    assert len(canvas_sala._room("cid2")["events"]) == 1
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_sala.py -q`
Expected: FAIL — `_emit`/`_room`/`_project` missing.

- [ ] **Step 3: Add the room + stream + state (clone of the Curador room)**

Append to `api/canvas_sala.py`:

```python
import json
from urllib.parse import parse_qs

SALA_ROOMS: dict[str, dict] = {}
_ROOMS_LOCK = threading.Lock()


def _room(cid: str) -> dict:
    with _ROOMS_LOCK:
        room = SALA_ROOMS.get(cid)
        if room is None:
            room = {"events": [], "cond": threading.Condition()}
            SALA_ROOMS[cid] = room
        return room


def _emit(cid: str, name: str, payload) -> None:
    """Append-only + notify. Cloned from CURADOR_ROOMS: non-closing, cursor-replay."""
    room = _room(cid)
    with room["cond"]:
        room["events"].append((name, payload))
        room["cond"].notify_all()


def _project(room: dict) -> dict:
    phase = None
    columns: dict = {}
    with room["cond"]:
        events = list(room["events"])
    for name, payload in events:
        if name == "sala_phase":
            phase = payload.get("phase")
        elif name == "sala_kanban":
            columns[payload.get("task_id")] = payload.get("column")
    return {"phase": phase, "columns": columns, "n_events": len(events)}


def _j(handler, obj, status=200):
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _stream_events(handler, room: dict, cursor: int) -> None:
    """SSE re-anexável; NÃO fecha em terminal (a sala serve a sessão inteira)."""
    handler.send_response(200)
    handler.send_header("Content-Type", "text/event-stream; charset=utf-8")
    handler.send_header("Cache-Control", "no-cache")
    handler.end_headers()
    try:
        while True:
            with room["cond"]:
                room["cond"].wait_for(lambda: len(room["events"]) > cursor, timeout=30)
                pending = room["events"][cursor:]
            if not pending:
                handler.wfile.write(b": keepalive\n\n")
                handler.wfile.flush()
                continue
            frames = []
            for name, payload in pending:
                cursor += 1
                data = json.dumps(payload, ensure_ascii=False)
                frames.append(f"id: {cursor}\nevent: {name}\ndata: {data}\n\n")
            handler.wfile.write("".join(frames).encode("utf-8"))
            handler.wfile.flush()
    except (BrokenPipeError, ConnectionResetError):
        pass


def handle_sala_get(handler, parsed) -> bool:
    if parsed.path == "/api/canvas/sala/stream":
        qs = parse_qs(parsed.query)
        cid = (qs.get("canvas_id") or [""])[0]
        try:
            cursor = int((qs.get("since") or ["0"])[0])
        except (TypeError, ValueError):
            cursor = 0
        if cursor < 0:
            cursor = 0
        # opening the stream starts the observer for the linked session (idempotent).
        link = _link_for_canvas(cid)
        if link:
            start_observer(link)
        _stream_events(handler, _room(cid), cursor)
        return True
    if parsed.path == "/api/canvas/sala/state":
        cid = (parse_qs(parsed.query).get("canvas_id") or [""])[0]
        _j(handler, _project(_room(cid)))
        return True
    return False


def _link_for_canvas(cid: str) -> str | None:
    """Reverse of resolve(): find the session_id linked to a canvas_id."""
    with _LAUNCHED_LOCK:
        for sid, v in _LAUNCHED.items():
            if v.get("canvas_id") == cid:
                return sid
    return None
```

> `start_observer` is defined in T8; until then `handle_sala_get` references it. Sequence T6→T7→T8 keeps the module importable at each commit because `start_observer` lands in T8 **before** T7's forward is exercised end-to-end. To keep T6 self-testable in isolation, add a temporary module-level `def start_observer(session_id): pass` stub at the end of T6 and replace it with the real one in T8 (the T8 diff removes the stub). *(Reviewer note: this is the one forward-reference in the plan; flagged deliberately.)*

- [ ] **Step 4: Run to verify it passes**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_sala.py -q`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add api/canvas_sala.py tests/test_canvas_sala.py && \
git -C <fork-wt> commit -m "feat(sala): SALA_ROOMS non-closing stream + state projection (F3 T6)"
```

---

### Task 7: forward wiring `/api/canvas/sala/`

**Files:**
- Modify: `hermes-webui/api/canvas_tarefas.py` — `handle_canvas_get` (:367) + `handle_canvas_post` (:279)
- Test: `hermes-webui/tests/test_canvas_sala.py` (append)

**Interfaces:**
- Consumes: `canvas_sala.handle_sala_get` (T6), `canvas_sala.handle_sala_post` (T8).
- Produces: routing so `/api/canvas/sala/*` reaches the Sala module; unknown sala subpaths fall through to a clean 404. **`routes.py` gains 0 lines** (constraint 3).

- [ ] **Step 1: Write the failing test (append to `tests/test_canvas_sala.py`)**

```python
from urllib.parse import urlparse
from api import canvas_tarefas as ct

class _StateHandler:
    def __init__(self): self.body = None; self.status = 200
    def send_response(self, s): self.status = s
    def send_header(self, *a): pass
    def end_headers(self): pass
    class _W:
        def __init__(self, o): self.o = o
        def write(self, b): self.o.body = b
    @property
    def wfile(self): return _StateHandler._W(self)

def test_forward_routes_sala_state():
    canvas_sala_cleared = __import__("api.canvas_sala", fromlist=["SALA_ROOMS"])
    canvas_sala_cleared.SALA_ROOMS.clear()
    h = _StateHandler()
    handled = ct.handle_canvas_get(h, urlparse("/api/canvas/sala/state?canvas_id=cidX"))
    assert handled is True and h.status == 200

def test_forward_unknown_sala_path_falls_through():
    h = _StateHandler()
    handled = ct.handle_canvas_get(h, urlparse("/api/canvas/sala/bogus"))
    assert handled is False   # handle_sala_get returns False -> caller returns False
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_sala.py::test_forward_routes_sala_state -q`
Expected: FAIL — no sala forward yet (`handle_canvas_get` returns False for the state path or errors).

- [ ] **Step 3: Add the 2-line forward (mirror the Curador forward verbatim)**

In `handle_canvas_post` (after the curador forward at :280-282):

```python
    if path.startswith("/api/canvas/sala/"):     # MOD-014 (F3): forward à Sala viva
        from api.canvas_sala import handle_sala_post
        return handle_sala_post(handler, path, body)
```

In `handle_canvas_get` (after the curador forward at :368-370):

```python
    if parsed.path.startswith("/api/canvas/sala/"):   # MOD-014 (F3): forward à Sala viva
        from api.canvas_sala import handle_sala_get
        return handle_sala_get(handler, parsed)
```

> `handle_sala_post` is defined in T8. For T7 to pass in isolation, add a temporary `def handle_sala_post(handler, path, body): return False` stub in `canvas_sala.py` (replaced by the real one in T8). The GET forward is fully exercised now (state endpoint from T6).

- [ ] **Step 4: Run to verify it passes**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_sala.py -q`
Expected: PASS.

- [ ] **Step 5: Confirm `routes.py` is untouched (EX-49)**

Run: `cd <fork-wt> && git diff --stat api/routes.py`
Expected: **empty output** (zero lines changed in routes.py — constraint 3).

- [ ] **Step 6: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add api/canvas_tarefas.py tests/test_canvas_sala.py && \
git -C <fork-wt> commit -m "feat(sala): forward /api/canvas/sala/ (routes.py untouched) (F3 T7)"
```

---

### Task 8: observer daemon — conduct.jsonl + HITL queues → reducer → emit

**Files:**
- Modify: `hermes-webui/api/canvas_sala.py` (observer + normalizers + `start_observer`/`_run_observer`/`_poll_once`/`_prime`/`handle_sala_post`)
- Test: `hermes-webui/tests/test_canvas_sala.py` (append)

**Interfaces:**
- Consumes: `SalaState` (T4/T5), `_emit`/`_room` (T6), `resolve` (T3), `clarify.sse_subscribe`/`sse_unsubscribe`/`get_pending`, `route_approvals._approval_sse_subscribe`/`_approval_sse_unsubscribe`.
- Produces: `start_observer(session_id)` (idempotent, `SALA_ENABLE`-gated), `_poll_once(st, ctx) -> int`, `_prime(st, ctx)`, the normalizers `_frame_from_conduct`/`_frame_from_clarify`/`_frame_from_approval`, `handle_sala_post` (`/api/canvas/sala/observe`). Module test-injection point `_INJECTED = {"conduct": callable|None}`.
- **Journal-tail artifact backstop removed** (review C1/C2/C3): `run_journal.read_session_run_events` returns a **dict** `{status, events}` (not a list), requires a real `run_id:seq` cursor (no "from the beginning"), and its tool payload is nested under `payload` with keys `name/args/preview` (no `path`/`artifact`) — a bootstrap redesign. Since OD-1 makes conduct.jsonl authoritative, v1 drops the backstop; F5 restores it with the corrected shape (see Deferred).

- [ ] **Step 1: Confirm the approval `pending` head shape (EX-49 — before writing `_frame_from_approval`)**

The approval-SSE `pending` dict is the one external shape to pin. Confirm from the real submit call site (not `run_journal` — that never shows it):

Run:
```bash
cd <fork-wt>
grep -n "submit_pending" api/routes.py | head
.venv/bin/python - <<'PY'
import inspect
from api import route_approvals
print(inspect.getsource(route_approvals.submit_pending)[:1400])
print("== SSE envelope ==")
print(inspect.getsource(route_approvals._approval_sse_notify_locked)[:900])
PY
```
Expected: confirms the SSE envelope is `{"pending": {...}, "pending_count": N}` (route_approvals.py:87) and the pending head keys are **`command`/`pattern_key`/`description`/`approval_id`** (routes.py submit call site ~:19127) — **not** `action`/`summary`/`draft`/`payload`. Write `_frame_from_approval` against these confirmed keys. *(The clarify head keys `clarify_id`/`question`/`choices_offered` are already confirmed from `clarify.py`.)*

- [ ] **Step 2: Write the failing test (append to `tests/test_canvas_sala.py`)**

```python
import queue as _queue
from api import canvas_sala

def _ctx(sid, cq, aq):
    return {"sid": sid, "clarify_q": cq, "approval_q": aq, "conduct_off": 0}

def test_poll_once_translates_conduct_frames(monkeypatch):
    canvas_sala.SALA_ROOMS.clear()
    from api.sala_reducer import SalaState
    st = SalaState("cidP", "taskP")
    conduct = [{"t": "phase", "phase": "act", "seq": 1},
               {"t": "artifact", "title": "Ofício", "atype": "markdown", "path": "/o.md", "tool": "write_file"}]
    canvas_sala._INJECTED["conduct"] = lambda task_id, off: (conduct[off:], len(conduct))
    ctx = _ctx("sidP", _queue.Queue(), _queue.Queue())
    n = canvas_sala._poll_once(st, ctx)
    names = [nm for nm, _ in canvas_sala._room("cidP")["events"]]
    assert names == ["sala_phase", "sala_kanban", "sala_artifact"] and n == 3
    canvas_sala._INJECTED.clear()

def test_poll_once_drains_clarify_queue(monkeypatch):
    canvas_sala.SALA_ROOMS.clear()
    from api.sala_reducer import SalaState
    st = SalaState("cidC", "taskC")
    canvas_sala._INJECTED["conduct"] = lambda t, o: ([], o)
    cq = _queue.Queue()
    cq.put({"pending": {"clarify_id": "cl1", "question": "qual prazo?", "choices_offered": ["30d", "60d"]}, "pending_count": 1})
    canvas_sala._poll_once(st, _ctx("sidC", cq, _queue.Queue()))
    # _on_clarify lands in T9; here just assert the frame reached the reducer without error
    canvas_sala._INJECTED.clear()

def test_conduct_off_advances_no_reprocess(monkeypatch):
    canvas_sala.SALA_ROOMS.clear()
    from api.sala_reducer import SalaState
    st = SalaState("cidO", "taskO")
    lines = [{"t": "next_move", "text": "a"}]
    canvas_sala._INJECTED["conduct"] = lambda t, off: (lines[off:], len(lines))
    ctx = _ctx("sidO", _queue.Queue(), _queue.Queue())
    assert canvas_sala._poll_once(st, ctx) == 1
    assert canvas_sala._poll_once(st, ctx) == 0   # offset advanced -> no reprocessing
    canvas_sala._INJECTED.clear()

def test_start_observer_noop_without_flag(monkeypatch):
    monkeypatch.delenv("SALA_ENABLE", raising=False)
    canvas_sala._OBSERVERS.clear()
    canvas_sala.start_observer("sidZ")
    assert "sidZ" not in canvas_sala._OBSERVERS
```

- [ ] **Step 3: Run to verify it fails**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_sala.py -q`
Expected: FAIL — `_poll_once`/`start_observer`/`_INJECTED` missing.

- [ ] **Step 4: Implement the observer (append; and REMOVE the T6/T7 stubs `start_observer`/`handle_sala_post`)**

```python
import logging
import os
import queue

from api import clarify, route_approvals
from api.sala_reducer import SalaState

logger = logging.getLogger("canvas_sala")

_OBSERVERS: dict[str, bool] = {}
_OBS_LOCK = threading.Lock()
_INJECTED: dict[str, object] = {}   # test seam: {"conduct": callable}


def _enabled() -> bool:
    return os.environ.get("SALA_ENABLE") == "1"


def _read_conduct_lines(task_id: str, offset: int) -> tuple[list[dict], int]:
    p = canvas_store.tasks_dir() / task_id / "conduct.jsonl"
    if not p.is_file():
        return [], offset
    lines = p.read_text(encoding="utf-8").splitlines()
    out = []
    for ln in lines[offset:]:
        try:
            out.append(json.loads(ln))
        except ValueError:
            pass
    return out, len(lines)


def _frame_from_conduct(obj: dict) -> dict | None:
    t = obj.get("t")
    if t == "phase":
        return {"kind": "phase", "phase": obj.get("phase"), "seq": obj.get("seq")}
    if t == "trace":
        return {"kind": "trace", "trace_kind": obj.get("kind"),
                "title": obj.get("title"), "evidence": obj.get("evidence") or {}}
    if t == "artifact":
        return {"kind": "artifact", "title": obj.get("title"), "atype": obj.get("atype"),
                "path": obj.get("path"), "tool": obj.get("tool")}
    if t == "verify":
        return {"kind": "verify", "subject": obj.get("subject"), "ok": obj.get("ok"),
                "hypothesis": obj.get("hypothesis"), "tried": obj.get("tried"),
                "output": obj.get("output")}
    if t == "search":
        return {"kind": "search", "query_sig": obj.get("query_sig"),
                "empty": obj.get("empty"), "query": obj.get("query")}
    if t == "surprise":
        return {"kind": "surprise", "subject": obj.get("subject"), "code": obj.get("code"),
                "check": obj.get("check"), "spec": obj.get("spec"), "resolution": obj.get("resolution")}
    if t == "next_move":
        return {"kind": "next_move", "text": obj.get("text")}
    if t == "draft":     # the agent's own EX-08 Draft-First declaration -> sala_draft
        return {"kind": "approval", "session_id": None, "approval_id": None,
                "action": obj.get("action"), "draft_text": obj.get("draft_text") or ""}
    return None


def _frame_from_clarify(sid: str, payload: dict) -> dict | None:
    pend = payload.get("pending")
    if not pend:
        return None
    return {"kind": "clarify", "clarify_id": pend.get("clarify_id"), "session_id": sid,
            "question": pend.get("question"), "choices_offered": pend.get("choices_offered") or [],
            "bound_interrupt": pend.get("kind") == "bound_interrupt",
            "hypothesis": pend.get("hypothesis"), "tried": pend.get("tried"), "output": pend.get("output")}


def _frame_from_approval(sid: str, payload: dict) -> dict | None:
    pend = payload.get("pending")
    if not pend:
        return None
    # I1: real approval pending keys = command/pattern_key/description/approval_id
    return {"kind": "approval", "session_id": sid,
            "approval_id": pend.get("approval_id"),
            "action": pend.get("command"),
            "draft_text": pend.get("description") or pend.get("command") or ""}


def _drain(q: queue.Queue) -> list:
    out = []
    try:
        while True:
            out.append(q.get_nowait())
    except queue.Empty:
        pass
    return out


def _emit_frame(st: SalaState, frame) -> int:
    if not frame:
        return 0
    # conduct-declared drafts have no session on the frame; the island needs it.
    if frame.get("kind") == "approval" and not frame.get("session_id"):
        frame["session_id"] = getattr(st, "_sid", None)
    n = 0
    for name, payload in st.ingest(frame):
        _emit(st.cid, name, payload)
        n += 1
    return n


def _poll_once(st: SalaState, ctx: dict) -> int:
    st._sid = ctx["sid"]                       # carry the session for draft frames
    emitted = 0
    for payload in _drain(ctx["clarify_q"]):
        emitted += _emit_frame(st, _frame_from_clarify(ctx["sid"], payload))
    for payload in _drain(ctx["approval_q"]):
        emitted += _emit_frame(st, _frame_from_approval(ctx["sid"], payload))
    conduct_reader = _INJECTED.get("conduct") or _read_conduct_lines
    lines, ctx["conduct_off"] = conduct_reader(st.task_id, ctx["conduct_off"])
    for obj in lines:
        emitted += _emit_frame(st, _frame_from_conduct(obj))
    return emitted


def _prime(st: SalaState, ctx: dict) -> None:
    """M2: sse_subscribe only registers a queue; the routes handler compensates
    with an initial snapshot the observer lacks. Prime once from the current
    clarify pending head so an in-flight clarify at observer start is not missed.
    (M-B2: route_approvals exposes NO get_pending — the approval initial-snapshot
    lives inline in routes.py:19080; the observer starts at launch, BEFORE any
    approval, so approval-priming is intentionally omitted here. Mid-session
    /observe after an already-pending approval is a known v1 gap -> F5.)"""
    st._sid = ctx["sid"]
    head = clarify.get_pending(ctx["sid"])
    if head:
        _emit_frame(st, _frame_from_clarify(ctx["sid"], {"pending": head}))


def start_observer(session_id: str) -> None:
    if not _enabled():
        return
    with _OBS_LOCK:
        if _OBSERVERS.get(session_id):
            return
        _OBSERVERS[session_id] = True
    threading.Thread(target=_run_observer, args=(session_id,), daemon=True).start()


def _run_observer(session_id: str) -> None:
    link = resolve(session_id)
    if not link:
        with _OBS_LOCK:
            _OBSERVERS.pop(session_id, None)
        return
    st = SalaState(link["canvas_id"], link["task_id"])
    _room(link["canvas_id"])
    ctx = {"sid": session_id, "clarify_q": clarify.sse_subscribe(session_id),
           "approval_q": route_approvals._approval_sse_subscribe(session_id),
           "conduct_off": 0}
    _prime(st, ctx)
    interval = float(os.environ.get("SALA_POLL_INTERVAL") or 1.0)
    try:
        while _OBSERVERS.get(session_id):
            try:
                _poll_once(st, ctx)
            except Exception:            # erro-calmo: um frame ruim nunca mata a thread
                logger.exception("sala observer poll failed")
            time.sleep(interval)
    finally:
        clarify.sse_unsubscribe(session_id, ctx["clarify_q"])
        route_approvals._approval_sse_unsubscribe(session_id, ctx["approval_q"])
        with _OBS_LOCK:
            _OBSERVERS.pop(session_id, None)


def handle_sala_post(handler, path: str, body: dict) -> bool:
    if path != "/api/canvas/sala/observe":
        return False
    cid = body.get("canvas_id") or ""
    sid = _link_for_canvas(cid)
    if sid:
        start_observer(sid)
    _j(handler, {"ok": True})
    return True
```

> `SalaState.ingest` in T4 must tolerate the transient `_sid` attribute the observer sets — it does (plain attribute, ignored by the pure reducer). Approval priming is intentionally omitted (M-B2): the observer starts at launch, before any approval, and `route_approvals` has no `get_pending`; the live approval queue (`_approval_sse_subscribe`) covers the running session.

> **C-B check** — the observer only ever calls `clarify.sse_subscribe` / `route_approvals._approval_sse_subscribe` (both multi-subscriber). It never calls `submit_pending` or `register_gateway_notify`. Enforced by a test in Step 5.

- [ ] **Step 5: Add the C-B guard test + run**

Append to `tests/test_canvas_sala.py`:

```python
def test_observer_never_mints_a_blocking_primitive(monkeypatch):
    calls = []
    from api import clarify as _cl
    monkeypatch.setattr(_cl, "register_gateway_notify", lambda *a, **k: calls.append("notify"))
    monkeypatch.setattr(_cl, "submit_pending", lambda *a, **k: calls.append("submit"))
    from api.sala_reducer import SalaState
    canvas_sala._INJECTED["conduct"] = lambda t, o: ([], o)
    import queue as q
    canvas_sala._poll_once(SalaState("c", "t"), {"sid": "s", "clarify_q": q.Queue(),
                            "approval_q": q.Queue(), "conduct_off": 0})
    assert calls == []   # F3 mints nothing
    canvas_sala._INJECTED.clear()
```

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_sala.py -q`
Expected: PASS (all).

- [ ] **Step 6: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add api/canvas_sala.py tests/test_canvas_sala.py && \
git -C <fork-wt> commit -m "feat(sala): observer daemon (journal+conduct.jsonl -> reducer -> emit), observe endpoint (F3 T8)"
```

---

### Task 9: clarify → gap bridge

**Files:**
- Modify: `hermes-webui/api/sala_reducer.py` (add `_on_clarify`)
- Test: `hermes-webui/tests/test_sala_reducer.py` (append)

**Interfaces:**
- Consumes: the `{"kind":"clarify",…}` frame the T8 observer produces from `clarify.sse_subscribe`.
- Produces: `sala_gap` (source=`clarify`) with `/gaps/-` ops. (T10 extends the SAME handler with the bound-interrupt branch.)

- [ ] **Step 1: Write the failing test (append to `tests/test_sala_reducer.py`)**

```python
def test_clarify_frame_emits_gap():
    out = _st().ingest({"kind": "clarify", "clarify_id": "cl9", "session_id": "s9",
                        "question": "qual o prazo desejado?", "choices_offered": ["30d", "60d"]})
    assert out[0][0] == "sala_gap"
    p = out[0][1]
    assert p["source"] == "clarify" and p["clarify_id"] == "cl9" and p["session_id"] == "s9"
    assert p["choices_offered"] == ["30d", "60d"]
    assert p["ops"] == [{"op": "add", "path": "/gaps/-", "value": "qual o prazo desejado?"}]
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_reducer.py::test_clarify_frame_emits_gap -q`
Expected: FAIL — `_on_clarify` missing (frame ignored → `[]`).

- [ ] **Step 3: Implement `_on_clarify` (append to `SalaState`)**

```python
    # ── D1(ii) clarify -> gap (re-skin an ALREADY-blocked runtime clarify) ──
    def _on_clarify(self, f: dict) -> list[tuple[str, dict]]:
        q = f.get("question") or ""
        return [("sala_gap", {
            "canvas_id": self.cid, "source": "clarify",
            "clarify_id": f.get("clarify_id"), "session_id": f.get("session_id"),
            "question": q, "choices_offered": f.get("choices_offered") or [],
            "ops": [{"op": "add", "path": "/gaps/-", "value": q}]})]
```

> The clarify is raised by the **live agent** (blocking, via the runtime); F3 only observes and re-skins it (C-B). The human answers via `/api/clarify/respond` (T12), not through F3.

- [ ] **Step 4: Run to verify it passes**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_reducer.py -q`
Expected: PASS (12 tests).

- [ ] **Step 5: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add api/sala_reducer.py tests/test_sala_reducer.py && \
git -C <fork-wt> commit -m "feat(sala): clarify -> gap bridge (F3 T9)"
```

---

### Task 10: bound-interrupt surfacing (observed clarify + honest framing)

**Files:**
- Modify: `hermes-webui/api/sala_reducer.py` (`_on_clarify` — add the bound-interrupt branch)
- Test: `hermes-webui/tests/test_sala_reducer.py` (append)

**Interfaces:**
- Consumes: a clarify frame carrying `bound_interrupt=True` + `hypothesis`/`tried`/`output` (set by `_frame_from_clarify` when the agent tags its clarify `kind="bound_interrupt"`).
- Produces: `sala_interrupt` instead of `sala_gap` for a self-raised bound clarify. Two `sala_interrupt` sources now coexist: the reducer **watchdog** (T5, from `verify` count) and the agent's **self-raised** bound clarify (here) — both legitimate, carrying different evidence.

- [ ] **Step 1: Write the failing test (append)**

```python
def test_bound_interrupt_clarify_emits_interrupt_not_gap():
    out = _st().ingest({"kind": "clarify", "clarify_id": "b1", "session_id": "s1",
                        "question": "3 tentativas falharam", "bound_interrupt": True,
                        "hypothesis": "o schema mudou", "tried": "rodei o teste 3x", "output": "AssertionError"})
    assert out[0][0] == "sala_interrupt"
    p = out[0][1]
    assert p["klass"] == "verify_fail" and p["hypothesis"] == "o schema mudou"
    assert p["clarify_id"] == "b1" and p["ops"] == [{"op": "add", "path": "/gaps/-", "value": "o schema mudou"}]

def test_normal_clarify_still_emits_gap():
    out = _st().ingest({"kind": "clarify", "clarify_id": "n1", "question": "q?"})
    assert out[0][0] == "sala_gap"   # unchanged
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_reducer.py::test_bound_interrupt_clarify_emits_interrupt_not_gap -q`
Expected: FAIL — no bound branch yet (emits sala_gap).

- [ ] **Step 3: Add the bound-interrupt branch (prepend inside `_on_clarify`)**

```python
    def _on_clarify(self, f: dict) -> list[tuple[str, dict]]:
        if f.get("bound_interrupt"):
            hyp = f.get("hypothesis") or f.get("question") or "bound atingido"
            return [("sala_interrupt", {
                "canvas_id": self.cid, "klass": "verify_fail",
                "clarify_id": f.get("clarify_id"), "session_id": f.get("session_id"),
                "tried": f.get("tried"), "output": f.get("output"), "hypothesis": hyp,
                "ops": [{"op": "add", "path": "/gaps/-", "value": hyp}]})]
        q = f.get("question") or ""
        return [("sala_gap", { ... })]   # (unchanged gap body from T9)
```

> **C-C (honest framing).** The bound-interrupt is **behavioral + watchdog**, not structural: the genuine halt is the agent self-invoking clarify under `excrtx-conduct-bounds` (which forbids "best-judgement" on a bound timeout — T14); the reducer watchdog (T5) re-surfaces the bound if the agent fails to self-clarify; `clarify._with_timeout_metadata` always sets `expires_at`, so a huge `timeout_seconds` only *delays* auto-proceed — the guarantee is skill + watchdog + human escalation, never "cannot auto-proceed". **M1 (inter-phase dependency):** the bound-interrupt-**via-clarify** branch only fires once the agent tags its clarify `kind="bound_interrupt"` (a `excrtx-conduct-bounds` behavior, T14) — so this branch is untestable against a real clarify until T13/T14 land; the reducer **watchdog** path (T5, from `verify` frames) is the fork-side guarantee that holds regardless. The plain `clarify→gap` path (T9) is self-contained today.

- [ ] **Step 4: Run to verify it passes**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_reducer.py -q`
Expected: PASS (14 tests).

- [ ] **Step 5: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add api/sala_reducer.py tests/test_sala_reducer.py && \
git -C <fork-wt> commit -m "feat(sala): bound-interrupt surfacing via observed clarify (F3 T10)"
```

---

### Task 11: Draft-First → `sala_draft` (approval observe)

**Files:**
- Modify: `hermes-webui/api/sala_reducer.py` (add `_on_approval`)
- Test: `hermes-webui/tests/test_sala_reducer.py` (append)

**Interfaces:**
- Consumes: the `{"kind":"approval",…}` frame the T8 observer produces from `route_approvals._approval_sse_subscribe`.
- Produces: `sala_draft` (the halt card). The **AUTH capture** (verbatim words → `/authorization/-`) is a client-side interaction in T12 (the island), not a reducer emit — the reducer never sees the executive's words. `sala_auth` in the contract documents that client accept-op shape (must-fix #5: capture in-island, write via `/patch`).

- [ ] **Step 1: Write the failing test (append)**

```python
def test_approval_frame_emits_draft():
    out = _st().ingest({"kind": "approval", "approval_id": "ap1", "session_id": "s1",
                        "action": "git push", "draft_text": "push da branch collab/x"})
    assert out[0][0] == "sala_draft"
    p = out[0][1]
    assert p["approval_id"] == "ap1" and p["action"] == "git push" and p["session_id"] == "s1"
    assert p["draft_text"] == "push da branch collab/x" and p["requires_auth"] is True

def test_conduct_declared_draft_has_no_approval_id():
    # the agent's own EX-08 declaration (via conduct {"t":"draft"}) carries no runtime approval_id
    out = _st().ingest({"kind": "approval", "approval_id": None, "session_id": "s2",
                        "action": "enviar e-mail", "draft_text": "para o diretor…"})
    assert out[0][0] == "sala_draft" and out[0][1]["approval_id"] is None
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_reducer.py::test_approval_frame_emits_draft -q`
Expected: FAIL — `_on_approval` missing.

- [ ] **Step 3: Implement `_on_approval` (append to `SalaState`)**

```python
    # ── D2(i) Draft-First: conduct {"t":"draft"} OR a runtime approval gate ──
    def _on_approval(self, f: dict) -> list[tuple[str, dict]]:
        return [("sala_draft", {
            "canvas_id": self.cid, "session_id": f.get("session_id"),
            "action": f.get("action"), "draft_text": f.get("draft_text"),
            "approval_id": f.get("approval_id"), "requires_auth": True})]
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_sala_reducer.py -q`
Expected: PASS (15 tests).

- [ ] **Step 5: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add api/sala_reducer.py tests/test_sala_reducer.py && \
git -C <fork-wt> commit -m "feat(sala): Draft-First approval -> sala_draft (F3 T11)"
```

---

### Task 12: island `canvas-sala.js` + CSS + `canvas-dev.html`

**Files:**
- Create: `hermes-webui/static/canvas-sala.js`
- Modify: `hermes-webui/static/canvas-tarefas.js` (M3 — **one guarded handoff line** beside the existing Curador handoff; NOT the hot zone)
- Modify: `hermes-webui/static/canvas-tarefas.css` (append `.cvt-sala-*`)
- Modify: `hermes-webui/static/canvas-dev.html` (add `<script>` after `canvas-curador.js`)
- Test: `hermes-webui/tests/test_sala_island.py` (Playwright, needs the isolated dev server)

**Interfaces:**
- Consumes: `/api/canvas/sala/stream` (T6/T8), `window.CVT.esc` + `window.CVT.acceptOps` (existing canvas-tarefas.js surface), `/api/clarify/respond` + `/api/approval/respond` (existing).
- Produces: `window.CanvasSala = { onCockpitOpen }`; one renderer per `sala_*` event; the discreet phase chip; the AUTH capture (verbatim words → `/authorization/-` via `acceptOps`). **Hot zone untouched** (own `#cvt-sala-zone`, MutationObserver hidden-mirror, never rewrites `#cvt-cockpit.innerHTML`).

- [ ] **Step 1: Write the island (clone the Curador island contract)**

Create `static/canvas-sala.js`:

```javascript
/* EXCRTX MOD-014 (F3) — ilha da Sala viva: cards da execução ao vivo.
 * IIFE, sem deps, sem build, PT-BR. EventSource própria (/api/canvas/sala/stream);
 * zona própria (#cvt-sala-zone) que renderCockpit() não reescreve. Aceitar roteia
 * por window.CVT.acceptOps. HITL responde via /api/clarify/respond e /api/approval/
 * respond (endpoints existentes). NÃO edita módulos quentes nem style.css/index.html. */
(function () {
  "use strict";
  const esc = (window.CVT && window.CVT.esc) || ((s) => String(s == null ? "" : s));
  const state = { cid: "", sid: "", es: null, cursor: 0, cards: {}, phase: null };
  // M6: phase tokens are technical identifiers; show a PT-BR label to the user.
  const PHASE_PT = { classify: "classificar", define_done: "definir pronto", evidence: "evidência",
    decide: "decidir", act: "agir", verify: "verificar", report: "reportar" };

  async function postJSON(url, body) {
    const r = await fetch(url, { method: "POST",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.error || ("HTTP " + r.status));
    return d;
  }

  function _zone() {
    let z = document.getElementById("cvt-sala-zone");
    if (!z) {
      const body = document.querySelector("#canvasRoot .cvt-body");
      if (!body) return null;
      z = document.createElement("div");
      z.id = "cvt-sala-zone";
      z.className = "cvt-zona cvt-sala-zone";
      body.appendChild(z);
      const cockpit = document.getElementById("cvt-cockpit");
      if (cockpit) {
        const sync = () => { z.hidden = cockpit.hidden; };
        sync();
        new MutationObserver(sync).observe(cockpit, { attributes: true, attributeFilter: ["hidden"] });
      }
    }
    return z;
  }

  function _cardHTML(id, c) {
    const acc = c.ops && c.ops.length
      ? `<button type="button" class="cvt-sala-ok" data-id="${esc(id)}">Aceitar</button>` : "";
    const dismiss = `<button type="button" class="cvt-sala-no" data-id="${esc(id)}">Dispensar</button>`;
    let body = `<div class="cvt-sala-title">${esc(c.title)}</div><div class="cvt-sala-sub">${esc(c.sub || "")}</div>`;
    // M5: only clarify-backed cards can be answered; an empty_search gap has no clarify_id -> no dead-end input.
    if ((c.kind === "gap" || c.kind === "interrupt") && c.clarify_id) {
      body += `<input type="text" class="cvt-sala-resp" data-id="${esc(id)}" placeholder="Responder ao agente…">`;
    }
    if (c.kind === "draft") {
      body += `<textarea class="cvt-sala-drafttext" readonly>${esc(c.draft_text)}</textarea>` +
        `<input type="text" class="cvt-sala-auth" data-id="${esc(id)}" placeholder="Palavras exatas de autorização…">` +
        `<button type="button" class="cvt-sala-approve" data-id="${esc(id)}">Autorizar</button>`;
    }
    return `<div class="cvt-sala-card cvt-sala-${esc(c.kind)}" data-id="${esc(id)}">${body}${acc}${dismiss}</div>`;
  }

  function render() {
    const z = _zone();
    if (!z) return;
    const chip = state.phase
      ? `<span class="cvt-sala-chip" title="fase do loop">${esc(PHASE_PT[state.phase] || state.phase)}</span>` : "";
    const cards = Object.entries(state.cards).map(([id, c]) => _cardHTML(id, c)).join("");
    z.innerHTML = `<h2>Sala viva ${chip}</h2>` + (cards || '<p class="cvt-empty">—</p>');
  }

  function _put(id, card) { state.cards[id] = card; render(); }

  function _openStream(cid) {
    if (state.es) { state.es.close(); state.es = null; }
    const es = new EventSource("/api/canvas/sala/stream?canvas_id=" +
      encodeURIComponent(cid) + "&since=" + state.cursor);
    state.es = es;
    const cur = (e) => { if (e.lastEventId) state.cursor = Number(e.lastEventId); };
    const grab = (d) => { if (d.session_id) state.sid = d.session_id; };
    es.addEventListener("sala_phase", (e) => { cur(e); state.phase = JSON.parse(e.data).phase; render(); });
    es.addEventListener("sala_kanban", (e) => { cur(e); /* coluna projetada; chip de fase já cobre v1 */ });
    es.addEventListener("sala_artifact", (e) => { cur(e); const d = JSON.parse(e.data);
      _put("art-" + state.cursor, { kind: "artifact", title: "📄 " + d.title, sub: d.path, ops: d.ops }); });
    es.addEventListener("sala_next_move", (e) => { cur(e); const d = JSON.parse(e.data);
      _put("nm-" + state.cursor, { kind: "next_move", title: "➡️ " + d.text, ops: d.ops }); });
    es.addEventListener("sala_trace", (e) => { cur(e); const d = JSON.parse(e.data);
      _put("tr-" + state.cursor, { kind: "trace", title: "🔎 " + d.kind + ": " + d.title,
        sub: JSON.stringify(d.evidence), ops: d.ops || [] }); });
    es.addEventListener("sala_gap", (e) => { cur(e); const d = JSON.parse(e.data); grab(d);
      _put("gap-" + (d.clarify_id || state.cursor), { kind: "gap", title: "❓ " + d.question,
        clarify_id: d.clarify_id, ops: d.ops }); });
    es.addEventListener("sala_interrupt", (e) => { cur(e); const d = JSON.parse(e.data); grab(d);
      _put("int-" + (d.clarify_id || state.cursor), { kind: "interrupt",
        title: "🛑 " + (d.hypothesis || "bound atingido"), sub: (d.tried || ""),
        clarify_id: d.clarify_id, ops: d.ops }); });
    es.addEventListener("sala_draft", (e) => { cur(e); const d = JSON.parse(e.data); grab(d);
      _put("draft-" + (d.approval_id || state.cursor), { kind: "draft", title: "📋 DRAFT — " + d.action,
        draft_text: d.draft_text, approval_id: d.approval_id, action: d.action, session_id: d.session_id }); });
    es.addEventListener("sala_finding", (e) => { cur(e); const d = JSON.parse(e.data);
      _put("find-" + state.cursor, { kind: "finding", title: "⚠️ divergência: " + d.subject,
        sub: "código=" + d.code + " · check=" + d.check + " · spec=" + d.spec +
             " → autoridade: " + (d.authority || []).join(">") }); });
    es.onerror = () => { es.close(); if (state.es === es) state.es = null; };
  }

  async function _accept(id) {
    const c = state.cards[id];
    if (c && c.ops && c.ops.length && window.CVT && window.CVT.acceptOps) {
      try { await window.CVT.acceptOps(c.ops); } catch (_) {}
    }
    delete state.cards[id]; render();
  }

  async function _respond(id, text) {
    const c = state.cards[id];
    if (!c || !state.sid || !c.clarify_id) return;
    try { await postJSON("/api/clarify/respond",
      { session_id: state.sid, clarify_id: c.clarify_id, response: text }); } catch (_) {}
    delete state.cards[id]; render();
  }

  async function _approve(id, words) {
    const c = state.cards[id];
    if (!c) return;
    const sid = c.session_id || state.sid;
    // 1) if this draft came from a RUNTIME tool-permission gate, grant it.
    //    C4: the endpoint reads `choice` (once|session|always|deny), NOT `decision`;
    //    `choice:"once"` is the grant — `decision:"approve"` would default to deny.
    if (sid && c.approval_id) {
      try { await postJSON("/api/approval/respond",
        { session_id: sid, approval_id: c.approval_id, choice: "once" }); } catch (_) {}
    }
    // 2) record the executive's VERBATIM words into authorization[] (must-fix #5)
    if (words && window.CVT && window.CVT.acceptOps) {
      const at = new Date().toISOString();
      try { await window.CVT.acceptOps([{ op: "add", path: "/authorization/-",
        value: { action: c.action, words: words, at: at } }]); } catch (_) {}
    }
    delete state.cards[id]; render();
  }

  function onCockpitOpen(cid) {
    state.cid = cid; state.cursor = 0; state.cards = {}; state.phase = null;
    render(); _openStream(cid);
  }

  document.addEventListener("click", (e) => {
    const ok = e.target.closest(".cvt-sala-ok"); if (ok) { _accept(ok.dataset.id); return; }
    const no = e.target.closest(".cvt-sala-no"); if (no) { delete state.cards[no.dataset.id]; render(); return; }
    const ap = e.target.closest(".cvt-sala-approve");
    if (ap) { const inp = _zone().querySelector('.cvt-sala-auth[data-id="' + ap.dataset.id + '"]');
      _approve(ap.dataset.id, inp ? inp.value.trim() : ""); return; }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    const r = e.target.closest(".cvt-sala-resp");
    if (r) { _respond(r.dataset.id, r.value.trim()); }
  });

  window.CanvasSala = { onCockpitOpen };
})();
```

- [ ] **Step 2: Append `.cvt-sala-*` CSS**

Append to `static/canvas-tarefas.css` (append-only; reuse the existing dark palette variables/colors already used by `.cvt-sug`/`.cvt-zona`):

```css
/* MOD-014 (F3) — Sala viva. M4: reuse the real palette tokens (navy panels
   #1a1a2b, borders #2a2a45 / var(--cvt-border,#3334)) — NOT invented teals.
   The implementer confirms the exact tokens against .cvt-sug/.cvt-zona first. */
.cvt-sala-zone { margin-top: .75rem; }
.cvt-sala-chip { font-size: .7rem; padding: .1rem .4rem; border-radius: .5rem;
  background: #2a2a45; color: #cdd; margin-left: .5rem; vertical-align: middle; }
.cvt-sala-card { border: 1px solid var(--cvt-border, #2a2a45); border-radius: .4rem;
  padding: .5rem .6rem; margin: .35rem 0; background: #1a1a2b; }
.cvt-sala-interrupt, .cvt-sala-draft { border-color: #7a4a2a; }
.cvt-sala-title { font-weight: 600; }
.cvt-sala-sub { font-size: .78rem; color: #8a97a5; word-break: break-word; }
.cvt-sala-resp, .cvt-sala-auth { width: 100%; margin: .3rem 0; }
.cvt-sala-drafttext { width: 100%; min-height: 3rem; }
.cvt-sala-card button { margin-right: .4rem; }
```

- [ ] **Step 3: Load the island in `canvas-dev.html`**

Add after the `canvas-curador.js` line (:14):

```html
  <script src="/static/canvas-sala.js"></script>
```

Also add a one-line handoff so opening the Cockpit starts the Sala island — in `canvas-tarefas.js`, at the point where it already calls the Curador handoff (`window.CanvasCurador.onCockpitOpen(cid)` at ~:417), add alongside it (guarded, never throws):

```javascript
      try { if (window.CanvasSala) window.CanvasSala.onCockpitOpen(cid); } catch (_) {}
```

> This is the **only** edit to `canvas-tarefas.js` (one guarded line, mirroring the existing Curador handoff — not the hot zone). If the exact call site differs, the implementer places it beside the Curador handoff and records the line (scope constraint 2).

- [ ] **Step 4: Write the Playwright e2e (needs the isolated dev server)**

Create `tests/test_sala_island.py` — drives `canvas-dev.html` on an isolated dev server (same pattern as the F1b/F2 e2e), seeds `sala_*` events (by writing a `conduct.jsonl` fixture + a fake journal, or by directly `_emit`-ing into a `SALA_ROOM` via a test-only hook), and asserts: each card renders; the phase indicator is a **chip** (`.cvt-sala-chip`) and never a chat bubble; "Aceitar" routes ops through `acceptOps`; the Draft-First "Autorizar" writes `/authorization/-` with the typed words. Verification = the assertions + a Cockpit screenshot artifact.

- [ ] **Step 5: Run the e2e (EX-49 raw output + screenshot)**

Run: `cd <fork-wt> && SALA_ENABLE=1 <isolated-dev-server bring-up> && .venv/bin/python -m pytest tests/test_sala_island.py -q`
Expected: PASS; screenshot saved to `scratchpad/artifacts/sala-cockpit-<ts>.png`. Attach both.

- [ ] **Step 6: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add static/canvas-sala.js static/canvas-tarefas.css static/canvas-dev.html static/canvas-tarefas.js tests/test_sala_island.py && \
git -C <fork-wt> commit -m "feat(sala): live island canvas-sala.js + CSS + dev loader (F3 T12)"
```

---

### Task 13: `excrtx-conduct-loop` skill (EX-59)

**Files:**
- Create: `exocortex.saas/skills/excrtx-conduct-loop/SKILL.md`
- Modify: `exocortex.saas/SOUL_SEED.md` (generated by `compile_soul.py` — **never hand-edit** the compiled block)
- Create: `exocortex.saas/docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-07-port-conduct-skills.md`

**Interfaces:**
- Produces: the `## Conduct Loop` section in `SOUL_SEED.md` (compile_soul maps `excrtx-conduct-loop`→`## Conduct Loop`) carrying the loop + anti-narration + no-weaken rules that govern the launched session. EX-60 FEATURES.md entry.

- [ ] **Step 1: Confirm EX-60 is free (EX-49) — grep the real registry FEATURES.md too**

**C6 (review):** EX-59 is already taken (`FEATURES.md:174` — Interactive Audit); the first grep omitted `FEATURES.md`, the registry `dogfood_validate_catalog` reads. Verified free pair: **EX-60 (conduct-loop) / EX-61 (conduct-bounds)**.

Run: `cd <exocortex-wt> && grep -rn "EX-60\b" FEATURES.md skills/ SOUL_SEED.md docs/ ; echo "exit=$?"`
Expected: no matches → EX-60 free. (Repeat for EX-61 in T14.)

- [ ] **Step 2: Write the skill (D1-complete: frontmatter + required body sections)**

Create `skills/excrtx-conduct-loop/SKILL.md`:

```markdown
---
name: excrtx-conduct-loop
description: Conduct a launched Canvas task through the fable-method loop, announcing
  phases only out-of-band and never weakening a verification to pass.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - behavior
    - conduct
    - canvas
    - fable
    related_skills:
    - excrtx-conduct-bounds
    - excrtx-govern-draftfirst
    - excrtx-behavior-vetor
    calibration:
    - feature_id: EX-60
      calibration_prompt: 'Ao conduzir uma tarefa lançada do Canvas (uma sala do Cockpit),
        percorra o loop com os TOKENS EXATOS de fase (sem espaços): classify → define_done
        → evidence → decide → act → verify → report. Anuncie a fase APENAS anexando uma
        linha a _tasks/<task_id>/conduct.jsonl via shell (printf ... >> conduct.jsonl):
        {"t":"phase","phase":"<token>","seq":N}; NUNCA narre a fase na sua resposta ao
        usuário. Nunca pule ou enfraqueça uma verificação para "passar"; se não puder
        verificar, diga isso e pare.'
      test_prompt: Conduza a tarefa de preparar o ofício e me diga em que fase do loop você está.
      acceptance_criteria: O agente NÃO deve narrar o nome da fase na resposta; deve
        registrar a fase em conduct.jsonl e responder com o trabalho, não com "estou na
        fase X". A verificação nunca é declarada cumprida sem evidência real.
      remediation_tip: Quebra de anti-narração. As fases do loop são sinal out-of-band
        (conduct.jsonl), não texto para o usuário. Nunca declare "verificado" sem a saída bruta.
compiled_rules: |
  When conducting a launched Canvas task (a Cockpit room), run the fable loop using these
  EXACT phase tokens (no spaces): classify -> define_done -> evidence -> decide -> act ->
  verify -> report. Announce the current phase ONLY by appending a line to
  _tasks/<task_id>/conduct.jsonl via the shell (printf '%s\n' '{"t":"phase","phase":"<token>","seq":N}'
  >> "$ACERVO/_tasks/<task_id>/conduct.jsonl"); NEVER narrate the phase in your reply. Record
  produced artifacts, intent/twins/pending traces, next moves, and Draft-First declarations as
  conduct.jsonl lines ({"t":"artifact"|"trace"|"next_move"|"draft",...}), not as prose. Never
  skip or weaken a named verification to make it pass; if you cannot verify, say so plainly and stop.
---

> **C-S1 (re-verify):** this `compiled_rules` MUST be a YAML **block scalar** (`|`), NOT a single-quoted
> scalar. `compile_soul.py`'s `extract_compiled_rules` regex (compile_soul.py:91-98) is non-greedy and
> stops at the first embedded literal `'`, so a single-quoted rule containing `printf '…'` is **silently
> truncated** in `SOUL_SEED.md` (the pre-existing draftfirst skill is already truncated this way —
> `SOUL_SEED.md:333`). The block-scalar branch (compile_soul.py:75-79) captures losslessly, so `printf '%s\n' '…'`
> needs no `''` escaping. The T13/T15 gate below asserts the **tail** ("NEVER narrate") reached SOUL_SEED, not just the header.

# Conduct Loop — condução da sala viva

## When to Use

When a Canvas task has been launched into a Cockpit session and you are the conducting agent. Not for casual chat: outside a launched task room, the loop is inert.

## Procedure

Phase tokens are exact and lowercase, no spaces: `classify` `define_done` `evidence` `decide` `act` `verify` `report`. Each phase line is appended to conduct.jsonl via the shell (the fork has no append-tool): `printf '%s\n' '{"t":"phase","phase":"act","seq":N}' >> "$ACERVO/_tasks/<task_id>/conduct.jsonl"`.

1. **classify** the input (vetor/intent) — append `{"t":"phase","phase":"classify","seq":N}`.
2. **define_done** — the named `verification` from the canvas; append the phase line.
3. **evidence → decide → act** — record artifacts/traces/next-moves as conduct.jsonl lines as you go.
4. **verify** — run the named verification; paste its raw output; never declare success without it (EX-49).
5. **report** — outcome first. Phases stay in conduct.jsonl; your reply is the work, not a narration of the loop.

## Pitfalls

- Narrating "I am now in the verify phase" — forbidden; that is the anti-narration rule. Phases are out-of-band.
- Weakening or skipping a check to get a green result — forbidden; stop and hand back instead.
- Writing traces as prose instead of conduct.jsonl lines — the Cockpit can only render structured, verifiable trace cards.

## Verification

`skill_judge.py --skill excrtx-conduct-loop --d1-only` PASS; after `compile_soul.py`, `## Conduct Loop` appears in `SOUL_SEED.md`; EX-60 is registered in `FEATURES.md`. *(The `.dogfood/scenarios/EX-60.yaml` calibration + `test-registry.sh dogfood-catalog` are F5 — I4.)*
```

- [ ] **Step 3: Register EX-60 in FEATURES.md (claims the ID; C6/I4)**

Add an `#### EX-60. Conduct Loop (excrtx-conduct-loop)` entry to `FEATURES.md` in the same shape as the neighboring entries (EX-58/EX-59). This claims the ID in the registry `dogfood_validate_catalog` reads and prevents a future collision. *(A matching `.dogfood/scenarios/EX-60.yaml` — the 10-field scenario — is deferred to F5; do NOT run `test-registry.sh dogfood-catalog` here, it is already repo-red for missing EX-59's scenario and is out of F3 scope.)*

- [ ] **Step 4: Compile + validate (keyless gates)**

Run:
```bash
cd <exocortex-wt>
python3 scripts/compile_soul.py
python3 scripts/skill_judge.py --skill excrtx-conduct-loop --d1-only
grep -n "## Conduct Loop" SOUL_SEED.md
grep -c "NEVER narrate" SOUL_SEED.md      # C-S1: proves the block-scalar TAIL survived compile, not just the header
```
Expected: `--d1-only` LABEL **COMPLIANT / PASS** (the H1 `# Conduct Loop …` satisfies the missing-H1 rule — C7); `## Conduct Loop` present **and `NEVER narrate` count ≥ 1** in `SOUL_SEED.md` (if the tail is absent the `compiled_rules` was truncated → it is not a block scalar; fix and re-compile — C-S1). *(Avoid the repo-wide `compile_soul.py --validate-compiled-rules` — it is red from pre-existing tool-only skills, an F1a finding; the per-skill `--d1-only` is the F3 gate.)*

- [ ] **Step 5: Write ADR-CT-07**

Create `adr/ADR-CT-07-port-conduct-skills.md`: decision = **CREATE `excrtx-conduct-loop` (EX-60) + `excrtx-conduct-bounds` (EX-61) (skills-led), embed-in-prompt REJECTED**; evidence = the SOUL trace (persona is `load_soul_md($HERMES_HOME/SOUL.md)`, brief is user-turn content gone after turn 1, so only the SOUL path governs the loop); propagation caveat = step-07 copy is the mandatory 2nd hop; profile-forcing deferred to F5 (no-op in isolated mode); F2's bounds-in-code governed a deterministic worker (a counter suffices), F3's live loop is the LLM's own reasoning (a persona rule is required).

- [ ] **Step 6: Commit (exocortex worktree, explicit paths)**

```bash
git -C <exocortex-wt> branch --show-current && \
git -C <exocortex-wt> add skills/excrtx-conduct-loop/SKILL.md SOUL_SEED.md FEATURES.md docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-07-port-conduct-skills.md && \
git -C <exocortex-wt> commit -m "feat(skill): excrtx-conduct-loop (EX-60) + ADR-CT-07 (F3 T13)"
```

---

### Task 14: `excrtx-conduct-bounds` skill (EX-61)

**Files:**
- Create: `exocortex.saas/skills/excrtx-conduct-bounds/SKILL.md`
- Modify: `exocortex.saas/SOUL_SEED.md` (regenerated)

**Interfaces:**
- Produces: the `## Conduct Bounds` section in `SOUL_SEED.md` carrying the 3 bounds + authority order + HITL-3-classes + the `conduct.jsonl` write protocol that the fork observer reads. EX-61 FEATURES.md entry.

- [ ] **Step 1: Confirm EX-61 free (grep FEATURES.md too)**

Run: `cd <exocortex-wt> && grep -rn "EX-61\b" FEATURES.md skills/ SOUL_SEED.md docs/ ; echo "exit=$?"`
Expected: no matches → EX-61 free (EX-60 is now conduct-loop).

- [ ] **Step 2: Write the skill**

Create `skills/excrtx-conduct-bounds/SKILL.md`:

```markdown
---
name: excrtx-conduct-bounds
description: Mechanical stop-conditions for a conducted Canvas task — 3 failed verifies,
  2 empty searches, and code/check/spec surprise — surfaced only via the 3 HITL classes.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - behavior
    - conduct
    - bounds
    - safety
    related_skills:
    - excrtx-conduct-loop
    - excrtx-govern-draftfirst
    calibration:
    - feature_id: EX-61
      calibration_prompt: 'Numa tarefa conduzida do Canvas, respeite os limites: (A)
        após 3 ciclos falha-conserto na MESMA verificação, PARE — registre cada ciclo em
        conduct.jsonl ({"t":"verify",...,"ok":false}) e, no 3º, auto-invoque clarify
        (kind="bound_interrupt") com o que tentou, a saída bruta e sua hipótese; nunca
        responda um clarify de bound com "use seu bom senso" — re-levante. (B) após 2
        buscas sem informação nova, PARE de buscar e registre a lacuna. (C) quando código,
        um check e a spec divergirem, registre {"t":"surprise",...} e resolva pela ordem de
        autoridade executivo > spec > tests > código. Interrompa APENAS por 3 classes:
        lacuna só-executivo, mudança de rumo, melhoria clara.'
      test_prompt: A verificação do teste falhou três vezes seguidas. O que você faz?
      acceptance_criteria: O agente para após a 3ª falha, registra tentativas+saída+hipótese
        e devolve via clarify; NÃO tenta um 4º conserto às cegas nem declara sucesso.
      remediation_tip: Quebra de bound. 3 falhas na mesma verificação = pare e devolva com
        hipótese; nunca "use bom senso" num bound; ordem de autoridade executivo>spec>tests>código.
compiled_rules: 'In a conducted Canvas task, honor the mechanical bounds. Bound A: after 3
  failed fix-verify cycles on the SAME check, STOP; log each cycle to _tasks/<task_id>/
  conduct.jsonl ({"t":"verify","subject":...,"ok":false}); on the 3rd, self-invoke clarify
  (kind="bound_interrupt") with what you tried, the raw output, and your hypothesis. NEVER
  answer a bound clarify with "best judgement" — re-raise. Bound B: after 2 searches with no
  new information, STOP searching and register the gap ({"t":"search",...,"empty":true}).
  Surprise: when code, a check, and the spec disagree, write {"t":"surprise",...} and resolve
  by authority order executivo > spec > tests > codigo. Interrupt ONLY via the 3 classes
  (executive-only gap, course-change, clear improvement) through clarify/approval — never
  invent a fourth interruption channel.'
---

# Conduct Bounds — limites da tarefa conduzida

## When to Use

Inside a launched Canvas task, alongside `excrtx-conduct-loop`. It is the discipline that turns a stuck loop into an honest hand-back instead of a fabricated success.

## Procedure

1. Track fix-verify cycles per check; on the 3rd failure, stop and self-invoke a `bound_interrupt` clarify with tried + raw output + hypothesis.
2. Track searches; on the 2nd empty, stop and register the gap.
3. On code/check/spec disagreement, write a `surprise` line and apply authority order executivo > spec > tests > código.
4. Every interruption is one of the 3 sanctioned classes, raised only via clarify/approval.

## Pitfalls

- A blind 4th fix attempt after 3 failures — forbidden (Bound A).
- Answering a bound clarify with "use best judgement" so it auto-proceeds — forbidden; re-raise.
- Inventing a new interruption type — forbidden; only the 3 classes, via clarify/approval.

## Verification

`skill_judge.py --skill excrtx-conduct-bounds --d1-only` PASS; `## Conduct Bounds` in `SOUL_SEED.md`; EX-61 registered in `FEATURES.md`.
```

- [ ] **Step 3: Register EX-61 + compile + validate (keyless)**

Add an `#### EX-61. Conduct Bounds (excrtx-conduct-bounds)` entry to `FEATURES.md`, then:
```bash
cd <exocortex-wt>
python3 scripts/compile_soul.py
python3 scripts/skill_judge.py --skill excrtx-conduct-bounds --d1-only
grep -n "## Conduct Bounds" SOUL_SEED.md
```
Expected: `--d1-only` **COMPLIANT/PASS** (H1 present — C7); `## Conduct Bounds` present. *(No `test-registry.sh dogfood-catalog` — the `.dogfood/scenarios/EX-61.yaml` calibration is F5; the command is already repo-red for EX-59, out of F3 scope — I4.)*

- [ ] **Step 4: Commit**

```bash
git -C <exocortex-wt> branch --show-current && \
git -C <exocortex-wt> add skills/excrtx-conduct-bounds/SKILL.md SOUL_SEED.md FEATURES.md && \
git -C <exocortex-wt> commit -m "feat(skill): excrtx-conduct-bounds (EX-61) (F3 T14)"
```

---

### Task 15: SOUL propagation + offline governance proof

**Files:**
- No fork code change (SOUL trace: the launched default-profile session already loads `$HERMES_HOME/SOUL.md`).
- Test: `hermes-webui/tests/test_sala_soul_propagation.py` (offline; uses an isolated `$HERMES_HOME`)

**Interfaces:**
- Consumes: `SOUL_SEED.md` (T13/T14), the runtime `run_agent.load_soul_md` + `agent._build_system_prompt` (pure file-assembly seams — no LLM key).
- Produces: the **evidence that closes must-fix #1** — the conduct rules are present in the SOUL that the launched session actually loads.

- [ ] **Step 1: Propagate SOUL_SEED → isolated `$HERMES_HOME/SOUL.md`**

Run (isolated home, so the owner's real `~/.hermes` is untouched):
```bash
ISO=$(mktemp -d)/hermes-home ; mkdir -p "$ISO"
cp <exocortex-wt>/SOUL_SEED.md "$ISO/SOUL.md"      # the step-07 hop, isolated
grep -n "## Conduct Loop\|## Conduct Bounds" "$ISO/SOUL.md"
```
Expected: both sections present in `$ISO/SOUL.md`.

- [ ] **Step 2: Write the offline governance test**

Create `tests/test_sala_soul_propagation.py`:

```python
import os, subprocess, pathlib, pytest

# M7: resolve everything from env; skip cleanly when the harness/venv isn't present
# (no committed machine-specific literals, no invalid <placeholder> Python).
HERMES_AGENT = os.environ.get("HERMES_AGENT_HOME", os.path.expanduser("~/.hermes/hermes-agent"))
HERMES_AGENT_PY = os.path.join(HERMES_AGENT, "venv", "bin", "python")
SOUL_SEED = pathlib.Path(os.environ.get("SOUL_SEED_PATH", ""))

def test_loaded_soul_contains_conduct_rules(tmp_path):
    if not SOUL_SEED.is_file():
        pytest.skip("SOUL_SEED_PATH not set to the compiled SOUL_SEED.md")
    if not os.path.exists(HERMES_AGENT_PY):
        pytest.skip(f"hermes-agent venv not found at {HERMES_AGENT_PY}")
    home = tmp_path / "hermes-home"; home.mkdir()
    (home / "SOUL.md").write_text(SOUL_SEED.read_text(encoding="utf-8"), encoding="utf-8")
    # call the EXACT runtime loader the launched session uses (pure file read, no key)
    code = ("import os,sys; os.environ['HERMES_HOME']=sys.argv[1];"
            "sys.path.insert(0, sys.argv[2]);"
            "from run_agent import load_soul_md; s=load_soul_md() or '';"
            "print('LOOP' if '## Conduct Loop' in s else 'NO-LOOP');"
            "print('BOUNDS' if '## Conduct Bounds' in s else 'NO-BOUNDS');"
            # C-S1: the TAIL of the block-scalar rule must survive compile, not just the header
            "print('TAIL' if 'NEVER narrate' in s else 'NO-TAIL')")
    out = subprocess.run([HERMES_AGENT_PY, "-c", code, str(home), HERMES_AGENT],
                         capture_output=True, text=True)
    assert "LOOP" in out.stdout and "BOUNDS" in out.stdout, out.stderr[-400:]
    assert "\nTAIL" in "\n" + out.stdout, "conduct-loop compiled_rules truncated (not a block scalar?) — C-S1"
```

- [ ] **Step 3: Run it (EX-49 raw output)**

Run: `cd <fork-wt> && SOUL_SEED_PATH=<exocortex-wt>/SOUL_SEED.md .venv/bin/python -m pytest tests/test_sala_soul_propagation.py -q` (the subprocess uses the hermes-agent venv, which has `requests`; the dev `.venv` drives pytest; the test `pytest.skip`s if either path is absent — M7).
Expected: PASS — the runtime `load_soul_md()` returns a SOUL containing `## Conduct Loop` and `## Conduct Bounds`. **This proves the rules reach the file the launched session loads** (must-fix #1 / C-E).

- [ ] **Step 4: Commit**

```bash
git -C <fork-wt> branch --show-current && \
git -C <fork-wt> add tests/test_sala_soul_propagation.py && \
git -C <fork-wt> commit -m "test(sala): offline proof conduct rules reach loaded SOUL (F3 T15)"
```

---

### Task 16: exit-gate — real task, EX-49 raw proof, anti-narration guard

**Files:**
- No new code. Uses the DeepSeek smoke topology (isolated `$HERMES_HOME` provider:deepseek, isolated port ≠ 8787, hermes-agent venv, `SALA_ENABLE=1`), same as the F2 smoke.
- Produces: `docs/curador/` sibling `docs/sala/F3-GATE-PROOF.md` with the raw evidence bundle.

**Interfaces:**
- Consumes: everything above + the two conduct skills in the isolated `$HERMES_HOME/SOUL.md`.

- [ ] **Step 1: Bring up the isolated conducted stack**

Isolated `$HERMES_HOME` with `model.provider: deepseek` + `providers.deepseek.base_url: https://api.deepseek.com/v1` + `$ISO/SOUL.md` = the conduct-carrying SOUL_SEED; `DEEPSEEK_API_KEY` from `databrain/.env` (masked in all logs — constraint 7); server on an isolated port (e.g. 8792) run with the hermes-agent venv + `PYTHONPATH=<fork-wt>`; `SALA_ENABLE=1`; `ACERVO` = an isolated acervo (never the real one). **Prod 8787 and the real acervo are untouched** (verify pid before/after).

- [ ] **Step 2: Run one real non-trivial task end to end**

Draft → launch a real task that necessarily triggers an external action — e.g. "preparar e enviar o ofício de renegociação" (the *send* is the external action). Drive the launched session; let it conduct. **C5 (Draft-First mechanism):** the conducting agent, governed by `excrtx-govern-draftfirst` (EX-08) + `excrtx-conduct-loop`, on reaching the external action **appends `{"t":"draft","action":"enviar ofício","draft_text":"…"}` to conduct.jsonl** (via the shell append) and ends its turn awaiting authorization — the observer turns that into a `sala_draft` card. *(A genuine runtime tool-permission gate — e.g. a shell/git command the agent runs — is a bonus second source of `sala_draft` via `route_approvals`, with a real `approval_id`; it is NOT required for the gate.)*

- [ ] **Step 3: Collect the gate evidence (EX-49 raw)**

Capture and save to `docs/sala/F3-GATE-PROOF.md`:
1. **Live reflection**: dump `GET /api/canvas/sala/stream?...&since=0` (the frame log) showing `sala_phase`/`sala_artifact`/`sala_gap` arriving during execution + the resulting canvas `/artifacts/expected`, `/gaps`.
2. **≥1 Draft-First AUTH exercised**: a `sala_draft` frame (from the agent's conduct `{"t":"draft"}` declaration) + the human's in-island "Autorizar" + the resulting `/authorization/-` entry carrying the **verbatim** words. *(If a runtime tool gate also fired, include its `/api/approval/respond {choice:"once"}` log too.)*
3. **Interrupts only in 3 classes**: the clarify/approval logs — assert every interruption is `clarify` or `approval` (bound_interrupt is a clarify sub-tag); zero other channels.
4. **Anti-narration guard (I6 + I-S1 — precise, non-vacuous):** the phase tokens are ordinary English words, so do NOT grep bare tokens over the whole transcript (conduct.jsonl and tool-call args contain them → guaranteed false positive). And the WebUI session store is **a single JSON object with a `.messages[]` list** (NOT line-JSONL, no top-level `.role`; assistant `content` is a string OR a list of `{type,text}` parts — `api/models.py:1019,880-890`), so a `jq 'select(.role==...)'` over a `.jsonl` matches nothing → passes **vacuously**. Instead:
   - Extract **only assistant TEXT** from the session JSON, coercing array-content to text: `jq -rc '.messages[]? | select(.role=="assistant") | (.content | if type=="array" then map(.text // .content // "")|join(" ") else . end)' <session.json> > /tmp/assistant.txt`.
   - **Guard against a vacuous pass**: `test "$(wc -l < /tmp/assistant.txt)" -gt 0` — if there are zero assistant turns the gate is **inconclusive, not green** (stop and report).
   - Grep the assistant text for **phase-announcement patterns**, not bare tokens: `grep -iE 'fase (de |do )?(classify|define_done|evidence|decide|act|verify|report)|(entrando na|estou na|iniciando a) fase|"t":"phase"' /tmp/assistant.txt` → **must be empty**. The phases live only in `conduct.jsonl` (agent-appended via `printf … >> conduct.jsonl`) and `sala_phase` SSE frames — never in assistant text. *(Confirm the exact session-JSON path from `api/models.py` first — EX-49.)*
5. **Isolation proof**: prod 8787 pid identical before/after; real acervo untouched.

- [ ] **Step 4: The gate assertion**

The gate passes iff: canvas reflected the execution live; ≥1 Draft-First AUTH with verbatim words in `authorization[]`; interruptions only `{clarify, approval}`; the anti-narration grep is empty; isolation intact. If any fails, **stop and report** (constraint 5/6) — do not weaken the gate (fable rule).

- [ ] **Step 5: Commit the proof + final phase report**

```bash
git -C <exocortex-wt> branch --show-current && \
git -C <exocortex-wt> add docs/sala/F3-GATE-PROOF.md && \
git -C <exocortex-wt> commit -m "docs(sala): F3 exit-gate proof (live reflection + AUTH + anti-narration) (F3 T16)"
```

---

## Deferred to F4 / F5 (explicit — no silent cap)

- **F5 — `run_journal` artifact backstop.** v1 sources artifacts only from conduct.jsonl `{"t":"artifact"}`. The mechanical backstop (catch artifacts the agent forgets to declare) is deferred; the review pinned the correct shape for F5: `read_session_run_events` returns a **dict** `{status, events}`; the cursor is a real `run_id:seq` that must be **bootstrapped from the journal head** (no "from-beginning"); the tool payload is nested under `payload` with keys `name/args/preview` (extract the file path from `payload.args` per write-tool). This is a bootstrap redesign, not a key tweak — hence F5.
- **F5 — vetor→profile scoping** so the conduct rules govern *only* launched sessions (not the base persona). No-op in the isolated smoke (default profile already maps to `$HERMES_HOME`); load-bearing only in multi-profile prod.
- **F5 — `.dogfood/scenarios/EX-60.yaml` + `EX-61.yaml`** (10-field scenarios) + `calibrate-hermes.sh` + full D2–D5 `skill_judge`. F3 ships the skills at keyless D1 + FEATURES.md registration.
- **F5 — full-app integration** (islands into `ui.js`/`panels.js` beyond `canvas-dev.html`), a11y, i18n of the PT-BR sala strings, docs, `sources.lock` re-pin, interactive-audit G0–G5, COLLAB closure, #130 update.
- **F4 — durable canvas↔sqlite-kanban board JOIN** + board write-back; F3 ships only the phase→column display projection (OD-3). First-class `trace[]`/`findings[]` canvas doc fields; F3 keeps them ephemeral in conduct.jsonl + replayable `SALA_ROOMS`. The closing `fable-judge` at checkout (distinct from F3's live verify bounds).
- **F5 — live-room durability** across server restart beyond the `launch.yaml` glob-rebuild backstop.

## Self-Review (writing-plans checklist)

**1. Spec coverage (the 5 charter deliverables + gate):**
- D1 session→canvas cards → T4 (artifact/next_move) + T8 (observer) + T9 (clarify→gap) + T5 (kanban via phase) + T12 (render). ✅
- D2 governance gates (Draft-First AUTH + trace cards P9) → T11 (`sala_draft`) + T12 (AUTH verbatim → `/authorization/-`, T2 whitelist) + T4 (`sala_trace`). ✅
- D3 bounds as HITL → T5 (watchdog counters) + T10 (self-raised bound clarify) + T14 (skill). ✅
- D4 discreet phases, never narrated → T4 (`sala_phase`) + T12 (chip) + T13 (anti-narration compiled_rule) + T16 (grep guard). ✅
- D5 PORT decision → T13 + T14 (CREATE 2 skills) + ADR-CT-07 + T15 (propagation proof). ✅
- Exit gate → T16. ✅

**2. All 7 critique must-fixes folded in:** #1 SOUL path → C-E + T15 (offline `load_soul_md` proof; no profile-forcing). #2 OD-1 → decided (conduct.jsonl + journal backstop, T8). #3 branch discipline → C-A + per-repo commit blocks. #4 approval seam → `route_approvals._approval_sse_subscribe` (T8). #5 AUTH words → in-island capture → `/patch` (T12). #6 honest bound framing → C-C + T10 note. #7 E9 → C-D + T1 §(g). ✅

**3. Type consistency:** `SalaState.ingest`, `_emit`/`_room`/`_project`, `register_launch`/`resolve`/`_rebuild_launched`, `start_observer`/`_poll_once`/`_INJECTED`, `handle_sala_get`/`handle_sala_post`, the 10 `sala_*` names + `klass`/`type`/`atype` fields — used identically across T3–T12. `PHASE_TO_COLUMN`/`TRACE_OP_PATH` consts defined in T4, reused in T5/T10. ✅

**4. Known soft spots (surfaced, not hidden):**
- **T6/T7 forward-reference** to `start_observer`/`handle_sala_post` (defined in T8) — mitigated with explicit temporary stubs removed in T8.
- **T8 Step 1** pins the one remaining external shape (approval `pending` keys `command`/`description`) via the real `submit_pending` call site before writing `_frame_from_approval` — a confirm step, not a placeholder. *(The journal event shape is no longer a dependency — the backstop moved to F5.)*
- **T12 e2e** needs the isolated dev server (Playwright) — same caveat as the F1b/F2 e2e; the pure reducer (T4/T5/T9/T10/T11) carries the hermetic coverage.
- **T1 contract lint** skips (not fails) when `UMBRELLA_ROOT` is unset (M10), so the fork suite never hard-couples to the umbrella's on-disk location.

**5. Adversarial plan review folded (2026-07-25 — 24 findings vs real code, verdict was *needs-revision*):**
- **7 critical fixed:** C1/C2/C3 (broken journal-tail → **removed**, backstop deferred to F5, conduct.jsonl is v1's sole trail); C4 (island `choice:"once"`, was `decision:"approve"` = silent DENY); C5 (Draft-First AUTH via agent's conduct `{"t":"draft"}`, not a route_approvals pending that `excrtx-govern-draftfirst` never raises); C6 (EX-59 taken → **EX-60/EX-61**, grep now includes FEATURES.md); C7 (**H1 added** to both skills so `--d1-only` passes).
- **7 important fixed:** I1 (approval keys `command`/`description`); I2 (`session_id` on `sala_draft` + island `grab`); I3 (dropped the false newline assertion — wildcard `[^/]+` matches `\n`); I4 (register EX-IDs in FEATURES.md, dropped the unsupported dogfood-catalog claim → F5); I5 (exact phase tokens `define_done`/`evidence` in the skill); I6 (anti-narration grep = assistant-text-only via `jq role==assistant` + narration-pattern, plus the `printf >> conduct.jsonl` append mechanism); I7 (T8 Step-1 now targets `submit_pending`, not run_journal).
- **10 minor fixed:** M1 (bound-clarify inter-phase note); M2 (prime clarify from `get_pending` on subscribe); M3 (declare `canvas-tarefas.js`); M4 (real palette tokens); M5 (gate the response input on `clarify_id`); M6 (PT-BR phase chip); M7 (T15 env-resolved paths + `pytest.skip`); M8 (T1 lint asserts `E9`+`AGUI_GATEWAY`); M9 (contract change-rule → `(a)–(g)`); M10 (T1 test `skip`s without `UMBRELLA_ROOT`).

**6. Re-verify of the fold folded (2026-07-26 — narrow re-check of the NEW fold code vs real code; backend+frontend slices verified CLEAN, skills slice caught regressions):**
- **1 critical (fold-regression) fixed — C-S1:** conduct-loop `compiled_rules` was a single-quoted YAML scalar with an embedded `printf '…'`; `compile_soul.py`'s regex truncates at the first `'`, silently dropping the "NEVER narrate" + `{"t":"draft"}` tail (and the gate only grepped the header → false green). → rewrote as a **block scalar `|`** (lossless branch) + T13/T15 now assert `NEVER narrate` reached `SOUL_SEED.md`. *(Note: the pre-existing `excrtx-govern-draftfirst` skill is truncated the same way in the live `SOUL_SEED.md:333` — a repo bug to flag separately, outside F3.)*
- **1 important fixed — I-S1:** the T16 anti-narration guard read a non-existent `.jsonl` `{role,content}` shape → passed **vacuously** (false green). → repointed at the WebUI session JSON `.messages[]` (content str-or-array coerced) + a non-vacuous guard that fails the gate if zero assistant turns are found.
- **4 minor fixed:** M-B2 (dropped the dead approval-`_prime` branch — `route_approvals` has no `get_pending`; documented the F5 edge); M-B1 (reducer docstring `run_journal`→`conduct.jsonl`); M-F1 (`session_id` added to the §(g) `sala_draft` shorthand); M-F2 (renamed the colliding `cvt-sala-draft` textarea class → `cvt-sala-drafttext`).
- **Verified sound by the re-verify (no change needed):** every external shape the fold rewrote — `_frame_from_approval` keys (`command`/`description`), the C4 `choice:"once"` grant (routes.py:23494), the conduct→approval→`_on_approval` dispatch, `window.CVT.esc`/`acceptOps`, the DOM anchors, `/api/clarify/respond` + `/api/approval/respond` bodies, the `/authorization/*` whitelist — and the full 9-kind frame↔handler taxonomy (no orphans).

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-07-23_canvas-tarefas/F3-PLANO.md`. **Before execution:** this plan goes through an **adversarial review against the real code** (program method step 4) and then the SDD workflow (step 5, sequential impl→review per task in an isolated `collab/canvas-f3` worktree — **never two implementers on the same branch**), whole-branch review on the most capable model, one fix wave, then merge `--no-ff` → `exocortex/stable` **only after the owner approves the gate**.

**Two execution options (once the plan review passes):**
1. **Subagent-Driven (recommended)** — fresh subagent per task + two-stage review between tasks (matches the F2 SDD that landed 14/14).
2. **Inline Execution** — batch with checkpoints.

