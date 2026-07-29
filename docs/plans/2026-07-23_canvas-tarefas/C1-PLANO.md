# C1 — Des-burocratizar o Cockpit + terminar o E3 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformar o Cockpit do Canvas de Tarefas de formulário burocrático em cartão-que-o-agente-preencheu: a frase vira headline, `vetor`/`intent_type`/`shape` viram chips, microverso vira dropdown dos 13 reais, o método colapsa, e as sugestões do Curador (Acervo/Personas/Skills) viram zonas de 1ª classe dentro do Cockpit — absorvendo a ilha bolt-on.

**Architecture:** UI vanilla no-build. `renderCockpit` (static/canvas-tarefas.js) é reordenado e ganha renderers novos (headline/chips/dropdown/collapse) + containers reservados que a ilha `canvas-curador.js` — mantida como **helper** (`fill()`) — preenche por `getElementById` (mata o hack `#cvt-curador-zone`+`MutationObserver`). Um endpoint aditivo read-only `GET /api/canvas/microversos` alimenta o dropdown. Backends do Curador/enquadrador/brief intocados (reuso). Base: spec `docs/superpowers/specs/2026-07-28-c1-cockpit-declutter-e3-design.md`.

**Tech Stack:** Python stdlib (http.server handler, sem framework), JS vanilla IIFE (sem deps, sem build), pytest keyless (FakeHandler), CSS append-only. Runner: `/home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest`.

## Global Constraints

Copiadas **verbatim** do contrato de execução (`00-INDEX.md` §Contrato) + emenda do owner (2026-07-26). Todo requisito de cada tarefa inclui implicitamente esta seção.

1. **Execute apenas a fase que tem PLANO detalhado.** Charter não é plano.
2. **Escopo é fechado**: toque somente os arquivos listados na tarefa. Precisar de arquivo fora da lista = **pare e reporte**, nunca expanda em silêncio.
3. **Nunca toque** (zona quente): `hermes-webui/static/{ui,messages,sessions,panels,boot}.js`, `static/style.css`, `static/index.html`, e `api/routes.py` (C1 = **0 linhas** em routes.py — o endpoint entra por forward já existente em `handle_canvas_get`).
4. **Zero dependências novas** (pip/npm), **zero build step**, strings de UI em **PT-BR**.
5. **Prova bruta por tarefa (EX-49)**: toda tarefa termina com o output real do comando de verificação. Sem output, a tarefa não está concluída — não marque.
6. **Bounds (fable-method)**: 3 ciclos falha-conserto na mesma verificação → pare, registre tentativas + saída real + hipótese, devolva. 2 buscas sem info nova → pare.
7. **Segredos nunca** em logs/commits/relatórios.
8. **`.quarantine/` não existe para você.**
9. Commits pequenos e frequentes na branch **`collab/canvas-c1`** (fork) do repo indicado pela tarefa; mensagens em inglês, prefixo convencional (`feat:`/`test:`/`docs:`); **verifique a branch no MESMO comando composto do commit**; **NUNCA `git add -A`** (paths explícitos); **nunca `git push`** sem instrução explícita.
10. Ações externas (push, issue, deploy) só quando a tarefa manda.

**Emenda do owner (2026-07-26):** o teto de "8 linhas" de routes.py e "zero deps" foram relaxados — o invariante real é **não perturbar o upstream nesquena** (dep Python pequeno OK sem build). Para C1 nada disso é exercido: **0 linhas routes.py, 0 deps, 0 build**.

**Regras 3/4 reforçadas p/ C1 (checkout compartilhado):** o owner roda sessões paralelas nos MESMOS checkouts. Trabalhe SEMPRE na worktree isolada da branch `collab/canvas-c1` (cortada de `origin/exocortex/stable@18b782da` — NUNCA do HEAD local `14d880b6`, que está 19 commits atrás e sem `canvas_sala.py`/`canvas-sala.js` em disco).

## Invariantes de C1 (todas as tarefas)

- **NÃO quebrar** `canvas-sala.js` (MOD-014/F3): o hook `window.CanvasSala.onCockpitOpen(cid)` em `abrirCockpit` fica **verbatim**.
- **NÃO mudar** `window.CVT` (superfície consumida por `canvas-curador.js` E `canvas-sala.js`): `esc`, `acceptOps: submitOps`, `getCanvas`, `currentCid` intactos.
- **NÃO tocar** o whitelist `_WHITELIST_RAW` (já cobre todo path que chips/dropdown/collapse gravam), nem `sugerir_itens`/`compile_brief`/`canvas_store`.
- **Regra 1 (anti-XSS):** todo valor dinâmico que entra em template `innerHTML` passa por `esc()`.
- **`nature` é SINGULAR** (`persona|template|skill|workflow`): Skills = `nature === "skill"`.

## File Structure

**Fork `hermes-webui` (branch `collab/canvas-c1`):**
- `api/canvas_tarefas.py` — +helper `_list_microversos()` + 1 branch em `handle_canvas_get` (aditivo).
- `static/canvas-tarefas.js` — reorganiza `renderCockpit`; +renderers headline/chips/dropdown/collapse/curadorZones; +state; +listeners; retira card ambíguo.
- `static/canvas-curador.js` — ilha vira helper: mata `_zone()`/`MutationObserver`; `render()`→`fill()`; 3 escritores nature-filtrados; "Atualizar"; `_accept` reordenado; `fill()` cid-guard.
- `static/canvas-tarefas.css` — append-only bloco `MOD-016`.
- `tests/test_canvas_microversos.py` (novo), `tests/test_canvas_ui_c1_source.py` (novo), `tests/test_curador_ui_source.py` (atualizado).
- `EXOCRTX_MODIFICATIONS.md` — entrada MOD-016.

**Umbrella `projetob` (worktree DETACHED em `origin/master@25c36d4`):**
- `.harness/contracts/exocortex-hermes-webui.md` — §(h) aditiva.
- `.harness/changes/2026-07-28_COLLAB_canvas-c1.md` (novo).

**Exocortex `exocortex.saas`:** nenhuma mudança de código (D10).

---

### Task 1: Endpoint `GET /api/canvas/microversos` (backend, aditivo)

**Files:**
- Modify: `api/canvas_tarefas.py` (helper `_list_microversos` após `_list_canvases`; 1 branch em `handle_canvas_get` antes do fallback `/stream`)
- Test: `tests/test_canvas_microversos.py` (novo)

**Interfaces:**
- Consumes: `curador_capabilities._microverso_slugs(root: pathlib.Path) -> list[str]` (curador_capabilities.py:63, já existe: `sorted` de dirs em `root/"micro"` sem prefixo `_`/`.`, `[]` se `micro/` ausente); `canvas_store.acervo_root()` (levanta `RuntimeError` sem acervo); `_j(handler, obj, status=200)`.
- Produces: `_list_microversos() -> list[str]`; rota `GET /api/canvas/microversos` → JSON array de slugs, **200 sempre**.

- [ ] **Step 1: Write the failing test**

Create `tests/test_canvas_microversos.py`:

```python
import io
import json
from urllib.parse import urlparse

from api import canvas_tarefas, canvas_store


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


def test_microversos_lista_slugs_ordenados(tmp_path, monkeypatch):
    micro = tmp_path / "micro"
    for slug in ("gabinete", "comercial", "sales-ai"):
        (micro / slug).mkdir(parents=True)
    monkeypatch.setenv("ACERVO", str(tmp_path))
    h = FakeHandler()
    assert canvas_tarefas.handle_canvas_get(h, urlparse("/api/canvas/microversos"))
    body = json.loads(h.wfile.getvalue())
    assert body == ["comercial", "gabinete", "sales-ai"]  # ordenado
    assert h.status == 200


def test_microversos_ignora_underscore_ocultos_e_arquivos(tmp_path, monkeypatch):
    micro = tmp_path / "micro"
    for name in ("comercial", "_tasks", ".git"):
        (micro / name).mkdir(parents=True)
    (micro / "leiame.txt").write_text("x", encoding="utf-8")
    monkeypatch.setenv("ACERVO", str(tmp_path))
    h = FakeHandler()
    canvas_tarefas.handle_canvas_get(h, urlparse("/api/canvas/microversos"))
    assert json.loads(h.wfile.getvalue()) == ["comercial"]


def test_microversos_sem_acervo_retorna_200_lista_vazia(monkeypatch):
    def _boom():
        raise RuntimeError("ACERVO não encontrado")
    monkeypatch.setattr(canvas_store, "acervo_root", _boom)
    h = FakeHandler()
    assert canvas_tarefas.handle_canvas_get(h, urlparse("/api/canvas/microversos"))
    assert json.loads(h.wfile.getvalue()) == []
    assert h.status == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest tests/test_canvas_microversos.py -q`
Expected: FAIL (a rota devolve `False`/404 — o branch ainda não existe).

- [ ] **Step 3: Write minimal implementation**

Em `api/canvas_tarefas.py`, adicione o helper logo **após** a função `_list_canvases()` (a que serve o `/api/canvas/list`):

```python
def _list_microversos() -> list[str]:
    """GET /api/canvas/microversos (C1/MOD-016) — slugs reais em $ACERVO/micro
    para o dropdown do Cockpit. Reusa a MESMA resolução de acervo e o MESMO
    filtro (_/. ignorados) do Curador; try/except → [] mantém a UI-only
    funcional sem acervo montado (200 [], nunca 500)."""
    from api import curador_capabilities
    try:
        return curador_capabilities._microverso_slugs(canvas_store.acervo_root())
    except Exception:
        return []
```

Em `handle_canvas_get`, insira o branch imediatamente **antes** da linha final `if parsed.path != "/api/canvas/stream": return False` (i.e. depois do bloco `/api/canvas/brief`):

```python
    if parsed.path == "/api/canvas/microversos":
        _j(handler, _list_microversos())
        return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest tests/test_canvas_microversos.py -q`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
cd <worktree> && test "$(git branch --show-current)" = "collab/canvas-c1" && \
git add api/canvas_tarefas.py tests/test_canvas_microversos.py && \
git commit -m "feat(canvas-c1): additive GET /api/canvas/microversos for the Cockpit dropdown"
```

---

### Task 2: Des-burocratizar o topo do Cockpit — headline + chips + dropdown

**Files:**
- Modify: `static/canvas-tarefas.js` (novos consts/state/renderers; `renderCockpit` reordenado; `onCockpitClick` +chip branch −ambig branch; `_build` +change listener; `abrirCockpit` +fetch microversos)
- Modify: `static/canvas-tarefas.css` (append bloco MOD-016 declutter)
- Test: `tests/test_canvas_ui_c1_source.py` (novo)

**Interfaces:**
- Consumes: `GET /api/canvas/microversos` (Task 1); existentes `esc`, `ptrGet`, `editableSpanHtml`, `submitOps`, `VETOR_OPTS`/`INTENT_OPTS`/`SHAPE_OPTS`, `getJSON`, `cockpitHeaderHtml`, `doneZoneHtml`, `listZoneHtml`, `LIST_FIELDS`, `briefSectionHtml`, `launchSectionHtml`.
- Produces: `headlineHtml()`, `chipRowHtml()`, `microversoSelectHtml()`, `ambiguousNudgeHtml()`, `CHIP_GROUPS`, `state.microversos`/`state.microversosLoaded`. (Task 3 adiciona `methodCollapseHtml`; Task 4 adiciona `curadorZonesHtml`+`fill` tail-call.)

- [ ] **Step 1: Write the failing test**

Create `tests/test_canvas_ui_c1_source.py`:

```python
import re
from pathlib import Path


def _js():
    return Path("static/canvas-tarefas.js").read_text(encoding="utf-8")


def _css():
    return Path("static/canvas-tarefas.css").read_text(encoding="utf-8")


def _strip_comments(js):
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)   # block comments
    js = re.sub(r"(?m)//.*$", "", js)               # line comments
    return js


def test_headline_edita_focus_nao_original_input():
    js = _js()
    assert "cvt-headline" in js
    assert 'editableSpanHtml("/focus"' in js
    assert "original_input_summary" in js          # display fallback (dot access)
    assert "/original_input_summary" not in js     # nunca é PATCH target


def test_chips_para_vetor_intent_shape():
    js = _js()
    assert "CHIP_GROUPS" in js
    assert "cvt-chip" in js
    assert "data-value" in js               # data-value é novo (chipHtml); data-field já existia
    assert 'closest(".cvt-chip")' in js
    assert "chip.dataset.field" in js and "chip.dataset.value" in js
    assert "cvt-ambig-btn" not in js               # card ambíguo antigo retirado


def test_microverso_dropdown_change_e_fallback():
    js, css = _js(), _css()
    assert "cvt-microverso-select" in js
    assert 'data-field="/microversos/primary"' in js
    assert "/api/canvas/microversos" in js         # fetch da lista
    assert 'addEventListener("change"' in js       # listener delegado
    assert "includes(cur)" in js                   # fallback fix-2 (valor fora dos slugs)
    assert "cvt-microverso-select" in css


def test_css_declutter_presente():
    css = _css()
    for cls in (".cvt-headline", ".cvt-chiprow", ".cvt-chip", ".cvt-chip.on"):
        assert cls in css
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest tests/test_canvas_ui_c1_source.py -q`
Expected: FAIL (renderers/classes ainda não existem).

- [ ] **Step 3: Write minimal implementation**

**(3a)** Em `static/canvas-tarefas.js`, após o bloco `const GRID_FIELDS = ...` (linha ~36) adicione:

```js
  // C1: os 3 enums fixos viram grupos de chips (não mais pencil+select).
  const CHIP_GROUPS = [
    { label: "Vetor", path: "/vetor", options: VETOR_OPTS },
    { label: "Tipo de intenção", path: "/intent_type", options: INTENT_OPTS },
    { label: "Formato", path: "/shape", options: SHAPE_OPTS },
  ];
```

**(3b)** No objeto `state` (linha ~51), adicione dois campos:

```js
    microversos: [], microversosLoaded: false,
```

**(3c)** Adicione os renderers novos (perto de `fieldZoneHtml`, antes de `renderCockpit`):

```js
  function headlineHtml() {
    // display cai p/ original_input_summary quando focus vazio, mas a edição
    // SEMPRE grava o campo focus (whitelisted); o campo original_input_summary
    // nunca vira PATCH-target. (NÃO escreva um pointer com barra neste comentário:
    // o teste assere que "/original_input_summary" não aparece no arquivo cru.)
    const frase = canvas.focus || canvas.original_input_summary || "";
    return '<div class="cvt-headline">' + editableSpanHtml("/focus", frase) + "</div>";
  }

  function chipHtml(path, value, current) {
    const on = value === current;
    const tint = path === "/vetor" ? " cvt-vetor-" + esc(value) : "";
    return '<button type="button" class="cvt-chip' + (on ? " on" : "") + tint +
      '" data-field="' + esc(path) + '" data-value="' + esc(value) +
      '" aria-pressed="' + (on ? "true" : "false") + '">' + esc(value) + "</button>";
  }

  function chipGroupHtml(g) {
    const current = ptrGet(canvas, g.path);
    return '<div class="cvt-chipgroup" role="group" aria-label="' + esc(g.label) + '">' +
      '<span class="cvt-chipgroup-label">' + esc(g.label) + "</span>" +
      g.options.map((o) => chipHtml(g.path, o, current)).join("") + "</div>";
  }

  function microversoSelectHtml() {
    const cur = ptrGet(canvas, "/microversos/primary");
    const slugs = state.microversos || [];
    // fix-2: sem lista (endpoint [] / sem acervo) OU valor guardado fora dos 13
    // slugs → controle free-text ✎, que sempre mostra o valor real (não deixa o
    // <select> auto-selecionar o slug 0 silenciosamente).
    if (!slugs.length || (cur && !slugs.includes(cur))) {
      return '<div class="cvt-chipgroup"><span class="cvt-chipgroup-label">Microverso</span>' +
        editableSpanHtml("/microversos/primary", cur) + "</div>";
    }
    const placeholder = cur ? "" :
      '<option value="" selected disabled>microverso…</option>';
    const opts = slugs.map((s) =>            // fix-4: esc() no value e no label
      '<option value="' + esc(s) + '"' + (s === cur ? " selected" : "") + ">" +
      esc(s) + "</option>").join("");
    return '<div class="cvt-chipgroup"><span class="cvt-chipgroup-label">Microverso</span>' +
      '<select class="cvt-microverso-select" data-field="/microversos/primary">' +
      placeholder + opts + "</select></div>";
  }

  function chipRowHtml() {
    return '<div class="cvt-chiprow">' +
      CHIP_GROUPS.map(chipGroupHtml).join("") + microversoSelectHtml() + "</div>";
  }

  function ambiguousNudgeHtml() {
    return '<div class="cvt-ambig-nudge"><span class="cvt-chip-amber">' +
      "resolver: escolha o vetor</span></div>";
  }
```

**(3d)** DELETE a função `ambiguousCardHtml()` (linhas ~161-166) — substituída por `ambiguousNudgeHtml`. DELETE também `const GRID_FIELDS = ...` (linhas ~36-37) e `function fieldZoneHtml(...)` (linhas ~137-139): renderCockpit deixa de usá-los (os enums viram chips, focus vira headline), então virariam dead code. **NÃO** remova `FIELDS`/`FIELD_BY_PATH` — seguem usados por `startEdit` (done_criteria/verification no colapso + fallback free-text do microverso, que casa `FIELD_BY_PATH["/microversos/primary"]`).

**(3e)** Substitua o corpo de `renderCockpit()` (linhas ~187-197) por (Task 2: topo novo, método/listas ainda antigos — Task 3 colapsa):

```js
  function renderCockpit() {
    if (!canvas) return;
    const el = _root().querySelector("#cvt-cockpit");
    let html = cockpitHeaderHtml();
    html += headlineHtml();
    if (canvas.vetor === "ambiguo") html += ambiguousNudgeHtml();
    html += chipRowHtml();
    html += '<div class="cvt-zona cvt-zona-pronto">' + doneZoneHtml() + "</div>";
    html += '<div class="cvt-canvas">' + LIST_FIELDS.map(listZoneHtml).join("") + "</div>";
    html += briefSectionHtml() + launchSectionHtml();
    el.innerHTML = html;
  }
```

**(3f)** Em `onCockpitClick`, **remova** o branch `ambigBtn` (linhas ~308-309) e adicione o branch de chip (mesmo lugar, após o branch `.cvt-x`):

```js
    const chip = e.target.closest(".cvt-chip");
    if (chip) { submitOps([{ op: "replace", path: chip.dataset.field, value: chip.dataset.value }]); return; }
```

**(3g)** Em `_build`, após o listener de `keydown` de `#cvt-cockpit` (linha ~456), adicione o listener `change` delegado para o dropdown:

```js
    root.querySelector("#cvt-cockpit").addEventListener("change", (e) => {
      const sel = e.target.closest(".cvt-microverso-select");
      if (sel) submitOps([{ op: "replace", path: sel.dataset.field, value: sel.value }]);
    });
```

**(3h)** Em `abrirCockpit`, logo após `switchView("cockpit");` (linha ~397) e antes de `status("carregando…")`, adicione o fetch memoizado:

```js
    if (!state.microversosLoaded) {
      try { state.microversos = await getJSON("/api/canvas/microversos"); }
      catch (_) { state.microversos = []; }
      state.microversosLoaded = true;
    }
```

**(3i)** Em `static/canvas-tarefas.css`, **append** ao final do arquivo:

```css
/* MOD-016 (C1) — Cockpit declutter: headline + chips + microverso dropdown */
.cvt-headline { font-size: 1.15rem; font-weight: 600; margin: .2rem 0 .8rem; }
.cvt-headline .cvt-field { display: inline-flex; }
.cvt-chiprow { display: flex; flex-wrap: wrap; gap: .8rem 1.2rem; align-items: center; margin-bottom: 1rem; }
.cvt-chipgroup { display: flex; flex-wrap: wrap; gap: .3rem; align-items: center; }
.cvt-chipgroup-label { font-size: .7rem; text-transform: uppercase; letter-spacing: .06em; color: #9a9ab0; margin-right: .2rem; }
.cvt-chip { padding: .25rem .7rem; border-radius: 999px; border: 1px solid #2a2a45; background: #1c1c2e; color: #9a9ab0; cursor: pointer; font: inherit; font-size: .85rem; }
.cvt-chip:hover { border-color: #5b5bd6; }
.cvt-chip.on { background: #242438; border-color: #5b5bd6; color: #e8e8f0; }
.cvt-microverso-select { padding: .25rem .5rem; border-radius: 8px; border: 1px solid #2a2a45; background: #1c1c2e; color: inherit; font: inherit; }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest tests/test_canvas_ui_c1_source.py tests/test_canvas_routes.py -q`
Expected: PASS (o novo source-lint + a suíte de rotas existente verde — regressão zero no patch/SSE/launch).

- [ ] **Step 5: Commit**

```bash
cd <worktree> && test "$(git branch --show-current)" = "collab/canvas-c1" && \
git add static/canvas-tarefas.js static/canvas-tarefas.css tests/test_canvas_ui_c1_source.py && \
git commit -m "feat(canvas-c1): declutter Cockpit top — headline + chips + microverso dropdown"
```

---

### Task 3: Colapsar o método atrás de "Detalhes do método ▸"

**Files:**
- Modify: `static/canvas-tarefas.js` (`LIST_BY_PATH`; `methodCollapseHtml`; `renderCockpit` main-list = só gaps+artifacts; `onCockpitClick` +toggle; `state.methodOpen`)
- Modify: `static/canvas-tarefas.css` (append collapse)
- Test: `tests/test_canvas_ui_c1_source.py` (adiciona 1 teste)

**Interfaces:**
- Consumes: `LIST_FIELDS`, `listZoneHtml`, `doneZoneHtml`, `state` (Task 2).
- Produces: `LIST_BY_PATH`, `methodCollapseHtml()`, `state.methodOpen`. renderCockpit passa a chamar `methodCollapseHtml()` e a renderizar só `/gaps`+`/artifacts/expected` no fluxo principal.

- [ ] **Step 1: Write the failing test**

Adicione a `tests/test_canvas_ui_c1_source.py`:

```python
def test_detalhes_metodo_colapsado_via_state():
    js = _js()
    assert "cvt-collapse-toggle" in js
    assert "state.methodOpen" in js
    assert "methodCollapseHtml" in js
    # os campos de método moram DENTRO do colapso (via LIST_BY_PATH), não no fluxo
    for expr in ('LIST_BY_PATH["/scope"]', 'LIST_BY_PATH["/assumptions"]',
                 'LIST_BY_PATH["/next_moves"]', 'LIST_BY_PATH["/microversos/related"]'):
        assert expr in js
    # o grid plano antigo (todas as listas) foi desmontado
    assert "LIST_FIELDS.map(listZoneHtml)" not in js
    # fluxo principal = só lacunas + artefatos
    assert 'LIST_BY_PATH["/gaps"]' in js
    assert 'LIST_BY_PATH["/artifacts/expected"]' in js
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest tests/test_canvas_ui_c1_source.py::test_detalhes_metodo_colapsado_via_state -q`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

**(3a)** Em `static/canvas-tarefas.js`, após `const LIST_FIELDS = [...]` (linha ~46), adicione:

```js
  const LIST_BY_PATH = {};
  LIST_FIELDS.forEach((f) => { LIST_BY_PATH[f.path] = f; });
```

**(3b)** No objeto `state`, adicione `methodOpen: false,` (junto de `microversos`/`microversosLoaded`).

**(3c)** Adicione `methodCollapseHtml` (perto de `doneZoneHtml`):

```js
  function methodCollapseHtml() {
    // state.methodOpen threaded no state (igual state.valid) — sobrevive ao
    // el.innerHTML wholesale de cada frame SSE. Corpo por render condicional.
    const open = !!state.methodOpen;
    const body = open ? (
      '<div class="cvt-collapse-body">' +
        '<div class="cvt-zona cvt-zona-pronto">' + doneZoneHtml() + "</div>" +
        '<div class="cvt-canvas">' +
          listZoneHtml(LIST_BY_PATH["/scope"]) +
          listZoneHtml(LIST_BY_PATH["/assumptions"]) +
          listZoneHtml(LIST_BY_PATH["/next_moves"]) +
          listZoneHtml(LIST_BY_PATH["/microversos/related"]) +
        "</div></div>"
    ) : "";
    return '<div class="cvt-collapse">' +
      '<button type="button" class="cvt-collapse-toggle cvt-link">' +
      (open ? "▾" : "▸") + " Detalhes do método</button>" + body + "</div>";
  }
```

**(3d)** Substitua o corpo de `renderCockpit()` (versão da Task 2) por (fluxo principal = só gaps+artifacts; método via collapse):

```js
  function renderCockpit() {
    if (!canvas) return;
    const el = _root().querySelector("#cvt-cockpit");
    let html = cockpitHeaderHtml();
    html += headlineHtml();
    if (canvas.vetor === "ambiguo") html += ambiguousNudgeHtml();
    html += chipRowHtml();
    html += '<div class="cvt-canvas">' +
      listZoneHtml(LIST_BY_PATH["/gaps"]) +
      listZoneHtml(LIST_BY_PATH["/artifacts/expected"]) + "</div>";
    html += methodCollapseHtml();
    html += briefSectionHtml() + launchSectionHtml();
    el.innerHTML = html;
  }
```

**(3e)** Em `onCockpitClick`, adicione o branch de toggle (antes de `#cvt-brief-btn`):

```js
    if (e.target.closest(".cvt-collapse-toggle")) { state.methodOpen = !state.methodOpen; renderCockpit(); return; }
```

**(3f)** Em `static/canvas-tarefas.css`, **append**:

```css
/* MOD-016 (C1) — método colapsado */
.cvt-collapse { margin: 1rem 0; }
.cvt-collapse-toggle { font-size: .85rem; }
.cvt-collapse-body { margin-top: .6rem; }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest tests/test_canvas_ui_c1_source.py -q`
Expected: PASS (todos os testes do source-lint C1).

- [ ] **Step 5: Commit**

```bash
cd <worktree> && test "$(git branch --show-current)" = "collab/canvas-c1" && \
git add static/canvas-tarefas.js static/canvas-tarefas.css tests/test_canvas_ui_c1_source.py && \
git commit -m "feat(canvas-c1): collapse method fields behind 'Detalhes do método'"
```

---

### Task 4: Zonas do Curador de 1ª classe + absorver a ilha

**Files:**
- Modify: `static/canvas-tarefas.js` (`curadorZonesHtml`; `renderCockpit` reserva containers + tail-call `fill()`)
- Modify: `static/canvas-curador.js` (mata `_zone()`/`MutationObserver`; `render()`→`fill()`; 3 escritores; "Atualizar"; `_accept` reordenado; `fill()` cid-guard; export `fill`)
- Modify: `static/canvas-tarefas.css` (append zonas)
- Test: `tests/test_canvas_ui_c1_source.py` (+2 testes), `tests/test_curador_ui_source.py` (atualizado)

**Interfaces:**
- Consumes: `window.CVT.getCanvas`/`currentCid`, `window.CVT.acceptOps`, `esc`, `state.sugestoes`/`state.cid`/`_openStream`/`_autoFireOnFraming`/`pedirSugestoes` (existentes na ilha).
- Produces: `curadorZonesHtml()` (containers `#cvt-cur-acervo`/`#cvt-cur-personas`/`#cvt-cur-skills`/`#cvt-cur-sug`); `renderCockpit` tail-call `window.CanvasCurador.fill()`; `window.CanvasCurador = {onCockpitOpen, pedirSugestoes, fill}`.

- [ ] **Step 1: Write the failing tests**

**(1a)** Adicione a `tests/test_canvas_ui_c1_source.py`:

```python
def test_zonas_curador_reservadas_e_fill_no_tail():
    js = _js()
    for zid in ('id="cvt-cur-acervo"', 'id="cvt-cur-personas"',
                'id="cvt-cur-skills"', 'id="cvt-cur-sug"'):
        assert zid in js
    assert "curadorZonesHtml" in js
    assert "window.CanvasCurador.fill" in js


def test_invariantes_cvt_e_sala_e_hot_zone():
    js = _js()
    for k in ("acceptOps: submitOps", "getCanvas:", "currentCid:"):
        assert k in js                       # window.CVT surface intacta
    assert "window.CanvasSala" in js         # hook da Sala (MOD-014) preservado
    code = _strip_comments(js)               # fix-1: ignora comentários de cabeçalho
    for hot in ("ui.js", "messages.js", "sessions.js", "panels.js", "boot.js",
                "style.css", "index.html"):
        assert hot not in code
```

**(1b)** Em `tests/test_curador_ui_source.py`, **substitua** `test_ilha_curador_tem_superficie_minima` (o que assere o hack) por:

```python
def test_ilha_curador_e_helper_sem_hack_de_zona_irma():
    src = _static("canvas-curador.js")   # _static() já prepende static/ (nome NU)
    assert "/api/canvas/curador/stream" in src
    assert "/api/canvas/curador/delegar" in src
    assert "EventSource" in src
    assert "window.CVT.acceptOps" in src
    assert "window.CanvasCurador" in src
    # C1: virou helper — sem zona-irmã, sem observer, sem o rótulo antigo
    assert "cvt-curador-zone" not in src
    assert "MutationObserver" not in src
    assert "Pedir sugestões" not in src
    # preenche containers reservados + expõe fill + botão "Atualizar"
    assert "getElementById" in src
    assert "fill" in src
    assert 'id="cvt-cur-pedir"' in src and "Atualizar" in src
    # Skills = nature SINGULAR
    assert '=== "skill"' in src
```

> **Nota (verificada contra o arquivo real):** o helper de leitura em `tests/test_curador_ui_source.py` chama-se **`_static(name)`** e recebe o **nome NU** do arquivo — ele mesmo prepende `static/` (`parent.parent / "static" / name`). Use `_static("canvas-curador.js")` — **NUNCA** `_static("static/canvas-curador.js")` (resolveria `static/static/...` → FileNotFoundError) nem `_ler` (não existe → NameError que quebra o arquivo de teste inteiro na coleção). A remoção das asserções do hack (`cvt-curador-zone`/`Pedir sugestões`/`MutationObserver`) vale **só** para asserções sobre o **source da ilha** (`canvas-curador.js`) — substitua a função antiga que as continha. **Mantenha intactos** `test_canvas_tarefas_expoe_surface_do_curador`, `test_ilha_nao_toca_zonas_quentes`, `test_canvas_dev_html_carrega_a_ilha` e **`test_css_tem_classes_da_ilha`** — este último assere `.cvt-curador-zone`/`.cvt-sug` no **CSS**, que o plano preserva (append-only, passo 3h), então segue **verde**.

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest tests/test_canvas_ui_c1_source.py tests/test_curador_ui_source.py -q`
Expected: FAIL (containers/`fill` ainda não existem; a ilha ainda tem o hack).

- [ ] **Step 3: Write minimal implementation**

**(3a)** Em `static/canvas-tarefas.js`, adicione `curadorZonesHtml` (perto dos outros renderers):

```js
  function curadorZonesHtml() {
    // containers de 1ª classe reservados; canvas-curador.js os preenche via
    // getElementById (fill). São filhos de #cvt-cockpit → herdam switchView.
    return '<div class="cvt-cur-row">' +
      '<div class="cvt-zona cvt-cur-subzone" id="cvt-cur-acervo"></div>' +
      '<div class="cvt-zona cvt-cur-subzone" id="cvt-cur-personas"></div>' +
      '<div class="cvt-zona cvt-cur-subzone" id="cvt-cur-skills"></div>' +
      '</div><div class="cvt-zona cvt-cur-pending" id="cvt-cur-sug"></div>';
  }
```

**(3b)** Substitua `renderCockpit()` (versão da Task 3) por (insere `curadorZonesHtml()` após os chips + tail-call `fill()`):

```js
  function renderCockpit() {
    if (!canvas) return;
    const el = _root().querySelector("#cvt-cockpit");
    let html = cockpitHeaderHtml();
    html += headlineHtml();
    if (canvas.vetor === "ambiguo") html += ambiguousNudgeHtml();
    html += chipRowHtml();
    html += curadorZonesHtml();
    html += '<div class="cvt-canvas">' +
      listZoneHtml(LIST_BY_PATH["/gaps"]) +
      listZoneHtml(LIST_BY_PATH["/artifacts/expected"]) + "</div>";
    html += methodCollapseHtml();
    html += briefSectionHtml() + launchSectionHtml();
    el.innerHTML = html;
    // tail-call best-effort: a ilha preenche as zonas reservadas. fill() faz
    // no-op se o Curador ainda não está apontado p/ este cockpit (fix-3).
    if (window.CanvasCurador && window.CanvasCurador.fill) {
      try { window.CanvasCurador.fill(); } catch (_) {}
    }
  }
```

**(3c)** Reescreva `static/canvas-curador.js`. **Substitua** o comentário de cabeçalho + `_zone()` + `_canvasZones()` + `render()` por o novo cabeçalho + `_set` + escritores + `fill()`. **Mantenha verbatim** (exceto as 2 trocas `render()`→`fill()` do passo 3e, que são DENTRO de `_openStream`): `esc`, `state`, `postJSON`, `pedirSugestoes`, `_openStream`, `_autoFireOnFraming`, o listener de nível-documento, e a estrutura geral. Trechos exatos:

Cabeçalho — **substitua APENAS o comentário (linhas 1-5). PRESERVE verbatim `(function () {` (linha 6), `"use strict";` (7), `const esc = ...` (8) e `const state = ...` (9)** — o anchor NÃO é "1-6" (isso apagaria a abertura da IIFE e quebraria o arquivo; o source-lint por string-match NÃO pega isso, só o gate ao vivo):

```js
/* EXCRTX MOD-013 (F2) evoluído por MOD-016 (C1) — Curador como HELPER de 1ª
 * classe: preenche os containers reservados por renderCockpit (#cvt-cur-acervo/
 * -personas/-skills/-sug) via getElementById. Sem zona-irmã, sem observer de mutação.
 * 2ª EventSource própria (/api/canvas/curador/stream). Aceitar roteia por
 * window.CVT.acceptOps (fonte única do canvas). IIFE, sem deps, sem build, PT-BR. */
```

DELETE `_zone()` (linhas ~19-39) e `_canvasZones()` (linhas ~41-56) e `render()` (linhas ~58-75). No lugar, adicione:

```js
  function _set(id, html) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;   // null-guard: no-op se o Cockpit não montou
  }

  function _liList(items, fmt) {
    if (!items.length) return '<p class="cvt-empty">—</p>';
    return '<ul class="cvt-cur-list">' + items.map(fmt).join("") + "</ul>";
  }

  function _sugCardsHtml() {
    return Object.values(state.sugestoes).map((s) => {
      const d = (s.parts && s.parts[0] && s.parts[0].data) || s;
      const untrusted = d.trust === "untrusted"
        ? '<span class="cvt-chip-amber">externo (confirme)</span>' : "";
      const fontes = (d.fontes || (d.path ? [d.path] : [])).map(esc).join(", ");
      return '<div class="cvt-sug" data-sid="' + esc(s.artifactId || s.sugestao_id) + '">' +
        '<div class="cvt-sug-porque">' + esc(s.description || d.porque || "") + " " + untrusted + "</div>" +
        '<div class="cvt-sug-fonte">' + esc(fontes) + "</div>" +
        '<button type="button" class="cvt-sug-ok">Aceitar</button>' +
        '<button type="button" class="cvt-sug-no">Dispensar</button></div>';
    }).join("");
  }

  function fill() {
    // fix-3: só pinta se a ilha aponta p/ o cockpit corrente; senão no-op (evita
    // first-paint com cards do canvas anterior antes de onCockpitOpen resetar).
    const curCid = (window.CVT && window.CVT.currentCid && window.CVT.currentCid()) || "";
    if (!state.cid || state.cid !== curCid) return;
    const c = (window.CVT && window.CVT.getCanvas && window.CVT.getCanvas()) || {};
    const aplicado = c.acervo_aplicado || [];
    const acervo = aplicado.filter((a) => (a.nature || "") !== "skill");
    const skills = aplicado.filter((a) => (a.nature || "") === "skill");   // SINGULAR
    const personas = (c.personas || {}).suggested || [];
    _set("cvt-cur-acervo", "<h2>📚 Acervo aplicado</h2>" +
      _liList(acervo, (a) => "<li>" + esc(a.path) + " — " + esc(a.porque || a.nature) + "</li>"));
    _set("cvt-cur-personas", "<h2>🎭 Personas</h2>" +
      _liList(personas, (p) => "<li>" + esc(p) + "</li>"));
    _set("cvt-cur-skills", "<h2>🛠️ Skills sugeridas</h2>" +
      _liList(skills, (a) => '<li class="cvt-cur-skill">' + esc(a.path) + " — " + esc(a.porque || "") + "</li>"));
    _set("cvt-cur-sug", "<h2>Sugestões do Curador</h2>" +
      '<button type="button" id="cvt-cur-pedir" class="cvt-btn">Atualizar</button>' +
      (_sugCardsHtml() || '<p class="cvt-empty">—</p>'));
  }
```

**(3d)** Em `_accept` (existente), mova o `delete` para ANTES do `acceptOps` e troque `render()`→`fill()`:

```js
  async function _accept(sid) {
    const s = state.sugestoes[sid];
    if (!s) return;
    const ops = (s.metadata && s.metadata.ops) || s.ops || [];
    delete state.sugestoes[sid];   // fix: remove antes p/ um único paint consistente
    fill();
    if (ops.length && window.CVT && window.CVT.acceptOps) {
      try { await window.CVT.acceptOps(ops); } catch (_) { /* status já mostrado */ }
    }
  }
  function _dismiss(sid) { delete state.sugestoes[sid]; fill(); }
```

**(3e)** Em `_openStream`, troque as 2 chamadas `render()` (nos handlers `onSug`/`onGap`) por `fill()`.

**(3f)** Em `onCockpitOpen`, troque `render();` por `fill();` (a ordem fica: set cid/cursor/sugestoes → `fill()` → `_openStream` → `_autoFireOnFraming`).

**(3g)** Troque o export final para:

```js
  window.CanvasCurador = { onCockpitOpen, pedirSugestoes, fill };
```

**(3h)** Em `static/canvas-tarefas.css`, **append**:

```css
/* MOD-016 (C1) — zonas do Curador de 1ª classe (a .cvt-curador-zone acima fica
   inerte/deprecada: a classe não é mais emitida) */
.cvt-cur-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: .8rem; margin-bottom: 1rem; }
.cvt-cur-subzone h2 { margin: 0 0 .4rem; font-size: .8rem; text-transform: uppercase; letter-spacing: .06em; color: #9a9ab0; }
.cvt-cur-list { list-style: none; margin: 0; padding: 0; font-size: .85rem; }
.cvt-cur-list li { padding: .15rem 0; word-break: break-word; }
.cvt-cur-skill { color: #7ad0ff; }
.cvt-cur-pending { margin-bottom: 1rem; }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest tests/test_canvas_ui_c1_source.py tests/test_curador_ui_source.py tests/test_canvas_sala.py -q`
Expected: PASS (source-lint C1 completo + ilha atualizada + Sala intacta).

- [ ] **Step 5: Commit**

```bash
cd <worktree> && test "$(git branch --show-current)" = "collab/canvas-c1" && \
git add static/canvas-tarefas.js static/canvas-curador.js static/canvas-tarefas.css tests/test_canvas_ui_c1_source.py tests/test_curador_ui_source.py && \
git commit -m "feat(canvas-c1): Curador zones first-class in Cockpit, absorb the bolt-on island"
```

---

### Task 5: MOD-016 + prova de regressão keyless completa (fork)

**Files:**
- Modify: `EXOCRTX_MODIFICATIONS.md` (entrada MOD-016)

**Interfaces:** nenhuma (doc + verificação).

- [ ] **Step 1: Adicionar a entrada MOD-016**

Em `hermes-webui/EXOCRTX_MODIFICATIONS.md`, **após** o bloco MOD-015 (C0) e antes do `---`/seção de rebase-workflow, adicione:

```markdown
### MOD-016: C1 — Cockpit declutter + zonas do Curador de 1ª classe

**Arquivos:** `static/canvas-tarefas.js`, `static/canvas-tarefas.css`, `static/canvas-curador.js`, `api/canvas_tarefas.py` (+`GET /api/canvas/microversos`), `tests/test_canvas_microversos.py`, `tests/test_canvas_ui_c1_source.py`, `tests/test_curador_ui_source.py`.

Des-burocratiza o Cockpit: a frase vira headline; `vetor`/`intent_type`/`shape` viram chips; microverso vira dropdown dos microversos reais (novo endpoint aditivo `GET /api/canvas/microversos`, read-only, lê `$ACERVO/micro` com o mesmo filtro do Curador); método colapsado. Termina o E3: Acervo Aplicado/Personas/Skills sugeridas viram zonas de 1ª classe DENTRO do `renderCockpit`, alimentadas pelo Curador — a ilha `canvas-curador.js` (MOD-013) é **absorvida** como helper `fill()` (mata `#cvt-curador-zone`+`MutationObserver`). **0 linhas em `routes.py`, 0 deps, 0 build.** Zona quente e `window.CVT`/`canvas-sala.js` (MOD-014) intactos. Contrato: superfície aditiva §(h) (umbrella). Skill-usage de domínio = só citação no brief (carregar-na-sessão = C3/F5).
```

> Confirme o número: MOD-014=Sala/F3, MOD-015=C0 (ambos em `origin/exocortex/stable@18b782da`). MOD-016 é o próximo livre.

- [ ] **Step 2: Rodar a prova de regressão keyless completa**

Run:
```bash
cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest -q \
  tests/test_canvas_microversos.py tests/test_canvas_ui_c1_source.py \
  tests/test_canvas_routes.py tests/test_curador_ui_source.py \
  tests/test_canvas_sala.py tests/test_sala_island.py \
  tests/test_curador_skills.py tests/test_curador_capabilities.py \
  tests/test_canvas_brief.py tests/test_canvas_store.py
```
Expected: **all PASS, 0 failed** — cole o rodapé real (`N passed`) como prova EX-49. Se algo falhar, aplique bounds (regra 6): 3 ciclos → pare e reporte com a saída real.

- [ ] **Step 3: Commit**

```bash
cd <worktree> && test "$(git branch --show-current)" = "collab/canvas-c1" && \
git add EXOCRTX_MODIFICATIONS.md && \
git commit -m "docs(canvas-c1): catalog MOD-016 (Cockpit declutter + Curador zones)"
```

---

### Task 6: Governança COLLAB no umbrella — contrato §(h) + change-record

> **Repo diferente.** Esta tarefa roda numa **worktree DETACHED do umbrella** em `origin/master@25c36d4` (o master local diverge). NÃO commitar no fork. NÃO `git push`.

**Files:**
- Modify: `.harness/contracts/exocortex-hermes-webui.md` (nova §(h), bump de versão, regra de mudança (a)–(h))
- Create: `.harness/changes/2026-07-28_COLLAB_canvas-c1.md`

**Interfaces:** nenhuma (docs de governança).

- [ ] **Step 1: Criar a worktree detached do umbrella em origin/master**

```bash
cd /home/elder/projetos/projetob && git fetch origin --quiet && \
git worktree add --detach <scratch>/c1-umbrella origin/master && \
cd <scratch>/c1-umbrella && git rev-parse HEAD   # deve == origin/master (25c36d4)
```

- [ ] **Step 2: Ler a §(g) real e adicionar a §(h)**

Leia `.harness/contracts/exocortex-hermes-webui.md` **nesta worktree** (a versão de `origin/master`, que já tem §(g) Sala viva — o local está stale). Adicione a **§(h)** após a §(g), antes de "## Notas de dívida / evolução" (ou seção equivalente):

```markdown
### (h) GET /api/canvas/microversos — lista de microversos reais (C1/MOD-016)

| Superfície | Direção | Tipo | Descrição |
|---|---|---|---|
| `GET /api/canvas/microversos` | hermes-webui → UI | read-only | Retorna um array JSON de slugs (`[string]`) dos microversos reais em `$ACERVO/micro`, ordenados, com o MESMO filtro de `curador_capabilities._microverso_slugs` (ignora dirs `_`/`.`-prefixados e arquivos; reusado por `refresh_capability_cache`). `200 []` quando não há acervo montado (nunca 500). Alimenta o dropdown de microverso do Cockpit. Aditivo, sem estado, sem escrita. Fork MOD-016. |
```

Atualize o cabeçalho de versão do contrato (bump minor, ex. `v1.2`→`v1.3` — use o valor real que estiver no arquivo de origin/master) e a linha "Regra de mudança" para cobrir `(a)–(h)`.

- [ ] **Step 3: Criar o change-record**

Create `.harness/changes/2026-07-28_COLLAB_canvas-c1.md` (siga o formato de `2026-07-28_COLLAB_canvas-c0.md`):

```markdown
# COLLAB — Canvas de Tarefas C1: des-burocratizar o Cockpit + terminar o E3

- **Data:** 2026-07-28
- **Modo:** COLLAB (superfície de contrato aditiva; código executável só no fork)
- **Repos:** hermes-webui (fork, MOD-016) · projetob (umbrella, contrato §(h) + este record)
- **Branch fork:** `collab/canvas-c1` (cortada de `origin/exocortex/stable@18b782da`)

## O que mudou
- **Endpoint aditivo** `GET /api/canvas/microversos` (read-only; lê `$ACERVO/micro`, mesmo filtro de (f); `200 []` sem acervo) → contrato §(h).
- **Cockpit des-burocratizado**: frase-headline, chips (vetor/intent/shape), dropdown de microverso, método colapsado. Fork `static/canvas-tarefas.{js,css}`.
- **E3 terminado**: Acervo Aplicado/Personas/Skills sugeridas como zonas de 1ª classe no `renderCockpit`, alimentadas pelo Curador (`sugerir_itens`, F2). A ilha `canvas-curador.js` foi **absorvida** como helper `fill()` (removidos `#cvt-curador-zone`+`MutationObserver`).
- **Skill-usage de domínio**: só citação no brief (já flui via `compile_brief`); carregar-na-sessão diferido → issue-filha C3/F5.

## Invariantes preservados
- Zona quente intocada (`static/{ui,messages,sessions,panels,boot}.js`, `style.css`, `index.html`); `routes.py` 0 linhas; 0 deps; 0 build.
- `window.CVT` e `canvas-sala.js` (MOD-014/F3) intactos; whitelist/`sugerir_itens`/`compile_brief` intocados.

## Prova (EX-49, keyless)
- `pytest` do fork: `test_canvas_microversos.py` (3) + `test_canvas_ui_c1_source.py` + `test_curador_ui_source.py` (atualizado) + regressão de `test_canvas_routes/test_canvas_sala/...` — verde. [colar rodapé real]
- Gate ao vivo (owner-gated): smoke DeepSeek isolado + Playwright do Cockpit.

## Governança
- Fork: MOD-016 em `EXOCRTX_MODIFICATIONS.md`.
- Umbrella: contrato §(h) + este change-record (commit separado do fork).
- Exocortex: sem mudança (D10).
```

- [ ] **Step 4: Verificação (doc-lint) + commit no umbrella**

Run (lint de contrato, se existir o script — senão, valide manualmente que §(h) e a regra (a)–(h) estão presentes):
```bash
cd <scratch>/c1-umbrella && grep -n "(h) GET /api/canvas/microversos" .harness/contracts/exocortex-hermes-webui.md && \
grep -n "(a)–(h)\|(a)-(h)" .harness/contracts/exocortex-hermes-webui.md && \
ls .harness/changes/2026-07-28_COLLAB_canvas-c1.md
```
Expected: as 3 linhas aparecem (prova EX-49).

Commit (branch detached — a orquestração fará o merge `--no-ff` no tip do origin depois; NÃO push aqui):
```bash
cd <scratch>/c1-umbrella && \
git add .harness/contracts/exocortex-hermes-webui.md .harness/changes/2026-07-28_COLLAB_canvas-c1.md && \
git commit -m "docs(collab): contract (h) GET /api/canvas/microversos + C1 change-record"
```

> O merge final `--no-ff` das branches (fork `collab/canvas-c1` → `origin/exocortex/stable`; umbrella este commit → `origin/master`) e o push são **owner-gated**, feitos pela orquestração via worktrees DETACHED nos tips do ORIGIN. NÃO faça aqui.

---

## Self-Review (feito pelo autor do plano)

**1. Spec coverage:** cada item do spec tem tarefa — endpoint (T1); headline/chips/dropdown (T2); método colapsado (T3); zonas Curador + absorção da ilha (T4); MOD + regressão (T5); contrato §(h) + change-record (T6). Os 4 achados da crítica: fix-1 (lint strip-comments) em T4; fix-2 (fallback do dropdown `includes(cur)`) em T2; fix-3 (`fill()` cid-guard) em T4; fix-4 (`esc()` nos slugs) em T2. **Sem gaps.**

**2. Placeholder scan:** todo step de código tem código real; nenhum "TBD/TODO/handle edge cases". Os únicos textos abertos são anchor-hints ("confirme o nome real do helper `_ler`") — legítimos: o arquivo real deve ser lido para ancorar a edição.

**3. Type/símbolo consistency:** `state.microversos`/`microversosLoaded`/`methodOpen` definidos em T2/T3 e usados consistentemente; `LIST_BY_PATH` definido em T3 e usado em T3/T4; `curadorZonesHtml`/`fill`/`_set`/`_liList`/`_sugCardsHtml` consistentes em T4; `_list_microversos`/`_microverso_slugs` batem com a assinatura real verificada. `renderCockpit` é reescrito cumulativamente (T2→T3→T4), cada versão completa e coerente em runtime.

## Review adversarial do plano (4 revisores + juiz, vs código REAL) — FOLDED

Rodado antes do SDD. Verdict inicial = needs-revision, 4 must-fix; **9 achados folded + re-verificados** contra `c1-ref-fork`:
- **[CRÍTICO T2]** o comentário do `headlineHtml` continha `/original_input_summary` → tripava `assert "/original_input_summary" not in js` (arquivo cru). Reescrito sem pointer com barra.
- **[CRÍTICO T4]** o novo cabeçalho da ilha continha "MutationObserver" → tripava `assert "MutationObserver" not in src`. Reescrito p/ "observer de mutação".
- **[IMPORTANTE T4]** helper de teste real é `_static("canvas-curador.js")` (nome nu, prepende `static/`), não `_ler(...)`. Corrigido código + nota.
- **[IMPORTANTE T4]** anchor "linhas 1-6" apagaria a abertura `(function () {` (linha 6) — o source-lint por string-match NÃO pegaria. Corrigido p/ "linhas 1-5" + preservar IIFE.
- **[MINOR T6]** §(h) atribuía o filtro a `_valid_allow_scopes` (é validador de sharing); o real é `curador_capabilities._microverso_slugs`. Corrigido.
- **[MINOR T4]** `_openStream` listado como "verbatim" mas 3e troca render→fill dentro dele. Anotado.
- **[MINOR T4]** nota dizia que `test_css_tem_classes_da_ilha` ficaria vermelho — na verdade lê o CSS (append-only preserva `.cvt-curador-zone`), segue verde. Nota corrigida.
- **[MINOR T2]** `assert "data-field" in js` era falso-positivo (pré-existente em `editableSpanHtml`). Trocado por `data-value` (genuinamente novo).
- **[MINOR T2]** `GRID_FIELDS`/`fieldZoneHtml` ficariam órfãos após T2 → deletados em 3d (cirúrgico; `FIELDS`/`FIELD_BY_PATH` preservados).

## Execução

Após aprovação do plano (e do review adversarial do plano vs código real), executar via **superpowers:subagent-driven-development**: fresh subagent por tarefa (impl→review), numa worktree isolada da branch `collab/canvas-c1`, **NUNCA 2 implementers na mesma branch**. Depois: review de branch inteira no modelo mais capaz → fix wave única → merge `--no-ff` (owner-gated) → gate ao vivo (smoke DeepSeek isolado + Playwright).
