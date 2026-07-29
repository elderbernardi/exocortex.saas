# F2 — Curador · Plano de Execução

> **Para workers agênticos:** SUB-SKILL OBRIGATÓRIA: use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para implementar este plano tarefa-a-tarefa. Os passos usam checkbox (`- [ ]`) para rastreio. Um task por vez; cada task termina com o output bruto do comando de verificação (EX-49).

**Goal:** Adicionar um agente paralelo ("Curador") in-process ao Cockpit do Canvas de Tarefas que responde delegações de busca no acervo, sugestão de itens e pesquisa externa devolvendo à Sala **só o artefato destilado citado** (nunca a trilha de busca), com semântica A2A, higiene de contexto provada e cards aceitar/dispensar em 1 clique.

**Architecture:** Registro/transporte **próprio** (`CURADOR_ROOMS` ≠ `CANVAS_JOBS`) + SSE próprio, para que os 3 obstáculos herdados do F1b (stream fecha em `canvas_done`, `_schedule_cleanup` de 300s, Cockpit não reabre) sumam por construção. Protocolo A2A **puro e testável** (`api/curador_a2a.py`: shapes wire-idênticos + máquina de estados como código) alimenta um worker singleton (1 thread por delegação, 1 delegação por vez via lock global + fila FIFO global ordenada). As delegações leem o acervo só via subprocess `acervoctl retrieve/posture` (guardrail read-only estrutural) e o LLM auxiliar (`call_llm(task="curator")`); só o `Artifact` destilado (≤ N tokens) cruza a fronteira SSE.

**Tech Stack:** Python 3.11–3.13 (fork hermes-webui, stdlib-only: `threading`, `collections.deque`, `itertools`, `subprocess`, `json`, `uuid`), pytest (repo-local `.venv` via `./scripts/test.sh`, rede isolada), JS vanilla (IIFE, sem build, sem deps), YAML (PyYAML já é requisito). LLM via `agent.auxiliary_client.call_llm(task="curator")`. Acervo via `acervoctl.py` (subprocess). Alvo de build: branch **`collab/canvas-tarefas`** do fork.

## Global Constraints

Toda task herda estas constraints (valores exatos, uma linha cada):

- **Só executar com este PLANO** — charter não é plano (00-INDEX regra 1).
- **Escopo fechado** — tocar só os arquivos listados na task; precisar de outro arquivo = parar e reportar, nunca expandir em silêncio (regra 2).
- **Zona quente NUNCA tocada** — `hermes-webui/static/{ui,messages,sessions,panels,boot}.js`, `static/style.css`, `static/index.html`, **`api/routes.py`**. O F1b JÁ consumiu o teto de **8 linhas novas** em `routes.py` (2 hooks × 4 linhas: GET L13110-13113, POST L15068-15071 — regra 3), então o **F2 adiciona 0 linhas em `routes.py`**: o Curador é despachado por FORWARD dentro de `api/canvas_tarefas.py` (fork, MOD-013), cujos `handle_canvas_get/post` já recebem TODA requisição `/api/canvas/*` (o hook do F1b em `routes.py` é dispatch incondicional — chama o handler do canvas para toda request; ele casa por path exato internamente e retorna `False` no miss). `canvas-dev.html`/`canvas-tarefas.css` são fork-owned e **não** são zona quente.
- **Zero dependências novas** (pip/npm), **zero build step**, strings de UI em **PT-BR** (regra 4).
- **Prova bruta por task (EX-49)** — toda task termina com o output real do comando de verificação; sem output, não está concluída (regra 5).
- **Bounds fable-method = gatilhos mecânicos** — "3 ciclos falha-conserto na mesma verificação → pare"; "2 buscas sem informação nova → pare e registre a lacuna" (regra 6). v1 = **só bounds-em-código** (contadores mecânicos no worker); as 4 skills `excrtx-conduct-*` ficam para F3.
- **Segredos nunca** em logs/commits/relatórios (chaves mascaradas) — relevante a `pesquisar` (regra 7).
- **`.quarantine/` não existe** — nunca ler/listar/escrever; já é invisível ao `retrieve` (regra 8).
- **Commits pequenos e frequentes** na branch `collab/canvas-tarefas`; mensagens EN, prefixo convencional (`feat:`/`test:`/`docs:`); **nunca `git push`** sem instrução explícita (regra 9).
- **Ações externas** (push, comentário em issue, deploy) só quando a task manda; relatório final cita cada uma (regra 10).
- **ADR-CT-04** — A2A in-process = padrão job+poll (thread daemon + `Condition` + log append-only), não síncrono streamado.
- **ADR-CT-05** — cards proativos em vanilla JS; reavaliar migração à ilha Preact se `canvas-curador.js` cruzar ~900 linhas OU ≥3 stores mutáveis interdependentes.
- **ADR-CT-06** — canvas v0.5: chave canônica `vetor` (não `vector`); campos de documento (`scope[]`/`assumptions[]`/`authorization[]`/`personas`) fora de `_CORE_TO_DOC`/`canvas_schema.py`. F2 não introduz variante própria de schema.
- **Curador NUNCA escreve no acervo** — estrutural: os módulos do Curador importam só verbos de leitura (`retrieve`/`posture`); nenhum import de `prepare_write`/`commit_write`/`new-object`.
- **Single-user, 1 worker por vez** — lock global (`_CURADOR_BUSY`) + fila FIFO global ordenada; UI mostra "Curador ocupado — na fila".
- **Sharing: allow > deny na leitura** — via `retrieve`/`posture` com `--scope`/`--allow-scope`; `sensitivity: restricted` é deny-sempre (nunca contornado). `acervo_validate_scope` é guarda de **escrita** — NÃO se aplica ao Curador (correção ao charter, registrada no contrato).

---

## Decisões travadas (OWNER — refletidas em todo o plano)

- **(a) Topologia = SINGLETON** — Tasks A2A keyed por `contextId=canvas_id`; "1 worker por vez" = lock global estrutural (`_CURADOR_BUSY`).
- **(b) Memória viva v1 = OFF-TRAIL CACHE** em `global/tools/state/curador/capabilities.json` — índice **derivado**, refresh **idempotente**, escrito por uma **rotina de refresh dedicada** (`refresh_capability_cache`), **nunca** pelo caminho de leitura do Curador. O worker **só lê** (`load_capability_card`). `_meta/capabilities.json` canônico por microverso = destino de **GRADUAÇÃO na F4** (fora do escopo F2). O cache vive **fora** da árvore de conhecimento do acervo (`global/tools/state/` = estado de ferramenta, disposable/gitignored) → o guardrail "Curador nunca escreve no acervo" continua válido.
- **(c) fable-method = só bounds-em-código na v1** — contadores mecânicos; skills `excrtx-conduct-*` → F3.
- **(d) Fila = FIFO GLOBAL ORDENADA** — `collections.deque` única de `task_id` em ordem de chegada, drenada sob lock (não dicts por-sala; não corrida de `_drain_next`).
- **(e) Alvo de build = `collab/canvas-tarefas`** (F2 nasce sobre o F1b não-mergeado). **Pré-condição do gate final "sala real": merge/deploy do F1b em `exocortex/stable`** (owner-gated).
- **(+) `pesquisar(tema)`** atrás da flag `CURADOR_ENABLE_PESQUISAR`, construído por ÚLTIMO; fora do caminho crítico do gate.
- **(+) `routes.py` = 0 linhas novas** — o F1b já esgotou o teto de 8 linhas da regra 3 (2 hooks × 4). O Curador é despachado por **forward** dentro de `api/canvas_tarefas.py` (seus handlers já recebem todo `/api/canvas/*` via o dispatch incondicional do F1b em `routes.py`). `routes.py` fica **INTOCADO**; contrato (f) registra "despacho por forward em `canvas_tarefas.py`, `routes.py` intocado".

---

## Estrutura de arquivos

Todos os paths do fork são relativos à worktree de `collab/canvas-tarefas` do repo `hermes-webui`. Paths do exocortex e do umbrella estão marcados.

**Arquivos novos (fork):**
| Arquivo | Responsabilidade |
|---|---|
| `api/curador_a2a.py` | Protocolo A2A **puro** (sem transporte/FS): builders `new_task`/`new_message`/`new_artifact`/`new_part`, leitores alias-tolerantes (`part_kind`/`context_id`), `TaskStore` (keyed por `contextId`), `transition()` máquina 6-estados, `CuradorProtocolError`. |
| `api/canvas_curador.py` | Transporte + worker in-process: `CURADOR_ROOMS`, SSE próprio (`_emit`/`_stream_events`/`_schedule_cleanup`), singleton `_CURADOR_BUSY` + fila FIFO (`_QUEUE`/`_pump`), `_call_llm_curator` (`task="curator"` + seam `CURADOR_LLM_CMD`), bounds mecânicos + `_budget_guard` + ledger de higiene, as 3 skills (`_skill_buscar_acervo`/`_skill_sugerir_itens`/`_skill_pesquisar`), handlers `handle_curador_get/post`, `delegar`. |
| `api/canvas_curador_retrieve.py` | Wrapper **só leitura** do acervo: `_resolve_acervoctl_dir`/`_acervoctl` (cópia do padrão de `acervo_studio_agent.py`), `curador_retrieve`, `curador_posture`. Nenhum verbo de escrita importado. |
| `api/curador_capabilities.py` | Memória viva off-trail: `build_agent_card(slug)` (pura), `refresh_capability_cache(root)` (rotina escritora, off-trail), `load_capability_card(slug)` (leitor do Curador). |
| `static/canvas-curador.js` | Ilha de UI: 2ª `EventSource` (`/api/canvas/curador/stream`), zona "Sugestões do Curador" (container próprio), botão manual "Pedir sugestões" (gatilho canônico), auto-fire best-effort em `canvas_done`, aceitar→`window.CVT.acceptOps`, dispensar client-side, render de `/personas/suggested` + `/acervo_aplicado`. |
| `tests/test_curador_a2a.py` | T1/T2 — protocolo puro + conformance de wire. |
| `tests/test_curador_worker.py` | T3/T4 — FIFO, lock, SSE, handlers, allow_scopes. |
| `tests/test_curador_retrieve.py` | T5 — wrapper de retrieve. |
| `tests/test_curador_bounds.py` | T6 — bounds + budget guard + ledger. |
| `tests/test_curador_skills.py` | T7/T8/T9 — as 3 delegações. |
| `tests/test_curador_capabilities.py` | T10 — AgentCard + cache off-trail. |
| `tests/test_curador_ui_source.py` | T11 — asserção de fonte da ilha JS. |
| `tests/test_curador_doc_extension.py` | T12 — extensão de documento + accept. |
| `tests/test_curador_hygiene.py` | T13 — prova de higiene (invariante + real-pipeline). |
| `tests/fixtures/a2a-shapes.json` | T2 — expectativas-golden do wire A2A. |
| `tests/fixtures/stub_curador_ok.py` | T3+ — stub de LLM do Curador (seam `CURADOR_LLM_CMD`). |
| `tests/fixtures/stub_acervoctl_retrieve.py` | T5+ — stub determinístico de `acervoctl retrieve --json`. |

**Arquivos editados:**
| Arquivo | Edição |
|---|---|
| `api/canvas_tarefas.py` (fork, MOD-013) | **Forward** (T4): `if path.startswith("/api/canvas/curador/"): return handle_curador_*(...)` no topo de `handle_canvas_get`/`handle_canvas_post` — despacha o Curador sem tocar `routes.py`. **`_WHITELIST_RAW`** (T12): `/personas/suggested/*`, `/acervo_aplicado/*`. **NÃO é zona quente** (fork-owned; já editado no F1b/F2). `routes.py` fica intocado. |
| `static/canvas-tarefas.js` (fork, **MOD-012 — edição permitida**) | **2 edições mínimas** (T11): expor `acceptOps`/`getCanvas`/`currentCid` em `window.CVT`; chamar `window.CanvasCurador.onCockpitOpen(cid)` no fim de `abrirCockpit`. |
| `static/canvas-dev.html` (fork — único carregador do Cockpit; NÃO é zona quente) | (T11): adicionar `<script src="/static/canvas-curador.js">` (a `<link>` de `canvas-tarefas.css` já existe). É a página onde o gate "sala real" é verificado. |
| `static/canvas-tarefas.css` (fork-owned; NÃO é `style.css`) | (T11): adicionar as classes da ilha (`cvt-curador-zone`, `cvt-sug`, `cvt-sug-*`). |
| `api/canvas_store.py` (fork) | `_MINIMAL` (T12): adicionar `personas`/`acervo_aplicado`. |
| `acervo/global/templates/harness-v0.4/canvas.yaml` (**exocortex.saas — fonte canônica**) | (T12): adicionar `acervo_aplicado: []` (`personas` já existe no canônico). |
| `.harness/contracts/exocortex-hermes-webui.md` (**umbrella**) | (T14): nova subseção "(f) Curador" + correção `acervo_validate_scope`. |
| `EXOCRTX_MODIFICATIONS.md` (fork) | (T14): novo `[MOD-013]`. |
| `.harness/changes/2026-07-25_COLLAB_curador.md` (**umbrella**) | (T14): change record COLLAB. |

**Comando de teste (todas as tasks):** `./scripts/test.sh tests/test_curador_<x>.py -v` (usa `.venv` repo-local, Python 3.11–3.13, rede isolada). Onde `./scripts/test.sh` não estiver disponível, `.venv/bin/python -m pytest tests/test_curador_<x>.py -v`.

---

## Fase P0 — Protocolo puro (sem transporte, sem I/O)

### Task 1: `api/curador_a2a.py` — shapes A2A + `TaskStore` + máquina de estados

**Files:**
- Create: `api/curador_a2a.py`
- Test: `tests/test_curador_a2a.py`

**Interfaces:**
- Produces (usado por T3+):
  - `CuradorProtocolError(Exception)`
  - `now_iso() -> str`
  - `new_task(*, contextId: str, skill: str, budget_tokens: int) -> dict`
  - `new_message(*, role: str, skill: str, task_id: str, metadata: dict | None = None, text: str | None = None) -> dict`
  - `new_artifact(*, name: str, description: str, data: dict, ops: list | None = None) -> dict`
  - `new_part(kind: str, **fields) -> dict`
  - `part_kind(part: dict) -> str` (aceita `kind` ou alias `type`)
  - `context_id(task: dict) -> str` (aceita `contextId` ou alias `sessionId`)
  - `transition(task: dict, to: str, *, message: dict | None = None) -> None`
  - `is_terminal(task: dict) -> bool`
  - `class TaskStore:` `add(task) -> dict`, `get(task_id) -> dict | None`, `for_context(context_id) -> list[dict]`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_curador_a2a.py
import pytest
from api import curador_a2a as a2a


def test_new_task_shape_e_estado_inicial():
    t = a2a.new_task(contextId="canvas_x", skill="buscar_acervo", budget_tokens=6000)
    assert t["id"].startswith("curador_task_")
    assert t["contextId"] == "canvas_x"
    assert t["status"]["state"] == "submitted"
    assert t["status"]["timestamp"] and t["status"]["message"] is None
    assert t["history"] == [] and t["artifacts"] == []
    assert t["metadata"]["skill"] == "buscar_acervo"
    assert t["metadata"]["budget_tokens"] == 6000
    assert t["metadata"]["attempts"] == 0 and t["metadata"]["empty_lookups"] == 0
    assert t["metadata"]["hygiene"] == {
        "executor_tokens": 0, "curador_internal_tokens": 0, "n_retrieves": 0}


def test_transicao_feliz_submitted_working_completed():
    t = a2a.new_task(contextId="c", skill="buscar_acervo", budget_tokens=6000)
    a2a.transition(t, "working")
    assert t["status"]["state"] == "working"
    a2a.transition(t, "completed")
    assert t["status"]["state"] == "completed" and a2a.is_terminal(t)


def test_transicao_ilegal_levanta():
    t = a2a.new_task(contextId="c", skill="buscar_acervo", budget_tokens=6000)
    with pytest.raises(a2a.CuradorProtocolError):
        a2a.transition(t, "completed")  # submitted -> completed é ilegal


def test_transicao_a_partir_de_terminal_levanta():
    t = a2a.new_task(contextId="c", skill="buscar_acervo", budget_tokens=6000)
    a2a.transition(t, "working")
    a2a.transition(t, "failed", message=a2a.new_message(
        role="agent", skill="buscar_acervo", task_id=t["id"], text="sem hit"))
    assert t["status"]["message"]["parts"][0]["text"] == "sem hit"
    with pytest.raises(a2a.CuradorProtocolError):
        a2a.transition(t, "working")


def test_artifact_e_message_shapes():
    m = a2a.new_message(role="user", skill="buscar_acervo", task_id="tid",
                        metadata={"query": "renegociar"}, text="buscar_acervo")
    assert m["role"] == "user" and m["taskId"] == "tid"
    assert m["parts"][0]["kind"] == "text" and m["parts"][0]["text"] == "buscar_acervo"
    assert m["metadata"]["skill"] == "buscar_acervo" and m["metadata"]["query"] == "renegociar"
    art = a2a.new_artifact(name="sugestao", description="d",
                           data={"tipo": "buscar_acervo", "path": "micro/x/k.md"},
                           ops=[{"op": "add", "path": "/next_moves/-", "value": "v"}])
    assert art["parts"][0]["kind"] == "data"
    assert art["parts"][0]["data"]["path"] == "micro/x/k.md"
    assert art["metadata"]["ops"][0]["path"] == "/next_moves/-"


def test_taskstore_keyed_por_context():
    store = a2a.TaskStore()
    a = store.add(a2a.new_task(contextId="c1", skill="buscar_acervo", budget_tokens=1))
    b = store.add(a2a.new_task(contextId="c1", skill="sugerir_itens", budget_tokens=1))
    store.add(a2a.new_task(contextId="c2", skill="pesquisar", budget_tokens=1))
    assert store.get(a["id"]) is a
    ids = {t["id"] for t in store.for_context("c1")}
    assert ids == {a["id"], b["id"]}


def test_leitores_alias_tolerantes():
    assert a2a.part_kind({"type": "data"}) == "data"       # alias
    assert a2a.part_kind({"kind": "text"}) == "text"       # canônico
    assert a2a.context_id({"sessionId": "s"}) == "s"       # alias
    assert a2a.context_id({"contextId": "c"}) == "c"       # canônico
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_a2a.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'api.curador_a2a'`.

- [ ] **Step 3: Write minimal implementation**

```python
# api/curador_a2a.py
"""EXCRTX MOD-013 (F2) — contrato A2A puro do Curador (sem transporte, sem I/O).

Shapes wire-idênticos ao A2A para upgrade futuro a HTTP real (nota de honestidade):
estados compostos HIFENIZADOS ("input-required"), Part.kind (alias "type" tolerado
na leitura), contextId (alias sessionId tolerado na leitura), ids opacos e estáveis.
Antes de qualquer upgrade HTTP, revalidar contra o spec.json A2A então corrente
(o teste de conformance em tests/test_curador_a2a.py é o guarda anti-drift)."""
from __future__ import annotations

import datetime
import uuid


class CuradorProtocolError(Exception):
    """Transição de estado ilegal na Task do Curador."""


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# Máquina de estados como CÓDIGO (não convenção). 3 exercitados em F2
# (submitted/working/completed|failed); input-required/canceled reservados
# (compat de schema + F3), nenhum código de F2 transiciona para eles.
_VALID = {
    "submitted": {"working"},
    "working": {"completed", "failed"},
    "input-required": {"working"},   # reservado (F3)
    "completed": set(),
    "failed": set(),
    "canceled": set(),
}
_TERMINAL = {"completed", "failed", "canceled"}


def new_task(*, contextId: str, skill: str, budget_tokens: int) -> dict:
    return {
        "id": "curador_task_" + uuid.uuid4().hex,
        "contextId": contextId,
        "status": {"state": "submitted", "timestamp": now_iso(), "message": None},
        "history": [],
        "artifacts": [],
        "metadata": {
            "skill": skill,
            "budget_tokens": budget_tokens,
            "attempts": 0,
            "empty_lookups": 0,
            "hygiene": {"executor_tokens": 0, "curador_internal_tokens": 0,
                        "n_retrieves": 0},
        },
    }


def new_part(kind: str, **fields) -> dict:
    part = {"kind": kind}
    part.update(fields)
    return part


def new_message(*, role: str, skill: str, task_id: str,
                metadata: dict | None = None, text: str | None = None) -> dict:
    return {
        "role": role,
        "parts": [new_part("text", text=text if text is not None else skill)],
        "messageId": uuid.uuid4().hex,
        "taskId": task_id,
        "metadata": {"skill": skill, **(metadata or {})},
    }


def new_artifact(*, name: str, description: str, data: dict,
                 ops: list | None = None) -> dict:
    return {
        "artifactId": uuid.uuid4().hex,
        "name": name,
        "description": description,
        "parts": [new_part("data", data=data)],
        "metadata": {"ops": list(ops or [])},
    }


def part_kind(part: dict) -> str:
    """kind canônico; tolera o alias 'type' de revisões A2A antigas."""
    return part.get("kind") or part.get("type") or ""


def context_id(task: dict) -> str:
    """contextId canônico; tolera o alias 'sessionId'."""
    return task.get("contextId") or task.get("sessionId") or ""


def is_terminal(task: dict) -> bool:
    return task["status"]["state"] in _TERMINAL


def transition(task: dict, to: str, *, message: dict | None = None) -> None:
    frm = task["status"]["state"]
    if to not in _VALID.get(frm, set()):
        raise CuradorProtocolError(f"transição inválida: {frm} → {to}")
    task["status"] = {"state": to, "timestamp": now_iso(), "message": message}


class TaskStore:
    """Store em memória, keyed por id; consultável por contextId=canvas_id."""

    def __init__(self) -> None:
        self._tasks: dict[str, dict] = {}

    def add(self, task: dict) -> dict:
        self._tasks[task["id"]] = task
        return task

    def get(self, task_id: str) -> dict | None:
        return self._tasks.get(task_id)

    def for_context(self, context_id_val: str) -> list[dict]:
        return [t for t in self._tasks.values() if t["contextId"] == context_id_val]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_a2a.py -v`
Expected: PASS — 7 passed (os testes de conformance de T2 ainda não existem).

- [ ] **Step 5: Commit**

```bash
cd <fork-worktree> && git checkout collab/canvas-tarefas
git add api/curador_a2a.py tests/test_curador_a2a.py
git commit -m "feat(curador): pure A2A protocol module (shapes + TaskStore + state machine)"
```

**Prova EX-49:** output de `./scripts/test.sh tests/test_curador_a2a.py -v` (7 passed) demonstra que os shapes serializam no formato correto e que `transition()` levanta em transição ilegal — a máquina de estados é código verificável, não convenção.

---

### Task 2: Conformance de wire-format contra `tests/fixtures/a2a-shapes.json`

**Files:**
- Create: `tests/fixtures/a2a-shapes.json`
- Modify: `tests/test_curador_a2a.py` (adiciona a classe de conformance)

**Interfaces:**
- Consumes: tudo de T1 (`api.curador_a2a`).
- Produces: guarda anti-drift — nenhuma API nova.

- [ ] **Step 1: Write the failing test**

Adicionar ao fim de `tests/test_curador_a2a.py`:

```python
import json
import pathlib


def _shapes():
    p = pathlib.Path(__file__).parent / "fixtures" / "a2a-shapes.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_conformance_estados_hifenizados():
    spec = _shapes()
    assert set(a2a._VALID.keys()) == set(spec["task_states"])
    for composto in spec["hyphenated_states"]:
        assert composto in a2a._VALID          # hifenizado, nunca underscore
        assert composto.replace("-", "_") not in a2a._VALID


def test_conformance_campos_obrigatorios():
    spec = _shapes()
    t = a2a.new_task(contextId="c", skill="buscar_acervo", budget_tokens=1)
    assert set(spec["task_required_fields"]).issubset(t.keys())
    assert set(spec["status_required_fields"]).issubset(t["status"].keys())
    m = a2a.new_message(role="user", skill="buscar_acervo", task_id=t["id"])
    assert set(spec["message_required_fields"]).issubset(m.keys())
    art = a2a.new_artifact(name="n", description="d", data={"tipo": "x"})
    assert set(spec["artifact_required_fields"]).issubset(art.keys())


def test_conformance_part_kind_e_context_id_canonicos():
    spec = _shapes()
    t = a2a.new_task(contextId="c", skill="buscar_acervo", budget_tokens=1)
    art = a2a.new_artifact(name="n", description="d", data={"tipo": "x"})
    assert a2a.part_kind(art["parts"][0]) in spec["part_kinds"]
    assert "kind" in art["parts"][0]           # emitimos "kind" canônico
    assert "contextId" in t                     # emitimos "contextId" canônico
    assert "sessionId" not in t
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_a2a.py::test_conformance_estados_hifenizados -v`
Expected: FAIL — `FileNotFoundError` (`a2a-shapes.json` ausente).

- [ ] **Step 3: Write the fixture**

```json
{
  "task_states": ["submitted", "working", "input-required", "completed", "failed", "canceled"],
  "hyphenated_states": ["input-required"],
  "part_kinds": ["text", "data"],
  "task_required_fields": ["id", "contextId", "status", "history", "artifacts", "metadata"],
  "status_required_fields": ["state", "timestamp", "message"],
  "message_required_fields": ["role", "parts", "messageId", "taskId", "metadata"],
  "artifact_required_fields": ["artifactId", "name", "description", "parts", "metadata"]
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_a2a.py -v`
Expected: PASS — 10 passed (7 de T1 + 3 de conformance).

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/a2a-shapes.json tests/test_curador_a2a.py
git commit -m "test(curador): A2A wire-format conformance guard (hyphenated states, kind, contextId)"
```

**Prova EX-49:** output `10 passed` — o guarda falha se alguém trocar `input-required`→`input_required`, `kind`→`type`, ou `contextId`→`sessionId`, protegendo o upgrade HTTP futuro.

---

## Fase P1 — Substrato do worker (transporte isolado)

### Task 3: `api/canvas_curador.py` — registro próprio, singleton, fila FIFO global, LLM auxiliar

**Files:**
- Create: `api/canvas_curador.py`
- Create: `tests/test_curador_worker.py`
- Create: `tests/fixtures/stub_curador_ok.py`

**Interfaces:**
- Consumes: `api.curador_a2a` (T1); `api.canvas_store.{acervo_root,load_canvas}` (F1b); `api.profiles.{get_active_profile_name,profile_env_for_background_worker}` (F1b substrate); `agent.auxiliary_client.call_llm` (runtime).
- Produces (usado por T4+):
  - `CURADOR_ROOMS: dict[str, dict]`, `_STORE: TaskStore`
  - `_CURADOR_BUSY: threading.Lock`, `_QUEUE: collections.deque`, `_QLOCK: threading.Lock`, `_SEQ`
  - `RETRIEVE_BUDGET=6000`, `POSTURE_BUDGET=12000`
  - `_SKILLS: dict[str, callable]` (registry preenchido em T7/T8/T9)
  - `_room(cid: str) -> dict`, `_emit(cid, name, payload) -> None`, `_schedule_cleanup(cid) -> None`
  - `_call_llm_curator(prompt: str) -> str`
  - `_run_skill(task) -> tuple[dict | None, str | None]` (retorna `(artifact, gap_reason)`, exatamente um não-None)
  - `_pump() -> None`, `_run_curador(task_id: str) -> None`
  - `delegar(canvas_id, kind, *, query=None, escopo=None, tema=None, allow_scopes=None) -> str`

> **Nota de FIFO (decisão d, achado I2):** a ordem é garantida por uma **`collections.deque` global única** de `task_id` em ordem de chegada, drenada por `_pump()` sob `_QLOCK`. `_pump()` só spawna um worker se conseguir `_CURADOR_BUSY.acquire(blocking=False)` **e** houver item na deque; ao terminar, `_run_curador` faz `release()` + `_pump()` no `finally`. Como enfileirar (append no tail) e drenar (popleft no head) passam pelo mesmo `_QLOCK`, uma delegação nova nunca "fura" uma já enfileirada — FIFO real, não best-effort.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_curador_worker.py
import threading
import time
import pytest

from api import canvas_curador, curador_a2a as a2a


@pytest.fixture()
def curador_env(tmp_path, monkeypatch):
    (tmp_path / "micro/comercial").mkdir(parents=True)
    (tmp_path / "_tasks").mkdir()
    monkeypatch.setenv("ACERVO", str(tmp_path))
    # canvas mínimo em disco p/ handle_curador_post validar load_canvas (T4)
    monkeypatch.setattr(canvas_curador.canvas_store, "load_canvas",
                        lambda cid: {"canvas_id": cid, "microversos": {"primary": "comercial"}})
    # estado de módulo limpo entre testes
    canvas_curador.CURADOR_ROOMS.clear()
    canvas_curador._STORE = a2a.TaskStore()
    canvas_curador._QUEUE.clear()
    if canvas_curador._CURADOR_BUSY.locked():
        canvas_curador._CURADOR_BUSY.release()
    return tmp_path


def _wait_state(task_id, state, timeout=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        t = canvas_curador._STORE.get(task_id)
        if t and t["status"]["state"] == state:
            return t
        time.sleep(0.01)
    raise AssertionError(f"{task_id} não chegou a {state}")


def _ok_skill(task):
    return (a2a.new_artifact(name="n", description="d",
            data={"tipo": task["metadata"]["skill"], "path": "micro/comercial/knowledge/k.md",
                  "query": task["metadata"]["args"].get("query")}), None)


def test_fifo_ordem_a_b_c(curador_env, monkeypatch):
    ordem = []
    gate = threading.Event()

    def slow_skill(task):
        gate.wait(timeout=2)               # segura o 1º worker até liberarmos
        ordem.append(task["metadata"]["args"]["query"])
        return _ok_skill(task)

    monkeypatch.setattr(canvas_curador, "_run_skill", slow_skill)
    ids = [canvas_curador.delegar("canvas_x", "buscar_acervo", query=q)
           for q in ("A", "B", "C")]
    # A já está em working (segurado no gate); B e C esperam na fila
    _wait_state(ids[0], "working")
    assert canvas_curador._STORE.get(ids[1])["status"]["state"] == "submitted"
    assert canvas_curador._STORE.get(ids[2])["status"]["state"] == "submitted"
    gate.set()
    for tid in ids:
        _wait_state(tid, "completed")
    assert ordem == ["A", "B", "C"]        # FIFO real


def test_um_worker_por_vez(curador_env, monkeypatch):
    concorrentes = {"max": 0, "cur": 0}
    lk = threading.Lock()
    rel = threading.Event()

    def counting_skill(task):
        with lk:
            concorrentes["cur"] += 1
            concorrentes["max"] = max(concorrentes["max"], concorrentes["cur"])
        rel.wait(timeout=2)
        with lk:
            concorrentes["cur"] -= 1
        return _ok_skill(task)

    monkeypatch.setattr(canvas_curador, "_run_skill", counting_skill)
    ids = [canvas_curador.delegar("c", "buscar_acervo", query=str(i)) for i in range(3)]
    _wait_state(ids[0], "working")
    rel.set()
    for tid in ids:
        _wait_state(tid, "completed")
    assert concorrentes["max"] == 1


def test_lock_liberado_em_excecao(curador_env, monkeypatch):
    monkeypatch.setattr(canvas_curador, "_run_skill",
                        lambda task: (_ for _ in ()).throw(RuntimeError("boom")))
    tid = canvas_curador.delegar("c", "buscar_acervo", query="q")
    _wait_state(tid, "failed")
    assert not canvas_curador._CURADOR_BUSY.locked()


def test_sugestao_emitida_e_completed(curador_env, monkeypatch):
    monkeypatch.setattr(canvas_curador, "_run_skill", _ok_skill)
    tid = canvas_curador.delegar("c", "buscar_acervo", query="renegociar")
    _wait_state(tid, "completed")
    nomes = [n for n, _ in canvas_curador.CURADOR_ROOMS["c"]["events"]]
    assert "curador_sugestao" in nomes


def test_gap_emitido_e_failed(curador_env, monkeypatch):
    monkeypatch.setattr(canvas_curador, "_run_skill",
                        lambda task: (None, "não encontrei após 2 buscas"))
    tid = canvas_curador.delegar("c", "buscar_acervo", query="x")
    _wait_state(tid, "failed")
    eventos = dict(canvas_curador.CURADOR_ROOMS["c"]["events"])
    assert "curador_gap" in [n for n, _ in canvas_curador.CURADOR_ROOMS["c"]["events"]]
    gap = eventos["curador_gap"]
    assert gap["ops"][0]["path"] == "/gaps/-"


def test_call_llm_curator_usa_seam(curador_env, monkeypatch):
    monkeypatch.setenv("CURADOR_LLM_CMD", "printf 'resposta-do-stub'")
    assert canvas_curador._call_llm_curator("prompt qualquer") == "resposta-do-stub"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_worker.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'api.canvas_curador'`.

- [ ] **Step 3: Write minimal implementation**

```python
# api/canvas_curador.py
"""EXCRTX MOD-013 (F2) — Curador: transporte in-process + worker singleton.

Registro PRÓPRIO (CURADOR_ROOMS ≠ CANVAS_JOBS do enquadrador): ids, ciclo de vida
e transporte independentes — é o que faz os 3 obstáculos herdados do F1b
(stream fecha em canvas_done; _schedule_cleanup de 300s; Cockpit não reabre)
sumirem por construção. Singleton (1 worker/vez) via _CURADOR_BUSY + fila FIFO
global ordenada (_QUEUE, drenada por _pump sob _QLOCK). Só o Artifact destilado
cruza a fronteira SSE (higiene P11)."""
from __future__ import annotations

import collections
import itertools
import json
import logging
import os
import subprocess
import threading
from urllib.parse import parse_qs

from api import canvas_store
from api import curador_a2a as a2a
from api.curador_a2a import TaskStore, new_message, new_task, transition

logger = logging.getLogger("canvas_curador")

RETRIEVE_BUDGET = 6000     # default do acervoctl retrieve
POSTURE_BUDGET = 12000     # default do acervoctl posture
_CLEANUP_DELAY = 300.0     # s — coleta a sala muito tempo após inatividade

CURADOR_ROOMS: dict[str, dict] = {}
_ROOMS_LOCK = threading.Lock()

_STORE = TaskStore()
_CURADOR_BUSY = threading.Lock()          # singleton: 1 worker por vez
_QUEUE: collections.deque[str] = collections.deque()   # FIFO global de task_id
_QLOCK = threading.Lock()                 # protege _QUEUE + handoff do busy
_SEQ = itertools.count()

# Registry de skills — preenchido por T7/T8/T9 (buscar_acervo/sugerir_itens/pesquisar).
_SKILLS: dict[str, callable] = {}


def _j(handler, obj, status=200):
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _room(cid: str) -> dict:
    with _ROOMS_LOCK:
        room = CURADOR_ROOMS.get(cid)
        if room is None:
            room = {"events": [], "cond": threading.Condition()}
            CURADOR_ROOMS[cid] = room
        return room


def _emit(cid: str, name: str, payload) -> None:
    """Anexa um evento ao log da sala e acorda streams abertos. Append-only —
    quem lê controla o próprio cursor (replay ilimitado)."""
    room = _room(cid)
    with room["cond"]:
        room["events"].append((name, payload))
        room["cond"].notify_all()


def _schedule_cleanup(cid: str) -> None:
    def _sweep():
        with _ROOMS_LOCK:
            room = CURADOR_ROOMS.get(cid)
            # só derruba se não há Task não-terminal para esta sala
            live = [t for t in _STORE.for_context(cid) if not a2a.is_terminal(t)]
            if room is not None and not live:
                CURADOR_ROOMS.pop(cid, None)

    t = threading.Timer(_CLEANUP_DELAY, _sweep)
    t.daemon = True
    t.start()


def _call_llm_seam(cmd: str, prompt: str) -> str:
    proc = subprocess.run(cmd, shell=True, input=prompt.encode("utf-8"),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(
            f"CURADOR_LLM_CMD exit {proc.returncode}: "
            f"{proc.stderr.decode('utf-8', 'replace')[-200:]}")
    return proc.stdout.decode("utf-8", "replace")


def _call_llm_curator(prompt: str) -> str:
    """Turno LLM no role AUXILIAR (task='curator', slot já em AUXILIARY_TASK_CATALOG
    — zero mudança de schema/config). Seam CURADOR_LLM_CMD para teste/dev (próprio,
    não reusa CANVAS_LLM_CMD do enquadrador)."""
    cmd = os.environ.get("CURADOR_LLM_CMD")
    if cmd:
        return _call_llm_seam(cmd, prompt)
    from api import profiles as profiles_api
    active = profiles_api.get_active_profile_name() or "default"
    with profiles_api.profile_env_for_background_worker(
            active, "canvas curador", logger_override=logger):
        from agent.auxiliary_client import call_llm
        resp = call_llm(task="curator",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0)
        return resp.choices[0].message.content or ""


def _run_skill(task) -> tuple[dict | None, str | None]:
    """Dispatch por skill via registry. Retorna (artifact, gap_reason); exatamente
    um não-None. As skills reais são registradas em _SKILLS por T7/T8/T9."""
    fn = _SKILLS.get(task["metadata"]["skill"])
    if fn is None:
        return (None, f"skill não registrada: {task['metadata']['skill']}")
    return fn(task)


def _pump() -> None:
    """Drena a próxima Task submitted em ordem FIFO, respeitando o singleton.
    claim + popleft + spawn são atômicos sob _QLOCK."""
    with _QLOCK:
        if not _QUEUE:
            return
        if not _CURADOR_BUSY.acquire(blocking=False):
            return  # um worker roda; ele re-pumpa no finally
        task_id = _QUEUE.popleft()
    threading.Thread(target=_run_curador, args=(task_id,), daemon=True).start()


def _run_curador(task_id: str) -> None:
    task = _STORE.get(task_id)
    cid = task["contextId"]
    try:
        transition(task, "working")
        _emit(cid, "curador_status", {"delegacao_id": task_id, "estado": "working"})
        artifact, gap = _run_skill(task)
        if artifact is not None:
            _emit(cid, "curador_sugestao", artifact)
            transition(task, "completed")
            _emit(cid, "curador_status", {"delegacao_id": task_id, "estado": "completed"})
        else:
            reason = gap or "Curador não encontrou resultado citável"
            ops = [{"op": "add", "path": "/gaps/-", "value": reason}]
            _emit(cid, "curador_gap",
                  {"delegacao_id": task_id, "motivo": reason, "ops": ops})
            transition(task, "failed", message=new_message(
                role="agent", skill=task["metadata"]["skill"], task_id=task_id,
                text=reason))
            _emit(cid, "curador_status", {"delegacao_id": task_id, "estado": "failed"})
    except Exception as exc:  # thread daemon: nunca deixa exceção subir (erro-calmo)
        try:
            if not a2a.is_terminal(task):
                transition(task, "failed")
        except Exception:
            pass
        _emit(cid, "curador_status",
              {"delegacao_id": task_id, "estado": "failed", "erro": str(exc)[-200:]})
    finally:
        _CURADOR_BUSY.release()
        _pump()
        _schedule_cleanup(cid)


def delegar(canvas_id: str, kind: str, *, query=None, escopo=None, tema=None,
            allow_scopes=None) -> str:
    budget = POSTURE_BUDGET if kind == "sugerir_itens" else RETRIEVE_BUDGET
    task = new_task(contextId=canvas_id, skill=kind, budget_tokens=budget)
    task["metadata"]["args"] = {"query": query, "escopo": escopo, "tema": tema,
                                "allow_scopes": list(allow_scopes or [])}
    task["metadata"]["seq"] = next(_SEQ)
    task["history"].append(new_message(
        role="user", skill=kind, task_id=task["id"],
        metadata=task["metadata"]["args"], text=kind))
    _STORE.add(task)
    _room(canvas_id)                        # garante sala p/ o stream anexar
    with _QLOCK:
        _QUEUE.append(task["id"])
    _pump()
    return task["id"]
```

- [ ] **Step 4: Write the LLM stub fixture**

```python
# tests/fixtures/stub_curador_ok.py
#!/usr/bin/env python3
import sys
sys.stdin.read()
print('{"porque": "usado nos 2 últimos ofícios", "resumo": "ok"}')
```

- [ ] **Step 5: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_worker.py -v`
Expected: PASS — 6 passed (FIFO A,B,C; 1-por-vez; lock liberado; sugestão; gap; seam).

- [ ] **Step 6: Commit**

```bash
git add api/canvas_curador.py tests/test_curador_worker.py tests/fixtures/stub_curador_ok.py
git commit -m "feat(curador): in-process worker — own registry, singleton, global FIFO queue, aux LLM"
```

**Prova EX-49:** `test_fifo_ordem_a_b_c` (ordem == [A,B,C]) prova FIFO real (achado I2 dobrado); `test_um_worker_por_vez` (max concorrência == 1) prova o singleton; `test_lock_liberado_em_excecao` prova que o lock nunca vaza.

---

### Task 4: Endpoints SSE + handlers + FORWARD em `canvas_tarefas.py` (routes.py intocado)

**Files:**
- Modify: `api/canvas_curador.py` (adiciona `_stream_events`, `_valid_allow_scopes`, `handle_curador_get`, `handle_curador_post`)
- Modify: `api/canvas_tarefas.py` (**fork, MOD-013 — NÃO é zona quente**: 1 linha de forward no topo de `handle_canvas_get` + 1 no topo de `handle_canvas_post`)
- Modify: `tests/test_curador_worker.py` (adiciona testes de handler/stream + forward)

> **Achado #2 dobrado — `routes.py` = 0 linhas novas:** o F1b já consumiu o teto de 8 linhas da regra 3 (GET L13110-13113 + POST L15068-15071). Verificado que o hook do F1b em `routes.py` é **dispatch incondicional** (`if _canvas_get(handler, parsed): return True` — chama `handle_canvas_get` para TODA requisição; ele casa por path exato internamente e retorna `False` no miss). Logo `/api/canvas/curador/*` já **chega** a `handle_canvas_get`/`handle_canvas_post`. O Curador é despachado por um **forward de 1 linha** no topo de cada handler do canvas — `routes.py` fica **INTOCADO**. `canvas_tarefas.py` é fork-owned e já é editado no F2 (whitelist, T12); o forward é do MOD-013.

**Interfaces:**
- Consumes: `delegar`, `_room`, `_STORE`, `_j`, `canvas_store.acervo_root/load_canvas` (T3/F1b).
- Produces (usado pelo forward de `canvas_tarefas.py` + T11):
  - `_valid_allow_scopes(scopes) -> bool`
  - `_stream_events(handler, room, cursor: int) -> None` (SSE que **não** fecha em evento terminal — só em disconnect; resolve o obstáculo F1b "stream fecha em canvas_done")
  - `handle_curador_get(handler, parsed) -> bool` (tri-valor `True|None|False`)
  - `handle_curador_post(handler, path, body) -> bool`
- Endpoints (contrato (f)):
  - `POST /api/canvas/curador/delegar {canvas_id, kind, query?/tema?, escopo?, allow_scopes?}` → `{delegacao_id}`
  - `GET /api/canvas/curador/stream?canvas_id=&since=N` → SSE re-anexável
  - `GET /api/canvas/curador/job?delegacao_id=` → `{state, empty_lookups, attempts, hygiene}`

- [ ] **Step 1: Write the failing tests**

Adicionar a `tests/test_curador_worker.py`:

```python
import io
import json as _json
from urllib.parse import urlparse


class _OneShotStream:
    """Handler fake p/ SSE: captura frames e aborta o loop após o 1º batch
    (BrokenPipeError no flush quando já há um frame 'event:' escrito)."""
    def __init__(self):
        self._buf = bytearray()
        self.status = None
        self.frames = b""
        outer = self

        class _W:
            def write(self, b):
                outer._buf.extend(b)
            def flush(self):
                outer.frames = bytes(outer._buf)
                if b"event:" in outer.frames:
                    raise BrokenPipeError
        self.wfile = _W()

    def send_response(self, c): self.status = c
    def send_header(self, *a): pass
    def end_headers(self): pass


class FakeHandler:
    def __init__(self):
        self.wfile = io.BytesIO()
        self.status = None
    def send_response(self, c): self.status = c
    def send_header(self, *a): pass
    def end_headers(self): pass


def test_delegar_endpoint_retorna_id(curador_env, monkeypatch):
    monkeypatch.setattr(canvas_curador, "_run_skill",
                        lambda task: (a2a.new_artifact(name="n", description="d",
                                      data={"tipo": "buscar_acervo", "path": "p"}), None))
    h = FakeHandler()
    assert canvas_curador.handle_curador_post(
        h, "/api/canvas/curador/delegar",
        {"canvas_id": "c", "kind": "buscar_acervo", "query": "q"}) is True
    did = _json.loads(h.wfile.getvalue())["delegacao_id"]
    assert did.startswith("curador_task_")


def test_delegar_kind_invalido_400(curador_env):
    h = FakeHandler()
    canvas_curador.handle_curador_post(h, "/api/canvas/curador/delegar",
                                       {"canvas_id": "c", "kind": "nope"})
    assert h.status == 400


def test_pesquisar_desabilitado_por_default_400(curador_env, monkeypatch):
    monkeypatch.delenv("CURADOR_ENABLE_PESQUISAR", raising=False)
    h = FakeHandler()
    canvas_curador.handle_curador_post(h, "/api/canvas/curador/delegar",
                                       {"canvas_id": "c", "kind": "pesquisar", "tema": "x"})
    assert h.status == 400


def test_allow_scopes_validado_server_side(curador_env):
    # 'comercial' existe (fixture criou micro/comercial); 'fantasma' não
    assert canvas_curador._valid_allow_scopes(["comercial"]) is True
    assert canvas_curador._valid_allow_scopes(["fantasma"]) is False
    assert canvas_curador._valid_allow_scopes("comercial") is False
    h = FakeHandler()
    canvas_curador.handle_curador_post(
        h, "/api/canvas/curador/delegar",
        {"canvas_id": "c", "kind": "buscar_acervo", "query": "q",
         "allow_scopes": ["fantasma"]})
    assert h.status == 400


def test_path_desconhecido_retorna_false(curador_env):
    assert canvas_curador.handle_curador_post(FakeHandler(), "/api/outro", {}) is False
    assert canvas_curador.handle_curador_get(
        FakeHandler(), urlparse("/api/outro")) is False


def test_stream_replay_por_cursor(curador_env):
    canvas_curador._emit("c", "curador_status", {"estado": "working"})
    canvas_curador._emit("c", "curador_sugestao", {"path": "p"})
    h = _OneShotStream()
    canvas_curador._stream_events(h, canvas_curador._room("c"), 0)
    assert b"event: curador_status" in h.frames
    assert b"event: curador_sugestao" in h.frames
    assert b"id: 1" in h.frames and b"id: 2" in h.frames


def test_job_endpoint_reporta_estado(curador_env, monkeypatch):
    monkeypatch.setattr(canvas_curador, "_run_skill",
                        lambda task: (a2a.new_artifact(name="n", description="d",
                                      data={"tipo": "buscar_acervo", "path": "p"}), None))
    tid = canvas_curador.delegar("c", "buscar_acervo", query="q")
    _wait_state(tid, "completed")
    h = FakeHandler()
    canvas_curador.handle_curador_get(h, urlparse(f"/api/canvas/curador/job?delegacao_id={tid}"))
    body = _json.loads(h.wfile.getvalue())
    assert body["state"] == "completed" and "hygiene" in body


def test_forward_via_canvas_tarefas(curador_env, monkeypatch):
    # achado #2: /api/canvas/curador/* é despachado pelo forward em canvas_tarefas.py
    # (routes.py intocado). O forward chega ao MESMO módulo canvas_curador.
    from api import canvas_tarefas
    monkeypatch.setattr(canvas_curador, "_run_skill",
                        lambda task: (a2a.new_artifact(name="n", description="d",
                                      data={"tipo": "buscar_acervo", "path": "p"}), None))
    h = FakeHandler()
    assert canvas_tarefas.handle_canvas_post(
        h, "/api/canvas/curador/delegar",
        {"canvas_id": "c", "kind": "buscar_acervo", "query": "q"}) is True
    assert _json.loads(h.wfile.getvalue())["delegacao_id"].startswith("curador_task_")
    # path não-curador ainda cai no handler nativo do canvas (não é forwardado)
    assert canvas_tarefas.handle_canvas_post(FakeHandler(), "/api/outro", {}) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_worker.py::test_delegar_endpoint_retorna_id -v`
Expected: FAIL — `AttributeError: module 'api.canvas_curador' has no attribute 'handle_curador_post'`.

- [ ] **Step 3: Add handlers + stream to `api/canvas_curador.py`**

Anexar ao fim de `api/canvas_curador.py`:

```python
def _valid_allow_scopes(scopes) -> bool:
    """Firewall de sharing validado SERVER-SIDE (achado M3): cada allow_scope tem
    de ser um microverso conhecido em disco. A única invariante estrutural é
    sensitivity:restricted (deny-sempre, dentro do retrieve); cross-scope é
    decisão do chamador single-user. Nunca confia na lista do cliente."""
    if not isinstance(scopes, list):
        return False
    try:
        micro = canvas_store.acervo_root() / "micro"
        known = {p.name for p in micro.iterdir()
                 if p.is_dir() and not p.name.startswith(("_", "."))} if micro.is_dir() else set()
    except Exception:
        known = set()
    return all(isinstance(s, str) and s in known for s in scopes)


def _stream_events(handler, room: dict, cursor: int) -> None:
    """SSE re-anexável. Diferente do enquadrador, NÃO fecha em evento terminal —
    a sala do Curador serve N delegações ao longo da sessão; o stream só encerra
    quando o cliente desconecta. Resolve o obstáculo F1b 'stream fecha em canvas_done'."""
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
            for name, payload in pending:
                cursor += 1
                data = json.dumps(payload, ensure_ascii=False)
                handler.wfile.write(
                    f"id: {cursor}\nevent: {name}\ndata: {data}\n\n".encode("utf-8"))
                handler.wfile.flush()
    except (BrokenPipeError, ConnectionResetError):
        pass


def handle_curador_post(handler, path, body) -> bool:
    if path != "/api/canvas/curador/delegar":
        return False
    cid = body.get("canvas_id") or ""
    kind = body.get("kind") or ""
    if kind not in ("buscar_acervo", "sugerir_itens", "pesquisar"):
        _j(handler, {"error": "kind inválido"}, 400)
        return True
    if kind == "pesquisar" and os.environ.get("CURADOR_ENABLE_PESQUISAR") != "1":
        _j(handler, {"error": "pesquisar desabilitado (CURADOR_ENABLE_PESQUISAR)"}, 400)
        return True
    allow = body.get("allow_scopes") or []
    if not _valid_allow_scopes(allow):
        _j(handler, {"error": "allow_scopes inválido"}, 400)
        return True
    try:
        canvas_store.load_canvas(cid)
    except Exception:
        _j(handler, {"error": "canvas desconhecido"}, 404)
        return True
    did = delegar(cid, kind, query=body.get("query"), escopo=body.get("escopo"),
                  tema=body.get("tema"), allow_scopes=allow)
    _j(handler, {"delegacao_id": did})
    return True


def handle_curador_get(handler, parsed) -> bool:
    if parsed.path == "/api/canvas/curador/stream":
        qs = parse_qs(parsed.query)
        cid = (qs.get("canvas_id") or [""])[0]
        try:
            cursor = int((qs.get("since") or ["0"])[0])
        except (TypeError, ValueError):
            cursor = 0
        if cursor < 0:
            cursor = 0
        _stream_events(handler, _room(cid), cursor)
        return True
    if parsed.path == "/api/canvas/curador/job":
        qs = parse_qs(parsed.query)
        did = (qs.get("delegacao_id") or [""])[0]
        task = _STORE.get(did)
        if task is None:
            _j(handler, {"error": "delegação desconhecida"}, 404)
            return True
        m = task["metadata"]
        _j(handler, {"state": task["status"]["state"],
                     "empty_lookups": m.get("empty_lookups", 0),
                     "attempts": m.get("attempts", 0),
                     "hygiene": m.get("hygiene", {})})
        return True
    return False
```

- [ ] **Step 4: Add the FORWARD to `api/canvas_tarefas.py` (routes.py intocado)**

Em `api/canvas_tarefas.py`, no topo de `handle_canvas_post` (L278, antes de `if path == "/api/canvas/patch":`), inserir:

```python
    if path.startswith("/api/canvas/curador/"):   # MOD-013 (F2): forward ao Curador
        from api.canvas_curador import handle_curador_post
        return handle_curador_post(handler, path, body)
```

Em `api/canvas_tarefas.py`, no topo de `handle_canvas_get` (L363, antes de `if parsed.path == "/api/canvas/get":`), inserir:

```python
    if parsed.path.startswith("/api/canvas/curador/"):   # MOD-013 (F2): forward ao Curador
        from api.canvas_curador import handle_curador_get
        return handle_curador_get(handler, parsed)
```

> Import tardio (lazy) evita ciclo: `canvas_curador` importa `canvas_store`/`curador_a2a`/`curador_capabilities`/`canvas_curador_retrieve` — nunca `canvas_tarefas`. O forward vive em `canvas_tarefas.py` (fork, MOD-013), **`routes.py` = 0 linhas novas**. Os handlers do canvas já recebem toda requisição `/api/canvas/*` (dispatch incondicional do F1b em `routes.py`), então o prefixo `/api/canvas/curador/` é despachado sem tocar a zona quente.

- [ ] **Step 5: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_worker.py -v`
Expected: PASS — 14 passed (6 de T3 + 8 de T4, incl. o forward via `canvas_tarefas`).

- [ ] **Step 6: Commit**

```bash
git add api/canvas_curador.py api/canvas_tarefas.py tests/test_curador_worker.py
git commit -m "feat(curador): SSE stream + delegate/job handlers + canvas_tarefas forward (routes.py untouched) + server-side allow_scopes"
```

**Prova EX-49:** `test_forward_via_canvas_tarefas` (delegar via `canvas_tarefas.handle_canvas_post` retorna `{delegacao_id}`) prova o despacho com `routes.py` intocado (achado #2); `test_stream_replay_por_cursor` (frames `id: 1`/`id: 2`) prova o SSE re-anexável; `test_allow_scopes_validado_server_side` (400 em `fantasma`) prova o firewall server-side (M3).

---

## Fase P2 — Acesso read-only ao acervo + bounds mecânicos

### Task 5: `api/canvas_curador_retrieve.py` — wrapper só-leitura de `acervoctl retrieve/posture`

**Files:**
- Create: `api/canvas_curador_retrieve.py`
- Create: `tests/test_curador_retrieve.py`
- Create: `tests/fixtures/stub_acervoctl_retrieve.py`

**Interfaces:**
- Produces (usado por T7/T8):
  - `_resolve_acervoctl_dir() -> str | None`
  - `_acervoctl(scripts_dir: str, args: list[str]) -> subprocess.CompletedProcess`
  - `curador_retrieve(query: str, scope: str, *, budget: int = 6000, k: int = 5, allow_scopes=()) -> dict`
  - `curador_posture(query: str, scope: str, *, mode: str = "decision", budget: int = 12000, k: int = 8, allow_scopes=()) -> dict`
  - Ambos retornam o JSON parseado da saída do `acervoctl` (que `main()` sempre imprime via `print_json`, sem precisar de `--json`): `{found, items[], citations[], total_tokens, ...}`. Abstenção (`found=false`) **não** é erro. Seam de teste: env `CURADOR_ACERVOCTL_CMD` (override do binário) — permite stub determinístico sem chave real.

> **Achado #1 dobrado — sem `--json`:** verificado em `scripts/acervoctl.py` que o subparser `posture` (L409-417) **não** declara `--json` (passá-lo → `argparse` exit 2) e que `retrieve` (L385-397) só o aceita "por compatibilidade de contrato"; `main()` (L524-530) faz `print_json(payload)` incondicionalmente. Por isso `_run` **não** anexa `--json` — o shape `{found/items/citations/total_tokens}` continua idêntico.

> **Guardrail read-only ESTRUTURAL (achado I1, parte read-only):** este módulo importa **só** `subprocess`/`os`/`sys`/`json` e chama `acervoctl.py` com os subcomandos `retrieve`/`posture`. **Nenhum** import ou invocação de `prepare-write`/`commit-write`/`new-object`. Não há caminho de código de escrita — a garantia é a ausência da superfície de I/O, não uma política de prompt (`u-acervo-retrieval §5`).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_curador_retrieve.py
import json
import sys
import pytest

from api import canvas_curador_retrieve as ret


@pytest.fixture()
def stub_cmd(monkeypatch):
    monkeypatch.setenv("CURADOR_ACERVOCTL_CMD",
                       f"{sys.executable} tests/fixtures/stub_acervoctl_retrieve.py")


def test_retrieve_devolve_items_e_citacoes(stub_cmd):
    out = ret.curador_retrieve("renegociar", "comercial", budget=6000, k=5)
    assert out["found"] is True
    assert out["citations"] == ["Acervo: micro/comercial/knowledge/renegociacao.md"]
    assert out["items"][0]["header"]
    assert out["total_tokens"] == 410


def test_retrieve_abstencao_nao_e_erro(stub_cmd, monkeypatch):
    monkeypatch.setenv("CURADOR_ACERVOCTL_STUB_MODE", "empty")
    out = ret.curador_retrieve("inexistente", "comercial")
    assert out["found"] is False
    assert out["citations"] == []
    # não levanta — abstenção honesta


def test_posture_usa_mesmo_shape(stub_cmd):
    out = ret.curador_posture("decidir preço", "comercial", mode="decision")
    assert "items" in out and "total_tokens" in out


def test_read_only_estrutural_sem_verbos_de_escrita():
    src = __import__("pathlib").Path(ret.__file__).read_text(encoding="utf-8")
    for verbo in ("prepare-write", "commit-write", "new-object",
                  "prepare_write", "commit_write"):
        assert verbo not in src, f"módulo do Curador não pode referenciar {verbo}"


def test_nao_anexa_json_flag():
    # achado #1: posture rejeita --json; _run nunca deve anexá-lo
    src = __import__("pathlib").Path(ret.__file__).read_text(encoding="utf-8")
    assert '"--json"' not in src and "'--json'" not in src
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_retrieve.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'api.canvas_curador_retrieve'`.

- [ ] **Step 3: Write the stub fixture**

```python
# tests/fixtures/stub_acervoctl_retrieve.py
#!/usr/bin/env python3
"""Stub determinístico de `acervoctl retrieve|posture`. Lê os args (SEM depender de
`--json` — o acervoctl real sempre imprime JSON) e imprime um JSON no formato de
acervo_retrieve.retrieve. CURADOR_ACERVOCTL_STUB_MODE=empty força abstenção
(found=false)."""
import json
import os
import sys

args = sys.argv[1:]
mode = os.environ.get("CURADOR_ACERVOCTL_STUB_MODE", "hit")
if mode == "empty":
    print(json.dumps({"query": "", "scope": "comercial", "found": False,
                      "items": [], "view": [], "citations": [], "total_tokens": 0,
                      "message": "nada encontrado"}))
else:
    print(json.dumps({
        "query": "renegociar", "route": "semantic", "scope": "comercial",
        "allow_scopes": [], "k": 5, "budget_tokens": 6000, "found": True,
        "view": [], "notes": [],
        "items": [{"role": "result", "header": "Renegociação de contratos",
                   "content": "Playbook de renegociação...", "score": 0.8,
                   "source": "catalog+fts", "stub": False, "tokens_est": 410}],
        "citations": ["Acervo: micro/comercial/knowledge/renegociacao.md"],
        "total_tokens": 410,
    }))
```

- [ ] **Step 4: Write minimal implementation**

```python
# api/canvas_curador_retrieve.py
"""EXCRTX MOD-013 (F2) — wrapper SÓ-LEITURA do acervo para o Curador.

Roda `acervoctl retrieve/posture --json` como subprocess (padrão _acervoctl de
api/acervo_studio_agent.py). Read-only ESTRUTURAL: nenhum verbo de escrita é
importado ou invocado. Abstenção (found=false) não é erro."""
from __future__ import annotations

import json
import os
import subprocess
import sys

_TIMEOUT = 60


def _resolve_acervoctl_dir() -> str | None:
    """Localiza um dir de control-plane runnable (tem acervoctl.py). O cache do
    installer é a cópia canônica runnable (não provisionada em ~/.hermes)."""
    candidates = []
    env_dir = os.environ.get("EXOCORTEX_SCRIPTS_DIR")
    if env_dir:
        candidates.append(env_dir)
    home = os.path.expanduser("~")
    candidates += [
        os.path.join(home, ".exocortex-installer", "scripts"),
        os.path.join(home, "exocortex", "scripts"),
    ]
    for d in candidates:
        if d and os.path.isfile(os.path.join(d, "acervoctl.py")):
            return d
    return None


def _acervoctl(scripts_dir: str, args: list[str]) -> subprocess.CompletedProcess:
    """Roda um subcomando acervoctl (list form, sem shell). Seam de teste:
    CURADOR_ACERVOCTL_CMD substitui o binário (stub determinístico)."""
    override = os.environ.get("CURADOR_ACERVOCTL_CMD")
    if override:
        return subprocess.run(override.split() + args, capture_output=True,
                              text=True, timeout=_TIMEOUT)
    env = dict(os.environ)
    env["PYTHONPATH"] = scripts_dir + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable or "python3", os.path.join(scripts_dir, "acervoctl.py")] + args,
        cwd=scripts_dir, env=env, capture_output=True, text=True, timeout=_TIMEOUT)


def _run(subcmd: str, extra: list[str]) -> dict:
    # NB: NÃO anexar `--json`. Verificado no acervoctl real: `posture` NÃO tem o
    # flag `--json` (o parser rejeita → exit 2) e `retrieve` só o aceita "por
    # compatibilidade"; `main()` SEMPRE faz print_json(payload). Anexar `--json`
    # quebraria `posture` (→ sugerir_itens sem candidatos em prod).
    scripts_dir = os.environ.get("CURADOR_ACERVOCTL_CMD") and "." or _resolve_acervoctl_dir()
    if not os.environ.get("CURADOR_ACERVOCTL_CMD") and scripts_dir is None:
        return {"found": False, "items": [], "citations": [], "total_tokens": 0,
                "message": "acervo control plane não encontrado"}
    proc = _acervoctl(scripts_dir or ".", [subcmd] + extra)
    if proc.returncode != 0:
        return {"found": False, "items": [], "citations": [], "total_tokens": 0,
                "message": f"acervoctl {subcmd} exit {proc.returncode}: "
                           f"{(proc.stderr or '')[-200:]}"}
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return {"found": False, "items": [], "citations": [], "total_tokens": 0,
                "message": "acervoctl não retornou JSON válido"}


def curador_retrieve(query: str, scope: str, *, budget: int = 6000, k: int = 5,
                     allow_scopes=()) -> dict:
    extra = ["--query", query, "--scope", scope, "--budget", str(budget), "--k", str(k)]
    for s in allow_scopes:
        extra += ["--allow-scope", s]
    return _run("retrieve", extra)


def curador_posture(query: str, scope: str, *, mode: str = "decision",
                    budget: int = 12000, k: int = 8, allow_scopes=()) -> dict:
    extra = ["--mode", mode, "--query", query, "--scope", scope,
             "--budget", str(budget), "--k", str(k)]
    for s in allow_scopes:
        extra += ["--allow-scope", s]
    return _run("posture", extra)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_retrieve.py -v`
Expected: PASS — 5 passed (imprime `citations`/`total_tokens` reais do JSON; abstenção não-erro; sem verbos de escrita; sem `--json`).

- [ ] **Step 6: Commit**

```bash
git add api/canvas_curador_retrieve.py tests/test_curador_retrieve.py tests/fixtures/stub_acervoctl_retrieve.py
git commit -m "feat(curador): read-only acervoctl retrieve/posture wrapper (structural no-write)"
```

**Prova EX-49:** `test_read_only_estrutural_sem_verbos_de_escrita` (source scan sem `commit-write`/`new-object`) prova o guardrail estrutural para as 2 delegações de subprocess (achado I1, parte read-only — `pesquisar` é tratado à parte em T9).

---

### Task 6: Bounds mecânicos + `_budget_guard` + ledger de higiene

**Files:**
- Modify: `api/canvas_curador.py` (adiciona constantes + helpers de bounds/budget/ledger)
- Create: `tests/test_curador_bounds.py`

**Interfaces:**
- Produces (usado por T7/T8/T9):
  - `ARTIFACT_BUDGET_N = 700`, `MAX_ARTIFACTS = 3`, `MAX_FETCHES = 3`
  - `_tokens_est(obj) -> int` (heurística chars/4, sem dep)
  - `_budget_guard(artifact: dict) -> dict` (comprime-1×-depois-trunca; nunca deixa passar > N)
  - `_fit_ok(data: dict) -> bool` (Bound 3 fit-gate: exige `path` ou `fonte`/`fontes`)
  - `_bump_empty(task, results_signature: str) -> None` (Bound 1: incrementa `empty_lookups` em 0-citáveis OU assinatura duplicada)
  - `_empty_exhausted(task) -> bool` (`empty_lookups >= 2`)
  - `_bump_attempt(task) -> None` / `_attempts_exhausted(task) -> bool` (Bound 2: `attempts >= 3`)
  - `_ledger_retrieve(task, out: dict) -> None` (soma `total_tokens` ao `curador_internal_tokens`, incrementa `n_retrieves`)
  - `_ledger_emit(task, payload: dict) -> None` (soma `_tokens_est(payload)` ao `executor_tokens`)

> **Achado M4 dobrado:** Bound 2 (`attempts >= 3`, auto-verificação iterativa) só faz sentido nas skills que iteram. É armado por `_bump_attempt`, mas só é **chamado** em `_skill_buscar_acervo` (re-busca, T7) e `_skill_pesquisar` (loop de agente, T9) — nunca em `sugerir_itens` (one-shot, T8). Não há "Bound 2 vestigial" gravado como no-op; o helper existe e é exercido só onde há iteração.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_curador_bounds.py
import pytest
from api import canvas_curador as cc, curador_a2a as a2a


def _task():
    return a2a.new_task(contextId="c", skill="buscar_acervo", budget_tokens=6000)


def test_tokens_est_heuristica():
    assert cc._tokens_est({"a": "x" * 400}) >= 100   # ~chars/4


def test_budget_guard_pequeno_passa(monkeypatch):
    monkeypatch.setattr(cc, "_call_llm_curator", lambda p: "não deveria ser chamado")
    art = a2a.new_artifact(name="n", description="d",
                           data={"tipo": "buscar_acervo", "path": "p", "porque": "curto"})
    out = cc._budget_guard(art)
    assert cc._tokens_est(out) <= cc.ARTIFACT_BUDGET_N


def test_budget_guard_grande_comprime_uma_vez(monkeypatch):
    chamou = {"n": 0}
    def fake(prompt):
        chamou["n"] += 1
        return '{"tipo": "buscar_acervo", "path": "p", "porque": "resumo curto"}'
    monkeypatch.setattr(cc, "_call_llm_curator", fake)
    big = a2a.new_artifact(name="n", description="d",
                           data={"tipo": "buscar_acervo", "path": "p", "porque": "x" * 5000})
    out = cc._budget_guard(big)
    assert chamou["n"] == 1
    assert cc._tokens_est(out) <= cc.ARTIFACT_BUDGET_N


def test_budget_guard_ainda_grande_trunca(monkeypatch):
    monkeypatch.setattr(cc, "_call_llm_curator", lambda p: "y" * 6000)  # comprime falha
    big = a2a.new_artifact(name="n", description="d",
                           data={"tipo": "buscar_acervo", "path": "p", "porque": "x" * 6000})
    out = cc._budget_guard(big)
    assert cc._tokens_est(out) <= cc.ARTIFACT_BUDGET_N
    assert "[destilado truncado" in out["parts"][0]["data"]["porque"]


def test_fit_gate_exige_citacao():
    assert cc._fit_ok({"path": "micro/x/k.md"}) is True
    assert cc._fit_ok({"fontes": ["https://ex.com"]}) is True
    assert cc._fit_ok({"fonte": "acervoctl retrieve"}) is True
    assert cc._fit_ok({"porque": "boa ideia sem citação"}) is False


def test_bound1_empty_lookups():
    t = _task()
    cc._bump_empty(t, "sig-A")            # 0 citáveis
    assert not cc._empty_exhausted(t)
    cc._bump_empty(t, "sig-A")            # assinatura duplicada
    assert cc._empty_exhausted(t)         # 2 -> pare


def test_bound2_attempts():
    t = _task()
    for _ in range(2):
        cc._bump_attempt(t)
    assert not cc._attempts_exhausted(t)
    cc._bump_attempt(t)
    assert cc._attempts_exhausted(t)      # 3 -> pare


def test_ledger_separa_internal_de_executor():
    t = _task()
    cc._ledger_retrieve(t, {"total_tokens": 5000})
    cc._ledger_retrieve(t, {"total_tokens": 5000})
    cc._ledger_emit(t, {"path": "p", "porque": "curto"})
    h = t["metadata"]["hygiene"]
    assert h["curador_internal_tokens"] == 10000     # trilha interna cresce
    assert h["n_retrieves"] == 2
    assert h["executor_tokens"] <= cc.ARTIFACT_BUDGET_N  # o que a Sala paga fica ≤ N
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_bounds.py -v`
Expected: FAIL — `AttributeError: module 'api.canvas_curador' has no attribute '_tokens_est'`.

- [ ] **Step 3: Add bounds/budget/ledger to `api/canvas_curador.py`**

Anexar ao fim de `api/canvas_curador.py`:

```python
ARTIFACT_BUDGET_N = 700    # teto de tokens do destilado que cruza a fronteira (o "N" do gate)
MAX_ARTIFACTS = 3          # sugerir_itens: no máx. 3 itens
MAX_FETCHES = 3            # teto duro de buscas por delegação (bounds param antes disso)

_TRUNC_MARK = "[destilado truncado a %d tokens]" % ARTIFACT_BUDGET_N


def _tokens_est(obj) -> int:
    """Heurística chars/4 (sem dep nova), consistente com o --budget do acervoctl."""
    return len(json.dumps(obj, ensure_ascii=False)) // 4


def _budget_guard(artifact: dict) -> dict:
    """P11 no ponto de emissão: se o artefato > N tokens, comprime UMA vez (turno
    auxiliar preservando path/fonte) e reconta; se ainda > N, TRUNCA o campo
    'porque' com marcador. A fronteira nunca deixa passar mais que N."""
    if _tokens_est(artifact) <= ARTIFACT_BUDGET_N:
        return artifact
    data = artifact["parts"][0]["data"]
    prompt = ("Resuma o JSON abaixo em no máximo %d tokens preservando "
              "EXATAMENTE os campos 'path'/'fonte'/'fontes'/'tipo'/'nature'. "
              "Responda SOMENTE com o JSON.\n\n%s"
              % (ARTIFACT_BUDGET_N, json.dumps(data, ensure_ascii=False)))
    try:
        comp = json.loads(_call_llm_curator(prompt))
        if isinstance(comp, dict):
            for keep in ("tipo", "nature", "path", "fonte", "fontes"):
                if keep in data and keep not in comp:
                    comp[keep] = data[keep]
            artifact["parts"][0]["data"] = comp
            data = comp
    except Exception:
        pass
    if _tokens_est(artifact) > ARTIFACT_BUDGET_N:
        # trunca o campo textual mais volumoso, preservando citação
        por = str(data.get("porque") or data.get("resumo") or "")
        keep_chars = max(0, ARTIFACT_BUDGET_N * 4 - _tokens_est(
            {k: v for k, v in data.items() if k not in ("porque", "resumo")}) * 4)
        data["porque"] = (por[:keep_chars] + " " + _TRUNC_MARK).strip()
        data.pop("resumo", None)
        logger.warning("curador: artefato truncado a %d tokens", ARTIFACT_BUDGET_N)
    return artifact


def _fit_ok(data: dict) -> bool:
    """Bound 3 (fit gate): só emite Artifact com citação verificável."""
    return bool(data.get("path") or data.get("fonte") or data.get("fontes"))


def _bump_empty(task, results_signature: str) -> None:
    """Bound 1: incrementa empty_lookups em 0-citáveis OU assinatura idêntica à
    anterior (dedup por path/URL, não por 'relevância')."""
    m = task["metadata"]
    prev = m.get("_last_sig")
    if not results_signature or results_signature == prev:
        m["empty_lookups"] = m.get("empty_lookups", 0) + 1
    m["_last_sig"] = results_signature


def _empty_exhausted(task) -> bool:
    return task["metadata"].get("empty_lookups", 0) >= 2


def _bump_attempt(task) -> None:
    task["metadata"]["attempts"] = task["metadata"].get("attempts", 0) + 1


def _attempts_exhausted(task) -> bool:
    return task["metadata"].get("attempts", 0) >= 3


def _ledger_retrieve(task, out: dict) -> None:
    h = task["metadata"]["hygiene"]
    h["curador_internal_tokens"] += int(out.get("total_tokens") or 0)
    h["n_retrieves"] += 1


def _ledger_emit(task, payload: dict) -> None:
    task["metadata"]["hygiene"]["executor_tokens"] += _tokens_est(payload)
```

- [ ] **Step 4: Wire the ledger + budget guard into the worker**

Substituir a função `_run_curador` inteira (definida em T3) por esta versão — o ramo de sugestão agora passa por fit-gate (Bound 3), `_budget_guard` (P11) e `_ledger_emit`. Substituição da função completa (não patch parcial) para evitar erro de âncora:

```python
def _run_curador(task_id: str) -> None:
    task = _STORE.get(task_id)
    cid = task["contextId"]
    try:
        transition(task, "working")
        _emit(cid, "curador_status", {"delegacao_id": task_id, "estado": "working"})
        artifact, gap = _run_skill(task)
        if artifact is not None and not _fit_ok(artifact["parts"][0]["data"]):
            artifact, gap = None, "Curador não achou citação verificável"   # Bound 3
        if artifact is not None:
            artifact = _budget_guard(artifact)                              # P11 no boundary
            _ledger_emit(task, artifact["parts"][0]["data"])
            _emit(cid, "curador_sugestao", artifact)
            transition(task, "completed")
            _emit(cid, "curador_status", {"delegacao_id": task_id, "estado": "completed"})
        else:
            reason = gap or "Curador não encontrou resultado citável"
            ops = [{"op": "add", "path": "/gaps/-", "value": reason}]
            _emit(cid, "curador_gap",
                  {"delegacao_id": task_id, "motivo": reason, "ops": ops})
            transition(task, "failed", message=new_message(
                role="agent", skill=task["metadata"]["skill"], task_id=task_id,
                text=reason))
            _emit(cid, "curador_status", {"delegacao_id": task_id, "estado": "failed"})
    except Exception as exc:  # thread daemon: nunca deixa exceção subir (erro-calmo)
        try:
            if not a2a.is_terminal(task):
                transition(task, "failed")
        except Exception:
            pass
        _emit(cid, "curador_status",
              {"delegacao_id": task_id, "estado": "failed", "erro": str(exc)[-200:]})
    finally:
        _CURADOR_BUSY.release()
        _pump()
        _schedule_cleanup(cid)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_bounds.py tests/test_curador_worker.py -v`
Expected: PASS — 8 (bounds) + 13 (worker) = 21 passed.

- [ ] **Step 6: Commit**

```bash
git add api/canvas_curador.py tests/test_curador_bounds.py
git commit -m "feat(curador): mechanical bounds + budget-guard (compress-then-truncate) + hygiene ledger"
```

**Prova EX-49:** `test_budget_guard_ainda_grande_trunca` (payload de 6000 chars → `≤ N` com marcador de truncamento) prova que a fronteira nunca vaza > N tokens; `test_ledger_separa_internal_de_executor` (internal 10000 × executor ≤ 700) é a base da prova P11 de T13.

---

## Fase P3 — As 3 delegações

### Task 7: `_skill_buscar_acervo` — completo, ITERANTE (Bound 1 dispara no gate)

**Files:**
- Modify: `api/canvas_curador.py` (adiciona `_skill_buscar_acervo` + registra em `_SKILLS`)
- Modify: `tests/test_curador_skills.py` (criar arquivo, começa por buscar_acervo)

**Interfaces:**
- Consumes: `curador_retrieve` (T5); bounds/budget/ledger (T6); `_call_llm_curator` (T3); `canvas_store.load_canvas`.
- Produces: `_skill_buscar_acervo(task) -> tuple[dict | None, str | None]`; registra `_SKILLS["buscar_acervo"] = _skill_buscar_acervo`.

> **Achado I5 dobrado:** `buscar_acervo` **itera** — se a 1ª busca abstém (0 citáveis), re-busca UMA vez com escopo alargado (`--allow-scope` dos `microversos.related` do canvas). Se a 2ª também abstém/duplica, `empty_lookups` chega a 2 → Bound 1 dispara → gap, sem Artifact. Assim o hard-requirement P10 é exercitado **dentro do gate** (buscar_acervo é skill do gate), não só em `pesquisar`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_curador_skills.py
import json
import pytest
from api import canvas_curador as cc, curador_a2a as a2a


@pytest.fixture()
def skills_env(tmp_path, monkeypatch):
    (tmp_path / "micro/comercial/knowledge").mkdir(parents=True)
    (tmp_path / "micro/comercial/knowledge/renegociacao.md").write_text("x", encoding="utf-8")
    monkeypatch.setenv("ACERVO", str(tmp_path))
    monkeypatch.setattr(cc.canvas_store, "load_canvas", lambda cid: {
        "canvas_id": cid, "microversos": {"primary": "comercial", "related": ["gabinete"]}})
    return tmp_path


def _task(skill="buscar_acervo", **args):
    t = a2a.new_task(contextId="c", skill=skill, budget_tokens=6000)
    t["metadata"]["args"] = {"query": args.get("query"), "escopo": args.get("escopo"),
                             "tema": args.get("tema"),
                             "allow_scopes": args.get("allow_scopes", [])}
    return t


def test_buscar_acervo_artefato_citado(skills_env, monkeypatch):
    monkeypatch.setattr(cc, "curador_retrieve", lambda q, s, **k: {
        "found": True, "total_tokens": 410,
        "items": [{"header": "Renegociação", "content": "playbook", "tokens_est": 410}],
        "citations": ["Acervo: micro/comercial/knowledge/renegociacao.md"]})
    # LLM destila, mas NÃO reescreve a citação (verbatim do retrieve)
    monkeypatch.setattr(cc, "_call_llm_curator", lambda p: json.dumps(
        {"porque": "playbook de renegociação do microverso"}))
    art, gap = cc._skill_buscar_acervo(_task(query="renegociar", escopo="comercial"))
    assert gap is None
    data = art["parts"][0]["data"]
    assert data["citations"] == ["Acervo: micro/comercial/knowledge/renegociacao.md"]
    assert data["path"] == "micro/comercial/knowledge/renegociacao.md"
    assert cc._tokens_est(art) <= cc.ARTIFACT_BUDGET_N


def test_buscar_acervo_bound1_dispara_apos_2_buscas(skills_env, monkeypatch):
    calls = {"n": 0}
    def empty(q, s, **k):
        calls["n"] += 1
        return {"found": False, "items": [], "citations": [], "total_tokens": 0}
    monkeypatch.setattr(cc, "curador_retrieve", empty)
    t = _task(query="inexistente", escopo="comercial")
    art, gap = cc._skill_buscar_acervo(t)
    assert art is None and gap                      # gap honesto, sem Artifact
    assert calls["n"] == 2                          # itera 2x, não 3 (Bound 1 corta antes da 3ª)
    assert cc._empty_exhausted(t)


def test_buscar_acervo_ops_pousam_em_next_moves(skills_env, monkeypatch):
    monkeypatch.setattr(cc, "curador_retrieve", lambda q, s, **k: {
        "found": True, "total_tokens": 100,
        "items": [{"header": "H", "content": "c", "tokens_est": 100}],
        "citations": ["Acervo: micro/comercial/knowledge/renegociacao.md"]})
    monkeypatch.setattr(cc, "_call_llm_curator", lambda p: json.dumps(
        {"porque": "p", "next_move": "revisar cláusula 5"}))
    art, _ = cc._skill_buscar_acervo(_task(query="q", escopo="comercial"))
    ops = art["metadata"]["ops"]
    assert any(o["path"] == "/next_moves/-" for o in ops)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_skills.py::test_buscar_acervo_artefato_citado -v`
Expected: FAIL — `AttributeError: module 'api.canvas_curador' has no attribute '_skill_buscar_acervo'`.

- [ ] **Step 3: Add the skill + register it**

Anexar ao fim de `api/canvas_curador.py` (import de `curador_retrieve` no topo do módulo junto aos demais imports — adicionar `from api.canvas_curador_retrieve import curador_retrieve, curador_posture`):

```python
_BUSCAR_PROMPT = """Você é o Curador (role auxiliar). Destile os resultados do acervo
abaixo em um objeto JSON com: "porque" (1 frase, por que isto ajuda a tarefa) e,
opcionalmente, "next_move" (1 próximo passo acionável). NUNCA reescreva as citações;
não invente paths. Responda SOMENTE com o JSON.

Consulta: {query}
Resultados (citações verbatim): {citations}
Conteúdo: {items}
"""


def _primary_scope(canvas: dict, escopo) -> str:
    if escopo:
        return escopo
    return (canvas.get("microversos") or {}).get("primary") or "global"


def _sig(out: dict) -> str:
    """Assinatura de dedup: paths citados ordenados (dedup por path, não relevância)."""
    return "|".join(sorted(out.get("citations") or []))


def _skill_buscar_acervo(task) -> tuple[dict | None, str | None]:
    args = task["metadata"]["args"]
    query = args.get("query") or ""
    canvas = canvas_store.load_canvas(task["contextId"])
    scope = _primary_scope(canvas, args.get("escopo"))
    related = (canvas.get("microversos") or {}).get("related") or []
    allow = list(args.get("allow_scopes") or [])
    fetches = 0
    while fetches < MAX_FETCHES:
        out = curador_retrieve(query, scope, budget=RETRIEVE_BUDGET, k=5, allow_scopes=allow)
        _ledger_retrieve(task, out)
        fetches += 1
        if out.get("found") and out.get("citations"):
            break
        _bump_empty(task, _sig(out))
        if _empty_exhausted(task):
            return (None, f"Curador não encontrou '{query}' após {fetches} buscas")
        allow = list(dict.fromkeys(allow + related))  # alarga o escopo p/ a 2ª busca
    citations = out.get("citations") or []
    items_txt = "; ".join(i.get("header", "") for i in (out.get("items") or []))[:1500]
    try:
        distilled = json.loads(_call_llm_curator(_BUSCAR_PROMPT.format(
            query=query, citations=citations, items=items_txt)))
    except Exception:
        distilled = {"porque": "resultado do acervo"}
    path = citations[0].replace("Acervo: ", "") if citations else ""
    data = {"tipo": "buscar_acervo", "path": path, "citations": citations,
            "porque": distilled.get("porque", ""), "fonte": "acervoctl retrieve",
            "trust": "trusted", "tokens_est": out.get("total_tokens", 0)}
    ops = []
    if distilled.get("next_move"):
        ops.append({"op": "add", "path": "/next_moves/-", "value": distilled["next_move"]})
    art = a2a.new_artifact(name="busca_acervo",
                           description=(distilled.get("porque") or "")[:120],
                           data=data, ops=ops)
    return (art, None)


_SKILLS["buscar_acervo"] = _skill_buscar_acervo
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_skills.py -v`
Expected: PASS — 3 passed (artefato citado ≤ N; Bound 1 dispara em 2 buscas; ops em `/next_moves/-`).

- [ ] **Step 5: Commit**

```bash
git add api/canvas_curador.py tests/test_curador_skills.py
git commit -m "feat(curador): buscar_acervo delegation — iterating, cited, Bound-1 fires in-gate"
```

**Prova EX-49:** `test_buscar_acervo_bound1_dispara_apos_2_buscas` (2 buscas → gap, `empty_lookups>=2`) prova que o bound P10 obrigatório **tem casa no gate** (achado I5 dobrado); `test_buscar_acervo_artefato_citado` prova citações verbatim + destilado ≤ N.

---

### Task 8: `_skill_sugerir_itens` — lê AgentCard off-trail + posture; ≤3 itens com `ops`

**Files:**
- Modify: `api/canvas_curador.py` (adiciona `_skill_sugerir_itens` + registra)
- Modify: `tests/test_curador_skills.py`

**Interfaces:**
- Consumes: `curador_posture` (T5); `curador_capabilities.load_capability_card` (**T10 — dependência dura, ver DAG**); `_call_llm_curator`, bounds/budget, `canvas_store.load_canvas`.
- Produces: `_skill_sugerir_itens(task) -> tuple[dict | None, str | None]`; registra `_SKILLS["sugerir_itens"] = _skill_sugerir_itens`. Como `sugerir_itens` pode gerar até 3 itens mas o worker emite 1 Artifact por evento, retorna o **primeiro** item como Artifact e emite os demais via `_emit(cid,"curador_sugestao",...)` extra (ver Step 3). É one-shot: **não** chama `_bump_attempt` (achado M4).

> **Zonas de pouso (achado I4):** persona → `ops` em `/personas/suggested/-`; template/skill/workflow → `ops` em `/acervo_aplicado/-` com valor `{path, nature, porque}`. Essas zonas são whitelisted em T12, mas isso só importa no **ACEITE** (T11/T12): `sugerir_itens` apenas **PRODUZ** os `ops` — **não depende de T12 para rodar** (a ordem recomendada executa T8 **antes** de T12).

- [ ] **Step 1: Write the failing test**

Adicionar a `tests/test_curador_skills.py`:

```python
def test_sugerir_itens_persona_e_acervo(skills_env, monkeypatch):
    monkeypatch.setattr(cc, "load_capability_card", lambda slug: {
        "name": "comercial", "skills": [
            {"id": "comercial/persona", "name": "persona", "count": 1,
             "examples": ["persona/negociador.md"], "porque": "negociação dura"}]})
    monkeypatch.setattr(cc, "curador_posture", lambda q, s, **k: {
        "found": True, "total_tokens": 300,
        "items": [{"header": "template de ofício", "content": "...",
                   "path": "micro/comercial/templates/oficio.md", "tokens_est": 120}],
        "citations": ["Acervo: micro/comercial/templates/oficio.md"]})
    monkeypatch.setattr(cc, "_call_llm_curator", lambda p: json.dumps({"itens": [
        {"nature": "persona", "titulo": "negociador",
         "path": "micro/comercial/persona/negociador.md", "porque": "negociação dura"},
        {"nature": "template", "titulo": "ofício",
         "path": "micro/comercial/templates/oficio.md", "porque": "modelo pronto"}]}))
    art, gap = cc._skill_sugerir_itens(_task(skill="sugerir_itens"))
    assert gap is None
    data = art["parts"][0]["data"]
    assert data["nature"] == "persona"
    assert art["metadata"]["ops"][0]["path"] == "/personas/suggested/-"


def test_sugerir_itens_fit_gate_descarta_sem_path(skills_env, monkeypatch):
    monkeypatch.setattr(cc, "load_capability_card", lambda slug: None)
    monkeypatch.setattr(cc, "curador_posture", lambda q, s, **k: {
        "found": True, "total_tokens": 10, "items": [], "citations": []})
    monkeypatch.setattr(cc, "_call_llm_curator", lambda p: json.dumps({"itens": [
        {"nature": "skill", "titulo": "boa ideia", "porque": "sem path"}]}))
    art, gap = cc._skill_sugerir_itens(_task(skill="sugerir_itens"))
    assert art is None and gap                      # nenhum item citável -> gap
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_skills.py::test_sugerir_itens_persona_e_acervo -v`
Expected: FAIL — `AttributeError: ... has no attribute '_skill_sugerir_itens'`.

- [ ] **Step 3: Add the skill + register it**

No topo de `api/canvas_curador.py`, adicionar o import: `from api.curador_capabilities import load_capability_card`. Anexar ao fim:

```python
_SUGERIR_PROMPT = """Você é o Curador (role auxiliar). Dadas as capacidades do
microverso e os candidatos rankeados, sugira até {n} itens (persona|template|skill|
workflow) úteis à tarefa. Cada item: {{"nature","titulo","path","porque"}}. Use SÓ
paths presentes nos candidatos; NUNCA invente path. Responda SOMENTE com
{{"itens": [...]}}.

Capacidades do microverso: {card}
Candidatos (posture): {candidatos}
Foco da tarefa: {focus}
"""


def _op_for_item(item: dict) -> dict | None:
    """persona -> /personas/suggested/-; demais -> /acervo_aplicado/- ({path,nature,porque})."""
    nature = (item.get("nature") or "").lower()
    if nature == "persona":
        return {"op": "add", "path": "/personas/suggested/-",
                "value": item.get("titulo") or item.get("path")}
    return {"op": "add", "path": "/acervo_aplicado/-",
            "value": {"path": item.get("path"), "nature": nature,
                      "porque": item.get("porque", "")}}


def _skill_sugerir_itens(task) -> tuple[dict | None, str | None]:
    cid = task["contextId"]
    canvas = canvas_store.load_canvas(cid)
    scope = _primary_scope(canvas, task["metadata"]["args"].get("escopo"))
    card = load_capability_card(scope) or {}         # OFF-TRAIL cache (decisão b); só leitura
    out = curador_posture(canvas.get("focus", "") or "sugerir itens", scope,
                          mode="decision", budget=POSTURE_BUDGET, k=8)
    _ledger_retrieve(task, out)
    candidatos = [{"header": i.get("header"), "path": i.get("path")}
                  for i in (out.get("items") or [])]
    try:
        parsed = json.loads(_call_llm_curator(_SUGERIR_PROMPT.format(
            n=MAX_ARTIFACTS, card=json.dumps(card, ensure_ascii=False)[:1500],
            candidatos=json.dumps(candidatos, ensure_ascii=False)[:1500],
            focus=canvas.get("focus", ""))))
        itens = [i for i in (parsed.get("itens") or []) if _fit_ok(i)][:MAX_ARTIFACTS]
    except Exception:
        itens = []
    if not itens:
        return (None, "Curador não encontrou itens citáveis para sugerir")
    arts = []
    for it in itens:
        op = _op_for_item(it)
        data = {"tipo": "sugerir_itens", "nature": it.get("nature"),
                "path": it.get("path"), "porque": it.get("porque", ""),
                "fonte": "acervoctl posture", "trust": "trusted"}
        arts.append(a2a.new_artifact(name="sugestao_%s" % it.get("nature"),
                    description=(it.get("porque") or "")[:120], data=data,
                    ops=[op] if op else []))
    # emite os itens EXTRA já pelo boundary (com budget guard + ledger); retorna o 1º
    for extra in arts[1:]:
        extra = _budget_guard(extra)
        _ledger_emit(task, extra["parts"][0]["data"])
        _emit(cid, "curador_sugestao", extra)
    return (arts[0], None)


_SKILLS["sugerir_itens"] = _skill_sugerir_itens
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_skills.py -v`
Expected: PASS — 5 passed (3 de T7 + 2 de T8). **Requer T10 concluída** (import de `load_capability_card`).

- [ ] **Step 5: Commit**

```bash
git add api/canvas_curador.py tests/test_curador_skills.py
git commit -m "feat(curador): sugerir_itens delegation — off-trail card + posture, personas/acervo_aplicado ops"
```

**Prova EX-49:** `test_sugerir_itens_persona_e_acervo` (op em `/personas/suggested/-`, ≥1 item com `path` real) prova a sugestão citada aplicável; `test_sugerir_itens_fit_gate_descarta_sem_path` prova o fit-gate (Bound 3) descartando item sem citação.

---

### Task 9: `_skill_pesquisar` — atrás de `CURADOR_ENABLE_PESQUISAR` (aux role, toolset restrito, untrusted)

**Files:**
- Modify: `api/canvas_curador.py` (adiciona `_skill_pesquisar` + `_web_search` seam + registra)
- Modify: `tests/test_curador_skills.py`

**Interfaces:**
- Consumes: `_call_llm_curator` (aux, T3); bounds (T6); `_web_search` (novo seam).
- Produces: `_skill_pesquisar(task) -> tuple[dict | None, str | None]`; `_web_search(query: str) -> list[dict]` (cada `{title,url,snippet}`); registra `_SKILLS["pesquisar"] = _skill_pesquisar`.

> **Achado I1 dobrado — `pesquisar` NÃO é read-only estrutural; a garantia é config-trust:** ao contrário de buscar/sugerir (subprocess sem superfície de escrita), pesquisar itera com LLM. Portanto: (1) **role auxiliar** — usa `_call_llm_curator` (`task="curator"`), **nunca** `_resolve_main_runtime`; (2) **toolset restrito** — o único "tool" é `_web_search` (busca web read-only, seam `CURADOR_WEB_CMD`); **não** existe no caminho nenhuma ferramenta de FS/shell/acervo-write → a garantia "não escreve" é **config-trust auditável** (a ausência de outras tools no loop), registrada como tal no contrato; (3) `data.trust="untrusted"`, `data.fontes[]` obrigatório (URLs), **segredos mascarados**, `ops` **só** `/gaps/-`. Atrás da flag, construído por último, fora do gate.

- [ ] **Step 1: Write the failing tests**

Adicionar a `tests/test_curador_skills.py`:

```python
def test_pesquisar_sintese_com_fontes(skills_env, monkeypatch):
    monkeypatch.setenv("CURADOR_ENABLE_PESQUISAR", "1")
    monkeypatch.setattr(cc, "_web_search", lambda q: [
        {"title": "Preços 2026", "url": "https://ex.example.com/a", "snippet": "..."}])
    monkeypatch.setattr(cc, "_call_llm_curator", lambda p: json.dumps(
        {"sintese": "mercado subiu 3%", "suficiente": True}))
    art, gap = cc._skill_pesquisar(_task(skill="pesquisar", tema="preços de mercado"))
    assert gap is None
    data = art["parts"][0]["data"]
    assert data["trust"] == "untrusted"
    assert data["fontes"] == ["https://ex.example.com/a"]
    # ops de pesquisar só podem tocar /gaps/-
    for op in art["metadata"]["ops"]:
        assert op["path"] == "/gaps/-"


def test_pesquisar_bound1_duas_buscas_vazias_vira_gap(skills_env, monkeypatch):
    monkeypatch.setenv("CURADOR_ENABLE_PESQUISAR", "1")
    calls = {"n": 0}
    monkeypatch.setattr(cc, "_web_search",
                        lambda q: (calls.__setitem__("n", calls["n"] + 1), [])[1])
    monkeypatch.setattr(cc, "_call_llm_curator", lambda p: json.dumps(
        {"sintese": "", "suficiente": False, "refinar": "outra query"}))
    t = _task(skill="pesquisar", tema="tema obscuro")
    art, gap = cc._skill_pesquisar(t)
    assert art is None and gap
    assert calls["n"] == 2 and cc._empty_exhausted(t)


def test_pesquisar_mascara_segredos_em_fontes(skills_env, monkeypatch):
    monkeypatch.setenv("CURADOR_ENABLE_PESQUISAR", "1")
    monkeypatch.setattr(cc, "_web_search", lambda q: [
        {"title": "t", "url": "https://ex.example.com/x?api_key=SEGREDO123&z=1",
         "snippet": "s"}])
    monkeypatch.setattr(cc, "_call_llm_curator", lambda p: json.dumps(
        {"sintese": "ok", "suficiente": True}))
    art, _ = cc._skill_pesquisar(_task(skill="pesquisar", tema="x"))
    assert "SEGREDO123" not in json.dumps(art)
    assert "api_key=***" in art["parts"][0]["data"]["fontes"][0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_skills.py::test_pesquisar_sintese_com_fontes -v`
Expected: FAIL — `AttributeError: ... has no attribute '_skill_pesquisar'`.

- [ ] **Step 3: Add the skill + web seam + register it**

Anexar ao fim de `api/canvas_curador.py`:

```python
import re as _re

_SECRET_RE = _re.compile(r"(api[_-]?key|token|secret|password)=([^&\s]+)", _re.I)


def _mask_secrets(url: str) -> str:
    return _SECRET_RE.sub(lambda m: f"{m.group(1)}=***", url or "")


def _web_search(query: str) -> list[dict]:
    """Toolset restrito de pesquisar: ÚNICA ferramenta do loop, read-only web.
    Seam CURADOR_WEB_CMD (JSON no stdout: [{title,url,snippet}]) para teste/dev;
    em produção, plugar last30days/agent-reach/firecrawl via Hermes. Não há
    nenhuma outra tool no caminho — o guardrail 'não escreve' é config-trust."""
    cmd = os.environ.get("CURADOR_WEB_CMD")
    if not cmd:
        return []
    proc = subprocess.run(cmd, shell=True, input=query.encode("utf-8"),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    try:
        rows = json.loads(proc.stdout.decode("utf-8", "replace"))
        return rows if isinstance(rows, list) else []
    except ValueError:
        return []


_PESQUISAR_PROMPT = """Você é o Curador (role auxiliar) fazendo pesquisa externa
(conteúdo UNTRUSTED). Dadas as fontes web abaixo, produza {{"sintese": <1-3 frases>,
"suficiente": <bool>, "refinar": <query alternativa se insuficiente>}}. Baseie-se SÓ
nas fontes; não invente. Responda SOMENTE com o JSON.

Tema: {tema}
Fontes: {fontes}
"""


def _skill_pesquisar(task) -> tuple[dict | None, str | None]:
    tema = task["metadata"]["args"].get("tema") or ""
    query = tema
    fontes: list[str] = []
    fetches = 0
    while fetches < MAX_FETCHES:
        rows = _web_search(query)
        fetches += 1
        _bump_attempt(task)                         # loop de agente: Bound 2 se aplica
        urls = [_mask_secrets(r.get("url", "")) for r in rows if r.get("url")]
        sig = "|".join(sorted(urls))
        if not urls:
            _bump_empty(task, "")
        else:
            fontes = urls
            _bump_empty(task, sig)                   # dedup por URL
        blob = json.dumps([{"title": r.get("title"), "url": _mask_secrets(r.get("url", "")),
                            "snippet": r.get("snippet")} for r in rows], ensure_ascii=False)[:2000]
        try:
            parsed = json.loads(_call_llm_curator(_PESQUISAR_PROMPT.format(
                tema=tema, fontes=blob)))
        except Exception:
            parsed = {"sintese": "", "suficiente": False}
        if parsed.get("suficiente") and fontes:
            data = {"tipo": "pesquisar", "porque": parsed.get("sintese", ""),
                    "fontes": fontes, "trust": "untrusted", "fonte": "web"}
            return (a2a.new_artifact(name="pesquisa", description=parsed.get("sintese", "")[:120],
                    data=data, ops=[]), None)         # ops vazio; pesquisar nunca toca campo canônico
        if _empty_exhausted(task) or _attempts_exhausted(task):
            return (None, f"Curador não obteve pesquisa citável para '{tema}' após {fetches} buscas")
        query = parsed.get("refinar") or (tema + " detalhes")
    return (None, f"Curador esgotou o orçamento de busca para '{tema}'")


_SKILLS["pesquisar"] = _skill_pesquisar
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_skills.py -v`
Expected: PASS — 8 passed (3 T7 + 2 T8 + 3 T9).

- [ ] **Step 5: Commit**

```bash
git add api/canvas_curador.py tests/test_curador_skills.py
git commit -m "feat(curador): pesquisar delegation behind CURADOR_ENABLE_PESQUISAR (aux role, restricted web-only toolset, untrusted, masked secrets)"
```

**Prova EX-49:** `test_pesquisar_mascara_segredos_em_fontes` (`SEGREDO123` ausente, `api_key=***` presente) prova o mascaramento (regra 7); `test_pesquisar_bound1_duas_buscas_vazias_vira_gap` prova o bound iterativo; a construção (aux role via `_call_llm_curator`, única tool `_web_search`) prova I1 (config-trust auditável).

---

## Fase P4 — Memória viva (OFF-TRAIL CACHE, decisão b)

### Task 10: `api/curador_capabilities.py` — AgentCard + cache off-trail idempotente

**Files:**
- Create: `api/curador_capabilities.py`
- Create: `tests/test_curador_capabilities.py`

**Interfaces:**
- Produces (usado por T8):
  - `build_agent_card(slug: str, *, root=None) -> dict` — **pura**, deriva de `micro/{slug}/_meta/index.md` (+ `catalog query` se `catalog.sqlite` existir; degrada sem ele). Shape AgentCard A2A-fiel; `version` = digest do conteúdo (idempotência).
  - `refresh_capability_cache(root=None) -> pathlib.Path` — **rotina escritora dedicada** (não o Curador): itera microversos, escreve `global/tools/state/curador/capabilities.json`. Idempotente (mesma entrada → mesmo digest → reescrita no-op).
  - `load_capability_card(slug: str, *, root=None) -> dict | None` — **leitor do Curador**: lê só o cache off-trail; `None` se cache/slug ausente. **Nunca** deriva/escreve.

> **Decisão (b) — OFF-TRAIL CACHE:** o cache vive em `global/tools/state/curador/` (fora da árvore de conhecimento do acervo; mesmo lugar disposable/gitignored de `catalog.sqlite`). O **escritor** é `refresh_capability_cache` (rotina de infra/owner/cron), **nunca** `_run_curador` — o worker importa só `load_capability_card`. `_meta/capabilities.json` canônico por microverso = graduação **F4** (fora do escopo F2). Guardrail "Curador nunca escreve no acervo" preservado.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_curador_capabilities.py
import json
import pytest
from api import curador_capabilities as cap


@pytest.fixture()
def acervo(tmp_path):
    idx = tmp_path / "micro/comercial/_meta"
    idx.mkdir(parents=True)
    (idx / "index.md").write_text(
        "# Index — comercial\n\n### Persona\n- persona/negociador.md — negociação dura\n"
        "### Templates\n- templates/oficio.md — modelo de ofício\n", encoding="utf-8")
    (tmp_path / "global/tools/state").mkdir(parents=True)
    return tmp_path


def test_build_agent_card_deriva_de_index(acervo):
    card = cap.build_agent_card("comercial", root=acervo)
    assert card["name"] == "comercial"
    assert card["version"]                              # digest presente
    natures = {s["name"] for s in card["skills"]}
    assert "persona" in natures


def test_build_agent_card_idempotente(acervo):
    a = cap.build_agent_card("comercial", root=acervo)
    b = cap.build_agent_card("comercial", root=acervo)
    assert a["version"] == b["version"]                 # mesma entrada -> mesmo digest


def test_refresh_escreve_cache_off_trail(acervo):
    p = cap.refresh_capability_cache(root=acervo)
    assert p == acervo / "global/tools/state/curador/capabilities.json"
    assert p.is_file()
    blob = json.loads(p.read_text(encoding="utf-8"))
    assert "comercial" in blob["microversos"]


def test_refresh_idempotente_nao_muda_digest(acervo):
    p = cap.refresh_capability_cache(root=acervo)
    d1 = json.loads(p.read_text(encoding="utf-8"))["digest"]
    p = cap.refresh_capability_cache(root=acervo)
    d2 = json.loads(p.read_text(encoding="utf-8"))["digest"]
    assert d1 == d2


def test_load_le_so_o_cache(acervo):
    assert cap.load_capability_card("comercial", root=acervo) is None   # sem cache ainda
    cap.refresh_capability_cache(root=acervo)
    card = cap.load_capability_card("comercial", root=acervo)
    assert card and card["name"] == "comercial"


def test_load_degrada_sem_cache(acervo):
    assert cap.load_capability_card("inexistente", root=acervo) is None


def test_modulo_leitor_do_curador_nao_importa_escritor():
    import api.canvas_curador as cc, pathlib
    src = pathlib.Path(cc.__file__).read_text(encoding="utf-8")
    assert "load_capability_card" in src
    assert "refresh_capability_cache" not in src        # worker nunca escreve o cache
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_capabilities.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'api.curador_capabilities'`.

- [ ] **Step 3: Write minimal implementation**

```python
# api/curador_capabilities.py
"""EXCRTX MOD-013 (F2) — memória viva de capacidades por microverso (OFF-TRAIL).

build_agent_card = derivação PURA de _meta/index.md (+ catalog.sqlite se existir).
refresh_capability_cache = rotina ESCRITORA dedicada -> global/tools/state/curador/
capabilities.json (fora da árvore de conhecimento; disposable). load_capability_card
= leitor do Curador (só lê o cache). O Curador NUNCA escreve: importa só load_*.
_meta/capabilities.json canônico = graduação F4 (fora do escopo)."""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

_STATE_REL = "global/tools/state/curador"
_CACHE_NAME = "capabilities.json"


def _acervo_root(root=None) -> pathlib.Path:
    if root is not None:
        return pathlib.Path(root)
    from api.canvas_store import acervo_root
    return acervo_root()


def _parse_index(md: str) -> list[dict]:
    """Extrai (nature, [exemplos], porque) das seções '### Nature' + bullets do index.md."""
    skills: list[dict] = []
    cur = None
    for line in md.splitlines():
        h = re.match(r"^#{3,}\s+(.+?)\s*$", line)
        if h:
            cur = {"name": h.group(1).strip().lower(), "examples": [], "porque": ""}
            skills.append(cur)
            continue
        b = re.match(r"^\s*[-*]\s+(\S+)\s*(?:—|-)\s*(.+?)\s*$", line)
        if b and cur is not None:
            cur["examples"].append(b.group(1).strip())
            if not cur["porque"]:
                cur["porque"] = b.group(2).strip()
    return [s for s in skills if s["examples"]]


def build_agent_card(slug: str, *, root=None) -> dict:
    root = _acervo_root(root)
    idx = root / "micro" / slug / "_meta" / "index.md"
    md = idx.read_text(encoding="utf-8") if idx.is_file() else ""
    parsed = _parse_index(md)
    skills = []
    for s in parsed:
        entry = {"id": f"{slug}/{s['name']}", "name": s["name"],
                 "examples": s["examples"][:5], "porque": s["porque"]}
        # catalog.sqlite é opcional/disposable; contagem só se existir (degrada sem)
        cat = root / "global/tools/state/catalog.sqlite"
        if cat.is_file():
            entry["count"] = len(s["examples"])   # placeholder estrutural do count real
        skills.append(entry)
    digest = hashlib.sha256(json.dumps(skills, sort_keys=True, ensure_ascii=False)
                            .encode("utf-8")).hexdigest()[:16]
    return {"name": slug, "version": digest, "skills": skills}


def _microverso_slugs(root: pathlib.Path) -> list[str]:
    micro = root / "micro"
    if not micro.is_dir():
        return []
    return sorted(p.name for p in micro.iterdir()
                  if p.is_dir() and not p.name.startswith(("_", ".")))


def refresh_capability_cache(root=None) -> pathlib.Path:
    """ROTINA ESCRITORA (não o Curador). Idempotente: mesma entrada -> mesmo digest."""
    root = _acervo_root(root)
    cards = {slug: build_agent_card(slug, root=root) for slug in _microverso_slugs(root)}
    digest = hashlib.sha256(
        json.dumps({k: v["version"] for k, v in cards.items()}, sort_keys=True)
        .encode("utf-8")).hexdigest()[:16]
    out_dir = root / _STATE_REL
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / _CACHE_NAME
    payload = {"digest": digest, "microversos": cards}
    new_blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    if not (path.is_file() and path.read_text(encoding="utf-8") == new_blob):
        path.write_text(new_blob, encoding="utf-8")   # reescrita no-op se digest igual
    return path


def load_capability_card(slug: str, *, root=None) -> dict | None:
    """LEITOR DO CURADOR — só lê o cache off-trail; nunca deriva/escreve."""
    root = _acervo_root(root)
    path = root / _STATE_REL / _CACHE_NAME
    if not path.is_file():
        return None
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None
    return (blob.get("microversos") or {}).get(slug)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_capabilities.py -v`
Expected: PASS — 7 passed (deriva de index; idempotente; cache off-trail; load só-lê; degrada; worker não importa o escritor).

- [ ] **Step 5: Commit**

```bash
git add api/curador_capabilities.py tests/test_curador_capabilities.py
git commit -m "feat(curador): living-memory off-trail cache (build/refresh/load), idempotent, curador reads only"
```

**Prova EX-49:** `test_refresh_idempotente_nao_muda_digest` (digest estável) prova refresh idempotente; `test_modulo_leitor_do_curador_nao_importa_escritor` (`refresh_capability_cache` ausente em `canvas_curador.py`) prova estruturalmente que o worker só lê o cache (decisão b + guardrail).

---

## Fase P5 — Cards proativos + aceitar + extensão de documento

### Task 12: Extensão canônica do documento v0.5 (`personas`/`acervo_aplicado`) — fonte + espelhos

> **Ordem:** T12 vem **antes/junto** de T11 (as zonas de pouso têm de existir para o accept de T11 funcionar). Numeração mantém T11/T12 do synthesis, mas o DAG executa T12 primeiro.

**Files:**
- Modify: `acervo/global/templates/harness-v0.4/canvas.yaml` (**exocortex.saas — FONTE CANÔNICA**)
- Modify: `api/canvas_store.py` (fork — `_MINIMAL`, espelho)
- Modify: `api/canvas_tarefas.py` (fork — `_WHITELIST_RAW`, espelho)
- Create: `tests/test_curador_doc_extension.py` (fork)

**Interfaces:**
- Consumes: `_handle_patch`/`_WHITELIST_RAW` (F1b, reusados tal como estão), `validate_core` (F1b).
- Produces: whitelist aceita `/personas/suggested/*` e `/acervo_aplicado/*`; `_MINIMAL` e template canônico contêm as zonas.

> **Achado I4 dobrado — mudança CANÔNICA no exocortex, não só espelho:** a fonte da verdade do documento canvas é o exocortex (contrato (b)). Verificado no código real: `personas: {suggested, explicit, evaluators}` **já existe** no template canônico (`acervo/global/templates/harness-v0.4/canvas.yaml:42-45`) — então persona pousa em `/personas/suggested/-` (não num `personas[]` flat, correção ao synthesis). `acervo_aplicado` é **genuinamente novo** → adicionado ao **template canônico** E espelhado no fork. Ambos são campos de **documento** (fora de `canvas_schema.py`, que é `additionalProperties:false` só do **núcleo** — verificado: núcleo só tem focus/vetor/intent_type/… ). Portanto `_CORE_TO_DOC` e `canvas_schema.py` **não** são tocados (não disparam `additionalProperties:false`).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_curador_doc_extension.py  (fork)
import io, json, pytest
from api import canvas_tarefas, canvas_store


class FakeHandler:
    def __init__(self): self.wfile = io.BytesIO(); self.status = None
    def send_response(self, c): self.status = c
    def send_header(self, *a): pass
    def end_headers(self): pass


@pytest.fixture()
def acervo(tmp_path, monkeypatch):
    (tmp_path / "_tasks").mkdir()
    monkeypatch.setenv("ACERVO", str(tmp_path))
    return tmp_path


def _draft(acervo):
    # create_draft deixa focus="" (via _MINIMAL); validate_core exige focus não-vazio
    # (minLength 3) -> setar antes do accept, senão `assert valid is True` falha.
    cid, canvas = canvas_store.create_draft("renegociar contrato")
    canvas["focus"] = "renegociar contrato Alfa"
    canvas["vetor"] = "execucao"
    canvas["intent_type"] = "produzir"
    canvas_store.save_canvas(cid, canvas)
    return cid


def test_minimal_tem_zonas_do_curador():
    assert "personas" in canvas_store._MINIMAL
    assert canvas_store._MINIMAL["personas"]["suggested"] == []
    assert canvas_store._MINIMAL["acervo_aplicado"] == []


def test_whitelist_aceita_personas_e_acervo_aplicado():
    assert canvas_tarefas._path_editavel("/personas/suggested/-")
    assert canvas_tarefas._path_editavel("/acervo_aplicado/-")
    assert canvas_tarefas._path_editavel("/acervo_aplicado/0")


def test_aceitar_persona_pousa_e_valida(acervo):
    cid = _draft(acervo)
    h = FakeHandler()
    canvas_tarefas._handle_patch(h, {"canvas_id": cid, "ops": [
        {"op": "add", "path": "/personas/suggested/-", "value": "negociador"}]})
    body = json.loads(h.wfile.getvalue())
    assert body["ok"] is True and body["valid"] is True
    doc = canvas_store.load_canvas(cid)
    assert doc["personas"]["suggested"] == ["negociador"]


def test_aceitar_acervo_aplicado_objeto(acervo):
    cid = _draft(acervo)
    h = FakeHandler()
    canvas_tarefas._handle_patch(h, {"canvas_id": cid, "ops": [
        {"op": "add", "path": "/acervo_aplicado/-",
         "value": {"path": "micro/comercial/templates/oficio.md",
                   "nature": "template", "porque": "modelo pronto"}}]})
    assert json.loads(h.wfile.getvalue())["ok"] is True
    doc = canvas_store.load_canvas(cid)
    assert doc["acervo_aplicado"][0]["nature"] == "template"


def test_path_nao_whitelisted_400(acervo):
    cid = _draft(acervo)
    h = FakeHandler()
    canvas_tarefas._handle_patch(h, {"canvas_id": cid, "ops": [
        {"op": "add", "path": "/personas/explicit/-", "value": "x"}]})
    assert h.status == 400          # só /personas/suggested/* é whitelisted p/ o Curador
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_doc_extension.py -v`
Expected: FAIL — `KeyError: 'acervo_aplicado'` / `_path_editavel` retorna False.

- [ ] **Step 3a: Add `acervo_aplicado` to the CANONICAL template (exocortex.saas)**

Em `acervo/global/templates/harness-v0.4/canvas.yaml`, após a linha `next_moves: []` (fim do arquivo), adicionar:

```yaml
acervo_aplicado: []     # itens do acervo aplicados pelo Curador (F2): {path, nature, porque}
```

(`personas.suggested` já existe no canônico — nenhuma mudança para persona.)

- [ ] **Step 3b: Mirror into fork `_MINIMAL` (`api/canvas_store.py`)**

Localizar `_MINIMAL` (L26-34) e adicionar as duas chaves antes do fechamento `}`:

```python
    "scope": [], "assumptions": [], "authorization": [],
    "personas": {"suggested": [], "explicit": [], "evaluators": []},
    "acervo_aplicado": [],
}
```

- [ ] **Step 3c: Mirror into fork `_WHITELIST_RAW` (`api/canvas_tarefas.py`)**

Localizar `_WHITELIST_RAW` (L31-36) e adicionar duas entradas antes do fechamento `)`:

```python
    "/next_moves/*",
    "/personas/suggested/*", "/acervo_aplicado/*",
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_doc_extension.py -v`
Expected: PASS — 5 passed (zonas em `_MINIMAL`; whitelist; persona pousa+valida; acervo_aplicado objeto; não-whitelisted 400).

- [ ] **Step 5: Commit (dois repos)**

```bash
# fork
git add api/canvas_store.py api/canvas_tarefas.py tests/test_curador_doc_extension.py
git commit -m "feat(canvas): mirror v0.5 doc extension — personas.suggested + acervo_aplicado (whitelist + _MINIMAL)"
# exocortex.saas (fonte canônica) — mesma branch collab/canvas-tarefas? NÃO: exocortex.saas usa sua própria branch
cd <exocortex.saas> && git add acervo/global/templates/harness-v0.4/canvas.yaml
git commit -m "feat(harness): canonical canvas v0.5 gains acervo_aplicado[] document field (F2 Curador)"
```

**Prova EX-49:** `test_aceitar_persona_pousa_e_valida` (persona em `/personas/suggested/-`, `valid=True`) + `test_path_nao_whitelisted_400` provam accept em 1 clique nas zonas novas sem quebrar `validate_core`. Mudança nasce na fonte canônica (exocortex) e é espelhada no fork no mesmo COLLAB (I4).

---

### Task 11: `static/canvas-curador.js` — ilha de cards + 2 edições mínimas em `canvas-tarefas.js`

**Files:**
- Create: `static/canvas-curador.js` (fork)
- Modify: `static/canvas-tarefas.js` (fork — **MOD-012, edição permitida**; 2 edições cirúrgicas)
- Modify: `static/canvas-dev.html` (fork — **único carregador** do Cockpit; adiciona `<script>` da ilha)
- Modify: `static/canvas-tarefas.css` (fork-owned; adiciona classes da ilha)
- Create: `tests/test_curador_ui_source.py` (fork)

**Interfaces:**
- Consumes: `window.CVT.{acceptOps,getCanvas,currentCid}` (exposto abaixo); endpoints `/api/canvas/curador/{delegar,stream}` (T4).
- Produces: `window.CanvasCurador.onCockpitOpen(cid)` (hook chamado por `canvas-tarefas.js`).

> **Achado #3 dobrado — carregamento via `canvas-dev.html`:** verificado que **não existe** "manifest de assets do Cockpit"; o **único** carregador de `canvas-tarefas.js` é `static/canvas-dev.html` (standalone; L13 `<script src="/static/canvas-tarefas.js">`, L6 `<link ... canvas-tarefas.css>`). `static/index.html` **não** inclui o canvas. Logo a ilha é carregada adicionando `<script src="/static/canvas-curador.js">` a `canvas-dev.html` (fork-owned, NÃO zona quente); a "sala real" do gate item 1 é a página `canvas-dev.html`.

> **Achado I3 dobrado — accept em 1 clique exige tocar `canvas-tarefas.js`:** `submitOps`/`renderCockpit`/`state`/`canvas` vivem no closure IIFE de `canvas-tarefas.js` (verificado: `submitOps` L253-263; export `window.CVT = {toggle, iniciar, abrirCockpit, applyPatch, esc}` L516). Como é arquivo DO FORK (MOD-012), **editar é permitido**. Escolha: **rotear o accept do Curador pelo mesmo `submitOps`** (fonte única do `canvas` em memória + re-render do Cockpit), via 2 edições mínimas: (A) expor `acceptOps/getCanvas/currentCid` em `window.CVT`; (B) chamar `window.CanvasCurador.onCockpitOpen(cid)` no fim de `abrirCockpit`. A ilha renderiza sua zona num **container próprio** (`#cvt-curador-zone`, irmão de `#cvt-cockpit`) que `renderCockpit()` **não** reescreve.
>
> **Achado M2 dobrado — auto-fire confiável:** o botão manual "Pedir sugestões" é o **gatilho canônico** (sempre presente na zona). O auto-fire de `sugerir_itens` é **best-effort**: em `onCockpitOpen`, a ilha abre um **leitor próprio transitório** no stream do enquadrador (`/api/canvas/stream`; contrato (d) garante N leitores) só para captar `canvas_done` e então disparar 1 delegação; se a janela já passou (job limpo), só o botão manual dispara. Nunca depende do stream do enquadrador estar vivo.
>
> **Minor — esconder a zona fora do Cockpit:** `#cvt-curador-zone` é irmã de `#cvt-cockpit` e `switchView` (canvas-tarefas.js L219-224) só alterna `#cvt-hangar`/`#cvt-cockpit` — não toca a zona. A ilha resolve isso **sem** editar `switchView`: um `MutationObserver` em `#cvt-cockpit` espelha o atributo `hidden` para `#cvt-curador-zone` (visível só quando o Cockpit está visível).

- [ ] **Step 1: Write the failing test (source assertion — determinístico, sem browser)**

```python
# tests/test_curador_ui_source.py  (fork)
import pathlib


def _static(name):
    return (pathlib.Path(__file__).resolve().parent.parent / "static" / name).read_text(
        encoding="utf-8")


def test_canvas_tarefas_expoe_surface_do_curador():
    src = _static("canvas-tarefas.js")
    assert "acceptOps: submitOps" in src
    assert "getCanvas:" in src and "currentCid:" in src
    assert "window.CanvasCurador" in src and "onCockpitOpen" in src


def test_ilha_curador_tem_superficie_minima():
    src = _static("canvas-curador.js")
    assert "/api/canvas/curador/stream" in src
    assert "/api/canvas/curador/delegar" in src
    assert "EventSource" in src
    assert "window.CVT.acceptOps" in src
    assert "cvt-curador-zone" in src             # container próprio, sobrevive a renderCockpit
    assert "Pedir sugestões" in src              # gatilho manual canônico (PT-BR)
    assert "MutationObserver" in src             # esconde a zona fora do Cockpit
    assert "window.CanvasCurador" in src


def test_canvas_dev_html_carrega_a_ilha():
    # achado #3: canvas-dev.html é o ÚNICO carregador do Cockpit
    html = _static("canvas-dev.html")
    assert "/static/canvas-curador.js" in html
    assert "/static/canvas-tarefas.css" in html   # já existia (link da ilha reusa)


def test_css_tem_classes_da_ilha():
    css = _static("canvas-tarefas.css")
    for cls in (".cvt-curador-zone", ".cvt-sug"):
        assert cls in css


def test_ilha_nao_toca_zonas_quentes():
    src = _static("canvas-curador.js")
    for hot in ("ui.js", "messages.js", "sessions.js", "panels.js", "boot.js",
                "style.css", "index.html"):
        assert hot not in src
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_ui_source.py -v`
Expected: FAIL — `FileNotFoundError: canvas-curador.js` / asserts de `canvas-tarefas.js` falham.

- [ ] **Step 3a: Two minimal edits to `static/canvas-tarefas.js`**

**Edit A** — expor a surface do Curador. Localizar a linha 516:

```javascript
  window.CVT = { toggle, iniciar, abrirCockpit, applyPatch, esc };
```

e substituir por:

```javascript
  // MOD-013 (F2): superfície mínima e estável para a ilha do Curador
  // (static/canvas-curador.js). acceptOps roteia os ops pré-computados de um
  // card pelo MESMO submitOps do editor manual — canvas em memória + re-render
  // do Cockpit ficam com fonte única. getCanvas/currentCid deixam a ilha ler o
  // microverso âncora e renderizar suas próprias zonas.
  window.CVT = {
    toggle, iniciar, abrirCockpit, applyPatch, esc,
    acceptOps: submitOps,
    getCanvas: () => canvas,
    currentCid: () => state.cid,
  };
```

**Edit B** — notificar a ilha quando um Cockpit abre. Localizar o fim de `abrirCockpit` (após o bloco `if (job && job.status === "running") {...} else {...}`, imediatamente antes do `}` que fecha a função, ~L417):

```javascript
    // MOD-013 (F2): entrega o canvas recém-aberto à ilha do Curador (se carregada).
    try { window.CanvasCurador && window.CanvasCurador.onCockpitOpen(cid); }
    catch (_) { /* ilha é opcional; nunca quebra o Cockpit */ }
```

- [ ] **Step 3b: Create `static/canvas-curador.js`**

```javascript
/* EXCRTX MOD-013 (F2) — ilha do Curador: cards proativos (aceitar/dispensar).
 * IIFE, sem deps, sem build, PT-BR. 2ª EventSource própria (/api/canvas/curador/
 * stream); zona em container próprio (#cvt-curador-zone) que renderCockpit() não
 * reescreve. Aceitar roteia por window.CVT.acceptOps (fonte única do canvas).
 * NÃO edita ui.js/messages.js/sessions.js/panels.js/boot.js/style.css/index.html. */
(function () {
  "use strict";
  const esc = (window.CVT && window.CVT.esc) || ((s) => String(s == null ? "" : s));
  const state = { cid: "", es: null, cursor: 0, sugestoes: {} };

  async function postJSON(url, body) {
    const r = await fetch(url, { method: "POST",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.error || ("HTTP " + r.status));
    return d;
  }

  function _zone() {
    let z = document.getElementById("cvt-curador-zone");
    if (!z) {
      const body = document.querySelector("#canvasRoot .cvt-body");
      if (!body) return null;
      z = document.createElement("div");
      z.id = "cvt-curador-zone";
      z.className = "cvt-zona cvt-curador-zone";
      body.appendChild(z);
      // minor: switchView (canvas-tarefas.js) só alterna #cvt-hangar/#cvt-cockpit e
      // não toca esta zona-irmã. Espelha o `hidden` do Cockpit p/ escondê-la fora dele.
      const cockpit = document.getElementById("cvt-cockpit");
      if (cockpit) {
        const sync = () => { z.hidden = cockpit.hidden; };
        sync();
        new MutationObserver(sync).observe(cockpit, {
          attributes: true, attributeFilter: ["hidden"] });
      }
    }
    return z;
  }

  function _canvasZones() {
    // renderiza /personas/suggested e /acervo_aplicado já aplicados (lidos do canvas)
    const c = (window.CVT && window.CVT.getCanvas && window.CVT.getCanvas()) || {};
    const personas = ((c.personas || {}).suggested || []);
    const aplicado = (c.acervo_aplicado || []);
    let html = "";
    if (personas.length) {
      html += "<h3>🎭 Personas</h3><ul>" +
        personas.map((p) => `<li>${esc(p)}</li>`).join("") + "</ul>";
    }
    if (aplicado.length) {
      html += "<h3>📚 Acervo aplicado</h3><ul>" +
        aplicado.map((a) => `<li>${esc(a.path)} — ${esc(a.porque || a.nature)}</li>`).join("") + "</ul>";
    }
    return html;
  }

  function render() {
    const z = _zone();
    if (!z) return;
    const cards = Object.values(state.sugestoes).map((s) => {
      const d = (s.parts && s.parts[0] && s.parts[0].data) || s;
      const untrusted = d.trust === "untrusted"
        ? '<span class="cvt-chip-amber">externo (confirme)</span>' : "";
      const fontes = (d.fontes || (d.path ? [d.path] : [])).map(esc).join(", ");
      return `<div class="cvt-sug" data-sid="${esc(s.artifactId || s.sugestao_id)}">` +
        `<div class="cvt-sug-porque">${esc(s.description || d.porque || "")} ${untrusted}</div>` +
        `<div class="cvt-sug-fonte">${esc(fontes)}</div>` +
        `<button type="button" class="cvt-sug-ok">Aceitar</button>` +
        `<button type="button" class="cvt-sug-no">Dispensar</button></div>`;
    }).join("");
    z.innerHTML = "<h2>Sugestões do Curador</h2>" +
      '<button type="button" id="cvt-cur-pedir" class="cvt-btn">Pedir sugestões</button>' +
      (cards || '<p class="cvt-empty">—</p>') + _canvasZones();
  }

  async function _accept(sid) {
    const s = state.sugestoes[sid];
    if (!s) return;
    const ops = (s.metadata && s.metadata.ops) || s.ops || [];
    if (ops.length && window.CVT && window.CVT.acceptOps) {
      try { await window.CVT.acceptOps(ops); } catch (_) { /* status já mostrado */ }
    }
    delete state.sugestoes[sid];
    render();
  }
  function _dismiss(sid) { delete state.sugestoes[sid]; render(); }

  async function pedirSugestoes() {
    if (!state.cid) return;
    try { await postJSON("/api/canvas/curador/delegar",
      { canvas_id: state.cid, kind: "sugerir_itens" }); }
    catch (_) { /* silencioso: card não aparece se falhar */ }
  }

  function _openStream(cid, cursor) {
    if (state.es) { state.es.close(); state.es = null; }
    const es = new EventSource("/api/canvas/curador/stream?canvas_id=" +
      encodeURIComponent(cid) + "&since=" + cursor);
    state.es = es;
    const onSug = (e) => {
      if (e.lastEventId) state.cursor = Number(e.lastEventId);
      const art = JSON.parse(e.data);
      state.sugestoes[art.artifactId || art.sugestao_id || String(state.cursor)] = art;
      render();
    };
    const onGap = (e) => {
      if (e.lastEventId) state.cursor = Number(e.lastEventId);
      const g = JSON.parse(e.data);
      state.sugestoes["gap-" + state.cursor] = {
        artifactId: "gap-" + state.cursor, description: "Lacuna: " + (g.motivo || ""),
        ops: g.ops, parts: [{ data: { porque: g.motivo } }] };
      render();
    };
    es.addEventListener("curador_sugestao", onSug);
    es.addEventListener("curador_gap", onGap);
    es.onerror = () => { es.close(); if (state.es === es) state.es = null; };
  }

  function _autoFireOnFraming(cid) {
    // best-effort: leitor transitório do stream do enquadrador só p/ captar
    // canvas_done e disparar 1 sugerir_itens; se a janela já passou, no-op.
    let es;
    try { es = new EventSource("/api/canvas/stream?canvas_id=" + encodeURIComponent(cid)); }
    catch (_) { return; }
    const done = () => { es.close(); pedirSugestoes(); };
    es.addEventListener("canvas_done", done);
    es.onerror = () => { es.close(); };
    setTimeout(() => { try { es.close(); } catch (_) {} }, 60000);
  }

  function onCockpitOpen(cid) {
    state.cid = cid;
    state.cursor = 0;
    state.sugestoes = {};
    render();
    _openStream(cid, 0);
    _autoFireOnFraming(cid);
  }

  document.addEventListener("click", (e) => {
    if (e.target.closest("#cvt-cur-pedir")) { pedirSugestoes(); return; }
    const ok = e.target.closest(".cvt-sug-ok");
    if (ok) { _accept(ok.closest(".cvt-sug").dataset.sid); return; }
    const no = e.target.closest(".cvt-sug-no");
    if (no) { _dismiss(no.closest(".cvt-sug").dataset.sid); return; }
  });

  window.CanvasCurador = { onCockpitOpen, pedirSugestoes };
})();
```

- [ ] **Step 3c: Load the island via `static/canvas-dev.html` + add CSS classes**

`static/canvas-dev.html` é o **único** carregador do Cockpit (verificado: `index.html` não inclui o canvas). Após a linha `<script src="/static/canvas-tarefas.js"></script>` (L13), adicionar:

```html
  <script src="/static/canvas-curador.js"></script>
```

A `<link rel="stylesheet" href="/static/canvas-tarefas.css">` (L6) já existe — a ilha reusa esse CSS. Anexar ao fim de `static/canvas-tarefas.css` as classes da ilha:

```css
/* MOD-013 (F2) — ilha do Curador */
.cvt-curador-zone { margin-top: 12px; }
.cvt-curador-zone h2 { font-size: 1rem; margin: 0 0 8px; }
.cvt-curador-zone h3 { font-size: .85rem; margin: 8px 0 4px; opacity: .8; }
.cvt-sug { border: 1px solid var(--cvt-border, #3334); border-radius: 8px;
           padding: 8px 10px; margin: 6px 0; }
.cvt-sug-porque { font-size: .9rem; }
.cvt-sug-fonte { font-size: .75rem; opacity: .7; margin: 2px 0 6px; word-break: break-all; }
.cvt-sug-ok, .cvt-sug-no { font-size: .8rem; margin-right: 6px; cursor: pointer; }
```

> Se `canvas-dev.html` ou `canvas-tarefas.css` não existirem onde esperado, **parar e reportar** (escopo fechado) — nunca editar `index.html`/`style.css` (zona quente).

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_ui_source.py -v`
Expected: PASS — 5 passed (surface CVT; superfície da ilha + MutationObserver; `canvas-dev.html` carrega a ilha; CSS tem as classes; não toca zona quente).

- [ ] **Step 5: Commit**

```bash
git add static/canvas-curador.js static/canvas-tarefas.js static/canvas-dev.html static/canvas-tarefas.css tests/test_curador_ui_source.py
git commit -m "feat(curador): proactive cards island + minimal CVT surface + canvas-dev.html loader + CSS"
```

**Prova EX-49:** `test_canvas_tarefas_expoe_surface_do_curador` + `test_ilha_curador_tem_superficie_minima` + `test_canvas_dev_html_carrega_a_ilha` provam a integração cross-módulo (I3) e o carregamento real (achado #3). A confirmação visual em sala real (`canvas-dev.html`: card aparece → 1 clique muta o canvas) é parte do gate (T13, owner-gated pós-merge do F1b).

---

## Fase P6 — Prova de higiene + contrato + gate

### Task 13: Prova de higiene P11 — real-pipeline (não stub-proxy) + invariante de regressão

**Files:**
- Create: `tests/test_curador_hygiene.py` (fork)
- Create: `docs/curador/HYGIENE-PROOF.md` (fork — tabela anexada ao gate; local de doc do fork)

**Interfaces:**
- Consumes: `delegar`/`_STORE`/`CURADOR_ROOMS` (T3/T4); `_handle_patch`/`compile_brief`/`create_draft` (F1b, pipeline real); skills (T7/T8) via seams determinísticos.

> **Achado C1 dobrado — prova real-room, não proxy em stub:** são **dois** entregáveis distintos:
> - **(a) Invariante de regressão** (`test_hygiene_invariante_boundary`): payload pequeno vs grande → `_tokens_est` do que cruza a fronteira fica ≤ N. Guarda de regressão, **complemento** — não é a prova do gate.
> - **(b) MEDIÇÃO REAL-ROOM antes/depois** (`test_hygiene_real_room`): sobe o **pipeline real do canvas** (`create_draft` → `compile_brief` = contexto injetado no executor, por contrato (e)) e mede os **tokens do contexto do EXECUTOR** antes e depois de **N delegações** do Curador com volume interno crescente (pequeno vs enorme). Prova que `executor_tokens` fica **constante** enquanto o volume interno do Curador (`curador_internal_tokens` do ledger) cresce ordens de magnitude — e que só sobe (≤ N por item) quando o executor **aceita** um card. Não mede o payload SSE em stub; mede o brief real que vai à sessão.
> - **Campo do accept (achado #4):** `compile_brief` (`api/canvas_brief.py`) renderiza `focus/postura/done/microversos/gaps/scope/assumptions/artifacts.expected/next_moves` — **NÃO** renderiza `personas.suggested` nem `acervo_aplicado`. Então o accept do teste real-room usa `/next_moves/-` (campo renderizado) para que Δ do contexto seja **> 0 e ≤ N**. Nota de reconciliação com o **entregável 4**: aceitar personas/acervo_aplicado hoje muta o **documento** do canvas (auditável, persiste, aparece no Cockpit via a ilha) mas **não** entra no brief do executor — é aceitável na v1 (o brief é intencionalmente enxuto; incorporar essas zonas ao brief é evolução F3+), e está **declarado** aqui e no contrato (f).
> - **Pré-condição do gate final** (decisão e): a confirmação de ponta-a-ponta com **sessão LLM viva** ("sala real" com o executor rodando) exige **merge/deploy do F1b em `exocortex/stable`** — owner-gated. O teste determinístico (b) prova o invariante agora sobre `collab/canvas-tarefas`; a confirmação live é o último passo do gate, após o merge.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_curador_hygiene.py  (fork)
import io, json, time, pytest
from api import canvas_curador as cc, curador_a2a as a2a, canvas_store, canvas_brief


class FakeHandler:
    def __init__(self): self.wfile = io.BytesIO(); self.status = None
    def send_response(self, c): self.status = c
    def send_header(self, *a): pass
    def end_headers(self): pass


@pytest.fixture()
def room(tmp_path, monkeypatch):
    (tmp_path / "_tasks").mkdir()
    (tmp_path / "micro/comercial/knowledge").mkdir(parents=True)
    monkeypatch.setenv("ACERVO", str(tmp_path))
    cc.CURADOR_ROOMS.clear(); cc._STORE = a2a.TaskStore(); cc._QUEUE.clear()
    if cc._CURADOR_BUSY.locked(): cc._CURADOR_BUSY.release()
    return tmp_path


def _est(obj):
    return len(json.dumps(obj, ensure_ascii=False)) // 4


def _wait(tid, st, timeout=5):
    dl = time.time() + timeout
    while time.time() < dl:
        t = cc._STORE.get(tid)
        if t and t["status"]["state"] == st: return t
        time.sleep(0.01)
    raise AssertionError("timeout")


def test_hygiene_invariante_boundary(room, monkeypatch):
    # (a) complemento: payload pequeno vs grande -> o que cruza fica <= N
    monkeypatch.setattr(cc, "_call_llm_curator", lambda p: json.dumps(
        {"tipo": "buscar_acervo", "path": "p", "porque": "curto"}))
    small = a2a.new_artifact(name="n", description="d",
                             data={"tipo": "buscar_acervo", "path": "p", "porque": "curto"})
    big = a2a.new_artifact(name="n", description="d",
                           data={"tipo": "buscar_acervo", "path": "p", "porque": "x" * 8000})
    assert _est(cc._budget_guard(small)) <= cc.ARTIFACT_BUDGET_N
    assert _est(cc._budget_guard(big)) <= cc.ARTIFACT_BUDGET_N


def test_hygiene_real_room(room, monkeypatch):
    # (b) real-room: pipeline real; mede o CONTEXTO DO EXECUTOR (brief compilado)
    cid, canvas = canvas_store.create_draft("renegociar contrato Alfa")
    canvas["focus"] = "renegociar contrato Alfa"
    canvas["vetor"] = "execucao"; canvas["intent_type"] = "produzir"
    canvas_store.save_canvas(cid, canvas)
    brief_antes = canvas_brief.compile_brief(canvas_store.load_canvas(cid))
    exec_tokens_antes = _est(brief_antes)

    tabela = []
    for rotulo, internal in (("pequena", 400), ("enorme", 40000)):
        # retrieve stub com volume INTERNO controlado (total_tokens), mas destilado curto
        monkeypatch.setattr(cc, "curador_retrieve", lambda q, s, _tt=internal, **k: {
            "found": True, "total_tokens": _tt,
            "items": [{"header": "H", "content": "c" * (_tt), "tokens_est": _tt}],
            "citations": ["Acervo: micro/comercial/knowledge/renegociacao.md"]})
        monkeypatch.setattr(cc, "_call_llm_curator",
                            lambda p: json.dumps({"porque": "playbook"}))
        tid = cc.delegar(cid, "buscar_acervo", query="renegociar")
        _wait(tid, "completed")
        h = cc._STORE.get(tid)["metadata"]["hygiene"]
        # o brief do executor NÃO muda com a delegação (nada auto-injeta)
        exec_tokens_depois = _est(canvas_brief.compile_brief(canvas_store.load_canvas(cid)))
        tabela.append((rotulo, h["curador_internal_tokens"], exec_tokens_depois))
        assert exec_tokens_depois == exec_tokens_antes    # contexto do executor CONSTANTE

    # internal cresce ~100x entre pequena e enorme; executor constante
    assert tabela[1][1] > tabela[0][1] * 10
    assert tabela[0][2] == tabela[1][2] == exec_tokens_antes

    # aceitar UM card sobe o executor em Δ REAL (>0) e <= N (nunca pelo volume interno).
    # IMPORTANTE (achado #4): compile_brief renderiza next_moves/scope/assumptions/gaps,
    # mas NÃO personas.suggested nem acervo_aplicado (ver api/canvas_brief.py) — então o
    # accept do gate usa /next_moves/- (campo renderizado) para produzir Δ mensurável.
    art_ops = [{"op": "add", "path": "/next_moves/-",
                "value": "revisar cláusula 5 com base no playbook de renegociação"}]
    fh = FakeHandler()
    from api import canvas_tarefas
    canvas_tarefas._handle_patch(fh, {"canvas_id": cid, "ops": art_ops})
    exec_apos_accept = _est(canvas_brief.compile_brief(canvas_store.load_canvas(cid)))
    delta = exec_apos_accept - exec_tokens_antes
    assert 0 < delta <= cc.ARTIFACT_BUDGET_N

    # grava a tabela p/ anexar ao gate
    import pathlib
    out = pathlib.Path(cc.__file__).resolve().parent.parent / "docs/curador/HYGIENE-PROOF.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Prova de higiene de contexto (P11) — F2 Curador\n",
             "| Delegação | curador_internal_tokens | executor_tokens (contexto da Sala) |",
             "|---|---|---|"]
    for rot, intern, ex in tabela:
        lines.append(f"| {rot} | {intern} | {ex} |")
    lines.append(f"\nexecutor constante = {exec_tokens_antes}; "
                 f"após aceitar 1 card = {exec_apos_accept} (Δ ≤ N={cc.ARTIFACT_BUDGET_N}).")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert out.is_file()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test.sh tests/test_curador_hygiene.py -v`
Expected: FAIL — `NameError`/`AssertionError` até o pipeline e skills existirem (depende de T7 + T12).

- [ ] **Step 3: Make it pass**

Não há novo código de produção: T13 usa o pipeline real (T3/T4/T6/T7/T12). Ajustar o teste ao comportamento real se necessário (ex.: garantir que `compile_brief` aceita o canvas de fixture). Rodar iterativamente até verde.

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test.sh tests/test_curador_hygiene.py -v`
Expected: PASS — 2 passed; `docs/curador/HYGIENE-PROOF.md` gerado com a tabela `internal × executor`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_curador_hygiene.py docs/curador/HYGIENE-PROOF.md
git commit -m "test(curador): real-room hygiene proof (executor context constant while internal grows) + regression invariant"
```

**Prova EX-49:** o output de `test_hygiene_real_room` + a tabela em `docs/curador/HYGIENE-PROOF.md` (`internal` pequena vs enorme com fator ≥10, `executor_tokens` constante; Δ ≤ N ao aceitar) É a medição do entregável 5 (achado C1 dobrado: real-pipeline, contexto do executor, antes/depois — não proxy em stub). A confirmação com sessão LLM viva é owner-gated pós-merge do F1b.

---

### Task 14: Contrato COLLAB (f) + correção `acervo_validate_scope` + MOD-013 + change record

**Files:**
- Modify: `.harness/contracts/exocortex-hermes-webui.md` (**umbrella**)
- Modify: `EXOCRTX_MODIFICATIONS.md` (fork)
- Create: `.harness/changes/2026-07-25_COLLAB_curador.md` (**umbrella**)

**Interfaces:** documentação — nenhuma API nova. Toca superfícies (b)/(d) (esquema compartilhado + concorrência) → é **COLLAB**, não SOLO.

- [ ] **Step 1: Add subsection "(f) Curador" to the contract**

Em `.harness/contracts/exocortex-hermes-webui.md`, após a subseção "(e) Pipeline de launch", adicionar:

```markdown
### (f) Curador (fork; MOD-013, F2) — agente paralelo in-process

**Endpoints** (despacho por **forward** dentro de `api/canvas_tarefas.py` — `if path.startswith("/api/canvas/curador/")`; **`routes.py` INTOCADO**, pois o F1b já esgotou o teto de 8 linhas da regra 3):
| Método/rota | Request → Response |
|---|---|
| `POST /api/canvas/curador/delegar` | `{canvas_id, kind: buscar_acervo\|sugerir_itens\|pesquisar, query?/tema?, escopo?, allow_scopes?}` → `{delegacao_id}` |
| `GET /api/canvas/curador/stream?canvas_id=&since=N` | SSE re-anexável (log PRÓPRIO do Curador, `CURADOR_ROOMS`, replay por cursor; não fecha em terminal) |
| `GET /api/canvas/curador/job?delegacao_id=` | → `{state, empty_lookups, attempts, hygiene}` (poll de fallback) |

**Eventos SSE** (log próprio `CURADOR_ROOMS[cid]["events"]`, não `CANVAS_JOBS`):
- `curador_sugestao` `<Artifact A2A>` — o destilado (≤ 700 tokens); `metadata.ops` = JSON-Patch RFC 6902 que "aceitar" aplica via `POST /api/canvas/patch`.
- `curador_status` `{delegacao_id, estado}` — estados A2A (opcional/estético).
- `curador_gap` `{delegacao_id, motivo, ops:[/gaps/-]}` — hand-back honesto (bound disparado); **human-accepted** (o usuário clica "Registrar lacuna" → `/patch`), preservando "Curador só lê".

**Extensão do documento canvas v0.5** (doc-only, fonte canônica no exocortex): `personas.suggested[]` (já canônico) recebe personas sugeridas; nova chave `acervo_aplicado[]` (`{path, nature, porque}`). Espelhos do fork: `_WHITELIST_RAW` (`/personas/suggested/*`, `/acervo_aplicado/*`) + `_MINIMAL`. Núcleo (`canvas_schema.py`/`_CORE_TO_DOC`) intocado.

**Protocolo/concorrência**: in-process, upgradeable a A2A HTTP; shapes Task/Message/Artifact wire-idênticos (estados HIFENIZADOS `input-required`, `Part.kind`, `contextId`); envelope JSON-RPC 2.0 e `tasks/get`/`cancel` adiados ao upgrade. **Singleton**, Tasks keyed por `contextId=canvas_id`, **fila FIFO global ordenada**, 1 worker por vez.

**Guardrails**:
- Curador **NUNCA escreve no acervo** — estrutural para `buscar_acervo`/`sugerir_itens` (subprocess `retrieve`/`posture`, sem superfície de escrita); **config-trust** para `pesquisar` (role auxiliar + toolset web-only restrito, atrás de `CURADOR_ENABLE_PESQUISAR`).
- **Memória viva v1 = off-trail cache** (`global/tools/state/curador/capabilities.json`), escrito por rotina de refresh dedicada, lido pelo Curador; `_meta/capabilities.json` canônico = graduação F4.
- **Correção ao charter**: sharing na busca é via `retrieve`/`--scope`/`--allow-scope` + `sensitivity:restricted` (deny-sempre) — **NÃO** `acervo_validate_scope` (esse é guarda de **escrita**, `guard_write_path`, não se aplica a um agente read-only). `allow_scopes` validado **server-side** (único invariante: `sensitivity:restricted`; cross-scope = decisão do chamador single-user).
```

Atualizar o cabeçalho do contrato: bump de versão e nota "F2 Curador adicionado".

- [ ] **Step 2: Add MOD-013 to the fork's modification catalog**

Em `EXOCRTX_MODIFICATIONS.md` (fork), adicionar entrada `[MOD-013]` descrevendo: novos `api/curador_a2a.py`, `api/canvas_curador.py`, `api/canvas_curador_retrieve.py`, `api/curador_capabilities.py`, `static/canvas-curador.js`; edições em `api/canvas_tarefas.py` (**forward** do Curador + espelho de whitelist — `routes.py` intocado), `static/canvas-tarefas.js` (surface CVT), `static/canvas-dev.html` (carrega a ilha), `static/canvas-tarefas.css` (classes da ilha), `api/canvas_store.py` (espelho `_MINIMAL`); guardrails; relação com MOD-011/MOD-012.

- [ ] **Step 3: Create the COLLAB change record**

Criar `.harness/changes/2026-07-25_COLLAB_curador.md` seguindo `.harness/templates/COLLAB.md`: modo COLLAB; subprojetos tocados (hermes-webui + exocortex.saas + umbrella); superfícies (b)/(d)/(f); decisões travadas (a)–(e)+flags; branch `collab/canvas-tarefas`; link para `F2-PLANO.md`.

- [ ] **Step 4: Verify**

Run: `.harness/bin/registry-status.sh`
Expected: OK (sem DRIFT/MISSING/UNDECLARED).

- [ ] **Step 5: Commit (umbrella + fork)**

```bash
# umbrella
cd <umbrella> && git add .harness/contracts/exocortex-hermes-webui.md .harness/changes/2026-07-25_COLLAB_curador.md
git commit -m "docs(contract): F2 Curador — subsurface (f) + acervo_validate_scope correction + COLLAB record"
# fork
cd <fork> && git add EXOCRTX_MODIFICATIONS.md
git commit -m "docs(mod): MOD-013 Curador (F2) modification catalog entry"
```

**Prova EX-49:** output de `.harness/bin/registry-status.sh` (OK) + o diff do contrato citando §(f) wire + guardrails. A correção `acervo_validate_scope` fecha o achado do charter (guarda de escrita ≠ leitura).

---

## Gate de saída F2

O gate (charter + 00-INDEX tabela de fases) fecha quando **todos** os itens abaixo têm prova bruta anexada:

1. **Sugestão citada aplicada em 1 clique** — `test_sugerir_itens_persona_e_acervo` (T8) + `test_aceitar_persona_pousa_e_valida` / `test_aceitar_acervo_aplicado_objeto` (T12) + surface `acceptOps` (T11): um card do Curador com `ops` pré-computado muta o canvas via `/patch` e `validate_core` permanece PASS.
2. **Delegação de busca retorna artefato destilado ≤ N tokens (budget explícito)** — `test_buscar_acervo_artefato_citado` (T7, `_tokens_est(art) ≤ ARTIFACT_BUDGET_N=700`) + `_budget_guard` (T6).
3. **Prova de higiene de contexto anexada (real-room)** — `test_hygiene_real_room` (T13) + `docs/curador/HYGIENE-PROOF.md`: `executor_tokens` constante enquanto `curador_internal_tokens` cresce ≥10×; Δ ≤ N ao aceitar.
4. **Bound fable-method dispara** — `test_buscar_acervo_bound1_dispara_apos_2_buscas` (T7): "2 buscas sem informação nova → gap", dentro do gate (achado I5).
5. **Higiene por construção** — registro próprio (`CURADOR_ROOMS` ≠ `CANVAS_JOBS`, T3) + só o Artifact cruza a fronteira (T6 `_ledger_emit`/`_budget_guard`).

**Pré-condição do gate final (owner-gated, decisão e):** a verificação "**numa sala real**" ponta-a-ponta (a página `static/canvas-dev.html` — único carregador do Cockpit + ilha — com **sessão LLM viva**, card renderizado, 1 clique observado no browser) EXIGE o **merge/deploy do F1b em `exocortex/stable`** — F2 nasce sobre `collab/canvas-tarefas` não-mergeado. Os testes determinísticos (T1–T13) fecham os itens 1–5 sobre `collab/canvas-tarefas` agora; a confirmação live no browser (`canvas-dev.html` via Playwright + sessão real) é o último passo, após o owner aprovar/mergear o F1b. `pesquisar` (T9) é enriquecimento atrás de flag — **fora** do gate.

---

## Dependências entre tarefas (DAG)

```
T1 (a2a puro) ─► T2 (conformance)
T1 ─► T3 (worker) ─► T4 (SSE + forward em canvas_tarefas.py; routes.py 0 linhas)
T3 ─► T5 (retrieve) ─► T6 (bounds+budget+ledger)
T6 ─► T7 (buscar_acervo)
T6 ─► T9 (pesquisar, flag)
T10 (capabilities off-trail) ─► T8 (sugerir_itens)   [T8 importa load_capability_card de T10]
T6 ─► T8                                              [T8 NÃO depende de T12: só PRODUZ ops]
T12 (doc extension) ─► T11 (island, accept persona/acervo precisa das zonas)
T4 + T11 + T12 ─► gate item 1 (accept persona/acervo em 1 clique)
T7 ─► T13 (hygiene)   [T13 aceita /next_moves/- — já whitelisted no F1b; NÃO depende de T12]
T14 (contrato) por último
```

**Ordem de execução recomendada:** T1 → T2 → T3 → T4 → T5 → T6 → T7 → T10 → T8 → T12 → T11 → T9 → T13 → T14 (esta ordem já roda T8 **antes** de T12, coerente com "T8 não depende de T12").

**Gate fecha em:** T4 + T7 + T8 + T11 + T12 + T13 (com T3/T5/T6/T10 como suporte). T9 é opcional (flag). T2/T14 são guarda/contrato.

**Suíte completa (regressão F2):** `./scripts/test.sh tests/test_curador_a2a.py tests/test_curador_worker.py tests/test_curador_retrieve.py tests/test_curador_bounds.py tests/test_curador_skills.py tests/test_curador_capabilities.py tests/test_curador_doc_extension.py tests/test_curador_ui_source.py tests/test_curador_hygiene.py -v` — esperado all green; nenhum teste do enquadrador (F1b) regride.

---

## Auto-review (writing-plans)

**1. Cobertura vs charter + crítica:**
- Entregável 1 (contrato A2A) → T1/T2. Entregável 2 (buscar/sugerir/pesquisar) → T7/T8/T9. Entregável 3 (memória viva) → T10. Entregável 4 (cards HITL) → T11 + T12. Entregável 5 (prova higiene) → T13. Gate → seção Gate. ✔ Todos cobertos.
- **C1** (prova real-room não-stub) → T13 `test_hygiene_real_room` mede `compile_brief` (contexto do executor) antes/depois sobre o pipeline real; unit-invariante mantido como complemento; pré-condição live owner-gated.
- **I1** (`pesquisar` read-only + role) → T9: role auxiliar via `_call_llm_curator(task="curator")`, toolset restrito (`_web_search` único), config-trust documentado, `fontes[]` obrigatório, segredos mascarados, `ops` só `/gaps/-`, atrás de flag.
- **I2** (FIFO real) → T3: `collections.deque` global + `_pump()` sob `_QLOCK`; `test_fifo_ordem_a_b_c` prova ordem A,B,C.
- **I3** (accept 1-clique toca `canvas-tarefas.js`) → T11: 2 edições mínimas (surface `acceptOps` + hook `onCockpitOpen`), diff exato; zona em container próprio; MOD-012 permite editar o fork.
- **I4** (esquema canônico no exocortex) → T12: `acervo_aplicado` na fonte canônica (exocortex.saas) + `personas.suggested` (já canônico) espelhados no fork no mesmo COLLAB; núcleo intocado.
- **I5** (bound dispara no gate) → T7: `buscar_acervo` itera → `test_buscar_acervo_bound1_dispara_apos_2_buscas`.
- **Menores:** auto-fire best-effort + botão manual canônico (T11, M2); `allow_scopes` server-side (T4, M3); Bound 2 só nas skills iterantes (T6/T9, M4); nenhum "Bound 2 vestigial" gravado como no-op.

**1b. Correções da 2ª revisão adversarial (verificadas na worktree):**
- **#1** (`--json`) → T5: `_run` não anexa `--json` (posture o rejeita, `main()` sempre imprime JSON — `acervoctl.py:409-417,524-530`); `test_nao_anexa_json_flag`.
- **#2** (routes.py = 0) → T4: forward de 1 linha no topo de `handle_canvas_get/post` de `canvas_tarefas.py`; `routes.py` intocado (F1b já usou 8/8 — L13110-13113,15068-15071, dispatch incondicional); `test_forward_via_canvas_tarefas`.
- **#3** (loader real) → T11: `static/canvas-dev.html` (único carregador; `index.html` não inclui o canvas) recebe `<script>` da ilha; CSS em `canvas-tarefas.css`; `test_canvas_dev_html_carrega_a_ilha`.
- **#4** (accept em campo do brief) → T13: accept usa `/next_moves/-` (renderizado por `compile_brief`; personas/acervo_aplicado NÃO entram no brief — `canvas_brief.py`), assere `0 < Δ ≤ N`; nota de reconciliação com o entregável 4.
- **#5** (`focus` não-vazio) → T12: `_draft` seta `focus`/`vetor`/`intent_type` antes do accept (`create_draft` deixa `focus=""` — `canvas_store.py:66-76`).
- **Minor** hide-zone → T11: `MutationObserver` em `#cvt-cockpit` espelha `hidden` (switchView não toca a zona-irmã); CSS classes em `canvas-tarefas.css`.

**2. Scan de placeholders:** sem "TBD/TODO/implementar depois". Todo passo que muda código mostra o código completo. Único "ajustar iterativamente até verde" é T13 step 3, que não introduz código novo (usa pipeline já construído) — aceitável.

**3. Consistência de tipos/assinaturas:** `new_task/new_message/new_artifact/transition/TaskStore` (T1) usados verbatim em T3/T6/T7/T8/T9/T13. `_SKILLS` registry (T3) preenchido por T7/T8/T9. `curador_retrieve/curador_posture` (T5) chamados em T7/T8. `load_capability_card` (T10) importado em T8. `handle_curador_get/post` (T4) consumidos pelo forward em `canvas_tarefas.py` (T4) e chamados direto nos testes. `_budget_guard/_fit_ok/_ledger_*/_bump_*/_empty_exhausted/_attempts_exhausted` (T6) usados em T7/T8/T9/`_run_curador`. `window.CVT.{acceptOps,getCanvas,currentCid}` + `window.CanvasCurador.onCockpitOpen` (T11) casam entre os dois JS. Nomes conferidos: `ARTIFACT_BUDGET_N`, `RETRIEVE_BUDGET`, `POSTURE_BUDGET`, `MAX_ARTIFACTS`, `MAX_FETCHES` — únicos e consistentes.

**Correções de divergência synthesis↔F1b real aplicadas inline:**
- Testes são flat `tests/test_curador_*.py` (não `tests/canvas/` como no synthesis) — verificado `tests/test_canvas_*.py`.
- Persona pousa em `/personas/suggested/-` (nested, já canônico) — não `personas[]` flat do synthesis — verificado `canvas.yaml:42-45`.
- `_call_llm_inprocess` do enquadrador usa `_resolve_main_runtime` + `call_llm(provider=…)`; o Curador troca por `call_llm(task="curator")` (aux) — verificado `canvas_enquadrador.py:64-85`.
- Gap = evento próprio `curador_gap` (human-accepted), não `canvas_delta` reusado — o `CANVAS_JOBS` do enquadrador pode estar limpo/fechado (registro separado); verificado `canvas_tarefas.py:107-114,357-358`.
- SSE do Curador NÃO fecha em evento terminal (serve N delegações) — diverge do `_stream_events` do F1b que fecha em `canvas_done` (`canvas_tarefas.py:357`).
- `routes.py` = 0 linhas (não 2 hooks): o F1b já esgotou o teto de 8 (dispatch incondicional em L13110-13113/15068-15071); o Curador é despachado por forward em `canvas_tarefas.py`.
- Wrapper de retrieve sem `--json` (posture rejeita o flag; `main()` já imprime JSON) — verificado `acervoctl.py:409-417,524-530`.
- Ilha carregada por `static/canvas-dev.html` (único loader), não por "manifest do MOD-012" (inexistente) — verificado `canvas-dev.html:6,13`, `index.html` sem canvas.
- Accept do gate de higiene em `/next_moves/-` (campo renderizado por `compile_brief`); personas/acervo_aplicado não entram no brief na v1 — verificado `canvas_brief.py`.

---

## Handoff de execução

Plano salvo em `docs/plans/2026-07-23_canvas-tarefas/F2-PLANO.md`. Duas opções:
1. **Subagent-Driven (recomendado)** — um subagente fresco por task, review entre tasks (SUB-SKILL: `superpowers:subagent-driven-development`).
2. **Inline** — execução em lote com checkpoints (SUB-SKILL: `superpowers:executing-plans`).

Antes de T1: garantir worktree isolada de `collab/canvas-tarefas` do fork (`superpowers:using-git-worktrees`). Nunca `git push` sem instrução. O gate final é owner-gated (merge do F1b).









