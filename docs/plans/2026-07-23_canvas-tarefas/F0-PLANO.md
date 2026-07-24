# F0 — Spike do Canvas de Tarefas: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Antes de qualquer tarefa, leia o contrato de execução em `00-INDEX.md` (mesma pasta).**

**Goal:** Provar o pipeline "1 frase → núcleo de canvas validado (schema v0.4) → deltas via SSE → render mínimo no browser" e decidir ADR-CT-04 (invocação síncrona vs job+poll) e ADR-CT-05 (vanilla vs ilha Preact) com medição real.

**Architecture:** Módulos novos no fork `hermes-webui` (padrão MOD-009/010: arquivos novos + prefix dispatch, `routes.py` ganha só 2 hooks). Estado do canvas server-side em `$ACERVO/_tasks/{id}/canvas.yaml` (harness v0.4). O LLM entra por um seam externo (`CANVAS_LLM_CMD`) — a integração com o runtime in-process é objeto da ADR, não pré-requisito do spike. Duas camadas de dado: **núcleo** (forma achatada do `canvas_schema.py`: focus/vetor/intent_type/…, validada estrito) e **documento** (template rico `canvas.yaml`, que usa `vector:`); um mapeador liga os dois — o drift `vetor`×`vector` é achado documentado do spike.

**Tech Stack:** Python stdlib + PyYAML (já é dependência), vanilla JS, SSE. Zero dependências novas.

## Global Constraints

- Repo alvo: `/home/elder/projetos/projetob/hermes-webui`, branch **`collab/canvas-tarefas`** (criada na T0 a partir de `exocortex/stable`).
- `api/routes.py`: máximo 8 linhas novas, somente nos 2 hooks indicados na T4. Nenhum outro arquivo pré-existente do frontend é tocado.
- Zero `pip install` / `npm install`; zero build step; strings de UI em PT-BR.
- Todo passo de verificação exige o output real (EX-49). 3 falhas no mesmo passo → parar e reportar (contrato do INDEX).
- `$ACERVO` resolve para `~/exocortex/acervo` nesta máquina; os testes SEMPRE usam um acervo temporário via env — nunca escrever no acervo real durante testes.

---

### Task 0: Branch e baseline

**Files:** nenhum (git apenas)

- [ ] **Step 1: Criar a branch a partir do stable**

```bash
cd /home/elder/projetos/projetob/hermes-webui
git checkout exocortex/stable && git pull origin exocortex/stable
git checkout -b collab/canvas-tarefas
git branch --show-current
```
Expected: `collab/canvas-tarefas`

- [ ] **Step 2: Baseline de testes (anote o resultado — é a régua de "não quebrei nada")**

```bash
python3 -m pytest tests/ -q -p no:cacheprovider 2>&1 | tail -3
```
Expected: sumário final (`N passed, M skipped...`). Guarde a linha para comparar na T7. Se já houver falhas pré-existentes, anote-as — elas não são suas, e não devem crescer.

---

### Task 1: `api/canvas_store.py` — store do canvas em `_tasks/`

**Files:**
- Create: `api/canvas_store.py`
- Test: `tests/test_canvas_store.py`

**Interfaces:**
- Produces: `acervo_root() -> Path` · `create_draft(focus_text: str) -> tuple[str, dict]` · `load_canvas(canvas_id) -> dict` · `save_canvas(canvas_id, dict)` · `apply_patch(canvas: dict, ops: list[dict]) -> dict` (subset RFC 6902: add/replace/remove) · `core_to_patch(core: dict) -> list[dict]` (mapeia núcleo→documento: `vetor`→`/vector`, `microverso_primary`→`/microversos/primary`, `gaps` append).

- [ ] **Step 1: Escrever os testes (falhando)** — `tests/test_canvas_store.py`:

```python
import pytest

from api import canvas_store


@pytest.fixture()
def acervo(tmp_path, monkeypatch):
    (tmp_path / "_tasks").mkdir()
    (tmp_path / "global/templates/harness-v0.4").mkdir(parents=True)
    monkeypatch.setenv("ACERVO", str(tmp_path))
    return tmp_path


def test_create_draft_persiste_yaml(acervo):
    cid, canvas = canvas_store.create_draft("Renegociar contrato Alfa")
    assert (acervo / "_tasks" / cid / "canvas.yaml").is_file()
    assert canvas["original_input_summary"] == "Renegociar contrato Alfa"
    assert canvas_store.load_canvas(cid)["canvas_id"] == cid


def test_drafts_nao_compartilham_estado(acervo):
    _, c1 = canvas_store.create_draft("a")
    canvas_store.apply_patch(c1, [{"op": "add", "path": "/gaps/-", "value": "g"}])
    _, c2 = canvas_store.create_draft("b")
    assert c2["gaps"] == []


def test_apply_patch_add_replace_remove(acervo):
    cid, canvas = canvas_store.create_draft("x")
    canvas = canvas_store.apply_patch(canvas, [
        {"op": "replace", "path": "/focus", "value": "Foco novo"},
        {"op": "add", "path": "/gaps/-", "value": "Teto de desconto?"},
    ])
    assert canvas["focus"] == "Foco novo"
    assert canvas["gaps"] == ["Teto de desconto?"]
    canvas = canvas_store.apply_patch(canvas, [{"op": "remove", "path": "/gaps/0"}])
    assert canvas["gaps"] == []


def test_core_to_patch_mapeia_nucleo_para_documento(acervo):
    ops = canvas_store.core_to_patch({
        "focus": "F", "vetor": "execucao", "intent_type": "produzir",
        "microverso_primary": "comercial", "gaps": ["g1", "g2"],
    })
    assert {"op": "replace", "path": "/vector", "value": "execucao"} in ops
    assert {"op": "replace", "path": "/microversos/primary", "value": "comercial"} in ops
    assert {"op": "add", "path": "/gaps/-", "value": "g2"} in ops


def test_canvas_id_invalido_rejeitado(acervo):
    with pytest.raises(ValueError):
        canvas_store.load_canvas("../../etc/passwd")
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
python3 -m pytest tests/test_canvas_store.py -q 2>&1 | tail -3
```
Expected: erros de import (`No module named` / `has no attribute`).

- [ ] **Step 3: Implementar `api/canvas_store.py`**

```python
"""EXCRTX MOD-011 (spike F0) — Canvas de Tarefas: store server-side em $ACERVO/_tasks/.

Fonte da verdade é o YAML em disco (harness v0.4). A UI recebe snapshot +
deltas (subset RFC 6902). Sem dependências novas (PyYAML já é requisito).
"""
from __future__ import annotations

import copy
import os
import re
import threading
import time
from pathlib import Path

import yaml

_LOCK = threading.Lock()
_TEMPLATE_REL = "global/templates/harness-v0.4/canvas.yaml"

_MINIMAL = {
    "canvas_id": "", "focus": "", "original_input_summary": "",
    "vector": "evolucao", "intent_type": "explorar",
    "user_intention": {"explicit": "", "inferred": "", "confidence": "medium"},
    "microversos": {"primary": None, "related": []},
    "gaps": [], "dependencies": [], "risks": [], "next_moves": [],
}


def acervo_root() -> Path:
    for cand in (os.environ.get("ACERVO"),
                 os.path.expanduser("~/exocortex/acervo"),
                 os.path.expanduser("~/.hermes/acervo")):
        if cand and Path(cand).is_dir():
            return Path(cand)
    raise RuntimeError(
        "ACERVO não encontrado ($ACERVO, ~/exocortex/acervo, ~/.hermes/acervo)")


def tasks_dir() -> Path:
    d = acervo_root() / "_tasks"
    d.mkdir(parents=True, exist_ok=True)
    return d


def new_canvas_id(slug: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")[:40] or "tarefa"
    return f"canvas_{time.strftime('%Y%m%d_%H%M%S')}_{slug}"


def _canvas_path(canvas_id: str) -> Path:
    if not re.fullmatch(r"canvas_[0-9]{8}_[0-9]{6}_[a-z0-9-]+", canvas_id):
        raise ValueError(f"canvas_id inválido: {canvas_id!r}")
    d = tasks_dir() / canvas_id
    d.mkdir(parents=True, exist_ok=True)
    return d / "canvas.yaml"


def create_draft(focus_text: str) -> tuple[str, dict]:
    tpl = acervo_root() / _TEMPLATE_REL
    if tpl.is_file():
        canvas = yaml.safe_load(tpl.read_text(encoding="utf-8"))
    else:
        canvas = copy.deepcopy(_MINIMAL)
    cid = new_canvas_id(focus_text)
    canvas["canvas_id"] = cid
    canvas["original_input_summary"] = focus_text.strip()
    save_canvas(cid, canvas)
    return cid, canvas


def save_canvas(canvas_id: str, canvas: dict) -> None:
    p = _canvas_path(canvas_id)
    with _LOCK:
        p.write_text(yaml.safe_dump(canvas, allow_unicode=True, sort_keys=False),
                     encoding="utf-8")


def load_canvas(canvas_id: str) -> dict:
    return yaml.safe_load(_canvas_path(canvas_id).read_text(encoding="utf-8"))


# --- subset RFC 6902: add / replace / remove --------------------------------

def _resolve(doc, pointer: str):
    if not pointer.startswith("/"):
        raise ValueError(f"pointer inválido: {pointer!r}")
    parts = [p.replace("~1", "/").replace("~0", "~")
             for p in pointer.split("/")[1:]]
    parent = doc
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    return parent, parts[-1]


def apply_patch(canvas: dict, ops: list[dict]) -> dict:
    for op in ops:
        parent, key = _resolve(canvas, op["path"])
        kind = op["op"]
        if isinstance(parent, list):
            idx = len(parent) if key == "-" else int(key)
            if kind == "add":
                parent.insert(idx, op["value"])
            elif kind == "replace":
                parent[idx] = op["value"]
            elif kind == "remove":
                parent.pop(idx)
            else:
                raise ValueError(f"op não suportada: {kind}")
        else:
            if kind in ("add", "replace"):
                parent[key] = op["value"]
            elif kind == "remove":
                parent.pop(key, None)
            else:
                raise ValueError(f"op não suportada: {kind}")
    return canvas


# --- mapeador núcleo (schema v0.4, chave `vetor`) → documento (template, `vector`)

_CORE_TO_DOC = {
    "focus": "/focus",
    "vetor": "/vector",
    "intent_type": "/intent_type",
    "microverso_primary": "/microversos/primary",
}


def core_to_patch(core: dict) -> list[dict]:
    ops: list[dict] = []
    for key, path in _CORE_TO_DOC.items():
        if core.get(key) is not None:
            ops.append({"op": "replace", "path": path, "value": core[key]})
    for gap in core.get("gaps") or []:
        ops.append({"op": "add", "path": "/gaps/-", "value": gap})
    return ops
```

- [ ] **Step 4: Rodar e ver passar**

```bash
python3 -m pytest tests/test_canvas_store.py -q 2>&1 | tail -3
```
Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add api/canvas_store.py tests/test_canvas_store.py
git commit -m "feat(canvas-f0): server-side canvas store in \$ACERVO/_tasks (MOD-011 spike)"
```

---

### Task 2: `api/canvas_validate.py` — validação do núcleo contra o schema oficial

**Files:**
- Create: `api/canvas_validate.py`
- Test: `tests/test_canvas_validate.py`

**Interfaces:**
- Consumes: `canvas_store.acervo_root()`
- Produces: `validate_core(core: dict) -> tuple[bool, list[str]]` · `load_schema() -> dict | None` (carrega `CANVAS_SCHEMA` de `$ACERVO/global/tools/harness/canvas_schema.py` via importlib; retorna None se ausente).

Nota de contexto (por que "núcleo"): o schema oficial v0.4 valida a forma achatada com `vetor` e `additionalProperties: False`; o documento rico do template usa `vector`. O LLM emite o núcleo (pequeno e estrito = JSON confiável); `core_to_patch` (T1) leva ao documento.

- [ ] **Step 1: Testes (falhando)** — `tests/test_canvas_validate.py`:

```python
import pytest

from api import canvas_validate

CORE_OK = {"focus": "Renegociar contrato Alfa", "vetor": "execucao",
           "intent_type": "produzir", "gaps": ["Teto de desconto?"]}


@pytest.fixture()
def acervo(tmp_path, monkeypatch):
    (tmp_path / "global/tools/harness").mkdir(parents=True)
    monkeypatch.setenv("ACERVO", str(tmp_path))
    return tmp_path


def test_core_valido_passa(acervo):
    ok, errors = canvas_validate.validate_core(dict(CORE_OK))
    assert ok, errors


def test_obrigatorio_ausente_falha(acervo):
    core = dict(CORE_OK); core.pop("vetor")
    ok, errors = canvas_validate.validate_core(core)
    assert not ok and any("vetor" in e for e in errors)


def test_enum_invalido_falha(acervo):
    core = dict(CORE_OK); core["vetor"] = "turbo"
    ok, errors = canvas_validate.validate_core(core)
    assert not ok


def test_campo_desconhecido_falha(acervo):
    core = dict(CORE_OK); core["surpresa"] = 1
    ok, errors = canvas_validate.validate_core(core)
    assert not ok and any("desconhecido" in e for e in errors)


def test_schema_oficial_usado_quando_presente(acervo):
    (acervo / "global/tools/harness/canvas_schema.py").write_text(
        "CANVAS_SCHEMA = {'type': 'object', 'required': ['focus']}\n")
    assert canvas_validate.load_schema() == {"type": "object", "required": ["focus"]}
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
python3 -m pytest tests/test_canvas_validate.py -q 2>&1 | tail -3
```
Expected: erros de import.

- [ ] **Step 3: Implementar `api/canvas_validate.py`**

```python
"""EXCRTX MOD-011 (spike F0) — validação do NÚCLEO do canvas (schema v0.4 oficial).

Valida manualmente (obrigatórios, enums, campos extras) e, se `jsonschema`
estiver instalado E o schema oficial existir no acervo, valida também contra
ele. Nunca exige dependência nova.
"""
from __future__ import annotations

import importlib.util

from api.canvas_store import acervo_root

_REQUIRED = ("focus", "vetor", "intent_type")
_ENUMS = {
    "vetor": {"execucao", "evolucao", "manutencao", "ambiguo"},
    "intent_type": {"explorar", "decidir", "produzir", "revisar", "manter"},
    "macroverso_status": {"resolved", "partial", "placeholder", "missing"},
    "urgency": {"alta", "media", "baixa"},
}
_ALLOWED = set(_ENUMS) | {"focus", "microverso_primary", "gaps"}


def load_schema() -> dict | None:
    path = acervo_root() / "global/tools/harness/canvas_schema.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("excrtx_canvas_schema", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "CANVAS_SCHEMA", None)


def validate_core(core) -> tuple[bool, list[str]]:
    if not isinstance(core, dict):
        return False, ["núcleo não é objeto JSON"]
    errors = [f"campo obrigatório ausente/vazio: {k}"
              for k in _REQUIRED if not core.get(k)]
    errors += [f"campo desconhecido: {k}" for k in core if k not in _ALLOWED]
    for field, allowed in _ENUMS.items():
        v = core.get(field)
        if v is not None and v not in allowed:
            errors.append(f"{field} fora do enum: {v!r}")
    mp = core.get("microverso_primary")
    if mp is not None and not isinstance(mp, str):
        errors.append("microverso_primary deve ser string ou null")
    if core.get("gaps") is not None and (
            not isinstance(core["gaps"], list)
            or any(not isinstance(g, str) for g in core["gaps"])):
        errors.append("gaps deve ser lista de strings")
    schema = load_schema()
    if schema is not None:
        try:
            import jsonschema
            jsonschema.validate(core, schema)
        except ImportError:
            pass  # sem dependência nova; validação manual acima cobre o essencial
        except Exception as exc:
            msg = str(exc).splitlines()[0]
            if msg not in errors:
                errors.append(f"schema: {msg}")
    return (not errors, errors)
```

- [ ] **Step 4: Rodar e ver passar**

```bash
python3 -m pytest tests/test_canvas_validate.py -q 2>&1 | tail -3
```
Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add api/canvas_validate.py tests/test_canvas_validate.py
git commit -m "feat(canvas-f0): core validation against official canvas schema v0.4"
```

---

### Task 3: `api/canvas_enquadrador.py` — 1 frase → núcleo do canvas

**Files:**
- Create: `api/canvas_enquadrador.py`
- Create: `scripts/spike_llm_cmd.py` (seam de LLM para o spike)
- Test: `tests/test_canvas_enquadrador.py` (+ stubs em `tests/fixtures/`)

**Interfaces:**
- Consumes: `canvas_store.acervo_root()`, `canvas_validate.validate_core()`
- Produces: `enquadrar(texto: str) -> tuple[dict, list[str]]` — retorna (núcleo, erros); com erros vazios o núcleo é válido; nunca lança exceção por resposta ruim do LLM (1 retry com os erros, depois devolve o que tem).
- Seam: env `CANVAS_LLM_CMD` = comando shell que lê o prompt no stdin e imprime a resposta no stdout. A integração com o runtime in-process é a questão da ADR-CT-04 — NÃO a implemente neste spike.

- [ ] **Step 1: Investigação bounded p/ a ADR-CT-04 (só leitura, registrar no F0-RESULTADO)**

```bash
grep -rn "def .*complete\|def .*chat(\|def ask_\|_chat_completion" api/providers.py api/config.py api/streaming.py 2>/dev/null | grep -v test | head -10
grep -n "run_conversation" api/streaming.py | head -3
```
Anote: existe helper interno de completions single-shot reutilizável? Qual? (Vai para a seção "Invocação" do `F0-RESULTADO.md`; NÃO refatore nada.)

- [ ] **Step 2: Testes (falhando)** — `tests/fixtures/stub_llm_ok.py`:

```python
#!/usr/bin/env python3
import sys; sys.stdin.read()
print('{"focus": "Renegociar contrato Alfa", "vetor": "execucao", '
      '"intent_type": "produzir", "microverso_primary": null, '
      '"gaps": ["Teto de desconto?"], "urgency": "alta", '
      '"macroverso_status": "partial"}')
```

`tests/fixtures/stub_llm_ruim.py`:

```python
#!/usr/bin/env python3
import sys; sys.stdin.read()
print("desculpe, não consigo")
```

`tests/test_canvas_enquadrador.py`:

```python
import sys

import pytest

from api import canvas_enquadrador


@pytest.fixture()
def acervo(tmp_path, monkeypatch):
    (tmp_path / "micro/comercial").mkdir(parents=True)
    (tmp_path / "micro/gabinete").mkdir(parents=True)
    monkeypatch.setenv("ACERVO", str(tmp_path))
    return tmp_path


def _use_stub(monkeypatch, name):
    monkeypatch.setenv("CANVAS_LLM_CMD",
                       f"{sys.executable} tests/fixtures/{name}")


def test_enquadrar_valido(acervo, monkeypatch):
    _use_stub(monkeypatch, "stub_llm_ok.py")
    core, errors = canvas_enquadrador.enquadrar("renegociar contrato")
    assert errors == []
    assert core["vetor"] == "execucao"


def test_enquadrar_resposta_ruim_nao_lanca(acervo, monkeypatch):
    _use_stub(monkeypatch, "stub_llm_ruim.py")
    core, errors = canvas_enquadrador.enquadrar("qualquer coisa")
    assert errors and isinstance(core, dict)


def test_prompt_lista_microversos(acervo, monkeypatch):
    seen = {}
    monkeypatch.setattr(canvas_enquadrador, "_call_llm",
                        lambda p: seen.setdefault("p", p) or "{}")
    canvas_enquadrador.enquadrar("x")
    assert "comercial" in seen["p"] and "gabinete" in seen["p"]
```

- [ ] **Step 3: Rodar e ver falhar**

```bash
python3 -m pytest tests/test_canvas_enquadrador.py -q 2>&1 | tail -3
```

- [ ] **Step 4: Implementar `api/canvas_enquadrador.py`**

```python
"""EXCRTX MOD-011 (spike F0) — enquadrador: 1 frase do executivo → núcleo do canvas.

O LLM entra por um seam externo (env CANVAS_LLM_CMD: lê prompt no stdin,
imprime resposta). A escolha definitiva de invocação (runtime in-process,
síncrono vs job+poll) é a ADR-CT-04 — decidida com as medições da T6.
"""
from __future__ import annotations

import json
import os
import subprocess

from api.canvas_store import acervo_root
from api.canvas_validate import validate_core

_PROMPT = """Você é o enquadrador do Exocórtex (EX-05/EX-06). Analise o pedido do executivo
e responda SOMENTE com um objeto JSON válido, sem markdown, com exatamente estes campos:
{{"focus": string, "vetor": "execucao"|"evolucao"|"manutencao"|"ambiguo",
 "intent_type": "explorar"|"decidir"|"produzir"|"revisar"|"manter",
 "macroverso_status": "resolved"|"partial"|"placeholder"|"missing",
 "microverso_primary": string|null, "gaps": [string], "urgency": "alta"|"media"|"baixa"}}

Regras: microverso_primary deve ser um dos microversos existentes (ou null se nenhum casa);
gaps são perguntas cuja resposta só o executivo tem (nunca invente); use vetor "ambiguo"
quando não dá para saber se é para executar, explorar ou manter.

Microversos existentes: {microversos}

Pedido do executivo: {texto}
"""


def _microversos() -> list[str]:
    micro = acervo_root() / "micro"
    if not micro.is_dir():
        return []
    return sorted(p.name for p in micro.iterdir()
                  if p.is_dir() and not p.name.startswith(("_", ".")))


def _call_llm(prompt: str) -> str:
    cmd = os.environ.get("CANVAS_LLM_CMD")
    if not cmd:
        raise RuntimeError("CANVAS_LLM_CMD não definido (seam do spike F0)")
    proc = subprocess.run(cmd, shell=True, input=prompt.encode("utf-8"),
                          stdout=subprocess.PIPE, timeout=120)
    return proc.stdout.decode("utf-8", "replace")


def _parse_json(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("resposta sem JSON")
    return json.loads(text[start:end + 1])


def enquadrar(texto: str) -> tuple[dict, list[str]]:
    prompt = _PROMPT.format(
        microversos=", ".join(_microversos()) or "(nenhum)", texto=texto.strip())
    try:
        core = _parse_json(_call_llm(prompt))
    except Exception as exc:
        return {}, [f"enquadrador falhou: {exc}"]
    ok, errors = validate_core(core)
    if ok:
        return core, []
    retry = (prompt + "\n\nSeu JSON anterior foi rejeitado: " + "; ".join(errors)
             + "\nResponda novamente SOMENTE com o JSON corrigido.")
    try:
        core2 = _parse_json(_call_llm(retry))
        ok2, errors2 = validate_core(core2)
        return (core2, []) if ok2 else (core2, errors2)
    except Exception as exc:
        return core, errors + [f"retry falhou: {exc}"]
```

E `scripts/spike_llm_cmd.py` (LLM real p/ T6, stdlib apenas — a chave vem do ambiente, NUNCA a imprima):

```python
#!/usr/bin/env python3
"""Seam de LLM do spike F0 (CANVAS_LLM_CMD): lê prompt no stdin, imprime resposta.
Endpoint OpenAI-compatível; usa DEEPSEEK_API_KEY ou EXOCORTEX_DEFAULT_API_KEY."""
import json
import os
import sys
import urllib.request

prompt = sys.stdin.read()
key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("EXOCORTEX_DEFAULT_API_KEY") or ""
base = os.environ.get("CANVAS_LLM_BASE", "https://api.deepseek.com/v1")
model = os.environ.get("CANVAS_LLM_MODEL", "deepseek-chat")
req = urllib.request.Request(
    base.rstrip("/") + "/chat/completions",
    data=json.dumps({"model": model, "temperature": 0,
                     "messages": [{"role": "user", "content": prompt}]}).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
with urllib.request.urlopen(req, timeout=110) as resp:
    print(json.load(resp)["choices"][0]["message"]["content"])
```

- [ ] **Step 5: Rodar e ver passar**

```bash
python3 -m pytest tests/test_canvas_enquadrador.py -q 2>&1 | tail -3
```
Expected: `3 passed`

- [ ] **Step 6: Commit**

```bash
git add api/canvas_enquadrador.py scripts/spike_llm_cmd.py tests/test_canvas_enquadrador.py tests/fixtures/stub_llm_ok.py tests/fixtures/stub_llm_ruim.py
git commit -m "feat(canvas-f0): enquadrador turn (phrase -> validated canvas core) behind LLM seam"
```

---

### Task 4: `api/canvas_tarefas.py` — endpoints `/api/canvas/*` + SSE (prefix dispatch)

**Files:**
- Create: `api/canvas_tarefas.py`
- Modify: `api/routes.py` (SOMENTE 2 hooks, ≤8 linhas — âncoras abaixo)
- Test: `tests/test_canvas_routes.py`

**Interfaces:**
- Consumes: `canvas_store.*`, `canvas_enquadrador.enquadrar`
- Produces: `handle_canvas_get(handler, parsed) -> bool` · `handle_canvas_post(handler, path: str, body: dict) -> bool` · registry `CANVAS_STREAMS: dict[str, queue.Queue]`. Endpoints: `POST /api/canvas/draft {text}` → `{canvas_id}`; `GET /api/canvas/stream?canvas_id=` → SSE `canvas_snapshot` / `canvas_delta` (lista JSON Patch) / `canvas_done {valid, errors}` + heartbeat; `GET /api/canvas/get?canvas_id=` → documento.

- [ ] **Step 1: Testes (falhando)** — `tests/test_canvas_routes.py`:

```python
import io
import json

import pytest

from api import canvas_tarefas


class FakeHandler:
    def __init__(self):
        self.wfile = io.BytesIO()
        self.status = None

    def send_response(self, code):
        self.status = code

    def send_header(self, *a):
        pass

    def end_headers(self):
        pass


@pytest.fixture()
def acervo(tmp_path, monkeypatch):
    (tmp_path / "_tasks").mkdir()
    (tmp_path / "global/templates/harness-v0.4").mkdir(parents=True)
    monkeypatch.setenv("ACERVO", str(tmp_path))
    return tmp_path


def test_draft_dispara_snapshot_delta_done(acervo, monkeypatch):
    monkeypatch.setattr(
        canvas_tarefas, "enquadrar",
        lambda t: ({"focus": "F", "vetor": "execucao",
                    "intent_type": "produzir", "gaps": ["g"]}, []))
    h = FakeHandler()
    assert canvas_tarefas.handle_canvas_post(
        h, "/api/canvas/draft", {"text": "renegociar Alfa"})
    cid = json.loads(h.wfile.getvalue())["canvas_id"]
    q = canvas_tarefas.CANVAS_STREAMS[cid]
    eventos = [q.get(timeout=5)[0] for _ in range(3)]
    assert eventos == ["canvas_snapshot", "canvas_delta", "canvas_done"]


def test_draft_sem_texto_400(acervo):
    h = FakeHandler()
    assert canvas_tarefas.handle_canvas_post(h, "/api/canvas/draft", {})
    assert h.status == 400


def test_path_desconhecido_retorna_false(acervo):
    assert not canvas_tarefas.handle_canvas_post(FakeHandler(), "/api/outro", {})
```

- [ ] **Step 2: Rodar e ver falhar**

```bash
python3 -m pytest tests/test_canvas_routes.py -q 2>&1 | tail -3
```

- [ ] **Step 3: Implementar `api/canvas_tarefas.py`**

```python
"""EXCRTX MOD-011 (spike F0) — endpoints /api/canvas/* (prefix dispatch, padrão MOD-009/010)."""
from __future__ import annotations

import json
import queue
import threading
from urllib.parse import parse_qs

from api import canvas_store
from api.canvas_enquadrador import enquadrar

CANVAS_STREAMS: dict[str, queue.Queue] = {}
_LOCK = threading.Lock()


def _j(handler, obj, status=200):
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _run_enquadrador(canvas_id: str, texto: str, q: queue.Queue) -> None:
    core, errors = enquadrar(texto)
    ops = canvas_store.core_to_patch(core)
    if ops:
        canvas = canvas_store.load_canvas(canvas_id)
        canvas_store.save_canvas(canvas_id, canvas_store.apply_patch(canvas, ops))
        q.put(("canvas_delta", ops))
    q.put(("canvas_done", {"valid": not errors, "errors": errors}))


def handle_canvas_post(handler, path: str, body: dict) -> bool:
    if path != "/api/canvas/draft":
        return False
    texto = (body.get("text") or "").strip()
    if not texto:
        _j(handler, {"error": "text obrigatório"}, 400)
        return True
    canvas_id, canvas = canvas_store.create_draft(texto)
    q: queue.Queue = queue.Queue()
    with _LOCK:
        CANVAS_STREAMS[canvas_id] = q
    q.put(("canvas_snapshot", canvas))
    threading.Thread(target=_run_enquadrador, args=(canvas_id, texto, q),
                     daemon=True).start()
    _j(handler, {"canvas_id": canvas_id})
    return True


def handle_canvas_get(handler, parsed) -> bool:
    if parsed.path == "/api/canvas/get":
        cid = (parse_qs(parsed.query).get("canvas_id") or [""])[0]
        try:
            _j(handler, canvas_store.load_canvas(cid))
        except Exception as exc:
            _j(handler, {"error": str(exc)}, 404)
        return True
    if parsed.path != "/api/canvas/stream":
        return False
    cid = (parse_qs(parsed.query).get("canvas_id") or [""])[0]
    with _LOCK:
        q = CANVAS_STREAMS.get(cid)
    if q is None:
        _j(handler, {"error": "stream desconhecido"}, 404)
        return True
    handler.send_response(200)
    handler.send_header("Content-Type", "text/event-stream; charset=utf-8")
    handler.send_header("Cache-Control", "no-cache")
    handler.end_headers()
    try:
        while True:
            try:
                name, payload = q.get(timeout=30)
            except queue.Empty:
                handler.wfile.write(b": heartbeat\n\n")
                handler.wfile.flush()
                continue
            data = json.dumps(payload, ensure_ascii=False)
            handler.wfile.write(f"event: {name}\ndata: {data}\n\n".encode("utf-8"))
            handler.wfile.flush()
            if name == "canvas_done":
                break
    except (BrokenPipeError, ConnectionResetError):
        pass
    finally:
        with _LOCK:
            CANVAS_STREAMS.pop(cid, None)
    return True
```

- [ ] **Step 4: Rodar e ver passar**

```bash
python3 -m pytest tests/test_canvas_routes.py -q 2>&1 | tail -3
```
Expected: `3 passed`

- [ ] **Step 5: Wire nos 2 hooks de `api/routes.py`** — localize as âncoras EXATAS (existentes, MOD-007..010):

```bash
grep -n "handle_acervo_get as _acervo_get" api/routes.py
grep -n "handle_acervo_post as _acervo_post" api/routes.py
```

Logo APÓS o bloco GET existente (3 linhas: import + `if ...(handler, parsed):` + `return`), insira, com a MESMA indentação e estrutura do vizinho:

```python
    # EXCRTX MOD-011 — Canvas de Tarefas (api/canvas_tarefas.py)
    from api.canvas_tarefas import handle_canvas_get as _canvas_get
    if _canvas_get(handler, parsed):
        return
```

E logo APÓS o bloco POST existente (mesma lógica do vizinho `_acervo_post(handler, parsed.path, body)`):

```python
    # EXCRTX MOD-011 — Canvas de Tarefas (api/canvas_tarefas.py)
    from api.canvas_tarefas import handle_canvas_post as _canvas_post
    if _canvas_post(handler, parsed.path, body):
        return
```

Confirme o dano mínimo:

```bash
git diff --stat api/routes.py
```
Expected: `1 file changed, 8 insertions(+)` (8 linhas, 0 deleções). Mais que isso = pare e reporte.

- [ ] **Step 6: Suíte não regrediu + commit**

```bash
python3 -m pytest tests/test_canvas_routes.py tests/test_canvas_store.py tests/test_canvas_validate.py tests/test_canvas_enquadrador.py -q 2>&1 | tail -2
git add api/canvas_tarefas.py api/routes.py tests/test_canvas_routes.py
git commit -m "feat(canvas-f0): /api/canvas prefix dispatch with SSE snapshot/delta/done"
```

---

### Task 5: Render mínimo no browser (página dev, zero acoplamento)

**Files:**
- Create: `static/canvas-dev.html`
- Create: `static/canvas-tarefas.js`
- Create: `static/canvas-tarefas.css`

**Interfaces:**
- Consumes: endpoints da T4.
- Produces: página dev standalone (`/static/canvas-dev.html`); global JS `CVT` (namespace `.cvt-*`). Integração com o command bar do Studio fica para F1 — NÃO toque em `acervo-studio.js`.

- [ ] **Step 1: Criar `static/canvas-dev.html`**

```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Canvas de Tarefas — spike F0</title>
  <link rel="stylesheet" href="/static/canvas-tarefas.css">
</head>
<body class="cvt-body">
  <main class="cvt-wrap">
    <h1>Canvas de Tarefas <small>(spike F0)</small></h1>
    <div class="cvt-intake">
      <input id="cvt-input" type="text"
             placeholder="O que vamos fazer?" autofocus>
      <button id="cvt-go">Enquadrar</button>
    </div>
    <p id="cvt-status" class="cvt-status">aguardando…</p>
    <section id="cvt-canvas" class="cvt-canvas"></section>
  </main>
  <script src="/static/canvas-tarefas.js"></script>
</body>
</html>
```

- [ ] **Step 2: Criar `static/canvas-tarefas.js`**

```javascript
/* EXCRTX MOD-011 (spike F0) — Canvas de Tarefas: render mínimo. Global CVT, namespace .cvt-* */
(function () {
  "use strict";
  const $ = (sel) => document.querySelector(sel);
  let canvas = null;

  function applyPatch(doc, ops) {
    for (const op of ops) {
      const parts = op.path.split("/").slice(1)
        .map((p) => p.replace(/~1/g, "/").replace(/~0/g, "~"));
      let parent = doc;
      for (const part of parts.slice(0, -1)) {
        parent = parent[Array.isArray(parent) ? Number(part) : part];
      }
      const key = parts[parts.length - 1];
      if (Array.isArray(parent)) {
        const idx = key === "-" ? parent.length : Number(key);
        if (op.op === "add") parent.splice(idx, 0, op.value);
        else if (op.op === "replace") parent[idx] = op.value;
        else if (op.op === "remove") parent.splice(idx, 1);
      } else if (op.op === "remove") {
        delete parent[key];
      } else {
        parent[key] = op.value;
      }
    }
  }

  function zona(titulo, corpoHtml) {
    return `<div class="cvt-zona"><h2>${titulo}</h2>${corpoHtml}</div>`;
  }

  function render() {
    if (!canvas) return;
    const micro = (canvas.microversos && canvas.microversos.primary) || "—";
    const gaps = (canvas.gaps || [])
      .map((g) => `<li>${g}</li>`).join("") || "<li>—</li>";
    $("#cvt-canvas").innerHTML =
      zona("Foco", `<p>${canvas.focus || "…"}</p>`) +
      zona("Vetor", `<p class="cvt-vetor cvt-vetor-${canvas.vector}">` +
        `${canvas.vector || "…"} · ${canvas.intent_type || ""}</p>`) +
      zona("Microverso âncora", `<p>${micro}</p>`) +
      zona("Lacunas", `<ul>${gaps}</ul>`);
  }

  async function iniciar() {
    const texto = $("#cvt-input").value.trim();
    if (!texto) return;
    $("#cvt-status").textContent = "enquadrando…";
    const r = await fetch("/api/canvas/draft", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: texto }),
    });
    const { canvas_id: cid } = await r.json();
    const es = new EventSource(
      "/api/canvas/stream?canvas_id=" + encodeURIComponent(cid));
    es.addEventListener("canvas_snapshot", (e) => {
      canvas = JSON.parse(e.data); render();
    });
    es.addEventListener("canvas_delta", (e) => {
      applyPatch(canvas, JSON.parse(e.data)); render();
    });
    es.addEventListener("canvas_done", (e) => {
      const d = JSON.parse(e.data);
      $("#cvt-status").textContent = d.valid
        ? "✓ canvas válido (schema v0.4)"
        : "⚠ inválido: " + d.errors.join("; ");
      es.close();
    });
  }

  window.CVT = { iniciar, applyPatch };
  document.addEventListener("DOMContentLoaded", () => {
    $("#cvt-go").addEventListener("click", iniciar);
    $("#cvt-input").addEventListener("keydown", (e) => {
      if (e.key === "Enter") iniciar();
    });
  });
})();
```

- [ ] **Step 3: Criar `static/canvas-tarefas.css`**

```css
/* EXCRTX MOD-011 (spike F0) — namespace .cvt-* */
.cvt-body { font: 15px/1.5 system-ui, sans-serif; margin: 0; background: #14141f; color: #e8e8f0; }
.cvt-wrap { max-width: 760px; margin: 3rem auto; padding: 0 1rem; }
.cvt-intake { display: flex; gap: .5rem; }
.cvt-intake input { flex: 1; padding: .6rem .8rem; border-radius: 8px; border: 1px solid #2a2a45; background: #1c1c2e; color: inherit; }
.cvt-intake button { padding: .6rem 1.2rem; border-radius: 8px; border: 0; background: #5b5bd6; color: #fff; cursor: pointer; }
.cvt-status { color: #9a9ab0; min-height: 1.4em; }
.cvt-canvas { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; }
.cvt-zona { border: 1px solid #2a2a45; border-radius: 10px; padding: .8rem 1rem; background: #1a1a2b; }
.cvt-zona h2 { margin: 0 0 .4rem; font-size: .8rem; text-transform: uppercase; letter-spacing: .06em; color: #9a9ab0; }
.cvt-vetor-execucao { color: #ffb454; }
.cvt-vetor-evolucao { color: #7ad0ff; }
.cvt-vetor-manutencao { color: #9ef0a0; }
.cvt-vetor-ambiguo { color: #ff8080; }
```

- [ ] **Step 4: Verificar end-to-end com stub (sem custo de LLM)** — suba o servidor local e abra a página:

```bash
grep -n "bootstrap.py\|ctl.sh" README.md | head -5   # confirme o comando de start documentado
CANVAS_LLM_CMD="python3 tests/fixtures/stub_llm_ok.py" ./ctl.sh start   # ou o comando que o README indicar
sleep 3 && curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8787/static/canvas-dev.html
```
Expected: `200`. (Se `401`: o middleware de auth está ativo — localize o token de dev com `grep -rn "auth" README.md docs/ | grep -i token | head -5` e registre o achado no F0-RESULTADO; se `404`: descubra a rota de estáticos com `grep -n '"/static' server.py api/routes.py | head -3` e ajuste APENAS a URL usada aqui.)
Depois, no browser: abra `http://127.0.0.1:8787/static/canvas-dev.html`, digite `renegociar contrato com o cliente Alfa até sexta`, clique **Enquadrar**. Expected: zonas Foco/Vetor/Microverso/Lacunas preenchem e o status mostra `✓ canvas válido (schema v0.4)`. Tire screenshot para o F0-RESULTADO.

- [ ] **Step 5: Commit**

```bash
git add static/canvas-dev.html static/canvas-tarefas.js static/canvas-tarefas.css
git commit -m "feat(canvas-f0): dev page rendering canvas zones from SSE snapshot+deltas"
```

---

### Task 6: Medição de latência + decidir ADR-CT-04 e ADR-CT-05

**Files:**
- Create: `scripts/spike_canvas_latency.py`
- Modify: `../exocortex.saas/docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-04-invocacao-enquadrador.md` (preencher "Decisão")
- Modify: `../exocortex.saas/docs/plans/2026-07-23_canvas-tarefas/adr/ADR-CT-05-vanilla-vs-ilha.md` (preencher "Decisão")

- [ ] **Step 1: Criar `scripts/spike_canvas_latency.py`**

```python
#!/usr/bin/env python3
"""Spike F0/T6 — mede t_first_delta e t_done do enquadramento p/ 3 frases reais."""
import json
import time
import urllib.request

BASE = "http://127.0.0.1:8787"
FRASES = [
    "Preparar ofício de renegociação do contrato com o cliente Alfa até sexta",
    "Estou pensando em como estruturar o lançamento do curso de extensão",
    "Revise as pendências do microverso exocortex-ops",
]


def post(texto):
    req = urllib.request.Request(
        BASE + "/api/canvas/draft",
        data=json.dumps({"text": texto}).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["canvas_id"]


for texto in FRASES:
    cid = post(texto)
    t0, t_delta, t_done, valido = time.time(), None, None, None
    with urllib.request.urlopen(BASE + "/api/canvas/stream?canvas_id=" + cid) as s:
        for raw in s:
            line = raw.decode().strip()
            if line == "event: canvas_delta" and t_delta is None:
                t_delta = time.time() - t0
            if line == "event: canvas_done":
                t_done = time.time() - t0
            if line.startswith("data:") and t_done is not None:
                valido = json.loads(line[5:]).get("valid")
                break
    print(f"{texto[:44]!r:48} first_delta={t_delta and round(t_delta, 1)}s "
          f"done={t_done and round(t_done, 1)}s valido={valido}")
```

- [ ] **Step 2: Rodar com LLM real (servidor reiniciado com o seam real; chave via ambiente, jamais no log)**

```bash
CANVAS_LLM_CMD="python3 scripts/spike_llm_cmd.py" ./ctl.sh restart   # ou o start do README
sleep 3 && python3 scripts/spike_canvas_latency.py
```
Expected: 3 linhas com tempos e `valido=True` em ≥2 das 3 frases. Cole o output bruto no F0-RESULTADO.

- [ ] **Step 3: Decidir as ADRs pelas regras escritas nelas** — abra os dois arquivos ADR (em `exocortex.saas/docs/plans/2026-07-23_canvas-tarefas/adr/`), aplique a regra de decisão de cada um aos números medidos e ao tamanho real do JS (`wc -l static/canvas-tarefas.js`), preencha a seção **Decisão** com a evidência, e mude `status:` para `decidida`.

- [ ] **Step 4: Commit (repo exocortex.saas — as ADRs vivem lá)**

```bash
git -C /home/elder/projetos/projetob/exocortex.saas add docs/plans/2026-07-23_canvas-tarefas/adr/
git -C /home/elder/projetos/projetob/exocortex.saas commit -m "docs(canvas-tarefas): decide ADR-CT-04 and ADR-CT-05 with F0 spike measurements"
git add scripts/spike_canvas_latency.py && git commit -m "feat(canvas-f0): latency measurement script"
```

---

### Task 7: Resultado, MOD-011, gate

**Files:**
- Create: `../exocortex.saas/docs/plans/2026-07-23_canvas-tarefas/F0-RESULTADO.md`
- Modify: `EXOCRTX_MODIFICATIONS.md` (entrada MOD-011)

- [ ] **Step 1: Escrever `F0-RESULTADO.md`** com estas seções, todas com output bruto: **Baseline vs suíte final** (as duas linhas do pytest, T0 vs agora); **E2E com stub** (screenshot + curl 200); **Latência real** (tabela da T6); **Invocação** (achados da investigação T3/Step 1); **ADRs decididas** (link + uma linha cada); **Achados de framework** (obrigatório incluir: drift `vetor`×`vector` entre `canvas_schema.py` e o template `canvas.yaml`; enum de `intent_type` divergente — 5 valores no schema, 8 no template; recomendação: unificar no canvas v0.5 durante F1); **Pendências deliberadas** (`PENDING:` se houver ação prescrita não tomada).

- [ ] **Step 2: Registrar MOD-011 em `EXOCRTX_MODIFICATIONS.md`** — siga o formato das entradas existentes; uma linha de sumário: `MOD-011 — Canvas de Tarefas (spike F0, experimental): /api/canvas/* prefix dispatch + store em $ACERVO/_tasks + página dev. Arquivos novos: api/canvas_{store,validate,enquadrador,tarefas}.py, static/canvas-{dev.html,tarefas.js,tarefas.css}; routes.py +8 linhas (2 hooks).`

- [ ] **Step 3: Suíte completa não regrediu**

```bash
python3 -m pytest tests/ -q -p no:cacheprovider 2>&1 | tail -3
```
Expected: mesmo resultado do baseline T0 + os novos testes passando (nenhuma falha NOVA).

- [ ] **Step 4: Commit final + push da branch (push autorizado pela issue F0)**

```bash
git add EXOCRTX_MODIFICATIONS.md
git commit -m "docs(canvas-f0): MOD-011 entry (spike, experimental)"
git push -u origin collab/canvas-tarefas
git -C /home/elder/projetos/projetob/exocortex.saas add docs/plans/2026-07-23_canvas-tarefas/F0-RESULTADO.md
git -C /home/elder/projetos/projetob/exocortex.saas commit -m "docs(canvas-tarefas): F0 spike results and framework findings"
git -C /home/elder/projetos/projetob/exocortex.saas push origin main
```

- [ ] **Step 5: Gate check + reporte na issue F0** — o gate do F0 é: (a) 1 frase real → canvas válido renderizado (screenshot); (b) ADR-CT-04 e ADR-CT-05 com `status: decidida` e evidência. Comente na issue F0 com o link do F0-RESULTADO.md e as provas; NÃO feche a issue — o owner fecha após revisar.

---

## Self-review do plano (executado na escrita)

- Cobertura: gate do F0 ↔ T5 (render) + T6 (ADRs); duas camadas núcleo/documento ↔ T1 (`core_to_patch`) + T2 (`validate_core`); seam LLM ↔ T3; contrato SSE ↔ T4.
- Consistência de nomes verificada entre tasks: `acervo_root`, `create_draft`, `apply_patch`, `core_to_patch`, `validate_core`, `load_schema`, `enquadrar`, `_call_llm`, `handle_canvas_get/post`, `CANVAS_STREAMS`.
- Sem placeholders: todo passo tem código ou comando com expected. Os pontos de incerteza do ambiente (auth 401, rota static) têm passo de descoberta bounded com fallback explícito.
