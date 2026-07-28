# C0 — Close the T16 gate via conduct-skill calibration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a launched Canvas session WRITE its fable-loop trail to `conduct.jsonl` (instead of narrating), so the live T16 gate produces ≥1 Sala card + ≥1 Draft-First AUTH from a real conducted session.

**Architecture:** Skills-only calibration (per ADR-CT-07: the persona governs the loop) plus one additive fork legibility fix — inject the `task_id` into the launch brief so the agent can target the append path without deriving it. No backstop, no new tool (owner decision OD-C0-1). Docs corrected for the destructive-`cp` provisioning hazard. Gate re-run on isolated DeepSeek.

**Tech Stack:** Python 3.12 (fork `api/`), Hermes skills (`compiled_rules:` → `compile_soul.py` → `SOUL_SEED.md`), vanilla JS (untouched here), pytest (fork `.venv`), isolated DeepSeek smoke.

## Global Constraints

- **Spec:** `exocortex.saas/docs/superpowers/specs/2026-07-28-c0-t16-conduct-calibration-design.md` (owner-approved). Owner decisions OD-C0-1..4 are binding.
- **Hot zone — NEVER touch:** `hermes-webui/static/{ui,messages,sessions,panels,boot}.js`, `static/style.css`, `static/index.html`; `api/routes.py` = 0 new lines (endpoints via forward in `api/canvas_tarefas.py`). Editable (fork-owned MOD): `api/canvas_*.py`, `static/canvas-*.js/.css`, `canvas-dev.html`. Invariant: never perturb upstream nesquena; **zero build step**; no JS/npm dep.
- **Skills-only fallback (OD-C0-1):** if honest calibration does not close the gate, STOP and bring the owner the finding + options. No observer backstop, no `conduct_append` tool.
- **Shared checkout hazard:** all work in **isolated worktrees** (scratchpad), branch `collab/canvas-c0` cut from **origin tips** (fork `origin/exocortex/stable`, exo `origin/main`, umbrella `origin/master`). Verify branch in the SAME composite commit command; **never `git add -A`** (explicit paths). Merge via **DETACHED worktree at the origin tip** → `--no-ff` → push, **owner-gated**.
- **Keyless runner:** `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest <files> -q` (PYTHONPATH=worktree). Skills: `python3 scripts/skill_judge.py --skill <n> --d1-only`. Compile: `python3 scripts/compile_soul.py` (block scalar `|`; **no blank/space-only line** inside `compiled_rules` — C-S1 truncates silently).
- **SOUL truncation budget (128K case):** `load_soul_md` keeps head 70% of `cap = context_length×4×0.06`. Current `SOUL_SEED.md` = 25,111 chars; conduct block 14,434–16,019. **Keep total ≤ 30,000 chars** (no truncation at cap 30,720) and the conduct block within the head window (< 21,504). Combined `compiled_rules` additions across both conduct skills ≤ ~5,000 chars.
- **Conduct.jsonl raw field schema (agent-written, from `_frame_from_conduct`):** `phase{phase,seq}` · `trace{kind∈intent|twins|pending,title,evidence}` · `artifact{title,atype,path,tool}` · `next_move{text}` · `draft{action,draft_text}` · `verify{subject,ok,tried,output,hypothesis}` · `search{query,query_sig,empty}` · `surprise{subject,code,check,spec,resolution}`. Missing keys → empty cards.
- **COLLAB 3-repos, separate commits per repo:** fork (task_id MOD-015 + island untouched), exocortex (skills + docs), umbrella (change record). Contract §(a)–(g) unchanged (brief content is not a contract surface — additive).
- **Prod isolation:** never touch prod `:8787` (verify pid before/after) or the real acervo. Smoke on `:8792`, isolated `HERMES_HOME`/`ACERVO`.

---

## File Structure

| File | Repo | Action | Responsibility |
|---|---|---|---|
| `api/canvas_brief.py` | fork | modify | add pure `with_task_id(brief, task_id)` |
| `api/canvas_tarefas.py` | fork | modify | call `with_task_id` in `_handle_launch` after task_id known |
| `tests/test_canvas_brief.py` | fork | modify | unit-test `with_task_id` |
| `EXCRTX_MODIFICATIONS.md` | fork | modify | MOD-015 entry |
| `skills/excrtx-conduct-loop/SKILL.md` | exo | modify | calibrated `compiled_rules` (append-first, task_id-from-brief, field schema, PT-BR anti-narration) |
| `skills/excrtx-conduct-bounds/SKILL.md` | exo | modify | calibrated `compiled_rules` (bound field schema, PT-BR) |
| `SOUL_SEED.md` | exo | regenerate | `compile_soul.py` output (never hand-edit compiled block) |
| `docs/sala/F3-GATE-PROOF.md` | exo | modify | widen anti-narration pattern to PT-BR; PARTIAL→COMPLETE after gate |
| `docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-07-port-conduct-skills.md` | exo | modify | surgical propagation recipe + destructive-cp warning |
| `FEATURES.md` | exo | modify | EX-60/EX-61 propagation line → surgical |
| `docs/plans/2026-07-23_canvas-tarefas/F3-PLANO.md` | exo | modify | C-E / T13 propagation notes → surgical (annotate) |
| `INSTALL.md` | exo | modify | Step-07 destructive-cp warning |
| `.harness/changes/2026-07-28_COLLAB_canvas-c0.md` | umbrella | create | COLLAB change record |

---

### Task 1: Fork — inject `task_id` into the launch brief (MOD-015)

**Files:**
- Modify: `hermes-webui/api/canvas_brief.py` (add `with_task_id`)
- Modify: `hermes-webui/api/canvas_tarefas.py` (`_handle_launch`, after `task_id = _register_task(...)` ~:248, before `return`/`_json(... "brief": brief ...)` ~:277)
- Test: `hermes-webui/tests/test_canvas_brief.py`
- Modify: `hermes-webui/EXCRTX_MODIFICATIONS.md`

**Interfaces:**
- Produces: `with_task_id(brief: str, task_id: str) -> str` — appends the exact marker line `Task ID (para o conduct.jsonl): <task_id>`. Task 2's skill instructs the agent to read the task_id from THIS marker.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_canvas_brief.py`:

```python
def test_with_task_id_appends_marker_and_preserves_brief():
    from api.canvas_brief import with_task_id
    out = with_task_id("Brief: renegociar\n\nPostura: execução\n", "task_20260728_ab12cd")
    assert out.startswith("Brief: renegociar")            # original preserved
    assert "Task ID (para o conduct.jsonl): task_20260728_ab12cd" in out
    assert out.endswith("\n")                              # trailing newline kept
    # idempotent shape: exactly one marker line
    assert out.count("Task ID (para o conduct.jsonl):") == 1
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd <fork-wt> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest tests/test_canvas_brief.py::test_with_task_id_appends_marker_and_preserves_brief -q`
Expected: FAIL — `ImportError: cannot import name 'with_task_id'`.

- [ ] **Step 3: Implement `with_task_id`**

Append to `api/canvas_brief.py`:

```python
def with_task_id(brief: str, task_id: str) -> str:
    """EXCRTX MOD-015 (C0) — append the launched task_id so the conducting
    agent targets $ACERVO/_tasks/<id>/conduct.jsonl without deriving it from
    $HERMES_SESSION_ID (fragile). The conduct skills read this exact marker.
    """
    return brief.rstrip("\n") + f"\n\nTask ID (para o conduct.jsonl): {task_id}\n"
```

- [ ] **Step 4: Wire it into `_handle_launch`**

In `api/canvas_tarefas.py`, after `task_id = _register_task(...)` succeeds (~:248) and **before the session/attachment staging** (`session = _new_session()` ~:261, which stages `brief_path` via `_stage_file` copying bytes off disk ~:262-263), add BOTH lines:

```python
    brief = canvas_brief.with_task_id(brief, task_id)
    brief_path.write_text(brief, encoding="utf-8")   # marker reaches the staged brief.md too
```

**Why the second line (review Finding 1):** `brief.md` is written pre-task_id at ~:245, and `_stage_file` (~:175-186) copies the file bytes into the session attachments. Mutating only the local `brief` var would give the agent a message WITH the marker but a staged `brief.md` WITHOUT it — if the agent reads the attachment, task_id resolution fails. Re-persisting `brief_path` after `with_task_id` keeps message + attachment in sync. Confirm `brief` is the same var returned as `"brief": brief` (~:277) → the agent's first message (`/api/chat/start message: res.brief`). Do NOT touch the hot zone.

- [ ] **Step 5: Run the unit test + full canvas suite (no regression)**

Run: `cd <fork-wt> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest tests/test_canvas_brief.py tests/test_canvas_sala.py tests/test_sala_reducer.py -q`
Expected: PASS (new test green; sala/brief suites unchanged).

- [ ] **Step 6: MOD catalog + commit**

Append a `[MOD-015]` entry to `EXCRTX_MODIFICATIONS.md` (follow the MOD-014 format): "C0 — inject launched `task_id` into the compile_brief output (`api/canvas_brief.py with_task_id`, one call in `_handle_launch`) so the conducting agent targets `_tasks/<id>/conduct.jsonl` without fragile `$HERMES_SESSION_ID` derivation. Additive; hot zone + island untouched."

```bash
git -C <fork-wt> branch --show-current | grep -qx collab/canvas-c0 && \
git -C <fork-wt> add api/canvas_brief.py api/canvas_tarefas.py tests/test_canvas_brief.py EXCRTX_MODIFICATIONS.md && \
git -C <fork-wt> commit -m "feat(canvas): inject task_id into launch brief for conduct trail (MOD-015, C0)"
```

---

### Task 2: exocortex — calibrate `excrtx-conduct-loop` compiled_rules

**Files:**
- Modify: `exocortex.saas/skills/excrtx-conduct-loop/SKILL.md` (`compiled_rules:` block only; body `## Procedure` field-schema line)

**Interfaces:**
- Consumes: the Task 1 brief marker `Task ID (para o conduct.jsonl): <id>`.
- Produces: the calibrated `## Conduct Loop` section (after compile in Task 4).

- [ ] **Step 1: Replace the `compiled_rules:` block (keep the YAML `|` block scalar; no blank lines inside)**

In `skills/excrtx-conduct-loop/SKILL.md`, replace the `compiled_rules: |` block with (indentation = 2 spaces, every line non-empty — C-S1):

```yaml
compiled_rules: |
  When conducting a launched Canvas task (a Cockpit room), your FIRST act in EVERY phase is
  a real shell command appending one line to the conduct trail — not prose in your reply. The
  reply is the work; the loop is signalled out-of-band only.
  Resolve your task id ONCE from the launch brief line "Task ID (para o conduct.jsonl): <id>"
  and reuse it. Append target is the absolute path "$ACERVO/_tasks/<id>/conduct.jsonl" (the
  dir already exists; >> creates the file).
  Run the fable loop with these EXACT phase tokens (no spaces): classify -> define_done ->
  evidence -> decide -> act -> verify -> report. At each phase boundary run:
  printf '%s\n' '{"t":"phase","phase":"<token>","seq":N}' >> "$ACERVO/_tasks/<id>/conduct.jsonl"
  incrementing N. After the FIRST append, self-verify once: wc -l "$ACERVO/_tasks/<id>/conduct.jsonl".
  Record every product as a conduct line with the EXACT keys the Cockpit renders (missing keys
  render empty cards): artifact -> {"t":"artifact","title":..,"atype":..,"path":..,"tool":..};
  trace -> {"t":"trace","kind":"intent|twins|pending","title":..,"evidence":{..}}; next move ->
  {"t":"next_move","text":..}; Draft-First -> {"t":"draft","action":..,"draft_text":..}.
  NEVER narrate a phase in your reply — no "Classificacao:", "Definicao de pronto:", "Fase:",
  "estou na fase X"; the phase is the conduct line, never text. Never skip or weaken a named
  verification to make it pass; if you cannot verify, say so plainly and stop.
```

- [ ] **Step 2: Pin the field schema in the body `## Procedure`**

In the same file's `## Procedure` section, replace the item-3 line with the exact raw keys so a hand reader matches the compiled rule:

```markdown
3. **evidence → decide → act** — as you produce them, append conduct lines with exact keys: `{"t":"artifact","title":…,"atype":…,"path":…,"tool":…}`, `{"t":"trace","kind":"intent|twins|pending","title":…,"evidence":{…}}`, `{"t":"next_move","text":…}`. A Draft-First (external action) is `{"t":"draft","action":…,"draft_text":…}`.
```

- [ ] **Step 3: D1 structural gate**

Run: `cd <exo-wt> && python3 scripts/skill_judge.py --skill excrtx-conduct-loop --d1-only`
Expected: PASS.

- [ ] **Step 4: Budget check (added chars within envelope)**

Run: `cd <exo-wt> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -c "import re,sys; t=open('skills/excrtx-conduct-loop/SKILL.md').read(); m=re.search(r'compiled_rules: \|\n((?:[ \t]+.+\n?)+)', t); print('loop compiled_rules chars:', len(m.group(1)))"`
Expected: prints a number ≤ ~2,200 (leaves room for bounds + margin under the 5,000 combined budget).

- [ ] **Step 5: Commit (compile happens in Task 4, after bounds too)**

```bash
git -C <exo-wt> branch --show-current | grep -qx collab/canvas-c0 && \
git -C <exo-wt> add skills/excrtx-conduct-loop/SKILL.md && \
git -C <exo-wt> commit -m "feat(conduct-loop): calibrate append-first + task_id-from-brief + PT-BR anti-narration + field schema (C0)"
```

---

### Task 3: exocortex — calibrate `excrtx-conduct-bounds` compiled_rules

**Files:**
- Modify: `exocortex.saas/skills/excrtx-conduct-bounds/SKILL.md` (`compiled_rules:` block; `## Procedure`)

**Interfaces:**
- Produces: the calibrated `## Conduct Bounds` section (after compile in Task 4).

- [ ] **Step 1: Replace the `compiled_rules:` block (block scalar `|`, no blank lines)**

```yaml
compiled_rules: |
  In a conducted Canvas task, honor the mechanical bounds and record each via a conduct line
  (out-of-band shell append, never prose) at "$ACERVO/_tasks/<id>/conduct.jsonl" (same id from
  the launch brief). Bound A: after 3 failed fix-verify cycles on the SAME check, STOP; append
  each cycle {"t":"verify","subject":..,"ok":false,"tried":..,"output":..,"hypothesis":..} and on
  the 3rd self-invoke clarify (kind="bound_interrupt") with tried + raw output + hypothesis;
  NEVER answer a bound clarify with "best judgement" — re-raise. Bound B: after 2 searches with
  no new information, STOP and append {"t":"search","query":..,"query_sig":..,"empty":true}.
  Surprise: when code, a check and the spec disagree, append {"t":"surprise","subject":..,
  "code":..,"check":..,"spec":..,"resolution":..} and resolve by authority order executivo > spec
  > tests > codigo. Interrupt ONLY via the 3 sanctioned classes (executive-only gap, course-change,
  clear improvement) through clarify/approval — never invent a fourth channel. Verify/search cards
  surface only at the bound threshold (3rd fail / 2nd empty) — by design.
```

- [ ] **Step 2: Pin the field schema in `## Procedure`**

Replace the `## Procedure` items 1–3 tail with exact keys:

```markdown
1. Track fix-verify cycles per check; append `{"t":"verify","subject":…,"ok":false,"tried":…,"output":…,"hypothesis":…}` each cycle; on the 3rd, stop and self-invoke a `bound_interrupt` clarify.
2. Track searches; on the 2nd empty, append `{"t":"search","query":…,"query_sig":…,"empty":true}` and stop.
3. On code/check/spec disagreement, append `{"t":"surprise","subject":…,"code":…,"check":…,"spec":…,"resolution":…}` and apply authority order executivo > spec > tests > código.
```

- [ ] **Step 3: D1 structural gate**

Run: `cd <exo-wt> && python3 scripts/skill_judge.py --skill excrtx-conduct-bounds --d1-only`
Expected: PASS.

- [ ] **Step 4: Budget check**

Run: `cd <exo-wt> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -c "import re; t=open('skills/excrtx-conduct-bounds/SKILL.md').read(); m=re.search(r'compiled_rules: \|\n((?:[ \t]+.+\n?)+)', t); print('bounds compiled_rules chars:', len(m.group(1)))"`
Expected: ≤ ~1,400.

- [ ] **Step 5: Commit**

```bash
git -C <exo-wt> branch --show-current | grep -qx collab/canvas-c0 && \
git -C <exo-wt> add skills/excrtx-conduct-bounds/SKILL.md && \
git -C <exo-wt> commit -m "feat(conduct-bounds): calibrate conduct-line field schema + PT-BR (C0)"
```

---

### Task 4: exocortex — recompile SOUL_SEED + verify sections/tail/budget

**Files:**
- Regenerate: `exocortex.saas/SOUL_SEED.md` (via `compile_soul.py` — never hand-edit)

**Interfaces:**
- Consumes: the calibrated skills from Tasks 2–3.
- Produces: `SOUL_SEED.md` with intact `## Conduct Loop` + `## Conduct Bounds` + anti-narration tail, total ≤ 30,000 chars.

- [ ] **Step 1: Compile**

Run: `cd <exo-wt> && python3 scripts/compile_soul.py`
Expected: exits 0; writes `SOUL_SEED.md`.

- [ ] **Step 2: Verify sections + tail survived (C-S1 not truncated) + budget**

Run:
```bash
cd <exo-wt> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python - <<'PY'
s = open("SOUL_SEED.md").read()
n = len(s)
assert "## Conduct Loop" in s, "missing ## Conduct Loop"
assert "## Conduct Bounds" in s, "missing ## Conduct Bounds"
assert "NEVER narrate a phase" in s, "anti-narration tail truncated (C-S1!)"
assert "printf '%s" in s, "printf few-shot truncated"
assert n <= 30000, f"SOUL_SEED too large ({n}) — truncation risk in 128K case"
# direct tail check (review Finding 2): the anti-narration line must sit inside the
# head window (21504), not a +1200 proxy of the section start.
tail = s.index("NEVER narrate a phase")
assert tail < 21504, f"anti-narration tail at {tail} — outside 128K head window"
print(f"OK — SOUL_SEED {n} chars; conduct sections present; tail at {tail} (<21504)")
PY
```
Expected: prints `OK …`; no assertion error.

- [ ] **Step 3: Desync sanity (review Finding 5 — cheap keyless)**

Run: `cd <exo-wt> && python3 scripts/compile_soul.py --validate-compiled-rules 2>&1 | grep -iE 'conduct-loop|conduct-bounds' ; echo "exit=$?"`
Expected: **no `conduct-loop`/`conduct-bounds` line** (they are body-synced). ⚠ A repo-wide `--validate-compiled-rules` is RED for ~7 pre-existing tool-only skills (known; use it only to confirm OUR two skills don't NEWLY appear) — do not gate the phase on the global exit code.

- [ ] **Step 4: Commit**

```bash
git -C <exo-wt> branch --show-current | grep -qx collab/canvas-c0 && \
git -C <exo-wt> add SOUL_SEED.md && \
git -C <exo-wt> commit -m "chore(soul): recompile SOUL_SEED with calibrated conduct rules (C0)"
```

---

### Task 5: exocortex — widen anti-narration check to PT-BR (F3-GATE-PROOF.md)

**Files:**
- Modify: `exocortex.saas/docs/sala/F3-GATE-PROOF.md`

**Interfaces:**
- Produces: the PT-BR-aware anti-narration pattern used by the Task 7 live gate. (Promotion to a committed script/test = F5, noted inline.)

- [ ] **Step 1: Write the pattern test (shell, keyless)**

Create a scratch fixture and assert the widened pattern catches the gate-proof's own PT-BR narration samples and is empty on a clean conduct-only reply:

```bash
# UTF-8 locale required for the accented bracket classes (review Finding 3 caveat).
PAT='fase (de |do )?(classify|define_done|evidence|decide|act|verify|report)|(entrando na|estou na|iniciando a) fase|"t":"phase"|Classifica[çc][ãa]o:|Defini[çc][ãa]o de pronto:|^[[:space:]]*(Fase|Evid[êe]ncia|Decis[ãa]o|A[çc][ãa]o|Verifica[çc][ãa]o|Relat[óo]rio):'
printf '%s\n' 'Classificação: Execução — entrego o artefato' | grep -iqE "$PAT" && echo "catches PT-BR classify: OK"
printf '%s\n' 'Definição de pronto: DRAFT aguardando aprovação' | grep -iqE "$PAT" && echo "catches PT-BR done: OK"
printf '%s\n' 'Verificação: os testes passam' | grep -iqE "$PAT" && echo "catches PT-BR verify: OK"
printf '%s\n' 'Ação: envio o e-mail' | grep -iqE "$PAT" && echo "catches PT-BR act: OK"
printf '%s\n' 'Segue o ofício em anexo; aguardo sua autorização.' | grep -iqE "$PAT" || echo "clean reply: OK (no false positive)"
```
Expected: five `OK` lines. All 7 fable phases now have a PT-BR method-label branch (review Finding 3: the earlier pattern caught only `classify`/`define_done`, letting `Evidência:`/`Decisão:`/`Ação:`/`Verificação:`/`Relatório:` narration pass as clean).

- [ ] **Step 2: Record the widened pattern + F5 note in F3-GATE-PROOF.md**

In `docs/sala/F3-GATE-PROOF.md`, under a new `## Anti-narration check (C0 — PT-BR)` section, document the pattern from Step 1 verbatim, state it supersedes the English-only I-S1 pattern, and add: *"Committed home (script/test that runs this over `.messages[]`) = F5; C0 uses it as the live-gate assertion."*

- [ ] **Step 3: Commit**

```bash
git -C <exo-wt> branch --show-current | grep -qx collab/canvas-c0 && \
git -C <exo-wt> add docs/sala/F3-GATE-PROOF.md && \
git -C <exo-wt> commit -m "docs(sala): widen anti-narration check to PT-BR method labels (C0)"
```

---

### Task 6: exocortex — correct the destructive propagation docs

**Files:**
- Modify: `exocortex.saas/docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-07-port-conduct-skills.md`
- Modify: `exocortex.saas/FEATURES.md` (EX-60 ~:604, EX-61 ~:614)
- Modify: `exocortex.saas/docs/plans/2026-07-23_canvas-tarefas/F3-PLANO.md` (C-E ~:40, T13 note ~:71)
- Modify: `exocortex.saas/INSTALL.md` (Step-07 ~:445-450)

**Interfaces:**
- Produces: every propagation instruction names the surgical `compile_soul.py --soul "$HERMES_HOME/SOUL.md"` path and warns that step-07's `cp` wipes onboarding on a personalized install.

- [ ] **Step 1: Fix ADR-CT-07 `## Consequências` + Evidence-3**

Replace the propagation sentence "A propagação ao acervo vivo … exige re-rodar `setup.sh` step-07 (ou `cp SOUL_SEED.md $HERMES_HOME/SOUL.md`)" with:

```markdown
A propagação das regras compiladas ao acervo vivo é **cirúrgica**:
`python3 scripts/compile_soul.py --soul "$HERMES_HOME/SOUL.md"` — `inject_into_soul` troca
**apenas** o bloco entre `<!-- COMPILED_RULES_START -->`/`END`, preservando a seção de
onboarding. **⚠ NÃO use `setup.sh` step-07 nem `cp SOUL_SEED.md $HERMES_HOME/SOUL.md`** num
install já personalizado: o `cp` sobrescreve o arquivo INTEIRO com o seed genérico, apagando
a identidade do onboarding (Identidade Raiz/Valores/Tom/Contexto de Negócio). O `cp`/step-07 só
é seguro num provisionamento novo ou num `$HERMES_HOME` isolado de smoke.
```
In "Evidência (trace SOUL) item 3", append after the step-07 description: *"(destrutivo num install personalizado — ver `## Consequências`; a propagação viva usa o compile cirúrgico, não o cp)."*

- [ ] **Step 2: Fix FEATURES.md EX-60/EX-61 "Instalação" rows**

In both rows replace "propagada ao runtime `$HERMES_HOME/SOUL.md` pelo step-07 (ADR-CT-07)" with:
```markdown
propagada ao runtime via `compile_soul.py --soul "$HERMES_HOME/SOUL.md"` (cirúrgico, preserva onboarding; **não** via step-07 `cp` — destrutivo num install personalizado; ADR-CT-07).
```

- [ ] **Step 3: Annotate F3-PLANO.md — two spots (review Finding 4)**

There are two distinct step-07/verbatim mentions with different wording (not one "T13 note"):
- **~:40** (the C-E paragraph): "…runtime `$HERMES_HOME/SOUL.md` is a **verbatim copy** installed by `setup.sh` **step-07** (which overwrites the in-place compile)."
- **~:71** (a file-table row for `$HERMES_HOME/SOUL.md`): "Receives `SOUL_SEED.md` verbatim via `setup.sh` step-07 (or `cp …`)."

Append the same inline NB to BOTH (don't expect a verbatim string match at :71): *"— NB (C0): esse `cp`/step-07 apaga o onboarding num install vivo; a propagação correta é `compile_soul.py --soul "$HERMES_HOME/SOUL.md"` (cirúrgico). O step-07/cp só vale no smoke isolado (é o que T15/T16 usam)."* Annotate only — do not rewrite the historical trace.

- [ ] **Step 4: Warn in INSTALL.md Step-07**

After the `cp "$SCRIPT_DIR/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"` block (~:450), add:
```markdown
> **⚠ Destrutivo num install personalizado.** Este `cp` sobrescreve `SOUL.md` inteiro com o
> seed — apaga a seção de onboarding. Só rode num provisionamento novo. Para propagar mudanças
> de `compiled_rules` a um install vivo, use o compile cirúrgico do Step 05b
> (`compile_soul.py --soul "$HERMES_HOME/SOUL.md"`), que preserva o onboarding.
```

- [ ] **Step 5: Verify + commit**

Run: `cd <exo-wt> && grep -c 'compile_soul.py --soul' docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-07-port-conduct-skills.md FEATURES.md INSTALL.md`
Expected: each file ≥ 1.

```bash
git -C <exo-wt> branch --show-current | grep -qx collab/canvas-c0 && \
git -C <exo-wt> add docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-07-port-conduct-skills.md FEATURES.md docs/plans/2026-07-23_canvas-tarefas/F3-PLANO.md INSTALL.md && \
git -C <exo-wt> commit -m "docs: correct SOUL propagation to surgical compile_soul (step-07 cp wipes onboarding) (C0)"
```

---

### Task 7: LIVE GATE — isolated DeepSeek smoke, iterate calibration, capture proof (owner-gated)

> **Not a unit test — the empirical exit gate.** Bounded iteration on Task 2/3 wording within the char budget + C-S1 rules. If it does not close after honest iteration → STOP and bring the owner the finding + options (OD-C0-1). No backstop.

**Files:**
- Modify: `exocortex.saas/docs/sala/F3-GATE-PROOF.md` (PARTIAL → COMPLETE with raw proof)

- [ ] **Step 1: Confirm prod untouched (pid before)**

Run: `pgrep -af 'HERMES_WEBUI_PORT=8787|server.py' | head; echo "prod pid noted"`. Record the prod `:8787` pid.

- [ ] **Step 2: Build the isolated smoke `HERMES_HOME` (pin context_length)**

Copy `~/.hermes/config.yaml` to an isolated `$HH`; override: `model.provider=deepseek`, `model.default=deepseek-v4-pro`, `model.base_url=https://api.deepseek.com/v1`, `model.api_mode=openai_chat_completions`, `providers.deepseek.base_url=https://api.deepseek.com/v1`; **pin `context_file_max_chars: 40000`** (removes the ≤64K truncation risk — B2). Export `DEEPSEEK_API_KEY` from `databrain/.env`. Build the SOUL surgically: `python3 scripts/compile_soul.py --soul "$HH/SOUL.md"` (NOT `cp`). Isolated `$ACERVO` = harness tools + templates copied from the real acervo.

- [ ] **Step 3: Bring up the isolated server on :8792**

Run `server.py` with `HERMES_WEBUI_PORT=8792 SALA_ENABLE=1`, hermes-agent venv, `PYTHONPATH=<fork-wt>`, `HERMES_HOME=$HH`, `ACERVO=<isolated>`. Confirm `/api/canvas/sala/state` responds.

- [ ] **Step 4: Run the canonical scenario end-to-end (one clean session)**

Frase: *"Redigir e enviar e-mail de cobrança da fatura 4471 ao Cliente Alfa até sexta."* (executable, external send → forces a Draft-First). `POST /api/canvas/draft` → `POST /api/canvas/launch` → open the Cockpit stream (`canvas-dev.html`, keep it open — do not reopen). Let the launched DeepSeek agent conduct. Then measure:
- `wc -l "$ACERVO/_tasks/<id>/conduct.jsonl"` > 0 (agent wrote the trail).
- `GET /api/canvas/sala/state` → `n_events > 0`.
- Playwright: the Sala zone shows ≥1 card + a Draft-First AUTH card with an authorization input.
- Anti-narration: extract assistant `.messages[]`, run the Task 5 PT-BR pattern → **empty**.

- [ ] **Step 5: Iterate or stop**

If any measure fails, adjust Task 2/3 wording (more imperative, reorder, tighten) within budget, `compile_soul.py --soul "$HH/SOUL.md"`, re-run Step 4. Cap: a handful of honest iterations. **If still failing → STOP; write the finding to `F3-GATE-PROOF.md` and bring the owner options.** Do not add a backstop.

- [ ] **Step 6: Record proof + confirm prod untouched (pid after)**

On success: update `docs/sala/F3-GATE-PROOF.md` GATE VERDICT PARTIAL → **COMPLETE**, with the raw `wc -l`, `n_events`, the empty anti-narration grep output, and the Cockpit screenshot path (`scratchpad/artifacts/c0-gate-<ts>.png`). Re-check prod `:8787` pid unchanged; real acervo unwritten.

```bash
git -C <exo-wt> branch --show-current | grep -qx collab/canvas-c0 && \
git -C <exo-wt> add docs/sala/F3-GATE-PROOF.md && \
git -C <exo-wt> commit -m "docs(sala): T16 gate CLOSED live — conduct.jsonl cards + Draft-First AUTH (C0)"
```

---

### Task 8: umbrella — COLLAB change record

**Files:**
- Create: `.harness/changes/2026-07-28_COLLAB_canvas-c0.md`

- [ ] **Step 1: Write the record**

Follow `.harness/conventions/CHANGE_LOG_PROTOCOL.md` + the F3 record format. Content: C0 mini-phase — conduct-skill calibration (EX-60/61) + `task_id`-in-brief (fork MOD-015) + surgical-propagation doc fixes; closes T16 live. Note **contract §(a)–(g) UNCHANGED** (brief content is not a contract surface — additive). Deferred (F5): step-07/step-04/step-05 idempotency, promote anti-narration grep to committed test, EX-60/61 dogfood, prod model alignment. New issue: provisioning idempotency.

- [ ] **Step 2: Contract lint (if the harness lint applies)**

Run: `cd <umbrella-wt> && UMBRELLA_ROOT=<umbrella-wt> <the repo's contract lint cmd, if present>`; else confirm the contract file is unchanged (`git -C <umbrella-wt> status --porcelain .harness/contracts/`).
Expected: no contract surface change.

- [ ] **Step 3: Commit**

```bash
git -C <umbrella-wt> branch --show-current | grep -qx collab/canvas-c0 && \
git -C <umbrella-wt> add .harness/changes/2026-07-28_COLLAB_canvas-c0.md && \
git -C <umbrella-wt> commit -m "docs(changes): COLLAB record — Canvas C0 (T16 conduct calibration)"
```

---

## Self-Review

**Spec coverage:** Spec §4 deliverables → Task map: (1) calibrate skills = T2/T3/T4; (2) task_id in brief = T1; (3) widen grep PT-BR = T5; (4) correct propagation docs = T6; (5) pin context_length = T7 Step 2; (6) re-run live gate = T7. Deferred/F5 + new issue = T8 record. All covered.

**Placeholder scan:** No TBD/TODO; all code and patterns are literal. `<fork-wt>`/`<exo-wt>`/`<umbrella-wt>`/`<id>`/`<ts>` are execution-time path/id substitutions (worktree paths + runtime task_id), not content placeholders — resolved when the isolated worktrees are created (subagent-driven-development sets them).

**Type consistency:** `with_task_id(brief, task_id) -> str` defined T1, consumed by T2's brief-marker instruction; the conduct-line field keys are identical across the Global Constraints schema, T2/T3 compiled_rules, and the reducer (`_frame_from_conduct`). Marker string `Task ID (para o conduct.jsonl): <id>` identical in T1 impl and T2 rule.

**Note on iteration:** T7 is intentionally an empirical loop (calibration is not deterministic); T2/T3 ship a complete first-cut wording, and T7 bounds the re-tuning with the stop-and-re-decide fallback.
