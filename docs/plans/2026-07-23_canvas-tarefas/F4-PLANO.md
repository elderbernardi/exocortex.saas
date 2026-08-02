# F4 — Colheita & Canonização · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Spec:** `exocortex.saas/docs/superpowers/specs/2026-08-01-canvas-f4-colheita-canonizacao-design.md` (decisões OD-F4-1..3 vinculantes).
> **Charter:** `docs/plans/2026-07-23_canvas-tarefas/F4-CHARTER.md`. **Contrato de execução:** `00-INDEX.md` §"Contrato de execução para agentes" (regras 1–10 vinculantes).

**Goal:** Fechar o ciclo de crescimento do Canvas de Tarefas — candidatos de execução acumulam numa bandeja sem interromper, são canonizados no acervo em 1 checkout HITL em lote, e o canvas vira receita reutilizável na galeria do Hangar.

**Architecture:** Padrão F2/F3 — dois módulos novos no fork (`api/canvas_colheita.py`, `api/canvas_receita.py`) com room+SSE próprios e forward-dispatch (0 linhas em `routes.py`); a canonização cruza pela CLI governada `acervoctl` (two-phase prepare→commit, OD-F4-1) via subprocess com seam de teste `ACERVOCTL_CMD`; fable-judge mecânico keyless no checkout; bandeja alimentada por linha conduct `{t:harvest}` (agente) + adoção manual (executivo). Exocortex expõe `--source-trust` no `acervoctl` e ganha o append `{t:harvest}` na skill EX-60.

**Tech Stack:** Python 3 (stdlib http.server handlers, subprocess, json, pathlib), pytest keyless com FakeHandler; JS vanilla IIFE (sem build, sem deps) para as ilhas; YAML frontmatter OKF v0.2; `acervoctl.py` (argparse). PT-BR nas strings de UI.

## Global Constraints

Copiadas verbatim do spec/00-INDEX (valem para TODA task):

- **Zona quente NUNCA tocada:** `hermes-webui/static/{ui,messages,sessions,panels,boot}.js`, `static/style.css`, `static/index.html`, e `api/routes.py` além dos 2 hooks já existentes (0 linhas novas — dispatch por forward em `api/canvas_tarefas.py`).
- **Zero dependências novas** (pip/npm), **zero build step**, strings de UI em **PT-BR**.
- **Escopo fechado:** toque só os arquivos listados na task. Precisar de arquivo fora da lista = surpresa → **pare e reporte**, nunca expanda em silêncio.
- **Prova bruta por task (EX-49):** toda task termina com o output real do comando de verificação. Sem output, a task não está concluída.
- **Segredos nunca** em logs/commits/relatórios/cards/receipts (mascarar).
- **`.quarantine/` não existe** — nunca ler/listar/escrever.
- **Escritas no acervo só via superfície semântica** (`acervoctl` prepare→commit); nunca escrita direta no FS do acervo.
- **Checkout compartilhado:** trabalho em **worktree isolada** (branch `collab/canvas-f4` cortada do tip de integração de ORIGIN — fork: `origin/exocortex/stable`; exocortex: `origin/main`; umbrella: `origin/master`); **verificar a branch no mesmo comando composto do commit**; **nunca `git add -A`** (paths explícitos); commits pequenos, mensagens em inglês, prefixo convencional; **nunca `git push` sem instrução explícita**.
- **Runner keyless do fork:** `cd <fork-worktree> && .venv/bin/python -m pytest <arquivos> -q` (PYTHONPATH=worktree). Exocortex: `python3 -m pytest tests/…` e `python3 scripts/skill_judge.py --skill … --d1-only` / `python3 scripts/compile_soul.py`.
- **Bounds (fable-method):** 3 ciclos falha-conserto na mesma verificação → pare e reporte; 2 buscas sem info nova → pare e registre a lacuna.

---

## Setup (Task 0) — worktrees isoladas

**Antes de qualquer task de código.** Branch **`collab/canvas-f4`** (nova; a `collab/canvas-tarefas` está 27 commits atrás de `exocortex/stable`, sem C0/C1 — NÃO reusar). Worktrees isoladas (checkouts principais são compartilhados com o owner):

- Fork: `git -C hermes-webui worktree add <path-fork-wt> -b collab/canvas-f4 origin/exocortex/stable`.
- Exocortex: `git -C exocortex.saas worktree add <path-exo-wt> -b collab/canvas-f4 origin/main`.
- Umbrella (só na Task 9): `git -C projetob worktree add <path-umb-wt> -b collab/canvas-f4 origin/master`.

Confirme a venv do fork existe na worktree (ou reuse `hermes-webui/.venv`). **Não** trabalhe nos checkouts principais. Nenhum commit de código nesta task.

- [ ] **Step 1:** Criar as worktrees fork+exocortex; `git -C <cada-wt> branch --show-current` = `collab/canvas-f4`.
- [ ] **Step 2:** `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_sala.py -q` → baseline verde (confirma o runner).
- [ ] **Step 3 (commit do spec+plano):** na worktree do exocortex, `git add docs/superpowers/specs/2026-08-01-canvas-f4-colheita-canonizacao-design.md docs/plans/2026-07-23_canvas-tarefas/F4-PLANO.md && git commit -m "docs(f4): spec + plano de Colheita & Canonização"` (paths explícitos; sem `-A`; sem push).

---

## Task 1: acervoctl — expor `--source-trust` (exocortex)

Pré-condição da OD-F4-1: o trust gate web precisa ser disparável pela CLI. Hoje `command_prepare_write`/`command_commit_write` hardcodam `source_trust="agent"`. Aditivo, pequeno.

**Files:**
- Modify: `scripts/acervoctl.py` (subcommands `prepare-write` ~L357-365 e `commit-write` ~L367-374; handlers `command_prepare_write` ~L64, `command_commit_write` ~L77)
- Test: `tests/test_acervoctl_source_trust.py` (Create)

**Interfaces:**
- Consumes: `acervo_semantic_core.prepare_write(..., source_trust="agent")` e `commit_write(prepared, ..., source_trust=None)` (já aceitam o kwarg).
- Produces: CLI `prepare-write --source-trust {executive|agent|untrusted}` (grava `receipt["source_trust"]`); `commit-write --source-trust {…}` (só pode *apertar* o trust vindo do receipt).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_acervoctl_source_trust.py
import json, subprocess, sys, os
from pathlib import Path

ACERVOCTL = Path(__file__).resolve().parents[1] / "scripts" / "acervoctl.py"

def _run(args, root):
    env = {**os.environ, "ACERVO_ROOT": str(root)}
    return subprocess.run([sys.executable, str(ACERVOCTL), *args],
                          capture_output=True, text=True, env=env)

def test_prepare_write_carries_untrusted_into_receipt(tmp_path):
    r = _run(["prepare-write", "--acervo-root", str(tmp_path),
              "--microverso", "receitas", "--nature", "knowledge",
              "--title", "Nota de teste", "--source-trust", "untrusted"], tmp_path)
    assert r.returncode == 0, r.stderr
    receipt = json.loads(r.stdout)
    assert receipt["source_trust"] == "untrusted"

def test_commit_write_untrusted_forces_status_draft(tmp_path):
    # prepare with untrusted, then commit valid OKF content, expect status: draft on disk
    pr = _run(["prepare-write", "--acervo-root", str(tmp_path), "--microverso", "receitas",
               "--nature", "knowledge", "--title", "Nota de teste",
               "--source-trust", "untrusted", "--receipt-out", str(tmp_path/"r.json")], tmp_path)
    assert pr.returncode == 0, pr.stderr
    content = (
        "---\nschema: acervo/v0.2\ntype: knowledge\ntitle: Nota de teste\n"
        "description: nota\ntags: []\ncreated_at: 2026-08-01T00:00:00Z\nclass: volátil\n"
        "status: active\nepistemic: observation\nconfidence: likely\n"
        "sources:\n  - type: agent-inference\n    ref: t1\nobserved_at: 2026-08-01\n"
        "extraction: agent\n---\ncorpo\n")
    (tmp_path/"c.md").write_text(content, encoding="utf-8")
    cm = _run(["commit-write", "--receipt", str(tmp_path/"r.json"),
               "--content-file", str(tmp_path/"c.md"), "--description", "nota"], tmp_path)
    assert cm.returncode == 0, cm.stderr
    committed = json.loads(cm.stdout)
    on_disk = Path(committed["target_path"]).read_text(encoding="utf-8")
    assert "status: draft" in on_disk  # trust gate forced it
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_acervoctl_source_trust.py -q`
Expected: FAIL — `prepare-write: error: unrecognized arguments: --source-trust`.

- [ ] **Step 3: Add the argument + pass-through**

Em `scripts/acervoctl.py`, no bloco do `prepare_cmd` (após `--receipt-out`):
```python
    prepare_cmd.add_argument("--source-trust", choices=["executive", "agent", "untrusted"],
                             default="agent", help="Nível de confiança da origem (08-write-policy §2)")
```
Em `command_prepare_write`, passar o kwarg:
```python
    payload = prepare_write(
        acervo_root=args.acervo_root, microverso=args.microverso, nature=args.nature,
        filename=filename, active_microverso=args.active_microverso or args.microverso,
        source_trust=args.source_trust,
    )
```
No `commit_cmd` (após `--class-name`):
```python
    commit_cmd.add_argument("--source-trust", choices=["executive", "agent", "untrusted"],
                            default=None, help="Aperta o trust do receipt (nunca afrouxa)")
```
Em `command_commit_write`, passar `source_trust=args.source_trust` ao `commit_write(...)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_acervoctl_source_trust.py -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
cd <exocortex-wt> && git branch --show-current   # deve imprimir collab/canvas-f4
git add scripts/acervoctl.py tests/test_acervoctl_source_trust.py
git commit -m "feat(acervoctl): expose --source-trust on prepare-write/commit-write (F4 trust gate)"
```

---

## Task 2: skill `excrtx-conduct-loop` (EX-60) — append `{t:harvest}` (exocortex)

O agente conduzido passa a poder **sinalizar promoções intencionais** escrevendo uma linha `{t:harvest}` no `conduct.jsonl` (mesmo canal out-of-band do C0). Aditivo ao `compiled_rules:` da EX-60; recompilar SOUL_SEED.

**Files:**
- Modify: `skills/excrtx-conduct-loop/SKILL.md` (bloco `compiled_rules:` + seção `## Procedure`)
- Modify: `SOUL_SEED.md` (regenerado por `compile_soul.py`; não editar à mão)
- Test/verify: `scripts/skill_judge.py --skill excrtx-conduct-loop --d1-only`; `scripts/compile_soul.py`; greps

**Interfaces:**
- Produces: convenção de linha `{"t":"harvest","nature":…,"scope":…,"title":…,"porque":…,"ref"|"body":…,"class":…,"source_trust":…}` em `_tasks/<task_id>/conduct.jsonl` (consumida pela Task 5 no fork).

- [ ] **Step 1: Add the harvest rule to `compiled_rules:`**

No `compiled_rules:` da EX-60, adicionar (respeitando o guard C-S1 — sem linha em branco dentro do block scalar `|`; orçamento de chars folgado, ver C0 change record):
```
  - No fechamento (fase report), para cada conhecimento/decisão/reflexão que MEREÇA virar memória canônica, faça UM append out-of-band (nunca narre): printf '%s\n' '{"t":"harvest","nature":"knowledge|decision|reflection","scope":"<microverso>","title":"…","porque":"…","ref":"<path do artefato>"|"body":"<texto curto>","class":"perene|volátil","source_trust":"agent"}' >> "$ACERVO/_tasks/$TID/conduct.jsonl"
  - Use ref quando o conteúdo já é um arquivo produzido; body para achado/reflexão sem arquivo. Nunca invente conteúdo só para preencher. Se nada merece promoção, não escreva harvest.
```

- [ ] **Step 2: Mirror the convention in `## Procedure`**

Adicionar um item na `## Procedure` descrevendo a linha `{t:harvest}` (schema de campos idêntico ao Step 1), para D1 (corpo-sincronizado com `compiled_rules`).

- [ ] **Step 3: Recompile SOUL_SEED**

Run: `python3 scripts/compile_soul.py`
Expected: exit 0; diff confinado à região da EX-60.

- [ ] **Step 4: Verify (keyless)**

Run:
```bash
python3 scripts/skill_judge.py --skill excrtx-conduct-loop --d1-only
grep -c '"t":"harvest"' SOUL_SEED.md            # ≥1
python3 scripts/compile_soul.py --validate-compiled-rules 2>&1 | grep -i conduct-loop || echo "conduct-loop em sync"
```
Expected: D1=COMPLIANT; grep ≥1; conduct-loop não aparece como desync.

- [ ] **Step 5: Commit**

```bash
cd <exocortex-wt> && git branch --show-current   # collab/canvas-f4
git add skills/excrtx-conduct-loop/SKILL.md SOUL_SEED.md
git commit -m "feat(ex-60): agent signals intentional promotions via conduct {t:harvest} (F4)"
```

---

## Task 3: `api/canvas_colheita.py` — store, card model, auto-gate, fable-judge mecânico (fork)

Núcleo puro/testável do módulo de colheita: store append-only, ingestão de candidato (card), cômputo automático do gate, e o **fable-judge mecânico**. Sem endpoints ainda (Task 4). Sem SSE ainda.

**Files:**
- Create: `api/canvas_colheita.py`
- Test: `tests/test_canvas_colheita.py`

**Interfaces:**
- Consumes: `canvas_store.tasks_dir()` (→ `$ACERVO/_tasks`); `canvas_store.load_canvas(canvas_id)` (doc dict).
- Produces (usadas por Tasks 4/5):
  - `ingest_candidate(canvas_id: str, cand: dict) -> dict` — normaliza + auto-gate + append em `_tasks/<canvas_id>/colheita.jsonl`; retorna o card `{id, nature, scope, title, porque, ref?, body?, class, source_trust, gate, status, origin}`.
  - `list_cards(canvas_id: str) -> list[dict]` — lê o `colheita.jsonl` (dedupe por `id`, último estado vence).
  - `set_status(canvas_id: str, card_id: str, status: str, **extra) -> dict` — append de atualização.
  - `compute_gate(nature: str, cls: str, source_trust: str) -> str` — `"draft-first"|"forced-draft"|"auto"`.
  - `judge_committed(target_path: str, log_path: str) -> dict` — fable-judge mecânico → `{ok: bool, checks: {exists, frontmatter, clean_portable, logged}, reasons: [str]}`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_canvas_colheita.py
import json
from pathlib import Path
import pytest
from api import canvas_colheita as C
from api import canvas_store

@pytest.fixture
def acervo(tmp_path, monkeypatch):
    (tmp_path / "_tasks" / "canvas_x").mkdir(parents=True)
    monkeypatch.setattr(canvas_store, "tasks_dir", lambda: tmp_path / "_tasks")
    return tmp_path

def test_compute_gate():
    assert C.compute_gate("knowledge", "perene", "agent") == "draft-first"
    assert C.compute_gate("persona", "volátil", "agent") == "draft-first"
    assert C.compute_gate("knowledge", "volátil", "untrusted") == "forced-draft"
    assert C.compute_gate("knowledge", "volátil", "agent") == "auto"

def test_ingest_and_list(acervo):
    card = C.ingest_candidate("canvas_x", {
        "nature": "knowledge", "scope": "cliente-alfa", "title": "Histórico",
        "porque": "reuso", "ref": "art/1.md", "class": "perene", "source_trust": "agent",
        "origin": "agent"})
    assert card["gate"] == "draft-first" and card["status"] == "pending" and card["id"]
    cards = C.list_cards("canvas_x")
    assert len(cards) == 1 and cards[0]["title"] == "Histórico"

def test_set_status_last_wins(acervo):
    c = C.ingest_candidate("canvas_x", {"nature": "knowledge", "scope": "s", "title": "t",
                                        "class": "volátil", "source_trust": "agent", "origin": "manual"})
    C.set_status("canvas_x", c["id"], "committed", receipt={"target_path": "x"})
    cards = C.list_cards("canvas_x")
    assert len(cards) == 1 and cards[0]["status"] == "committed"

def test_judge_committed_pass(tmp_path):
    f = tmp_path / "k.md"
    f.write_text("---\ntype: knowledge\ntitle: t\n---\ncorpo sem instancia\n", encoding="utf-8")
    log = tmp_path / "log.md"
    log.write_text("- CREATED k.md\n", encoding="utf-8")
    # stub the frontmatter validator to pass (real one lives in exocortex; see Task 4 seam)
    res = C.judge_committed(str(f), str(log), _validate=lambda p: True)
    assert res["ok"] and res["checks"]["clean_portable"] and res["checks"]["logged"]

def test_judge_committed_flags_instance_leak(tmp_path):
    f = tmp_path / "k.md"
    f.write_text("---\ntype: knowledge\n---\nvazou canvas_20260801_abc\n", encoding="utf-8")
    log = tmp_path / "log.md"; log.write_text("- CREATED k.md\n", encoding="utf-8")
    res = C.judge_committed(str(f), str(log), _validate=lambda p: True)
    assert res["ok"] is False and res["checks"]["clean_portable"] is False
```

- [ ] **Step 2: Run to verify fail**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_colheita.py -q`
Expected: FAIL — `ModuleNotFoundError: api.canvas_colheita`.

- [ ] **Step 3: Implement the pure core**

```python
# api/canvas_colheita.py
"""F4 Colheita — bandeja de candidatos + fable-judge mecânico (núcleo puro).
Store: $ACERVO/_tasks/<canvas_id>/colheita.jsonl (append-only, último estado por id vence)."""
import json, re, hashlib
from pathlib import Path
from api import canvas_store

_DRAFT_FIRST_NATURES = {"persona", "decision"}          # + class perene (abaixo)
_INSTANCE_PATTERNS = [re.compile(r"canvas_\d"), re.compile(r"\bsession[_-]?id\b", re.I),
                      re.compile(r"\btask_\d"), re.compile(r"(?i)api[_-]?key|secret|token")]

def _store(canvas_id: str) -> Path:
    return canvas_store.tasks_dir() / canvas_id / "colheita.jsonl"

def compute_gate(nature: str, cls: str, source_trust: str) -> str:
    if source_trust == "untrusted":
        return "forced-draft"
    if cls == "perene" or nature in _DRAFT_FIRST_NATURES or nature == "persona":
        return "draft-first"
    return "auto"

def _new_id(cand: dict) -> str:
    seed = f"{cand.get('title','')}|{cand.get('ref') or cand.get('body','')}"
    return "h_" + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]

def ingest_candidate(canvas_id: str, cand: dict) -> dict:
    cls = cand.get("class", "volátil")
    st = cand.get("source_trust", "agent")
    card = {
        "id": cand.get("id") or _new_id(cand),
        "nature": cand["nature"], "scope": cand.get("scope", ""),
        "title": cand.get("title", ""), "porque": cand.get("porque", ""),
        "ref": cand.get("ref"), "body": cand.get("body"),
        "class": cls, "source_trust": st,
        "gate": compute_gate(cand["nature"], cls, st),
        "status": "pending", "origin": cand.get("origin", "agent"),
    }
    p = _store(canvas_id); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(card, ensure_ascii=False) + "\n")
    return card

def set_status(canvas_id: str, card_id: str, status: str, **extra) -> dict:
    rec = {"id": card_id, "status": status, **extra}
    with _store(canvas_id).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec

def list_cards(canvas_id: str) -> list[dict]:
    p = _store(canvas_id)
    if not p.exists():
        return []
    merged: dict[str, dict] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        cur = merged.get(rec["id"], {})
        cur.update(rec)
        merged[rec["id"]] = cur
    return list(merged.values())

def judge_committed(target_path: str, log_path: str, _validate=None) -> dict:
    """fable-judge mecânico: verifica por execução/diff, nunca lendo relatório."""
    tp, lp = Path(target_path), Path(log_path)
    checks = {"exists": tp.exists(), "frontmatter": False, "clean_portable": False, "logged": False}
    reasons: list[str] = []
    if not checks["exists"]:
        reasons.append(f"arquivo ausente: {target_path}")
        return {"ok": False, "checks": checks, "reasons": reasons}
    body = tp.read_text(encoding="utf-8")
    validate = _validate or _default_validate
    checks["frontmatter"] = bool(validate(str(tp)))
    if not checks["frontmatter"]:
        reasons.append("frontmatter OKF inválido")
    leaks = [pat.pattern for pat in _INSTANCE_PATTERNS if pat.search(body)]
    checks["clean_portable"] = not leaks
    if leaks:
        reasons.append(f"clean-portable: possível vazamento de instância/segredo ({leaks})")
    checks["logged"] = lp.exists() and tp.name in lp.read_text(encoding="utf-8")
    if not checks["logged"]:
        reasons.append("sem entrada no _meta/log.md")
    return {"ok": all(checks.values()), "checks": checks, "reasons": reasons}

def _default_validate(path: str) -> bool:
    """Seam real (substituído em Task 4 pela chamada acervoctl validate-frontmatter)."""
    return True
```

- [ ] **Step 4: Run to verify pass**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_colheita.py -q`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
cd <fork-wt> && git branch --show-current   # collab/canvas-f4
git add api/canvas_colheita.py tests/test_canvas_colheita.py
git commit -m "feat(colheita): harvest tray core + auto-gate + mechanical fable-judge (F4)"
```

---

## Task 4: `api/canvas_colheita.py` — acervoctl wrapper + endpoints + forward dispatch (fork)

Adiciona a camada impura: wrapper `acervoctl` (subprocess, seam `ACERVOCTL_CMD`), os endpoints HTTP, e o forward em `canvas_tarefas.py`. O `preparar` roda `prepare-write` (propose); o `checkout` roda `commit-write` + `judge_committed` (approve→commit). Reusa o room+SSE **clonando o padrão de `api/canvas_sala.py`** (`_room`/`_emit`/`_stream_events`).

**Files:**
- Modify: `api/canvas_colheita.py`
- Modify: `api/canvas_tarefas.py` (topo de `handle_canvas_get` e `handle_canvas_post` — 1 `if path.startswith("/api/canvas/colheita/")` cada, forward; **0 linhas em routes.py**)
- Test: `tests/test_canvas_colheita.py` (append)

**Interfaces:**
- Consumes: `canvas_store.tasks_dir/load_canvas`; padrão de room/SSE de `api/canvas_sala.py` (`_room(cid)`, `_emit(cid, event, payload)`, `_stream_events(handler, cid, since)`); FakeHandler dos testes (ver `tests/test_canvas_sala.py`/`test_canvas_routes.py`).
- Produces:
  - `acervoctl(*args, input_file=None) -> tuple[int, str, str]` — subprocess do CLI resolvido por env `ACERVOCTL_CMD` (default `["python3", "<repo>/scripts/acervoctl.py"]`; em prod aponta pro acervoctl do runtime Hermes).
  - `handle_colheita_get(handler, parsed) -> bool`, `handle_colheita_post(handler, path, body) -> bool`.
  - Endpoints: `GET /list`, `GET /stream`, `POST /adotar`, `POST /preparar`, `POST /checkout`.
  - SSE events: `colheita_candidate|prepared|committed|rejected`.

- [ ] **Step 1: Write the failing tests (endpoints via FakeHandler + fake acervoctl)**

```python
# append to tests/test_canvas_colheita.py
import os
from api import canvas_colheita as C

class FakeHandler:  # mesmo shape usado em test_canvas_routes.py
    def __init__(self): self.status=None; self.headers={}; self._chunks=[]
    def send_response(self, s): self.status=s
    def send_header(self, k, v): self.headers[k]=v
    def end_headers(self): pass
    class _W:
        def __init__(s, o): s.o=o
        def write(s, b): s.o._chunks.append(b)
    @property
    def wfile(self): return FakeHandler._W(self)
    def body(self): return b"".join(self._chunks).decode("utf-8")

def _fake_acervoctl_ok(monkeypatch, tmp_path):
    """Fake: prepare-write imprime receipt; commit-write escreve o content-file e loga."""
    def fake(args, input_file=None):
        sub = args[0]
        if sub == "prepare-write":
            tgt = tmp_path / "receitas" / "knowledge" / "n.md"
            return 0, json.dumps({"target_path": str(tgt),
                "log_path": str(tmp_path/"receitas"/"_meta"/"log.md"),
                "relative_output": "knowledge/n.md", "source_trust": "agent"}), ""
        if sub == "commit-write":
            # simulate the real commit: read content, write target, append log
            rec = json.loads([a for i,a in enumerate(args) if args[i-1]=="--receipt"][0]) \
                  if "--receipt" in args else {}
            # in the real path we pass --receipt <file>; the fake reads content-file arg
            cf = args[args.index("--content-file")+1]
            tgt = tmp_path/"receitas"/"knowledge"/"n.md"; tgt.parent.mkdir(parents=True, exist_ok=True)
            tgt.write_text(Path(cf).read_text(encoding="utf-8"), encoding="utf-8")
            lg = tmp_path/"receitas"/"_meta"/"log.md"; lg.parent.mkdir(parents=True, exist_ok=True)
            lg.write_text("- CREATED knowledge/n.md\n", encoding="utf-8")
            return 0, json.dumps({"target_path": str(tgt), "log_path": str(lg)}), ""
        if sub == "validate-frontmatter":
            return 0, "{}", ""
        return 1, "", "unknown"
    monkeypatch.setattr(C, "acervoctl", fake)

def test_list_endpoint(acervo, monkeypatch):
    C.ingest_candidate("canvas_x", {"nature":"knowledge","scope":"s","title":"t",
                                    "class":"volátil","source_trust":"agent","origin":"agent"})
    h = FakeHandler()
    from urllib.parse import urlparse
    assert C.handle_colheita_get(h, urlparse("/api/canvas/colheita/list?canvas_id=canvas_x"))
    assert h.status == 200 and json.loads(h.body())[0]["title"] == "t"

def test_adotar_creates_manual_card(acervo):
    h = FakeHandler()
    assert C.handle_colheita_post(h, "/api/canvas/colheita/adotar",
        {"canvas_id":"canvas_x","source_event":{"title":"achado","body":"x"},
         "nature":"decision","scope":"cliente-alfa"})
    assert h.status == 200
    cards = C.list_cards("canvas_x")
    assert cards[0]["origin"] == "manual" and cards[0]["nature"] == "decision"

def test_preparar_then_checkout_commits_and_judges(acervo, tmp_path, monkeypatch):
    _fake_acervoctl_ok(monkeypatch, tmp_path)
    c = C.ingest_candidate("canvas_x", {"nature":"knowledge","scope":"receitas","title":"n",
        "body":"corpo limpo","class":"volátil","source_trust":"agent","origin":"agent"})
    h1 = FakeHandler()
    assert C.handle_colheita_post(h1, "/api/canvas/colheita/preparar", {"canvas_id":"canvas_x"})
    assert C.list_cards("canvas_x")[0]["status"] == "prepared"
    h2 = FakeHandler()
    assert C.handle_colheita_post(h2, "/api/canvas/colheita/checkout",
        {"canvas_id":"canvas_x","mode":"aprovar_tudo",
         "decisions":[{"card_id":c["id"],"action":"aprovar"}]})
    summary = json.loads(h2.body())
    assert summary["committed"] == 1 and summary["items"][0]["judge"]["ok"] is True
    assert C.list_cards("canvas_x")[0]["status"] == "committed"
```

- [ ] **Step 2: Run to verify fail**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_colheita.py -q`
Expected: FAIL — `handle_colheita_get`/`handle_colheita_post`/`acervoctl` não definidos.

- [ ] **Step 3: Implement wrapper + endpoints + frontmatter builder**

Adicionar em `api/canvas_colheita.py` (usar o `_json_response`/leitura de query já usados no módulo canvas; clonar o room+SSE de `api/canvas_sala.py`). Pontos-chave:
- `acervoctl(args, input_file=None)`: resolve `os.environ.get("ACERVOCTL_CMD")` (split) ou default `[sys.executable, str(REPO/"scripts"/"acervoctl.py")]`; roda `subprocess.run`, retorna `(rc, stdout, stderr)`.
- `_build_frontmatter(card) -> str`: monta OKF v0.2 (`schema: acervo/v0.2`, `type`=map nature→type (`knowledge|decision|reflection`→mesmo; `template`/`workflow`→`template`/`workflow`), `title/description/tags/created_at/class/status: active` + tier epistêmico p/ knowledge/decision/reflection: `epistemic: observation`, `confidence: likely`, `sources:[{type: agent-inference, ref: <canvas_id>}]`, `observed_at`, `extraction: agent`). `created_at`/`observed_at` = passados por `_now`/`_today` (seam para teste).
- `POST /preparar`: p/ cada card `pending` → `acervoctl("prepare-write","--microverso",scope,"--nature",nature,"--title",title,"--source-trust",trust,"--receipt-out",<tmp>)`; guarda receipt no card; `set_status(...,"prepared", receipt=…)`; `_emit(cid,"colheita_prepared",card)`.
- `POST /checkout`: p/ cada decisão `aprovar` → escreve `_build_frontmatter+corpo` num tmp content-file (corpo = `ref` lido do arquivo, senão `body`), `acervoctl("commit-write","--receipt",<receipt-file>,"--content-file",<tmp>,"--description",porque[:160],"--class-name",cls,"--source-trust",trust)`; roda `judge_committed(target,log,_validate=lambda p: acervoctl("validate-frontmatter","--path",p)[0]==0)`; `set_status("committed"|"committed_unverified", judge=…)`; `_emit("colheita_committed")`. `rejeitar` → `set_status("rejected")` + `_emit`. Retorna `{committed, unverified, rejected, items:[{card_id, judge}]}`.
- `GET /list` → `_json_response(handler, 200, list_cards(cid))`.
- `GET /stream` → `_stream_events(handler, cid, since)` (clone de canvas_sala).
- `POST /adotar` → `ingest_candidate(cid, {...source_event, nature, scope, origin:"manual"})` + `_emit("colheita_candidate")`.
- `handle_colheita_get/post`: dispatch por sufixo do path; retornam `True` se trataram.

Em `api/canvas_tarefas.py`, no **topo** de `handle_canvas_post` e `handle_canvas_get` (antes dos forwards de curador/sala já existentes):
```python
    if path.startswith("/api/canvas/colheita/"):
        from api.canvas_colheita import handle_colheita_post  # (get no handler GET)
        return handle_colheita_post(handler, path, body)
```

- [ ] **Step 4: Run to verify pass**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_colheita.py tests/test_canvas_routes.py -q`
Expected: PASS (colheita novos + regressão de canvas_routes verde).

- [ ] **Step 5: Commit**

```bash
cd <fork-wt> && git branch --show-current   # collab/canvas-f4
git add api/canvas_colheita.py api/canvas_tarefas.py tests/test_canvas_colheita.py
git commit -m "feat(colheita): acervoctl-backed prepare/checkout endpoints + forward dispatch (F4)"
```

---

## Task 5: bridge `{t:harvest}` no observador da Sala (fork)

O observador da Sala (`api/canvas_sala.py`) já segue `conduct.jsonl`. Ao ver `t:harvest`, roteia para `canvas_colheita.ingest_candidate` (+ `_emit` no room de colheita) em vez de tratar como card `sala_*`. Isso conecta o sinal do agente (Task 2) à bandeja (Task 3/4).

**Files:**
- Modify: `api/canvas_sala.py` (o loop que lê linhas do conduct — `_poll_once`/reducer feed, ver `_read_conduct_lines`)
- Modify: `api/sala_reducer.py` **somente se** o reducer for quem decide o tipo (senão tratar na casca impura `canvas_sala.py`, preferível — mantém o reducer puro sem IO de colheita)
- Test: `tests/test_canvas_sala.py` (append)

**Interfaces:**
- Consumes: `canvas_colheita.ingest_candidate(canvas_id, cand)`; o mapeamento `task_id → canvas_id` (o observer já resolve via `_LAUNCHED`/`launch.yaml`).
- Produces: efeito colateral — linha `{t:harvest}` no conduct vira card na bandeja do `canvas_id` correspondente; **não** gera evento `sala_*`.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_canvas_sala.py
def test_harvest_line_routes_to_colheita(tmp_path, monkeypatch):
    from api import canvas_sala, canvas_colheita, canvas_store
    monkeypatch.setattr(canvas_store, "tasks_dir", lambda: tmp_path / "_tasks")
    (tmp_path/"_tasks"/"canvas_y").mkdir(parents=True)
    captured = []
    monkeypatch.setattr(canvas_colheita, "ingest_candidate",
                        lambda cid, cand: captured.append((cid, cand)) or cand)
    frame = {"t":"harvest","nature":"knowledge","scope":"s","title":"H",
             "porque":"p","body":"b","class":"perene","source_trust":"agent"}
    # feed one conduct frame through the observer's per-line handler for canvas_y
    canvas_sala._handle_conduct_frame("canvas_y", frame)   # helper introduced by this task
    assert captured and captured[0][0] == "canvas_y" and captured[0][1]["nature"] == "knowledge"
```

- [ ] **Step 2: Run to verify fail**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_sala.py::test_harvest_line_routes_to_colheita -q`
Expected: FAIL — `_handle_conduct_frame` inexistente (ou não roteia harvest).

- [ ] **Step 3: Implement the routing**

Em `api/canvas_sala.py`, extrair/adicionar `_handle_conduct_frame(canvas_id, frame)` chamado no loop que hoje passa cada linha ao reducer:
```python
def _handle_conduct_frame(canvas_id: str, frame: dict) -> bool:
    if frame.get("t") == "harvest":
        from api import canvas_colheita
        card = canvas_colheita.ingest_candidate(canvas_id, {**frame, "origin": "agent"})
        canvas_colheita._emit(canvas_id, "colheita_candidate", card)  # room de colheita
        return True   # consumido; não vai ao reducer sala_*
    return False
```
No ponto de leitura das linhas do conduct (onde hoje se chama o reducer), inserir: `if _handle_conduct_frame(cid, frame): continue`.

- [ ] **Step 4: Run to verify pass**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_sala.py -q`
Expected: PASS (novo + regressão da Sala verde).

- [ ] **Step 5: Commit**

```bash
cd <fork-wt> && git branch --show-current   # collab/canvas-f4
git add api/canvas_sala.py tests/test_canvas_sala.py
git commit -m "feat(sala): route conduct {t:harvest} lines into the colheita tray (F4)"
```

---

## Task 6: `api/canvas_receita.py` — clean-portable transform + list + iniciar (fork, núcleo)

Núcleo puro/testável da receita: transforma o canvas em estrutura clean-portable, lista receitas do microverso `receitas`, e cria um canvas novo pré-preenchido a partir de uma receita. A canonização (escrita via acervoctl) entra na Task 7.

**Files:**
- Create: `api/canvas_receita.py`
- Test: `tests/test_canvas_receita.py`

**Interfaces:**
- Consumes: `canvas_store.load_canvas(canvas_id)`, `canvas_store.create_draft(text)` (retorna `{canvas_id, ...}`), `canvas_store.save_canvas(doc)`, `canvas_store.tasks_dir()`.
- Produces (usadas pela Task 7):
  - `clean_portable(doc: dict) -> dict` — remove instância, preserva estrutura.
  - `recipe_body(doc: dict) -> str` — YAML da estrutura clean-portable (corpo da receita).
  - `prefill_from_recipe(recipe: dict) -> dict` — doc de canvas novo semeado.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_canvas_receita.py
import pytest
from api import canvas_receita as R

CANVAS = {
    "canvas_id": "canvas_20260801_abc", "focus": "Renegociar com Cliente Alfa",
    "vetor": "execucao", "shape": "tarefa", "intent_type": "produzir",
    "done_criteria": "ofício aprovado", "verification": "manifest + SHA-256",
    "microversos": {"primary": "cliente-alfa", "related": ["juridico"]},
    "gaps": ["Teto de desconto?", "Prazo de vigência?"],
    "personas": {"suggested": ["redator-institucional"], "explicit": [], "evaluators": ["critico"]},
    "artifacts": {"expected": [{"title": "oficio.docx", "path": "x/oficio.docx", "type": "docx"}]},
    "authorization": [{"action": "enviar email", "words": "pode enviar", "at": "..."}],
    "promotion_candidates": {"knowledge": ["algo instanciado"]},
}

def test_clean_portable_strips_instance_keeps_structure():
    cp = R.clean_portable(CANVAS)
    assert "canvas_id" not in cp
    assert cp["microversos"]["primary"] is None          # vínculo de instância removido
    assert cp.get("authorization", []) == []             # palavras de AUTH removidas
    assert "promotion_candidates" not in cp              # instâncias removidas
    assert cp["vetor"] == "execucao" and cp["shape"] == "tarefa"     # estrutura preservada
    assert cp["verification"] == "manifest + SHA-256"
    assert cp["intake_questions"] == ["Teto de desconto?", "Prazo de vigência?"]  # gaps → intake
    assert cp["personas"]["slots"] == ["redator-institucional", "critico"]

def test_recipe_body_is_yaml_without_secrets():
    body = R.recipe_body(CANVAS)
    assert "canvas_20260801_abc" not in body and "pode enviar" not in body
    assert "vetor: execucao" in body

def test_prefill_from_recipe_seeds_new_canvas():
    cp = R.clean_portable(CANVAS)
    doc = R.prefill_from_recipe({"structure": cp, "focus_template": "Renegociar com <cliente>"})
    assert doc["vetor"] == "execucao" and doc["shape"] == "tarefa"
    assert doc["done_criteria"] == "ofício aprovado"
    assert doc["gaps"] == ["Teto de desconto?", "Prazo de vigência?"]
    assert doc["microversos"]["primary"] is None
```

- [ ] **Step 2: Run to verify fail**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_receita.py -q`
Expected: FAIL — `ModuleNotFoundError: api.canvas_receita`.

- [ ] **Step 3: Implement the pure core**

```python
# api/canvas_receita.py
"""F4 Receita — canvas → receita clean-portable (núcleo puro)."""
import yaml
from api import canvas_store

_STRUCTURE_KEYS = ("vetor", "shape", "intent_type", "done_criteria", "verification")

def clean_portable(doc: dict) -> dict:
    cp: dict = {k: doc.get(k) for k in _STRUCTURE_KEYS if doc.get(k) is not None}
    cp["microversos"] = {"primary": None, "related": list(doc.get("microversos", {}).get("related", []))}
    cp["intake_questions"] = list(doc.get("gaps", []))          # gaps recorrentes viram perguntas de intake
    p = doc.get("personas", {})
    cp["personas"] = {"slots": list(p.get("suggested", [])) + list(p.get("evaluators", []))}
    cp["artifacts_expected"] = [{"title": a.get("title"), "type": a.get("type")}
                                for a in doc.get("artifacts", {}).get("expected", [])]
    # instância removida: canvas_id, focus (nomes próprios), authorization, promotion_candidates, scope, assumptions
    return cp

def recipe_body(doc: dict) -> str:
    return yaml.safe_dump(clean_portable(doc), allow_unicode=True, sort_keys=False)

def prefill_from_recipe(recipe: dict) -> dict:
    cp = recipe["structure"]
    doc = canvas_store._MINIMAL.copy() if hasattr(canvas_store, "_MINIMAL") else {}
    doc = {**doc}
    for k in _STRUCTURE_KEYS:
        if k in cp:
            doc[k] = cp[k]
    doc["gaps"] = list(cp.get("intake_questions", []))
    doc["microversos"] = {"primary": None, "related": list(cp.get("microversos", {}).get("related", []))}
    doc["personas"] = {"suggested": list(cp.get("personas", {}).get("slots", [])), "explicit": [], "evaluators": []}
    doc["focus"] = recipe.get("focus_template", "")
    return doc
```
*(Se `yaml` não estiver disponível no runtime do fork — checar; o fork já lê/escreve canvas.yaml, então PyYAML existe. Se não, usar o mesmo dumper que `canvas_store` usa.)*

- [ ] **Step 4: Run to verify pass**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_receita.py -q`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
cd <fork-wt> && git branch --show-current   # collab/canvas-f4
git add api/canvas_receita.py tests/test_canvas_receita.py
git commit -m "feat(receita): clean-portable canvas→recipe transform + prefill (F4)"
```

---

## Task 7: `api/canvas_receita.py` — canonizar/list/iniciar endpoints + forward dispatch (fork)

Camada impura da receita: `canonizar` (clean-portable → acervoctl prepare→commit no microverso `receitas`), `list` (lê o dir), `iniciar` (cria canvas novo via `prefill_from_recipe`). Reusa o wrapper `acervoctl` da Task 4.

**Files:**
- Modify: `api/canvas_receita.py`
- Modify: `api/canvas_tarefas.py` (forward `if path.startswith("/api/canvas/receita/")` no topo dos handlers GET/POST)
- Test: `tests/test_canvas_receita.py` (append)

**Interfaces:**
- Consumes: `canvas_colheita.acervoctl(...)`; `clean_portable/recipe_body/prefill_from_recipe`; `canvas_store.tasks_dir/load_canvas/save_canvas/create_draft`.
- Produces: `handle_receita_get/post`; endpoints `POST /canonizar`, `GET /list`, `POST /iniciar`; receitas em `micro/receitas/{templates,workflows}/`.

- [ ] **Step 1: Write the failing tests** (FakeHandler + fake acervoctl, mesmos padrões da Task 4)

```python
# append to tests/test_canvas_receita.py
import json
from pathlib import Path
from api import canvas_receita as R
from api import canvas_colheita, canvas_store
from tests.test_canvas_colheita import FakeHandler   # reuse

def test_canonizar_writes_recipe(tmp_path, monkeypatch):
    monkeypatch.setattr(canvas_store, "load_canvas", lambda cid: CANVAS)
    def fake(args, input_file=None):
        if args[0] == "prepare-write":
            tgt = tmp_path/"receitas"/"templates"/"r.md"
            return 0, json.dumps({"target_path": str(tgt),
                "log_path": str(tmp_path/"receitas"/"_meta"/"log.md"),
                "relative_output": "templates/r.md"}), ""
        if args[0] == "commit-write":
            cf = args[args.index("--content-file")+1]
            tgt = tmp_path/"receitas"/"templates"/"r.md"; tgt.parent.mkdir(parents=True, exist_ok=True)
            tgt.write_text(Path(cf).read_text(encoding="utf-8"), encoding="utf-8")
            return 0, json.dumps({"target_path": str(tgt)}), ""
        return 0, "{}", ""
    monkeypatch.setattr(canvas_colheita, "acervoctl", fake)
    h = FakeHandler()
    assert R.handle_receita_post(h, "/api/canvas/receita/canonizar", {"canvas_id":"canvas_x"})
    assert h.status == 200
    written = (tmp_path/"receitas"/"templates"/"r.md").read_text(encoding="utf-8")
    assert "vetor: execucao" in written and "canvas_20260801_abc" not in written

def test_iniciar_creates_prefilled_canvas(monkeypatch):
    monkeypatch.setattr(R, "_load_recipe", lambda rid: {"structure": R.clean_portable(CANVAS),
                                                        "focus_template": "Renegociar com <cliente>"})
    created = {}
    monkeypatch.setattr(canvas_store, "create_draft", lambda text="": {"canvas_id": "canvas_new"})
    monkeypatch.setattr(canvas_store, "save_canvas", lambda doc: created.update(doc))
    h = FakeHandler()
    assert R.handle_receita_post(h, "/api/canvas/receita/iniciar", {"recipe_id":"r1"})
    assert json.loads(h.body())["canvas_id"] == "canvas_new"
    assert created["vetor"] == "execucao" and created["gaps"][0] == "Teto de desconto?"
```

- [ ] **Step 2: Run to verify fail** → `handle_receita_post` inexistente.

- [ ] **Step 3: Implement endpoints**

- `POST /canonizar`: `doc=load_canvas(cid)`; `nature = "workflow" if doc.get("shape")=="plano-primeiro" else "template"`; `title = doc.get("focus","receita")[:80]`; `acervoctl("prepare-write","--microverso","receitas","--nature",nature,"--title",title,"--receipt-out",<tmp>)`; escreve `_build_recipe_frontmatter()+recipe_body(doc)` num content-file; `acervoctl("commit-write","--receipt",<tmp>,"--content-file",<cf>,"--description",title,"--class-name","perene")`; `_json_response(200, {recipe_id, path})`.
- `GET /list`: varre `tasks_dir().parent/"micro"/"receitas"/{templates,workflows}/*.md` (ou o path do acervo montado) → `[{recipe_id, focus_template, vetor, path}]` (lê frontmatter/YAML). `200 []` se ausente (nunca 500).
- `POST /iniciar`: `recipe=_load_recipe(rid)`; `doc=prefill_from_recipe(recipe)`; `nd=create_draft(); doc["canvas_id"]=nd["canvas_id"]; save_canvas(doc)`; `_json_response(200, {"canvas_id": nd["canvas_id"]})`.
- `_build_recipe_frontmatter()`: OKF v0.2 `type: template|workflow`, `epistemic: rule`, `class: perene`, `status: active`, tags `[receita, canvas-tarefas]`.
- Forward em `canvas_tarefas.py` (topo dos handlers): `if path.startswith("/api/canvas/receita/"): from api.canvas_receita import handle_receita_post; return handle_receita_post(handler, path, body)` (e o `_get`).

- [ ] **Step 4: Run to verify pass**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_receita.py tests/test_canvas_routes.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd <fork-wt> && git branch --show-current
git add api/canvas_receita.py api/canvas_tarefas.py tests/test_canvas_receita.py
git commit -m "feat(receita): canonizar/list/iniciar endpoints + forward dispatch (F4)"
```

---

## Task 8a: UI — ilha Colheita + zona no Cockpit (fork)

Ilha vanilla clonada de `static/canvas-sala.js`: `#cvt-colheita-zone`, EventSource em `/api/canvas/colheita/stream`, 1 renderer por card com badge de gate + "diff sob demanda" + controles [Preparar]→[Aprovar tudo|Item a item|Rejeitar]. Ação "colher" nos cards da Sala. Testado por **asserção de fonte** (padrão `tests/test_canvas_ui_c1_source.py`), keyless/sem browser.

**Files:**
- Create: `static/canvas-colheita.js`
- Modify: `static/canvas-tarefas.js` (montar `#cvt-colheita-zone` no `renderCockpit`; expor hook), `static/canvas-tarefas.css` (classes da ilha), `static/canvas-dev.html` (1 `<script src="canvas-colheita.js">`)
- Test: `tests/test_canvas_ui_colheita_source.py` (Create)

**Interfaces:**
- Consumes: `window.CVT.acceptOps/getCanvas/currentCid`; endpoints da Task 4.
- Produces: elemento `#cvt-colheita-zone`; funções JS `renderColheita`, `colherFromSala`, controles de checkout.

- [ ] **Step 1: Write the failing source-assertion test**

```python
# tests/test_canvas_ui_colheita_source.py
from pathlib import Path
JS = Path(__file__).resolve().parents[1] / "static" / "canvas-colheita.js"
TAR = Path(__file__).resolve().parents[1] / "static" / "canvas-tarefas.js"
DEV = Path(__file__).resolve().parents[1] / "static" / "canvas-dev.html"

def test_colheita_island_wires_stream_and_controls():
    js = JS.read_text(encoding="utf-8")
    assert "/api/canvas/colheita/stream" in js
    assert "/api/canvas/colheita/preparar" in js and "/api/canvas/colheita/checkout" in js
    for ev in ("colheita_candidate", "colheita_prepared", "colheita_committed", "colheita_rejected"):
        assert ev in js
    assert "Aprovar tudo" in js and "Item a item" in js and "Rejeitar" in js  # PT-BR
    assert "cvt-colheita-zone" in js

def test_cockpit_mounts_colheita_zone_and_dev_loads_island():
    assert "cvt-colheita-zone" in TAR.read_text(encoding="utf-8")
    assert "canvas-colheita.js" in DEV.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run to verify fail** → arquivos/strings ausentes.

- [ ] **Step 3: Implement the island** (clonar estrutura de `canvas-sala.js`: IIFE, 2ª/4ª `EventSource`, cria/preenche `#cvt-colheita-zone`, renderers por evento, `window.CVT.acceptOps` onde couber; controles chamam `fetch` nos endpoints `preparar`/`checkout`/`adotar`; "diff sob demanda" faz fetch do receipt do card). Montar `#cvt-colheita-zone` no `renderCockpit` de `canvas-tarefas.js` (aditivo, ao lado da zona da Sala). Adicionar classes no `.css`. Adicionar `<script>` no `canvas-dev.html`. **Não tocar zona quente.**

- [ ] **Step 4: Run to verify pass**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_ui_colheita_source.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd <fork-wt> && git branch --show-current
git add static/canvas-colheita.js static/canvas-tarefas.js static/canvas-tarefas.css static/canvas-dev.html tests/test_canvas_ui_colheita_source.py
git commit -m "feat(colheita-ui): harvest tray island + Cockpit zone + checkout controls (F4)"
```

---

## Task 8b: UI — galeria de receitas no Hangar (fork)

`renderHangar()` ganha uma seção "Receitas" que lista `/api/canvas/receita/list`; clicar num card chama `/api/canvas/receita/iniciar` e abre o Cockpit pré-preenchido. Botão "Canonizar sala como receita" no Cockpit → `/api/canvas/receita/canonizar`.

**Files:**
- Modify: `static/canvas-tarefas.js` (`renderHangar` + botão canonizar no Cockpit), `static/canvas-tarefas.css`
- Test: `tests/test_canvas_ui_receita_source.py` (Create)

**Interfaces:**
- Consumes: endpoints da Task 7; `window.CVT.abrirCockpit(canvas_id)`.
- Produces: seção "Receitas" no Hangar; `iniciarDeReceita`, `canonizarReceita`.

- [ ] **Step 1: Write the failing source-assertion test**

```python
# tests/test_canvas_ui_receita_source.py
from pathlib import Path
TAR = Path(__file__).resolve().parents[1] / "static" / "canvas-tarefas.js"

def test_hangar_gallery_and_canonize_wired():
    js = TAR.read_text(encoding="utf-8")
    assert "/api/canvas/receita/list" in js
    assert "/api/canvas/receita/iniciar" in js
    assert "/api/canvas/receita/canonizar" in js
    assert "Receitas" in js and "Canonizar sala como receita" in js  # PT-BR
```

- [ ] **Step 2: Run to verify fail** → strings ausentes.

- [ ] **Step 3: Implement** — em `renderHangar`, após a lista de canvases recentes, fetch `/api/canvas/receita/list` e renderizar cards de receita (click → `iniciarDeReceita(recipe_id)` → `POST /iniciar` → `window.CVT.abrirCockpit(canvas_id)`). No `renderCockpit`, botão "Canonizar sala como receita" → `canonizarReceita(currentCid())`. Aditivo; zona quente intocada.

- [ ] **Step 4: Run to verify pass**

Run: `cd <fork-wt> && .venv/bin/python -m pytest tests/test_canvas_ui_receita_source.py tests/ -q`
Expected: PASS (suíte canvas inteira verde).

- [ ] **Step 5: Commit**

```bash
cd <fork-wt> && git branch --show-current
git add static/canvas-tarefas.js static/canvas-tarefas.css tests/test_canvas_ui_receita_source.py
git commit -m "feat(receita-ui): Hangar recipe gallery + canonize-as-recipe (F4)"
```

---

## Task 9: governança — MOD-017 (fork) + contrato v1.4 + change record (umbrella)

Documentação e superfícies de contrato. Aditivo. Fecha o rastro COLLAB.

**Files:**
- Modify: `hermes-webui/EXOCRTX_MODIFICATIONS.md` (Create MOD-017)
- Modify: `projetob/.harness/contracts/exocortex-hermes-webui.md` (v1.3→v1.4: §(i) Colheita, §(j) Receita, `{t:harvest}` em §(g); atualizar cabeçalho `version`)
- Create: `projetob/.harness/changes/2026-08-01_COLLAB_canvas-f4-colheita.md`

**Interfaces:** nenhuma de código. Verificação = consistência doc↔código.

- [ ] **Step 1:** MOD-017 no catálogo do fork (padrão MOD-014/016): resumo, arquivos novos/modificados, forward dispatch (0 linhas routes.py), rebase-safety, conflito provável, referência ao spec/plano/#130.
- [ ] **Step 2:** Contrato §(i)/§(j) + linha `{t:harvest}` em §(g) + bump de versão no cabeçalho; regra de mudança (aditivo=seguro). Copiar as tabelas de endpoints/eventos do spec §8.
- [ ] **Step 3:** Change record `2026-08-01_COLLAB_canvas-f4-colheita.md` (template COLLAB): pre-flight, mudanças por repo, contract impact (aditivo, v1.4), verification (colar rodapés reais dos pytest das Tasks 1–8b), post-flight, gate ao vivo owner-gated (Task 10).
- [ ] **Step 4: Verify**

Run:
```bash
grep -n "canvas/colheita" projetob/.harness/contracts/exocortex-hermes-webui.md   # §(i) presente
grep -n "canvas/receita" projetob/.harness/contracts/exocortex-hermes-webui.md    # §(j) presente
grep -n '"t":"harvest"\|t:harvest' projetob/.harness/contracts/exocortex-hermes-webui.md
grep -n "MOD-017" hermes-webui/EXOCRTX_MODIFICATIONS.md
```
Expected: todas casam.

- [ ] **Step 5: Commit (3 repos, separados; verificar branch em cada)**

```bash
cd <fork-wt> && git branch --show-current && git add EXOCRTX_MODIFICATIONS.md && git commit -m "docs(mod-017): catalog F4 Colheita & Receita"
cd <umbrella-wt> && git branch --show-current && git add .harness/contracts/exocortex-hermes-webui.md .harness/changes/2026-08-01_COLLAB_canvas-f4-colheita.md && git commit -m "docs(contract): exocortex↔hermes-webui v1.4 — Colheita & Receita surfaces (F4)"
```
*(umbrella: branch `collab/canvas-f4` cortada de `origin/master`, via worktree.)*

---

## Task 10: gate de saída ao vivo (OWNER-GATED)

Não é uma task TDD normal — é o gate de saída da F4, **executado pelo owner** (LLM real; prod :8787 + acervo real INTOCADOS; smoke isolado). Requer merge das branches (owner-gated) + provisionamento das skills calibradas (SOUL cirúrgico, NUNCA step-07 `cp` — ver C0).

- [ ] **Step 1:** Em smoke isolado, 1 frase → sala lançada → execução conduzida em que o agente emite ≥1 `{t:harvest}` (+ ≥1 adoção manual).
- [ ] **Step 2:** Bandeja mostra os cards com badges de gate; **Preparar** gera receipts/diffs.
- [ ] **Step 3:** **Checkout em lote** (aprovar tudo) → `commit-write` grava no acervo; **`_meta/log.md` do container mostra as entradas** (prova bruta EX-49); fable-judge mecânico verde (ou `committed_unverified` explicitados).
- [ ] **Step 4:** **Canonizar como receita** → objeto válido OKF v0.2 em `micro/receitas/`; aparece na galeria do Hangar.
- [ ] **Step 5:** **Iniciar de receita** → canvas novo pré-preenchido renderiza no Cockpit.
- [ ] **Step 6:** Registrar prova (screenshots Playwright + outputs brutos) no change record; atualizar `00-INDEX.md` (F4 gate FECHADO) e o status do contrato. Merge via worktree DETACHED nos tips de origin + push **owner-gated**.

---

## Self-Review (autor)

**Spec coverage:** §4.A→T3/T4; §4.B(fable-judge)→T3; §4.C→T6/T7; §4.D(Hangar)→T8b; §4.E(ilha)→T8a; §5(fluxo)→T4/T7/T10; §6(modelo dados: harvest line→T2, card→T3, receita→T6/T7); §7 item7(acervoctl)→T1; §8(contrato)→T9; §9(gate)→T10; §10(guardrails)→Global Constraints; §11 gap#1→T1(resolvido), gap#2→T4(gate no fork), gap#3(round-trip)→T4 nota, gap#4(nomes próprios)→T6 preserva focus. **OD-F4-1**→T1/T4/T7 (fork orquestra acervoctl). **OD-F4-2**→T2+T4(adotar)+T5. **OD-F4-3**→T3(judge_committed).

**Placeholders:** invocações acervoctl e schemas concretos; onde clono padrão existente (room/SSE de canvas_sala; FakeHandler; UI source-assertion) aponto o arquivo-fonte exato — não é placeholder, é instrução de reuso. Nenhum "TBD/TODO".

**Type consistency:** `ingest_candidate`/`list_cards`/`set_status`/`compute_gate`/`judge_committed` (T3) usados verbatim em T4/T5/T7; `acervoctl(args, input_file=None)` (T4) reusado em T7; `clean_portable`/`recipe_body`/`prefill_from_recipe` (T6) usados em T7; card shape (T3) = §6 do spec.

**Riscos residuais p/ o executor:** (a) confirmar PyYAML no runtime do fork (T6 nota); (b) o path real do acervo montado p/ `receita/list` (T7 Step 3) — resolver via `canvas_store` (mesma raiz de `tasks_dir`); (c) FakeHandler — usar exatamente o shape de `tests/test_canvas_routes.py` (pode divergir do stub aqui); ajustar no RED se necessário.
