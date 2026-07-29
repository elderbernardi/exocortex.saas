# C1 — Des-burocratizar o Cockpit + terminar o E3 (design spec)

> Fase C1 do programa Canvas de Tarefas (meta issue elderbernardi/exocortex.saas#130).
> Conserta o drift do E3: o Cockpit vira um **cartão que o agente preencheu e você
> _nudge_**, não um formulário a preencher; e as sugestões do Curador (Acervo/Personas/
> Skills) viram **zonas de 1ª classe dentro do Cockpit**, absorvendo a ilha bolt-on.
> **UI-only. Não toca prod `127.0.0.1:8787` nem o acervo real.**

- **Data:** 2026-07-28
- **Escopo travado pelo owner** (reconfirmado via AskUserQuestion nesta sessão).
- **Base (obrigatória):** cortar de `origin/exocortex/stable` = `18b782da` (tem MOD-014/Sala + MOD-015/C0). **NÃO** cortar do HEAD local `14d880b6` (19 commits atrás, sem `canvas_sala.py`/`canvas-sala.js` em disco).
- **Método de origem:** design workflow multiagente (4 leitores do código REAL → 2 arquiteturas → síntese + tabela de decisões → crítica adversarial). Os 4 achados da crítica (2 IMPORTANT + 2 MINOR) estão **folded** neste spec (§7).

---

## 1. Objetivo

O E3 · Canvas UI da visão tinha zonas fixas `Foco/Pronto · Vetor · Microversos · Acervo · Personas · Gaps · Artefatos · Colheita · Next`, alimentadas pelo Curador (E4). F1 (MVP) cortou o E3 para um subconjunto free-text; F2 entregou os **dados** (`acervo_aplicado[]`/`personas.suggested[]`) mas num render **mínimo numa ilha bolt-on** (`canvas-curador.js`, zona-irmã `#cvt-curador-zone` + `MutationObserver`). Nenhuma fase assumiu terminar o E3. Consequência sentida pelo owner: Cockpit **burocrático** (campos free-text via ✎, 0 dropdowns; microverso é texto livre — não escolhe dos 13 reais) + reuso de acervo/personas/skills **órfão** numa ilha à parte.

C1 conserta isso em duas frentes travadas pelo owner:

1. **Des-burocratizar o `renderCockpit`** ([static/canvas-tarefas.js:187](hermes-webui/static/canvas-tarefas.js#L187)): a frase vira headline no topo; `vetor`/`intent_type`/`shape` viram **chips**; microverso vira **dropdown dos 13 reais** (novo `GET /api/canvas/microversos`); método colapsado atrás de "Detalhes do método ▸".
2. **Terminar o E3**: Acervo Aplicado + Personas + **Skills sugeridas** viram **zonas de 1ª classe DENTRO** do `renderCockpit`, alimentadas pelo Curador (`sugerir_itens` já produz os dados); **absorve** a ilha `canvas-curador.js` (mata o hack `#cvt-curador-zone` + `MutationObserver`).
3. **Skill-usage de domínio**: **só CITAR no brief agora** (já flui via `compile_brief` → `personas.suggested`+`acervo_aplicado`, zero mudança de backend). Carregar-a-skill-na-sessão = **issue-filha C3/F5, FORA do escopo C1**.

## 2. Não-objetivos (YAGNI / fora do escopo)

- Carregar skills de domínio na sessão lançada (→ C3/F5).
- Qualquer mudança na zona quente: `static/{ui,messages,sessions,panels,boot}.js`, `static/style.css`, `static/index.html`. `routes.py` **fica 0 linhas** (o forward de `/api/canvas/*` GET já existe).
- Qualquer mudança nos backends do Curador/enquadrador (`canvas_curador.py`, `canvas_brief.py`, `canvas_store.py`, `curador_capabilities.py`) além de **leitura**/reuso. Sem mudança no `_WHITELIST_RAW`, `sugerir_itens`, `compile_brief`.
- Tocar a ilha da Sala viva (`canvas-sala.js`, MOD-014/F3) — deve continuar funcionando **verbatim**.
- Build step ou dependência JS/npm — proibido (invariante nesquena upstream).
- Colheita/canonização (E8 = C2/F4) e calibração das skills conduct (C3/F5).

## 3. Escopo travado (tabela de decisões do owner)

| # | Decisão | Escolha | Fonte |
|---|---|---|---|
| D1 | Frase como **headline** editável no topo (não célula "Foco:") | `headlineHtml()` reusa o wrapper `<span class="cvt-field" data-field="/focus">…✎`; display `esc(focus \|\| original_input_summary \|\| "…")`; edição **sempre** grava `/focus` (whitelisted); `/original_input_summary` nunca é escrito | owner-locked |
| D2 | `vetor`(4)/`intent_type`(8)/`shape`(3) = **chips** sempre visíveis | `chipRowHtml()`: `<button class="cvt-chip" data-field data-value aria-pressed>` por enum fixo; 1 branch em `onCockpitClick` generalizando o precedente `.cvt-ambig-btn` → `submitOps([{op:"replace",path,value}])` | owner-locked |
| D3 | Microverso primary = **dropdown dos 13 reais** | `microversoSelectHtml()`: `<select data-field="/microversos/primary">` populado de `state.microversos` (fetch 1× em `abrirCockpit` via `GET /api/canvas/microversos`); listener `change` delegado | owner-locked |
| D4 | Método **colapsado** atrás de "Detalhes do método ▸" | `methodCollapseHtml()` dirigido por `state.methodOpen` (threaded no state, sobrevive ao `innerHTML` de cada frame SSE); corpo via `[hidden]`; **sem `<details>`** (perderia open-state no re-render) | owner-locked |
| D5 | Zonas Curador (Acervo/Personas/Skills) = **1ª classe DENTRO** do Cockpit | `renderCockpit` reserva `.cvt-cur-row` com `#cvt-cur-acervo`/`#cvt-cur-personas`/`#cvt-cur-skills` + `#cvt-cur-sug`, na posição aprovada (depois dos chips, antes das Lacunas) | owner-locked |
| D6 | **Mata** o hack `#cvt-curador-zone` + `MutationObserver` | DELETE `canvas-curador.js` `_zone()` (L19-39); `render()` vira `fill()` escrevendo nos containers reservados via `getElementById` (null-guard = no-op se ausente) | owner-locked |
| D7 | Skills = **zona dedicada** 🛠️ | filtra `acervo_aplicado` por `nature==='skill'` (**SINGULAR** — o enum real é `persona\|template\|skill\|workflow`; plural deixaria a zona sempre vazia) | owner-locked + correção do design |
| D8 | Disparo das sugestões = **auto ao terminar enquadramento + botão manual** | mantém `_autoFireOnFraming()` verbatim; botão manual reusa `pedirSugestoes`; rótulo do botão → **"Atualizar"** (mantém o id `#cvt-cur-pedir`) | owner-locked |
| D9 | **Module boundary** = HELPER-MODULE (mantém `canvas-curador.js`), não fold-in | `canvas-curador.js` mantém sua 2ª EventSource, `state.sugestoes`, autofire, accept/dismiss e listener de nível-documento; expõe `fill()`; `renderCockpit` faz tail-call. Menos inchaço no arquivo quente de 530 linhas + boundary testável + `fill()` self-scoped não clobbera edição em andamento | agent-recommended |
| D10 | Skill-usage de domínio | **só citar no brief** (já flui); carregar-na-sessão = C3/F5 | owner-locked |

## 4. Arquitetura

### 4.1 Module boundary (Stance A — helper-module)

`canvas-curador.js` **sobrevive** e vira um preenchedor de zonas. `renderCockpit` reserva containers nomeados vazios dentro de `#cvt-cockpit` e faz **tail-call** `window.CanvasCurador && window.CanvasCurador.fill()` (best-effort, try/catch). Vantagens sobre o fold-in (deletar e absorver ~150 linhas): (a) satisfaz os 2 requisitos do owner (mata a zona-irmã; zonas viram filhas de 1ª classe); (b) **edge de correção** — `fill()` só repinta os containers do Curador via `getElementById`, então um frame SSE do Curador **não** clobbera um `startEdit()` em andamento no headline/método; (c) muda menos arquivos (`canvas-dev.html` intocado → sem risco de `<script>` pendurado); (d) mantém o listener de nível-documento do Curador (location-agnostic) → **nenhum** novo branch de Curador entra no `onCockpitClick` quente.

`window.CVT` fica **intocado** (só `window.CanvasCurador` ganha `fill`), então `canvas-sala.js` (MOD-014, F3) e suas deps `esc`/`acceptOps` seguem preservadas.

### 4.2 Novo endpoint — `GET /api/canvas/microversos` (aditivo, read-only)

- **Forward:** ZERO linhas em `routes.py` — o forward de todo `/api/canvas/*` GET para `canvas_tarefas.handle_canvas_get` já existe. Invariante "routes.py ~0 linhas" mantido.
- **Dispatch:** 1 branch novo **inline** em `handle_canvas_get` (não um forward-to-submódulo como `/curador/` ou `/sala/`, pois é um read trivial do mesmo tier de `/list`,`/job`,`/brief`), inserido logo antes do fallback `if parsed.path != "/api/canvas/stream": return False`:
  ```python
  if parsed.path == "/api/canvas/microversos":
      _j(handler, _list_microversos())
      return True
  ```
- **Leitura:** novo helper que **reusa** `curador_capabilities._microverso_slugs(canvas_store.acervo_root())` (a MESMA resolução de acervo do Curador, nunca paralela), em `try/except → []`:
  ```python
  def _list_microversos() -> list[str]:
      """GET /api/canvas/microversos — slugs reais em $ACERVO/micro p/ o dropdown."""
      from api import curador_capabilities  # lazy, como os outros forwards
      try:
          return curador_capabilities._microverso_slugs(canvas_store.acervo_root())
      except Exception:
          return []
  ```
  `_microverso_slugs` ([curador_capabilities.py:63-68](hermes-webui/api/curador_capabilities.py#L63)) já retorna `sorted(p.name for p in (root/"micro").iterdir() if p.is_dir() and not p.name.startswith(("_", ".")))` e `[]` se `micro/` não existe.
- **Resposta:** array JSON simples de slugs ordenados (ex.: `["comercial","consultoria",...]`). HTTP **200 sempre**.
- **Fallback vazio:** `acervo_root()` levanta `RuntimeError` quando não há acervo (o caso C1 UI-only) → o `try/except` retorna `[]` (200, nunca 500). O frontend trata `[]` como "sem acervo" e **degrada o dropdown para o controle free-text ✎ existente**.
- **Whitelist:** `_WHITELIST_RAW` **não** é tocado — todo path que chips/dropdown/collapse gravam já é coberto (`/focus`, `/vetor`, `/intent_type`, `/shape`, `/microversos/primary`, `/microversos/related/*`, `/gaps/*`, `/scope/*`, `/assumptions/*`, `/artifacts/expected/*`, `/next_moves/*`, `/personas/suggested/*`, `/acervo_aplicado/*`).

### 4.3 Ordem de render do Cockpit (aprovada)

1. `cockpitHeaderHtml()` — título + "← Hangar" (**preservado verbatim**, inclui o badge de validade).
2. **headline-frase** — `.cvt-headline` envolvendo `<span class="cvt-field" data-field="/focus">`; display `esc(focus \|\| original_input_summary \|\| "…")`; edição sempre grava `/focus`.
3. **nudge âmbar** — `.cvt-chip-amber` "resolver" inline **só** quando `vetor==='ambiguo'` (substitui os botões-resgate do `ambiguousCardHtml`).
4. **linha de chips + dropdown** — `chipRowHtml()`: grupos `role="group"` Vetor(4)·Tipo de intenção(8)·Formato(3) como `.cvt-chip aria-pressed`, chips de vetor tingidos com `.cvt-vetor-*`; + `microversoSelectHtml()` dropdown (ou fallback free-text) na mesma linha `.cvt-chiprow`.
5. **zonas Curador** — `.cvt-cur-row`: `[Acervo Aplicado #cvt-cur-acervo | Personas #cvt-cur-personas | Skills sugeridas #cvt-cur-skills]` (filhos 1ª classe) + `#cvt-cur-sug` (strip de cards pendentes accept/dismiss + botão "Atualizar"); reservadas vazias pelo `renderCockpit`, preenchidas por `window.CanvasCurador.fill()`.
6. **Lacunas** — `listZoneHtml("/gaps")`.
7. **Artefatos esperados** — `listZoneHtml("/artifacts/expected")`.
8. **"Detalhes do método ▸"** — `methodCollapseHtml()` dirigido por `state.methodOpen`: `done_criteria` · `verification` · `scope` · `assumptions` · Próximos passos (`/next_moves`) · Microversos de apoio (`/microversos/related`), **todos mantendo o ✎**.
9. **Preview do brief / Lançar** — `briefSectionHtml()` + `launchSectionHtml()` (**preservados**).

> **Resolução de gap do spec do owner:** o layout aprovado não posicionou `next_moves` nem `microversos/related`. Ambos os leitores flagaram. **Decisão:** ambos vão **dentro do colapso** (item 8) — mantém o fluxo principal enxуto, preserva os campos como ainda editáveis/removíveis, e não inventa zona proeminente nova.

### 4.4 Renderers (mecânica)

- **chips:** generaliza o precedente `ambiguousCardHtml` + seu branch em `onCockpitClick` (que já faz `submitOps replace /vetor` via `data-vetor`). Novo: `data-field`+`data-value` num `<button>` nativo (Tab/Enter/Space de a11y de graça). O branch de chip lê `chip.dataset.field`/`chip.dataset.value`. **Retira** os 3 botões `.cvt-ambig-btn` duplicados de `ambiguousCardHtml` + seu branch (elimina a colisão de dois controles gravando `/vetor`); mantém só o nudge âmbar.
- **dropdown microverso:** `<select class="cvt-microverso-select" data-field="/microversos/primary">` populado de `state.microversos`; listener `change` **delegado** em `#cvt-cockpit` (novo, pois `<select>` emite `change`, não `click`) → `submitOps replace`. `state.microversos` é buscado 1× (memoizado) em `abrirCockpit`.
- **método colapsado:** `state.methodOpen` (bool) threaded no objeto `state` (igual `state.valid`), re-aplicado dentro do `renderCockpit`; toggle branch em `onCockpitClick` flipa e re-renderiza; corpo via `[hidden]`. Reusa `editableSpanHtml`/`listZoneHtml` existentes para os campos internos — `.cvt-field/.cvt-edit/.cvt-pencil/.cvt-input` seguem load-bearing.
- **fill() (canvas-curador.js):** `render()`→`fill()` escreve nos containers reservados via `getElementById` (no-op se ausente). `_canvasZones` se divide em 3 escritores nature-filtrados: Acervo (`nature!=='skill'`) → `#cvt-cur-acervo`, Skills (`nature==='skill'` SINGULAR) → `#cvt-cur-skills`, Personas (`personas.suggested` strings) → `#cvt-cur-personas`; cards pendentes + botão manual → `#cvt-cur-sug`. Cada zona renderiza estado vazio `—` (nunca "loading" infinito — `MAX_ARTIFACTS=3` é **total** entre naturezas, então qualquer zona pode legitimamente ficar vazia).

## 5. Mapa de mudanças (file-by-file)

**Fork `hermes-webui` (1 commit, MOD-016):**

| Arquivo | Tipo | Mudança |
|---|---|---|
| `api/canvas_tarefas.py` | MOD (aditivo) | `_list_microversos()` helper (após `_list_canvases`, ~L348) + 1 branch em `handle_canvas_get`. Sem mudança no whitelist. |
| `static/canvas-tarefas.js` | MOD (arquivo quente-do-fork) | Reestrutura `renderCockpit` na ordem §4.3. Novos renderers: `headlineHtml`, `chipRowHtml`, `microversoSelectHtml`, `methodCollapseHtml`. Reserva `.cvt-cur-row`/`#cvt-cur-*`+`#cvt-cur-sug` + tail-call `fill()`. `state.methodOpen`+`state.microversos`. `abrirCockpit`: fetch `/api/canvas/microversos` (memoizado). `onCockpitClick`: branches `.cvt-chip` + `.cvt-collapse-toggle`. `_build`: listener `change` delegado p/ `.cvt-microverso-select`. Retira botões `.cvt-ambig-btn` + branch. **Preserva:** `window.CVT` surface, hooks `window.CanvasCurador.onCockpitOpen` (L417-419) e `window.CanvasSala.onCockpitOpen` (L420-421) verbatim, id `#cvt-cockpit`, wrapper `.cvt-body`. |
| `static/canvas-curador.js` | MOD (ilha vira helper) | DELETE `_zone()` (L19-39, incl. `MutationObserver`+`#cvt-curador-zone`). `render()`→`fill()` via `getElementById`. `_canvasZones` → 3 escritores nature-filtrados (Skills = `nature==='skill'`). Rótulo do botão → "Atualizar" (mantém id `#cvt-cur-pedir`). `_accept`: deletar `state.sugestoes[sid]` **antes** de `acceptOps(ops)`. **Mantém verbatim:** `_openStream` (2ª EventSource), `_autoFireOnFraming` (3ª transiente), `pedirSugestoes`, listener de nível-documento, `onCockpitOpen`. Export `{onCockpitOpen, pedirSugestoes, fill}`. |
| `static/canvas-tarefas.css` | MOD (append-only) | Bloco `/* MOD-016 (C1) */`: `.cvt-headline`; `.cvt-chiprow/.cvt-chipgroup/.cvt-chipgroup-label/.cvt-chip/.cvt-chip.on`; `.cvt-microverso-select`; `.cvt-cur-row/.cvt-cur-subzone/.cvt-cur-list/.cvt-cur-pending/.cvt-cur-skill`; `.cvt-collapse/.cvt-collapse-toggle/.cvt-collapse-body[hidden]`. Reusa tokens existentes (`.cvt-vetor-*`, `.cvt-chip-amber`, `.cvt-link`, `.cvt-input`). Regras `.cvt-curador-zone` ficam inertes com comentário "deprecated MOD-016". **Não** renomeia/remove `.cvt-sug*/.cvt-field/.cvt-edit/.cvt-pencil/.cvt-input`. |
| `static/canvas-dev.html` | MOD | **NENHUMA** (canvas-curador.js sobrevive → ordem de `<script>` intocada). |
| `tests/test_curador_ui_source.py` | MOD (test, atualização forçada) | Dropa asserts do hack (`cvt-curador-zone`, `MutationObserver`, "Pedir sugestões" — agora falsos). Adiciona: expõe `fill`, sem `MutationObserver`, filtra `nature==='skill'`, botão "Atualizar", mantém stream/delegar/EventSource/`window.CVT.acceptOps`. |
| `tests/test_canvas_microversos.py` | MOD (test novo, keyless) | 3 testes do endpoint (FakeHandler). |
| `tests/test_canvas_ui_c1_source.py` | MOD (test novo, keyless) | source-lint da UI C1. |
| `EXOCRTX_MODIFICATIONS.md` | MOD entry | `### MOD-016: C1 — Cockpit declutter …`. Após MOD-015 (C0). |

**Umbrella `projetob` (1 commit, separado):**

| Arquivo | Mudança |
|---|---|
| `.harness/contracts/exocortex-hermes-webui.md` | Nova **§(h)** `GET /api/canvas/microversos` (read-only, `[string]`, lê `$ACERVO/micro` com o mesmo filtro de (f)); bump versão; "Regra de mudança" (a)–(g)→(a)–(h). **Autorar contra `origin/master`** — o local está stale. |
| `.harness/changes/2026-07-28_COLLAB_canvas-c1.md` | Novo change-record COLLAB (endpoint aditivo + absorção das zonas Curador + remoção do hack); linka MOD-016 e §(h). Committado COM o bump do contrato, separado do fork. |

**Exocortex `exocortex.saas`:** **NENHUMA mudança de código** (D10: sem skill nova). Estes docs (spec/PLANO) ficam como working-docs **untracked** no checkout (precedente F3), não committados.

## 6. Plano de teste + provas EX-49 (tudo keyless)

Runner: `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest <arquivos> -q` (PYTHONPATH=worktree). Lint de contrato: `UMBRELLA_ROOT=<umbrella-wt>`.

| Entregável | Prova (keyless) |
|---|---|
| `GET /api/canvas/microversos` | `tests/test_canvas_microversos.py`: (a) slugs ordenados de `$ACERVO/micro`; (b) exclui `_`/`.`-prefixados e arquivos; (c) sem acervo/`micro/` ausente → **200 `[]`** (nunca 500). |
| Chips vetor/intent/shape | `test_canvas_ui_c1_source.py::test_chips_*`: `.cvt-chip` com `data-field`+`data-value` + branch `submitOps replace` em `onCockpitClick`. |
| Dropdown microverso | `test_canvas_ui_c1_source.py::test_microverso_dropdown_*`: `<select class="cvt-microverso-select" data-field="/microversos/primary">` + listener `change` delegado + fetch `/api/canvas/microversos` + **fallback free-text** (§7 fix-2). |
| Headline | `test_headline_edita_focus_nao_original_input`: `.cvt-headline` grava `/focus`, nunca `/original_input_summary`. |
| Método colapsado | `test_detalhes_metodo_colapsado_via_state`: `.cvt-collapse-toggle` + `state.methodOpen` threaded + corpo com done/verification/scope/assumptions/next_moves/microversos.related. |
| Zonas Curador 1ª classe + hack morto | `test_curador_ui_source.py` (ATUALIZADO): sem `MutationObserver`/`#cvt-curador-zone` + `fill` exposto + `nature==='skill'` singular; `test_zonas_curador_reservadas_e_fill_no_tail`: reserva os 3 containers + tail-call `fill()`. |
| Invariantes (Sala/CVT/hot-zone) | `test_invariantes_cvt_e_sala_e_hot_zone` (§7 fix-1: lint de hot-file **strip-comments/load-forms**, não substring cru) + suíte existente `test_canvas_routes/test_canvas_sala/test_curador_*` verde = prova de regressão. |
| Governança | doc-lint: §(h) + versão + (a)–(h) no contrato; MOD-016 no fork; change-record existe — inspecionável sem chave. |

**Gate ao vivo (owner-gated):** smoke DeepSeek isolado (porta LIVRE nova — :8792/:8793 podem ter smoke stale) + Playwright no Cockpit (`canvas-dev.html`): dropdown dos 13, chips clicáveis, método colapsa/expande, zonas Curador 1ª classe. Se o Playwright MCP estiver travado por sessão paralela → prova via DOM/SSE. **Prod :8787 (pid antes/depois) + acervo real INTOCADOS.**

## 7. Achados da crítica adversarial — FOLDED

1. **[IMPORTANT] Lint de hot-file com falso-positivo.** `canvas-tarefas.js:5` e `canvas-sala.js:1-6` **mencionam** `ui.js/messages.js/index.html`/`style.css` em **comentários de cabeçalho**. Um `assert "index.html" not in src` cru sobre esses arquivos **falha**. O `test_ilha_nao_toca_zonas_quentes` existente só passa porque linta `canvas-curador.js` (o único limpo). **Fix:** o lint de hot-file sobre `canvas-tarefas.js`/`canvas-sala.js` deve **remover comentários antes de asserir** (ou casar formas de _load_ perigosas: `<script src=".../boot.js">`, `import`/`require`, `fetch('/static/ui.js')`), não qualquer menção. Ajustar a claim EX-49 conforme.
2. **[IMPORTANT] Dropdown não representa o valor atual.** Se o acervo está montado (13 slugs) mas `canvas.microversos.primary` é `None` (default `_MINIMAL`) **ou** um valor free-text legado fora dos slugs (a norma pré-C1, pois `/microversos/primary` não tinha `options`), um `<select>` sem `<option>` casando **auto-seleciona o índice 0** silenciosamente → o Cockpit exibe o 1º slug como âncora enquanto o valor guardado é outro, sem disparar `change`. Regressão vs o free-text de hoje. **Fix:** (a) `<option value="" selected disabled>` placeholder quando `primary` vazio; (b) quando `primary` é não-vazio e **não** está em `state.microversos`, injetar um `<option selected>` extra com o valor guardado (escapado) — ou cair no free-text quando `primary && !slugs.includes(primary)`. Marcar `selected` explicitamente no `<option>` que casa.
3. **[MINOR] First-paint stale dos cards do Curador.** `renderCockpit` faz tail-call `fill()` (Stance A); em `abrirCockpit`, `renderCockpit` roda (L402/~413) **antes** de `window.CanvasCurador.onCockpitOpen` (L418) que reseta `state.sugestoes={}`. `state.sugestoes` vive no closure do `canvas-curador.js` e persiste entre aberturas → o 1º `fill()` de um canvas recém-aberto pinta os cards pendentes do canvas **anterior** até o reset. **Fix:** `fill()` faz no-op quando `state.cid` (do curador) ≠ o cid corrente do Cockpit — ou resetar mais cedo. Assim o 1º paint nunca mostra cards de outro canvas.
4. **[MINOR] XSS via `<option>` de slug não-escapado.** Os slugs vêm de nomes de diretório em `$ACERVO/micro` lidos do disco; um slug com aspa/`<` quebraria o atributo/tag. Probabilidade baixa (dirs owner-controlled), mas a Regra 1 do arquivo manda **todo** valor dinâmico em template `innerHTML` passar por `esc()`. **Fix:** `esc()` em cada slug — no `value` e no label visível de `microversoSelectHtml`.

## 8. Governança (COLLAB 3-repos → 2 repos tocados)

Classificação: **COLLAB** (adiciona uma superfície de endpoint no contrato exocortex↔hermes-webui, mesmo com todo o código executável no fork). Commits **separados por repo**:

1. **Contrato** (umbrella) — nova §(h), bump de versão, regra de mudança (a)–(h). **Autorar contra `origin/master`** (o §(g) Sala já está lá em `d5d0800`; o local está stale, nomear §(g) colidiria).
2. **Change-record** (umbrella) — `2026-07-28_COLLAB_canvas-c1.md` (UPPERCASE COLLAB, precedente do épico). Committado com o contrato, separado do fork.
3. **MOD fork** — `EXOCRTX_MODIFICATIONS.md` MOD-016 (livre: MOD-014=Sala, MOD-015=C0). Branch/commit contra `origin/exocortex/stable`.
4. **Exocortex acervo** — **nada** (D10: sem skill nova no C1).

⚠️ **Umbrella master DIVERGIU** (não só atrás): local 2 à frente (commits de harness F2) vs origin 5 à frente (incl. §(g)). O merge do contrato é via **worktree DETACHED no tip do `origin/master`** (não `git pull`) — reconciliação owner-gated.

## 9. Riscos abertos (registrados, não bloqueiam)

- **Base-branch drift (fork):** C1 corta de `origin/exocortex/stable`, NUNCA do HEAD local (sem `canvas_sala.py`/`canvas-sala.js` em disco).
- **Contrato de ids soft:** `canvas-tarefas.js` reserva `#cvt-cur-*` e `canvas-curador.js` preenche via `getElementById`; se os ids driftarem as zonas ficam silenciosamente vazias (a ilha é best-effort). Mitigado com source-lint asserindo os mesmos ids nos 2 arquivos + comentário compartilhado.
- **`el.innerHTML` wholesale a cada frame SSE do enquadrador** ainda pode clobberar um `startEdit` em andamento no headline `/focus` (Stance A remove só o clobber de frame-do-Curador). Mitigação opcional (defer-render enquanto edita, ou gate do edit `/focus` enquanto `job.status==='running'`); aceitável no spike single-user, flagado.
- **`_microverso_slugs` é underscore-private:** import cross-módulo é um leve _smell_ de convenção (o projeto já faz imports underscore internos). Reusar como está (evita tocar arquivo F2); alternativa = promover a público (1 linha), rejeitada por churn.
- **Dois padrões de zona coexistem pós-C1** (Curador native-inside vs Sala sibling-outside com seu próprio `MutationObserver`) — intencional (F2 in, F3 out). Mitigado com comentário de aviso no `_zone()` da Sala.

## 10. Base e worktrees

- **Fork:** worktree isolada em scratchpad, branch **`collab/canvas-c1`** cortada de `origin/exocortex/stable@18b782da`. NUNCA 2 implementers na mesma branch. Verificar branch no MESMO comando composto do commit; NUNCA `git add -A` (paths explícitos).
- **Umbrella:** worktree DETACHED no tip de `origin/master@25c36d4` para o commit do contrato/change-record.
- **Merge final:** `--no-ff` via worktrees DETACHED nos tips do ORIGIN → push (owner-gated).
