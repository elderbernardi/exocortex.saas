# F1b — MVP Cockpit no fork (webui): plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development (recomendado) ou superpowers:executing-plans, task a task. Leia o contrato de execução em `00-INDEX.md` antes de tudo.
> **PRÉ-CONDIÇÃO DURA (T0 verifica e ABORTA se falhar):** o PR do F1a (`collab/canvas-v05`) foi APROVADO E MERGEADO pelo owner no exocortex.saas. F1b depende do canvas v0.5.

**Goal:** Do intake à sessão dentro do cockpit: Hangar (lista + 1 frase) → canvas v0.5 verificável e **editável in loco** → Lançar (register + sessão + brief como 1ª mensagem) — com o enquadrador **in-process** (ADR-CT-04) e SSE com **replay/re-attach** (mata a race de double-connect).

**Architecture:** Superfície irmã do Acervo Studio (padrão MOD-010 replicado: `#canvasRoot` reparentado ao `<body>`, launcher próprio, global `CVT`, namespace `.cvt-*`, ZERO edição em `acervo-studio.js` — no máximo injeção RUNTIME de um botão de modo, typeof-guarded e degradável). Backend: job+poll por cima do registry existente com **log de eventos re-reproduzível por cursor** (forma dos frames = SSE do kanban: `id:`/`event:`/`data:` + `hello` + keepalive). Enquadrador troca o seam subprocess por `agent.auxiliary_client.call_llm` sob `profiles_api.profile_env_for_background_worker` (precedente: `api/streaming.py:3164` title_generation; padrão de calma offline: `api/acervo_studio_agent.py::_run_agent_text` + `_extract_json`). **Launch não depende do `#ctxTray`** — bug pré-existente confirmado no recon: `S.pendingContextAttachments` é renderizado mas nunca mesclado no send (`messages.js send()` só usa `S.pendingFiles`); o pipeline usa o contrato programático: `POST /api/session/new` → `POST /api/acervo/x/stage {session_id, source}` (retorna `{name,path,mime,size,is_image}`) → front dispara `POST /api/chat/start {session_id, message=brief, attachments=[shape acima]}` (validado: `_normalize_chat_attachments` aceita exatamente esse shape; `message` é obrigatório e não-vazio — o brief compilado É a 1ª mensagem).

**Tech Stack:** Python stdlib; vanilla JS (ADR-CT-05; gatilho de migração: ≥3 stores mutáveis interdependentes OU ~900 linhas); pytest.

## Global Constraints

- Repo: `/home/elder/projetos/projetob/hermes-webui`, branch **`collab/canvas-tarefas`** (continuar; T0 faz fast-forward sobre `exocortex/stable`).
- Arquivos permitidos: `api/canvas_{store,validate,enquadrador,tarefas}.py`, `static/canvas-{tarefas.js,tarefas.css,dev.html}`, `tests/test_canvas_*.py` + fixtures, `EXOCRTX_MODIFICATIONS.md` (MOD-012), e NADA mais no fork (routes.py JÁ tem os hooks; **zero linhas novas nele**). Umbrella: só `.harness/contracts/exocortex-hermes-webui.md` (T8). `acervo-studio.js`/`ui.js`/`messages.js`/`index.html`: INTOCADOS.
- Zero dependências novas; PT-BR na UI; **toda interpolação no DOM passa por `esc()`** (fecha o minor XSS do F0 antes do cockpit); prova bruta EX-49 por tarefa; bounds do INDEX.
- Testes SEMPRE com ACERVO temporário (monkeypatch env); LLM real só na T9 (E2E), nunca em testes.
- Push e comentário em issue SOMENTE na T9.

---

### Task 0: Gate F1a + propagação do harness + branch

- [ ] **Step 1: Verificar o gate (ABORTAR se não mergeado)**

```bash
gh pr list -R elderbernardi/exocortex.saas --head collab/canvas-v05 --state merged --json number,mergedAt | head -3
git -C /home/elder/projetos/projetob/exocortex.saas fetch origin main -q && git -C /home/elder/projetos/projetob/exocortex.saas log origin/main --oneline -5 | grep -i "canvas-v05\|ADR-CT-06" || { echo 'GATE F1a NÃO SATISFEITO — PARE e reporte BLOCKED'; exit 1; }
```
Expected: PR listado como merged + commit do v0.5 em origin/main. Caso contrário: **BLOCKED** (não prossiga).

- [ ] **Step 2: Propagar harness v0.5 ao acervo vivo** (cópia dirigida, mesmo efeito do step-04 sem rodar setup inteiro):

```bash
REPO=/home/elder/projetos/projetob/exocortex.saas; LIVE=~/exocortex/acervo
git -C "$REPO" pull origin main -q
cp "$REPO"/acervo/global/tools/harness/{canvas_schema.py,register_task_from_canvas.py} "$LIVE"/global/tools/harness/
cp "$REPO"/acervo/global/templates/harness-v0.4/{canvas.yaml,task.yaml} "$LIVE"/global/templates/harness-v0.4/
python3 - <<'EOF'
import importlib.util
spec = importlib.util.spec_from_file_location("cs", __import__("os").path.expanduser("~/exocortex/acervo/global/tools/harness/canvas_schema.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print("live schema:", m.CANVAS_SCHEMA["title"], "| shape ok:", "shape" in m.CANVAS_SCHEMA["properties"])
EOF
```
Expected: `live schema: Exocórtex Canvas v0.5 | shape ok: True`

- [ ] **Step 3: Branch em dia com o stable**

```bash
cd /home/elder/projetos/projetob/hermes-webui
git checkout collab/canvas-tarefas && git merge --ff-only exocortex/stable && git log --oneline -1
```
Expected: ff sem conflito (stable == branch tip pós-F0). Anote o SHA como BASE da F1b.

---

### Task 1: Espelhos v0.5 no fork (validate + store)

**Files:** Modify `api/canvas_validate.py`, `api/canvas_store.py`; Modify `tests/test_canvas_validate.py`, `tests/test_canvas_store.py`

**Interfaces (pós-tarefa):**
- `validate_core`: `intent_type` com 8 valores; `_ALLOWED` += `shape`, `done_criteria`, `verification`; enum `shape = {pergunta, plano-primeiro, tarefa}`.
- `canvas_store`: `_DEFAULTS`/`_MINIMAL` usam chave **`vetor`** (doc v0.5); `_CORE_TO_DOC` vira mapa-identidade em `vetor` (`/vetor`) e ganha `shape→/shape`, `done_criteria→/done_criteria`, `verification→/verification`; `load_canvas` aplica **normalização de leitura**: doc antigo com `vector` é lido e a chave é renomeada p/ `vetor` em memória (retrocompat com os 10 drafts-spike vivos).

- [ ] **Step 1: Testes primeiro** — em `tests/test_canvas_validate.py` acrescente:

```python
def test_v05_intent_type_8_e_campos_metodo(acervo):
    core = dict(CORE_OK, intent_type="publicar", shape="tarefa",
                done_criteria="oficio aprovado", verification="manifest+receipt")
    ok, errors = canvas_validate.validate_core(core)
    assert ok, errors


def test_v05_shape_invalido_falha(acervo):
    core = dict(CORE_OK, shape="epico")
    ok, errors = canvas_validate.validate_core(core)
    assert not ok and any("shape" in e for e in errors)
```

Em `tests/test_canvas_store.py` acrescente:

```python
def test_v05_core_to_patch_identidade_vetor(acervo):
    ops = canvas_store.core_to_patch({
        "focus": "F", "vetor": "execucao", "intent_type": "produzir",
        "shape": "tarefa", "done_criteria": "D", "verification": "V"})
    assert {"op": "replace", "path": "/vetor", "value": "execucao"} in ops
    assert {"op": "replace", "path": "/done_criteria", "value": "D"} in ops
    assert not any(o["path"] == "/vector" for o in ops)


def test_v05_load_normaliza_doc_antigo_vector(acervo):
    cid, canvas = canvas_store.create_draft("x")
    canvas.pop("vetor", None); canvas["vector"] = "manutencao"
    canvas_store.save_canvas(cid, canvas)
    doc = canvas_store.load_canvas(cid)
    assert doc.get("vetor") == "manutencao" and "vector" not in doc
```

- [ ] **Step 2: RED** — `python3 -m pytest tests/test_canvas_validate.py tests/test_canvas_store.py -q | tail -2` (novos falham).

- [ ] **Step 3: Implementar** — `canvas_validate.py`: `_ENUMS["intent_type"] = {"explorar","decidir","produzir","revisar","manter","publicar","ingestao","outro"}`; `_ENUMS["shape"] = {"pergunta","plano-primeiro","tarefa"}`; `_ALLOWED = set(_ENUMS) | {"focus","microverso_primary","gaps","done_criteria","verification"}`. `canvas_store.py`: em `_MINIMAL` troque `"vector": "evolucao"` por `"vetor": "evolucao"` e acrescente `"shape": "tarefa", "done_criteria": "", "verification": "", "scope": [], "assumptions": [], "authorization": []`; `_CORE_TO_DOC = {"focus": "/focus", "vetor": "/vetor", "intent_type": "/intent_type", "microverso_primary": "/microversos/primary", "shape": "/shape", "done_criteria": "/done_criteria", "verification": "/verification"}`; em `load_canvas`, após o `safe_load`: `if "vector" in doc and "vetor" not in doc: doc["vetor"] = doc.pop("vector")`.

- [ ] **Step 4: GREEN + regressão canvas** — `python3 -m pytest tests/test_canvas_store.py tests/test_canvas_validate.py tests/test_canvas_enquadrador.py tests/test_canvas_routes.py -q | tail -2` (ATENÇÃO: o teste F0 `test_v05...` não existe; se algum teste F0 asserta `/vector`, atualize-o para `/vetor` — mudança esperada, cite no report).

- [ ] **Step 5: Commit** — `git add api/canvas_validate.py api/canvas_store.py tests/test_canvas_validate.py tests/test_canvas_store.py && git commit -m "feat(canvas-f1): fork mirrors for canvas v0.5 (vetor key, 8 intents, method fields, legacy read-normalization)"`

---

### Task 2: Hardening do F0 (returncode, id único, 404 genérico)

**Files:** Modify `api/canvas_enquadrador.py`, `api/canvas_store.py`, `api/canvas_tarefas.py` + testes correspondentes

- [ ] **Step 1: Testes primeiro** (acrescentar):

```python
# tests/test_canvas_enquadrador.py
def test_call_llm_falha_de_comando_erro_diagnostico(acervo, monkeypatch):
    monkeypatch.setenv("CANVAS_LLM_CMD", "false")  # exit 1, stdout vazio
    core, errors = canvas_enquadrador.enquadrar("x")
    assert errors and any("exit" in e or "código" in e for e in errors)

# tests/test_canvas_store.py
def test_canvas_id_unico_mesmo_segundo(acervo):
    a, _ = canvas_store.create_draft("mesmo titulo")
    b, _ = canvas_store.create_draft("mesmo titulo")
    assert a != b

# tests/test_canvas_routes.py
def test_get_inexistente_nao_vaza_caminho(acervo):
    h = FakeHandler()
    from urllib.parse import urlparse
    canvas_tarefas.handle_canvas_get(h, urlparse("/api/canvas/get?canvas_id=canvas_20260101_000000_x0"))
    assert h.status == 404
    body = h.wfile.getvalue().decode()
    assert "/home/" not in body and "_tasks" not in body
```

- [ ] **Step 2: RED**, depois implementar:
  - `_call_llm`: capturar `stderr=subprocess.PIPE`; após `run`: `if proc.returncode != 0: raise RuntimeError(f"CANVAS_LLM_CMD exit {proc.returncode}: {proc.stderr.decode('utf-8','replace')[-200:]}")`.
  - `new_canvas_id`: sufixo `_{os.getpid() % 1000:03d}{next(_SEQ):02d}` onde `_SEQ = itertools.count()` no módulo (determinístico, sem random — regra do harness) e ajuste do regex de `_canvas_path` para `canvas_[0-9]{8}_[0-9]{6}_[a-z0-9-]+_[0-9]{5}`. ATENÇÃO: teste F0 `test_canvas_id_invalido_rejeitado` continua válido; o teste de cleanup usa ids gerados — nada a mudar.
  - `handle_canvas_get` (get): no except, `_j(handler, {"error": "canvas desconhecido"}, 404)`.
- [ ] **Step 3: GREEN** — mesmos 4 arquivos de teste, `| tail -2`.
- [ ] **Step 4: Commit** — `fix(canvas-f1): diagnostic seam errors, unique canvas ids, generic 404`

---

### Task 3: Enquadrador in-process (ADR-CT-04, sem seam por default)

**Files:** Modify `api/canvas_enquadrador.py`; Modify `tests/test_canvas_enquadrador.py`

**Interfaces:** `enquadrar(texto, session=None)` — ordem de resolução do LLM: (1) env `CANVAS_LLM_CMD` (override p/ testes/dev, comportamento atual); (2) **in-process**: `agent.auxiliary_client.call_llm` com runtime resolvido, sob `profile_env_for_background_worker`; (3) indisponível → `({}, ["enquadrador indisponível: <causa>"])` (estado calmo, nunca crash). Parsing passa a usar a lógica de `_extract_json` (mais robusta que find-braces p/ cercas markdown).

- [ ] **Step 1: Testes primeiro**:

```python
def test_inprocess_usado_quando_sem_seam(acervo, monkeypatch):
    monkeypatch.delenv("CANVAS_LLM_CMD", raising=False)
    chamado = {}

    def fake_inprocess(prompt):
        chamado["p"] = prompt
        return ('{"focus": "F", "vetor": "execucao", "intent_type": "produzir"}')

    monkeypatch.setattr(canvas_enquadrador, "_call_llm_inprocess", fake_inprocess)
    core, errors = canvas_enquadrador.enquadrar("fazer X")
    assert errors == [] and chamado


def test_inprocess_indisponivel_estado_calmo(acervo, monkeypatch):
    monkeypatch.delenv("CANVAS_LLM_CMD", raising=False)

    def boom(prompt):
        raise RuntimeError("agent runtime offline")

    monkeypatch.setattr(canvas_enquadrador, "_call_llm_inprocess", boom)
    core, errors = canvas_enquadrador.enquadrar("x")
    assert core == {} and any("indisponível" in e for e in errors)


def test_extract_json_com_cerca_markdown(acervo, monkeypatch):
    monkeypatch.setenv("CANVAS_LLM_CMD", "true")
    monkeypatch.setattr(
        canvas_enquadrador, "_call_llm",
        lambda p: '```json\n{"focus": "F", "vetor": "execucao", "intent_type": "produzir"}\n```')
    core, errors = canvas_enquadrador.enquadrar("x")
    assert errors == []
```

- [ ] **Step 2: RED**, depois implementar em `canvas_enquadrador.py`:

```python
def _call_llm_inprocess(prompt: str) -> str:
    """Turno único in-process (ADR-CT-04). Precedente: streaming.py title_generation
    + acervo_studio_agent._run_agent_text (profile env + runtime resolve)."""
    from api import profiles as profiles_api
    from api.acervo_studio_agent import _resolve_main_runtime
    with profiles_api.profile_env_for_background_worker(
            profiles_api.get_active_profile()):
        runtime = _resolve_main_runtime(None)
        from agent.auxiliary_client import call_llm
        resp = call_llm(provider=runtime["provider"], model=runtime["model"],
                        base_url=runtime.get("base_url"),
                        api_key=runtime.get("api_key"),
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0)
        return resp.choices[0].message.content or ""
```

`_call_llm` vira roteador: seam se `CANVAS_LLM_CMD` setado; senão `_call_llm_inprocess`; exceções do in-process → capturadas em `enquadrar` como `"enquadrador indisponível: {exc}"` (substituir a mensagem "enquadrador falhou" APENAS nesse ramo — o ramo seam mantém as mensagens atuais dos testes F0). `_parse_json`: adotar extração estilo `_extract_json` (strip de cercas ```/```json antes do find-braces). NOTA: as chaves exatas de `_resolve_main_runtime`/assinatura de `call_llm` foram verificadas no recon (acervo_studio_agent.py:43-113; auxiliary_client.py:6909) — se divergirem no código real, ajuste a chamada e CITE a divergência no report (não improvise além disso).

- [ ] **Step 3: GREEN** (arquivo todo) + **Step 4: Commit** — `feat(canvas-f1): in-process enquadrador via auxiliary_client under profile env (ADR-CT-04); seam kept as test override`

---

### Task 4: Job+poll + SSE com replay por cursor (mata double-connect)

**Files:** Modify `api/canvas_tarefas.py`; Modify `tests/test_canvas_routes.py`

**Interfaces (pós-tarefa):**
- Registry novo: `CANVAS_JOBS: dict[str, dict]` = `{"status": "running|done", "valid": bool|None, "errors": [], "events": [(nome, payload), ...], "cond": threading.Condition()}`. Producers dão `append` + `notify_all`; NENHUM consumo destrutivo (substitui a `queue.Queue` single-consumer — replay ilimitado, N leitores).
- `POST /api/canvas/draft` (mantido) → `{canvas_id}` e inicia job. `GET /api/canvas/job?canvas_id=` → `{status, valid, errors, n_events}`. `GET /api/canvas/stream?canvas_id=&since=N` → SSE com frames `id: <cursor>` + `event:` + `data:`, replay de `events[N:]`, keepalive `: keepalive` a cada 30s de silêncio, encerra após emitir `canvas_done` (forma dos frames = SSE do kanban). `GET /api/canvas/list` → `[{canvas_id, focus, vetor, status}]` lendo `_tasks/canvas_*/canvas.yaml` (para o Hangar). Sweep timer mantido (limpa `CANVAS_JOBS` após `_CLEANUP_DELAY` do done).

- [ ] **Step 1: Testes primeiro** (substituem os drenos de queue do F0 — atualize os 6 testes existentes para o novo registry; novos):

```python
def test_replay_por_cursor_dois_leitores(acervo, monkeypatch):
    monkeypatch.setattr(canvas_tarefas, "enquadrar",
                        lambda t, session=None: ({"focus": "F", "vetor": "execucao",
                                                  "intent_type": "produzir"}, []))
    h = FakeHandler()
    canvas_tarefas.handle_canvas_post(h, "/api/canvas/draft", {"text": "x"})
    cid = json.loads(h.wfile.getvalue())["canvas_id"]
    job = canvas_tarefas.CANVAS_JOBS[cid]
    with job["cond"]:
        job["cond"].wait_for(lambda: job["status"] == "done", timeout=5)
    nomes = [n for n, _ in job["events"]]
    assert nomes == ["canvas_snapshot", "canvas_delta", "canvas_done"]
    assert nomes == [n for n, _ in job["events"]]  # segunda leitura idêntica (replay)


def test_poll_endpoint(acervo, monkeypatch):
    monkeypatch.setattr(canvas_tarefas, "enquadrar",
                        lambda t, session=None: ({"focus": "F", "vetor": "execucao",
                                                  "intent_type": "produzir"}, []))
    h = FakeHandler()
    canvas_tarefas.handle_canvas_post(h, "/api/canvas/draft", {"text": "x"})
    cid = json.loads(h.wfile.getvalue())["canvas_id"]
    job = canvas_tarefas.CANVAS_JOBS[cid]
    with job["cond"]:
        job["cond"].wait_for(lambda: job["status"] == "done", timeout=5)
    h2 = FakeHandler()
    from urllib.parse import urlparse
    canvas_tarefas.handle_canvas_get(h2, urlparse(f"/api/canvas/job?canvas_id={cid}"))
    body = json.loads(h2.wfile.getvalue())
    assert body["status"] == "done" and body["valid"] is True and body["n_events"] == 3


def test_list_para_o_atrio(acervo, monkeypatch):
    from api import canvas_store
    cid, _ = canvas_store.create_draft("listar isto")
    h = FakeHandler()
    from urllib.parse import urlparse
    canvas_tarefas.handle_canvas_get(h, urlparse("/api/canvas/list"))
    lista = json.loads(h.wfile.getvalue())
    assert any(item["canvas_id"] == cid for item in lista)
```

- [ ] **Step 2: RED** → implementar a troca `queue.Queue` → registry `CANVAS_JOBS` (helper `_emit(cid, nome, payload)`: `with job["cond"]: job["events"].append((nome, payload)); job["cond"].notify_all()`; `_run_enquadrador` usa `_emit` e seta `status/valid/errors` antes do `canvas_done`); SSE handler: parse `since` (default 0), loop `while True`: emite `events[cursor:]` com `id:`, se viu `canvas_done` → break; senão `cond.wait(timeout=30)`; em timeout escreve `: keepalive\n\n`. `enquadrar` agora recebe `session=None` (repasse do T3). `/api/canvas/list`: iterar `tasks_dir().glob("canvas_*/canvas.yaml")`, `safe_load` de cada, extrair `{canvas_id, focus, vetor}` (com a normalização de leitura do T1), status = `CANVAS_JOBS.get(cid,{}).get("status","idle")`; limite 50, mais recentes primeiro (ordenar por nome desc — o id embute timestamp).
- [ ] **Step 3: GREEN** (test_canvas_routes.py inteiro; conte os testes e cite) + **Step 4: Commit** — `feat(canvas-f1): replayable event log + job poll + list endpoint; SSE reattach via since cursor (ADR-CT-04)`

---

### Task 5: Edição in loco (PATCH validado) + preview do brief

**Files:** Modify `api/canvas_tarefas.py`; Create `api/canvas_brief.py`; Modify `tests/test_canvas_routes.py`; Create `tests/test_canvas_brief.py`

**Interfaces:**
- `POST /api/canvas/patch {canvas_id, ops:[...]}` → aplica no doc (whitelist de paths editáveis: `/focus`, `/vetor`, `/intent_type`, `/shape`, `/done_criteria`, `/verification`, `/microversos/primary`, `/microversos/related/*`, `/gaps/*`, `/scope/*`, `/assumptions/*`, `/artifacts/expected/*`, `/next_moves/*` — op em path fora da whitelist → 400 `{"error": "path não editável"}`) → salva → re-extrai o núcleo do doc (`_doc_to_core`) → `validate_core` → resposta `{ok, valid, errors}` e `_emit(cid, "canvas_delta", ops)` + `_emit(cid, "canvas_validity", {valid, errors})`.
- `api/canvas_brief.py`: `compile_brief(doc: dict) -> str` — determinístico, PT-BR, SEM LLM: cabeçalho com focus; postura pelo vetor (3 frases fixas, uma por vetor — execucao/evolucao/manutencao; `ambiguo` → erro `ValueError("resolva o vetor antes de lançar")`); "Pronto quando: {done_criteria} — Verificação: {verification}" (se vazios → linha "DEFINIR PRONTO na sessão"); microverso âncora/apoios; premissas = gaps abertos com prefixo "Premissa (gap aberto):"; scope/assumptions/artifacts esperados/next_moves quando não vazios. `GET /api/canvas/brief?canvas_id=` → `{"brief": texto}`.
- `_doc_to_core(doc) -> dict`: inverso de `_CORE_TO_DOC` (extrai as chaves do núcleo do documento; `microversos.primary`→`microverso_primary`; ausentes ficam fora). Vive em `canvas_store.py`.

- [ ] **Step 1: Testes primeiro** — `tests/test_canvas_brief.py`:

```python
import pytest

from api import canvas_brief

DOC = {"focus": "Renegociar contrato Alfa", "vetor": "execucao",
       "intent_type": "produzir", "shape": "tarefa",
       "done_criteria": "oficio aprovado", "verification": "manifest+receipt",
       "microversos": {"primary": "comercial", "related": ["juridico"]},
       "gaps": ["Teto de desconto?"], "scope": [], "assumptions": [],
       "artifacts": {"existing": [], "expected": ["oficio.docx"]},
       "next_moves": []}


def test_brief_contem_blocos_essenciais():
    b = canvas_brief.compile_brief(dict(DOC))
    for trecho in ("Renegociar contrato Alfa", "oficio aprovado",
                   "manifest+receipt", "comercial", "juridico",
                   "Premissa (gap aberto): Teto de desconto?", "oficio.docx"):
        assert trecho in b, trecho


def test_brief_rejeita_ambiguo():
    with pytest.raises(ValueError):
        canvas_brief.compile_brief(dict(DOC, vetor="ambiguo"))


def test_brief_e_deterministico():
    assert canvas_brief.compile_brief(dict(DOC)) == canvas_brief.compile_brief(dict(DOC))
```

Em `tests/test_canvas_routes.py`:

```python
def test_patch_valido_persiste_e_emite(acervo):
    from api import canvas_store
    cid, _ = canvas_store.create_draft("editar")
    canvas_tarefas.CANVAS_JOBS[cid] = canvas_tarefas._new_job()
    h = FakeHandler()
    assert canvas_tarefas.handle_canvas_post(h, "/api/canvas/patch", {
        "canvas_id": cid,
        "ops": [{"op": "replace", "path": "/focus", "value": "Foco editado"},
                 {"op": "replace", "path": "/vetor", "value": "execucao"},
                 {"op": "replace", "path": "/intent_type", "value": "produzir"}]})
    assert json.loads(h.wfile.getvalue())["valid"] is True
    assert canvas_store.load_canvas(cid)["focus"] == "Foco editado"


def test_patch_path_fora_da_whitelist_400(acervo):
    from api import canvas_store
    cid, _ = canvas_store.create_draft("editar")
    h = FakeHandler()
    canvas_tarefas.handle_canvas_post(h, "/api/canvas/patch", {
        "canvas_id": cid, "ops": [{"op": "replace", "path": "/canvas_id", "value": "hack"}]})
    assert h.status == 400
```

- [ ] **Step 2: RED** → implementar (`_WHITELIST` como tupla de regexes; `_new_job()` helper extraído na T4; brief compiler ~60 linhas com f-strings por seção, listas só quando não vazias). **Step 3: GREEN** (3 arquivos de teste tocados). **Step 4: Commit** — `feat(canvas-f1): validated in-place patch endpoint + deterministic brief compiler/preview`

---

### Task 6: Launch backend (register + sessão + stage; front dispara o chat)

**Files:** Modify `api/canvas_tarefas.py`; Modify `tests/test_canvas_routes.py`

**Interfaces:** `POST /api/canvas/launch {canvas_id}` →
1. `doc = load_canvas` → `compile_brief(doc)` (ValueError ambiguo → 400 com a mensagem);
2. grava `brief.md` em `_tasks/<cid>/brief.md`;
3. **register**: `subprocess.run([sys.executable, str(acervo_root()/"global/tools/harness/register_task_from_canvas.py"), "--canvas", str(_tasks/<cid>/canvas.yaml), "--title", doc["focus"][:80]], env={**os.environ, "ACERVO": str(acervo_root())}, capture_output=True)` — returncode ≠0 → 500 `{"error": "register falhou", "detail": stderr[-200:]}`; extrai `task_id` do stdout (o script imprime; fallback: glob mais recente `task_*`);
4. **sessão**: `from api.models import new_session` → `s = new_session()`;
5. **stage**: `from api.upload import _upload_destination` + cópia dos bytes de `canvas.yaml` e `brief.md` → montar attachments `[{name, path, size, mime: "text/markdown"/"text/yaml", is_image: False}]` (mesmo shape do stage endpoint);
6. atualizar `links.yaml` da task com `session_id` (append yaml simples) e `_emit(cid, "canvas_launched", {...})`;
7. resposta `{"session_id": s.session_id, "task_id": ..., "brief": brief, "attachments": [...]}` — **o front chama `POST /api/chat/start`** com esses campos (mesmo contrato do `messages.js`).

- [ ] **Step 1: Testes primeiro**:

```python
def test_launch_cria_task_sessao_e_attachments(acervo, monkeypatch, tmp_path):
    from api import canvas_store
    cid, doc = canvas_store.create_draft("Renegociar Alfa")
    doc.update({"focus": "Renegociar Alfa", "vetor": "execucao",
                "intent_type": "produzir"})
    canvas_store.save_canvas(cid, doc)
    canvas_tarefas.CANVAS_JOBS[cid] = canvas_tarefas._new_job()

    class FakeSession:
        session_id = "sess123"

    monkeypatch.setattr(canvas_tarefas, "_new_session", lambda: FakeSession())
    monkeypatch.setattr(canvas_tarefas, "_stage_file",
                        lambda sid, p: {"name": p.name, "path": str(p),
                                        "size": p.stat().st_size,
                                        "mime": "text/plain", "is_image": False})
    reg = {"called": False}

    def fake_register(canvas_path, title):
        reg["called"] = True
        return "task_20260724_renegociar-alfa_120000"

    monkeypatch.setattr(canvas_tarefas, "_register_task", fake_register)
    h = FakeHandler()
    assert canvas_tarefas.handle_canvas_post(h, "/api/canvas/launch",
                                             {"canvas_id": cid})
    body = json.loads(h.wfile.getvalue())
    assert body["session_id"] == "sess123" and reg["called"]
    assert len(body["attachments"]) == 2 and "Renegociar Alfa" in body["brief"]


def test_launch_ambiguo_400(acervo):
    from api import canvas_store
    cid, doc = canvas_store.create_draft("x")
    doc["vetor"] = "ambiguo"; canvas_store.save_canvas(cid, doc)
    h = FakeHandler()
    canvas_tarefas.handle_canvas_post(h, "/api/canvas/launch", {"canvas_id": cid})
    assert h.status == 400
```

- [ ] **Step 2: RED** → implementar com os seams finos `_new_session()`, `_stage_file(session_id, path)`, `_register_task(canvas_path, title)` (imports tardios dentro deles — testável e sem custo de import no boot). **Step 3: GREEN** (arquivo todo). **Step 4: Commit** — `feat(canvas-f1): launch pipeline — register task, create session, stage brief+canvas; front fires chat/start`

---

### Task 7: UI Hangar + Cockpit (reescrita de `static/canvas-tarefas.js` + css)

**Files:** Modify `static/canvas-tarefas.js` (reescrita completa), `static/canvas-tarefas.css`, `static/canvas-dev.html` (só se o id de mount mudar)

**Interfaces/Requisitos (o código completo é longo — este é o ÚNICO passo do plano onde o implementer escreve JS a partir de spec fechada; TODA decisão está fixada abaixo, nada é escolha dele):**
1. IIFE, global `window.CVT = {toggle, iniciar, abrirCockpit, applyPatch, esc}`; namespace `.cvt-*`; `esc = (s) => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))` — **toda** interpolação passa por `esc()`.
2. **Superfície**: `_build()` cria `<div id="canvasRoot" hidden>` e REPARENTA para `<body>` (lição do Studio); `role="dialog" aria-modal="true"`; topo `.cvt-top` com botões [Chat] [Acervo] [Canvas] + input de intake; corpo `.cvt-body` com duas views alternáveis: `#cvt-atrio` e `#cvt-sala`. Botão Chat → `_close()`; botão Acervo → `_close()` + `typeof acervoStudioToggle==="function" && acervoStudioToggle()`.
3. **Launcher próprio** `#cvtLauncher` (botão flutuante "🗺️ Canvas", posição fixa acima do `#axsLauncher`); + **injeção runtime degradável** no Studio: em `DOMContentLoaded`+800ms, se `document.querySelector('#acervoStudioRoot .axs-mode')` existir, append `<button data-axs="canvas">Canvas</button>` com click → `_close Studio via acervoStudioToggle()` + `CVT.toggle()`; se não existir, silenciosamente não injeta (launcher basta). `acervo-studio.js` NÃO é editado.
4. **Hangar**: fetch `/api/canvas/list` → cards (focus ou "(sem foco)", vetor com classe de cor F0, status). Click → `abrirCockpit(cid)`. Intake: input + botão "Enquadrar" → POST `/api/canvas/draft` → `abrirCockpit(cid)` imediato (canvas nasce na Cockpit, preenchendo via stream).
5. **Cockpit**: snapshot via GET `/api/canvas/get`; stream `EventSource('/api/canvas/stream?canvas_id='+cid+'&since='+cursor)` com handlers p/ `canvas_snapshot|canvas_delta|canvas_validity|canvas_done|canvas_launched`; **`es.onerror` → status "reconectando…" e re-attach com o cursor corrente (o `id:` de cada frame é o cursor — guardar `e.lastEventId`)**; guard de re-entrância: `iniciar()`/`abrirCockpit()` fecham `es` anterior antes de abrir novo.
6. **Zonas editáveis** (a regra de render): cada campo editável renderiza como `<span class="cvt-edit" data-path="/focus" contenteditable="false">…</span>` + lápis; click → vira `<input>`/`<select>` (selects para `vetor` [4 opções], `intent_type` [8], `shape` [3]); blur/Enter → `POST /api/canvas/patch {canvas_id, ops:[{op:"replace", path, value}]}` → badge de validade atualizada pela resposta (`valid/errors`); Esc → cancela. Listas (`gaps`, `scope`, `assumptions`, `microversos.related`, `artifacts.expected`, `next_moves`): item com [×] (remove → op remove por índice) + input "+ adicionar" (op add `/campo/-`).
7. **Zona Pronto**: `done_criteria` + `verification` com destaque; vazios → chip âmbar "definir pronto".
8. **Vetor ambiguo** → cartão fixo com 3 botões (executar/explorar/manter) que fazem patch de `/vetor`.
9. **Preview do brief**: botão "Preview do brief" → GET `/api/canvas/brief` → `<pre>` em painel colapsável (esc()).
10. **Lançar**: botão primário → POST `/api/canvas/launch` → com a resposta, POST `/api/chat/start {session_id, message: brief, attachments}` → toast "Cockpit lançada — sessão {id}" + botão "ir para o chat" (`_close()` + se existir `typeof loadSession==="function"` → `loadSession(session_id)`; senão instrução textual). Erros 400/500 → status vermelho com a mensagem.
11. `canvas-dev.html` continua funcionando como harness (mount = mesmo root; se necessário só atualizar o script/ids).
12. **Orçamento**: JS ≤ ~550 linhas; se o implementer projetar >700, PARAR e reportar (gatilho ADR-CT-05 em risco). CSS: estender o F0 (~+60 linhas: top bar, cards, edit affordances, badges).

- [ ] **Step 1: Implementar** (sem TDD de browser; a verificação é E2E na T9 — mas rode `npm run lint:runtime` se existir no package.json: cite a saída).
- [ ] **Step 2: Sanidade estática** — `node --check static/canvas-tarefas.js` (Expected: sem erro) e `wc -l static/canvas-tarefas.js` (cite; ≤~550).
- [ ] **Step 3: Smoke com stub** — servidor + `CANVAS_LLM_CMD` ABSOLUTO p/ stub (lição F0), abrir a superfície pelo launcher, 1 frase → Cockpit preenche → editar focus in loco → badge válida → preview → **NÃO lançar ainda** (launch real é T9). Screenshot `.superpowers/sdd/t7-sala-stub.png`. Parar o servidor.
- [ ] **Step 4: Commit** — `feat(canvas-f1): Atrio+Cockpit surface — editable zones, ambiguity card, brief preview, launch wiring (vanilla, escaped)`

---

### Task 8: Contrato COLLAB + MOD-012

**Files:** Create `/home/elder/projetos/projetob/.harness/contracts/exocortex-hermes-webui.md` (umbrella!); Modify `EXOCRTX_MODIFICATIONS.md`

- [ ] **Step 1: Contrato** — seções: Partes (exocortex.saas = dono do método/harness; hermes-webui = superfície); Superfícies: (a) provisionamento (`provision/sources/sources.lock.yaml`, step-10b); (b) **canvas v0.5** (schema núcleo + template documento; chave `vetor`; enums; ADR-CT-06); (c) endpoints `/api/canvas/*` (draft/get/list/job/stream?since/patch/brief/launch — request/response de cada, 10 linhas); (d) eventos SSE (`canvas_snapshot|canvas_delta|canvas_validity|canvas_done|canvas_launched`, frames id/event/data, semântica de cursor); (e) pipeline de launch (register → session/new → stage shape `{name,path,mime,size,is_image}` → chat/start). Regra de mudança: aditivo ok; rename/remoção = COLLAB novo. Status: ativo a partir do merge F1b.
- [ ] **Step 2: MOD-012** no `EXOCRTX_MODIFICATIONS.md` — uma linha por superfície nova, modelo da MOD-011; registrar também o achado: "MOD-008 ctxTray: `pendingContextAttachments` sem consumidor no send() — bug pré-existente, launch do canvas não depende dele".
- [ ] **Step 3: Commits** — umbrella: `git -C /home/elder/projetos/projetob add .harness/contracts/exocortex-hermes-webui.md && git -C /home/elder/projetos/projetob commit -m "docs(harness): exocortex<->hermes-webui contract v1 (canvas v0.5 + /api/canvas/* + launch pipeline)"`; fork: `git add EXOCRTX_MODIFICATIONS.md && git commit -m "docs(canvas-f1): MOD-012 catalog entry + ctxTray finding"`. (Pushes só na T9.)

---

### Task 9: Regressão + E2E real + push + gate na #132

- [ ] **Step 1: Suíte completa** — `python3 -m pytest tests/ -q -p no:cacheprovider 2>&1 | tail -3` (~8min). Régua: baseline F0 (12F pré-existentes) + todos os canvas tests novos passando; NENHUMA falha nova (flake credential_pool conhecido: se aparecer, rode-o isolado e cite).
- [ ] **Step 2: E2E REAL** — servidor SEM `CANVAS_LLM_CMD` (in-process!; chaves via `set -a; source ~/.hermes/.env; set +a` antes do start; nunca ecoar): frase real → Cockpit preenche (enquadrador in-process) → editar 1 campo → definir done_criteria/verification se vazios → Lançar → **verificar na UI nativa que a sessão existe com o brief como 1ª mensagem e os 2 attachments** → screenshot `.superpowers/sdd/t9-launch-real.png` (desta vez com LLM REAL — fecha o caveat do F0) + `ls $ACERVO/_tasks/task_*/` mostrando task.yaml/canvas.yaml/links.yaml + cat do links.yaml com session_id. Parar servidor.
- [ ] **Step 3: Pushes** — fork: `git push origin collab/canvas-tarefas`; umbrella: `git -C /home/elder/projetos/projetob push origin master`.
- [ ] **Step 4: Gate na #132** — `gh issue comment 132 -R elderbernardi/exocortex.saas` (PT-BR): checklist do gate do F1-CHARTER item a item com provas (1 frase→sala lançada→sessão com brief ✓ screenshot real; `_tasks/` completo ✓ ls; edição in loco persiste+re-valida ✓ teste+demo; suíte sem falhas novas ✓ tail). **NÃO fechar a issue** — owner fecha e decide o merge p/ stable.

---

## Self-review do plano (executado na escrita)

- Charter F1 coberto: Hangar mínimo (T4 list + T7), canvas editável/verificável (T5+T7), campos v0.5 (T1, consumindo F1a), enquadrador definitivo (T3, ADR-CT-04), Compile & Launch (T5 brief + T6 + T7 item 10), contrato COLLAB (T8). Insumos do review final do F0: returncode (T2), escape HTML (T7 regra 1), sufixo id (T2), fan-out/replay (T4). Deferido com registro: mapeamento vetor→profile no launch (profile é per-client/cookie — fica p/ F3, anotado no contrato T8 como evolução).
- Fatos de recon citados com file:line no cabeçalho Architecture; pontos de possível divergência de assinatura têm instrução explícita de citar-e-ajustar (T3), nunca improvisar.
- Sem placeholders: única tarefa spec-driven (T7) tem TODAS as decisões fechadas em 12 regras numeradas + orçamento de linhas + gatilho de parada.
