# F4 — Colheita & Canonização (design)

> Fase do programa **Canvas de Tarefas** (meta issue elderbernardi/exocortex.saas#130).
> Fecha o **ciclo de crescimento**: conhecimentos/artefatos de uma sala são canonizados de volta ao
> acervo com HITL em lote, e o canvas vira **receita** reutilizável. Última fase de *feature* antes da
> F5 (polish/GA). Charter fonte: `docs/plans/2026-07-23_canvas-tarefas/F4-CHARTER.md`.
> Plano detalhado (task-by-task) sai depois deste spec, em `F4-PLANO.md`, via writing-plans.

## 1. Contexto e problema

F0–F3 + C0 + C1 shiparam em `hermes-webui@exocortex/stable` (contrato `exocortex-hermes-webui.md` v1.3):
o executivo declara o intento, o enquadrador monta o canvas, o Curador sugere itens do acervo, a Sala
viva reflete a execução em cards, e o agente conduzido escreve o `conduct.jsonl` fora de banda (C0).

**O que falta para o loop se fechar:** hoje os candidatos a canonização **fluem mas nunca são
canonizados**. Os eventos `sala_artifact`/`sala_finding`/`sala_next_move`/`sala_draft`
(`api/sala_reducer.py`) e as linhas do `conduct.jsonl` só viram cards efêmeros da Sala — nada volta ao
acervo, e nenhum canvas vira receita. O `_tasks/` enche de instâncias; o acervo não aprende. O campo
`promotion_candidates` já existe no template `harness-v0.4/canvas.yaml`, mas é placeholder sem UX nem
superfície de escrita.

**Objetivo da F4:** entregar a **bandeja de colheita** (acúmulo sem interrupção), o **checkout em
lote** (1 momento HITL, escrita via superfície governada do acervo), um **fable-judge mecânico** de
checkout, e a transformação **canvas → receita** (clean-portable) que realimenta a galeria do Hangar —
de modo que **o sistema melhore a cada uso**.

## 2. Decisões do owner (vinculantes)

| # | Decisão | Consequência |
|---|---|---|
| OD-F4-1 | **Fork orquestra `acervoctl`** no checkout (two-phase ADR-022): `prepare` → receipt/diff na UI → aprovação em lote → `commit-write`. A escrita cruza pela superfície semântica governada (guard_scope + gates trust/risk), não por acesso direto ao FS. | O propose-then-approve mapeia: **propose** = `prepare`/receipt exibido; **approve** = o HITL em lote; **commit** = `commit-write`. Testável keyless com seam fake (`ACERVOCTL_CMD`). O fork passa a *invocar* escrita (via CLI governada), diferente do Curador (read-only) — consistente com o launch já chamar `register_task_from_canvas.py`. |
| OD-F4-2 | **Bandeja híbrida**: (a) o agente sinaliza promoções intencionais via nova linha conduct `{t:harvest,…}`; (b) o executivo pode **adotar** manualmente cards da Sala viva que o agente não sinalizou. | Sinal intencional + rede de segurança humana. Toca **1 skill de condução no exocortex** (EX-60 `excrtx-conduct-loop` ganha o append `{t:harvest}`). Nada é auto-canonizado — a bandeja só acumula; a escrita é sempre no checkout. |
| OD-F4-3 | **fable-judge mecânico** (keyless) no checkout, **não** LLM. Verifica por execução/diff: arquivo existe, `validate_frontmatter.py` passa, clean-portable aplicado (sem instância/segredo), entrada no `_meta/log.md`. | Satisfaz "verificar por execução/diff, nunca lendo o relatório" (charter) sem gate LLM. **Juiz semântico LLM = deferido à F5.** |

**Defaults confirmados (não são decisões abertas):** receitas moram no microverso `receitas`
(`micro/receitas/`, nature `templates`/`workflows`, reusáveis cross-microverso); a bandeja tem SSE próprio (consistente
com Sala/Curador — enche durante a execução); prefill "iniciar de receita" é **obrigatório** (está no
gate de saída).

## 3. Seams (mapeamento read-only, 2026-08-01)

Confirmados por duas explorações (fork + exocortex). Referência para o plano:

- **Candidatos já fluem**: `api/sala_reducer.py` (`_on_artifact`/`_on_surprise`/`_on_next_move`) →
  eventos `sala_*`; `api/canvas_sala.py:_read_conduct_lines` segue `conduct.jsonl`
  (`t ∈ phase|trace|artifact|verify|search|surprise|next_move|draft`). **Nenhum caminho canoniza.**
- **Dispatch pronto**: forward em `api/canvas_tarefas.py` (`handle_canvas_get/post`,
  `if path.startswith(...)`) → **0 linhas novas em `routes.py`** (padrão Curador/Sala).
- **Hangar** (`static/canvas-tarefas.js:renderHangar`) lista só canvases recentes via
  `/api/canvas/list` — **sem galeria de receitas**. Cockpit não tem zona de colheita.
- **Escrita no acervo**: `scripts/acervoctl.py` — `new-object` (tipos `episode|entity|intention`) e
  `commit-write` (genérico: `--receipt`, `--content-file`, `--class-name`, `--entry-type`); two-phase
  `prepare`→`commit` (ADR-022, `acervo_semantic_core.py`); gates: `class:perene`→DRAFT-first,
  `source_trust:untrusted`→forced draft (`semantic_core.py:1392-1400`).
- **OKF v0.2**: frontmatter obrigatório `schema/type/title/description/tags/created_at/class/status`
  (+ tier epistêmico p/ knowledge/decision/reflection); `scripts/validate_frontmatter.py` valida.
- **Testes keyless**: pytest + FakeHandler + reducer puro (`tests/test_canvas_*.py`); seam de injeção
  já usado (`CANVAS_LLM_CMD`).

## 4. Arquitetura e componentes

Segue o padrão F2/F3: **room próprio + SSE re-anexável + forward-dispatch; `routes.py` intocado; zona
quente intocada; 0 deps; 0 build; PT-BR**.

### A. Bandeja de colheita — `api/canvas_colheita.py` (novo)
- Store próprio append-only: `_tasks/<canvas_id>/colheita.jsonl`.
- Alimentação híbrida (OD-F4-2):
  1. **Agente**: linha conduct `{t:harvest, nature, scope, title, porque, ref, class, source_trust}`.
     O observador da Sala reconhece `t:harvest` → anexa card + emite `colheita_candidate`.
  2. **Manual**: `POST /api/canvas/colheita/adotar {canvas_id, source_event}` a partir de um card da
     Sala → card `origin:manual`.
- **Card**: `{id, nature, scope, title, porque, ref?, body?, class, source_trust, gate, status, receipt?}`.
  **Corpo a gravar**: `ref` (path de um arquivo produzido na execução → corpo lido do arquivo, caso de
  `sala_artifact`) **ou** `body` inline (achado/reflexão sem arquivo, caso de `sala_finding`/
  `sala_next_move`); o `commit-write` usa o que existir. `gate` **auto-computado** (perene/persona/macro
  → `draft-first`; source_trust web → `forced-draft`; senão `auto`).
  `status ∈ pending|prepared|approved|committed|committed_unverified|rejected`.
- Endpoints (forward dispatch):
  | Rota | Request → Response |
  |---|---|
  | `GET /api/canvas/colheita/list?canvas_id=` | → `[card]` |
  | `GET /api/canvas/colheita/stream?canvas_id=&since=N` | SSE re-anexável (`colheita_candidate\|prepared\|committed\|rejected`) |
  | `POST /api/canvas/colheita/adotar` | `{canvas_id, source_event, nature?, scope?}` → `{card_id}` (card `pending`, `origin:manual`; nature/scope/class editáveis na zona antes do `preparar`) |
  | `POST /api/canvas/colheita/preparar` | `{canvas_id}` → roda `acervoctl prepare` por card pendente → anexa receipt/diff → `prepared` **(propose)** |
  | `POST /api/canvas/colheita/checkout` | `{canvas_id, mode: aprovar_tudo\|item_a_item, decisions:[{card_id, action: aprovar\|rejeitar}]}` → nos aprovados roda `acervoctl commit-write` → fable-judge → `{summary}` **(approve→commit)** |

### B. fable-judge mecânico (helper puro em `api/canvas_colheita.py`)
Após cada `commit-write`: (1) arquivo-alvo existe; (2) `validate_frontmatter.py` exit 0; (3)
clean-portable OK (scan do corpo sem `canvas_id`/`session_id`/`task_id`/padrões de segredo); (4)
`_meta/log.md` ganhou a entrada. Falha → card `committed_unverified` no sumário (nunca silencioso).
Keyless, testável em isolamento.

### C. Canvas → receita — `api/canvas_receita.py` (novo)
- `POST /api/canvas/receita/canonizar {canvas_id}` → **clean-portable** do canvas: remove instância
  (vínculo `microversos.primary`, ephemera de task/sessão, `promotion_candidates` instanciados,
  palavras de `authorization[]`); preserva estrutura (`vetor`, `shape`, `done_criteria`/`verification`
  como template, slots de persona, perguntas de intake derivadas dos gaps, shapes de
  `artifacts.expected`) → objeto nature `templates`/`workflows` via `acervoctl prepare-write`→receipt→
  approve→`commit-write` no **microverso `receitas`** (`micro/receitas/`, OKF v0.2 validado).
  *Nota:* destino é um microverso real (`receitas`), não o container `global/` — `prepare-write` exige
  `--microverso` e roteia por `ensure_microverso_structure`; refina o "global/templates/receitas" do
  charter por compatibilidade de CLI.
- `GET /api/canvas/receita/list` → lê o dir de receitas → `[{recipe_id, focus_template, vetor, path}]`.
- `POST /api/canvas/receita/iniciar {recipe_id}` → cria canvas NOVO pré-preenchido (via
  `canvas_store.create_draft` semeado com a estrutura da receita) → `{canvas_id}` → Cockpit abre
  preenchido.

### D. Galeria no Hangar — `static/canvas-tarefas.js`
`renderHangar()` ganha seção "Receitas" (fetch `/api/canvas/receita/list`; card → `receita/iniciar` →
Cockpit pré-preenchido). Aditivo à função existente; nenhum arquivo de zona quente tocado.

### E. Zona Colheita no Cockpit — ilha `static/canvas-colheita.js` (novo; clone de `canvas-sala.js`)
`#cvt-colheita-zone`, EventSource em `/api/canvas/colheita/stream`, 1 renderer por card com badge de
gate + "diff sob demanda" (fetch do receipt) + controles [Preparar] → [Aprovar tudo | Item a item |
Rejeitar]. Nos cards da Sala, ação "colher" → `adotar`. Botão "Canonizar sala como receita" →
`receita/canonizar`. Usa `window.CVT` (acceptOps/getCanvas/currentCid) como as ilhas do F2/F3.

## 5. Fluxo (do trabalho ao loop fechado)

1. **Execução** (Sala viva F3): agente emite `{t:harvest}` + executivo adota cards → bandeja enche ao
   vivo (`colheita.jsonl` + SSE), **zero interrupção**.
2. **Preparar** (fechamento): fork roda `acervoctl prepare` por card → receipts/diffs + badges de gate.
3. **Um único HITL em lote**: aprovar tudo / item a item / rejeitar.
4. `commit-write` por aprovado → **fable-judge mecânico** → **sumário outcome-first**.
5. (Opcional) **Canonizar como receita** → clean-portable → objeto no acervo → galeria do Hangar.
6. **Iniciar de receita** → canvas novo pré-preenchido → Cockpit. **Fecha o loop.**

## 6. Modelo de dados

- **Linha conduct `{t:harvest}`** (append pelo agente, `_tasks/<task_id>/conduct.jsonl`):
  `{"t":"harvest","nature":"knowledge|decision|reflection|template|workflow","scope":"<microverso>","title":"…","porque":"…","ref":"<path>"|"body":"<texto>","class":"perene|volátil","source_trust":"agent|executive|untrusted"}`
  (`ref` **ou** `body` — a fonte do corpo a canonizar; ver §4.A).
- **Card da bandeja** (§4.A) — projeção server-side em `colheita.jsonl`.
- **Receita** (objeto acervo): OKF v0.2, `type: template|workflow`, `epistemic: rule`,
  `class: perene`, corpo = estrutura clean-portable do canvas; sem dado de instância/segredo.

## 7. Escopo

### Dentro da F4
1. `api/canvas_colheita.py` (bandeja + SSE + preparar/checkout + fable-judge mecânico) — fork.
2. `api/canvas_receita.py` (canonizar/list/iniciar) — fork.
3. Ilha `static/canvas-colheita.js` + zona no Cockpit + galeria no Hangar (`canvas-tarefas.js`/`.css`) — fork.
4. Forward dispatch de `/api/canvas/{colheita,receita}/*` em `api/canvas_tarefas.py` (0 linhas `routes.py`) — fork.
5. Seam `ACERVOCTL_CMD` para testes; `tests/test_canvas_colheita.py` + `tests/test_canvas_receita.py` — fork.
6. Linha `{t:harvest}` na skill `excrtx-conduct-loop` (EX-60) + recompilar `SOUL_SEED.md` — exocortex.
7. **Confirmar/estender `acervoctl`** p/ `prepare`+`commit-write` genérico das natures de colheita
   (knowledge/decisions/reflections/templates/workflows) — exocortex (ver §11 gap #1).
8. Contrato v1.3→v1.4 (§(i)/§(j) + `{t:harvest}`) + MOD-017 (fork) + change record (umbrella).

### Fora da F4 (deferido, documentado)
- **Juiz semântico LLM** de colheita (skill EX + gate LLM) → F5.
- **`macro` risk gate** formalizado no `semantic_core` (hoje só `perene`); F4 trata macro como
  draft-first apenas no cômputo do gate do lado do fork.
- **Clean-portable de nomes próprios** no `focus` (remoção heurística do nome do cliente etc.): F4
  preserva o `focus` como template textual e remove só vínculos estruturais; refino heurístico → F5.
- Re-pin de `sources.lock`, a11y, i18n, dogfood, auditoria interativa, fechar #130 → F5.

### Não-objetivos
Nenhum auto-commit (propose-then-approve sempre); nenhuma taxonomia nova de receita (só
`templates`/`workflows`); nenhuma mudança na zona quente ou no runtime da sessão; nenhum toque em
`routes.py` além do já existente.

## 8. Superfícies de contrato (COLLAB — `exocortex-hermes-webui.md` v1.3 → v1.4, **aditivo**)
- **§(i) Colheita**: endpoints `/api/canvas/colheita/{list,stream,adotar,preparar,checkout}` + eventos
  SSE `colheita_{candidate,prepared,committed,rejected}`; store `_tasks/<canvas_id>/colheita.jsonl`.
- **§(j) Receita**: endpoints `/api/canvas/receita/{canonizar,list,iniciar}`; objetos no microverso
  `receitas` (`micro/receitas/`, nature templates/workflows, OKF v0.2).
- **§(g) atualização**: nova linha conduct `{t:harvest,…}` (aditiva ao conjunto de tipos já documentado).
- **Espelhos do fork**: nenhum campo *core* do canvas schema muda; se `promotion_candidates` for
  espelhado/whitelisted, atualizar `_WHITELIST_RAW`/`_MINIMAL` no mesmo COLLAB.
- **Regra de mudança**: tudo acima é **aditivo → seguro**; rename/remoção seria breaking (novo COLLAB).

## 9. Gate de saída (F4)

1 sala real fechada, ao vivo, com:
1. Colheita aprovada **em lote** gravada no acervo — `_meta/log.md` do container mostra as entradas
   (prova bruta EX-49).
2. **1 receita** canonizada (objeto nature templates/workflows válido OKF v0.2 em
   `global/templates/receitas/`).
3. **Nova sala iniciada a partir dessa receita** (canvas pré-preenchido renderizado no Cockpit).
4. fable-judge mecânico verde para os itens gravados (ou os `committed_unverified` explicitados no
   sumário — nunca silenciosos).

Gate ao vivo é **owner-gated** (smoke isolado; prod :8787 + acervo real INTOCADOS).

## 10. Guardrails e governança
- **Zona quente intocada**: `static/{ui,messages,sessions,panels,boot}.js`, `style.css`, `index.html`;
  `routes.py` = 0 linhas novas (forward). Sem dep JS/npm; zero build; upstream nesquena não perturbado.
- **Escritas só pela superfície semântica**: toda canonização via `acervoctl` (prepare→commit), nunca
  escrita direta no FS do acervo; `.quarantine` invisível; gates trust/risk aplicados por item; segredos
  nunca em card/receipt/log.
- **Checkout compartilhado**: trabalho em **worktree isolada**, branch `collab/canvas-tarefas` cortada
  dos **tips de origin**; verificar a branch no mesmo comando composto do commit; **nunca `git add -A`**
  (paths explícitos); merge via worktree DETACHED no tip do ORIGIN → `--no-ff`, **push owner-gated**.
- **Keyless**: pytest com seam `ACERVOCTL_CMD` (fake) + FakeHandler; skills via `skill_judge.py --d1-only`;
  `compile_soul.py` (guard C-S1). Gate ao vivo com LLM = owner-gated.
- **COLLAB 3-repos** (commits separados por repo): fork (código + MOD-017) · exocortex (skill EX-60 +
  acervoctl + SOUL recompilado) · umbrella (contrato v1.4 + change record). EX-08/EX-49/P1–P11 valem.

## 11. Gaps e riscos conhecidos (a resolver no plano)
1. **acervoctl para natures genéricas** — ✅ **RESOLVIDO na análise**: `prepare-write --microverso
   <slug> --nature <nature> --title <t> [--receipt-out]` + `commit-write --receipt --content-file
   --description --class-name` já aceitam nature/destino arbitrário (`ensure_microverso_structure`).
   `commit_write` já roda `require_no_secrets` + força `status:draft` p/ `untrusted` + `validate_entry`
   (OKF) + `update_index` + `append_log`. **Único gap aditivo restante**: o CLI `prepare-write`/
   `commit-write` **não expõe `--source-trust`** (hardcode `"agent"`) → o trust gate web não dispara
   pela CLI. Task 1 do plano adiciona `--source-trust` (aditivo, pass-through). Nota: o fork **monta o
   frontmatter OKF v0.2 ele mesmo** (o `prepare-write` só resolve path/guard; `commit_write` valida mas
   não monta) — builder de frontmatter no lado do fork.
2. **`macro`/`persona` no risk gate** — só `perene` é checado hoje; o fork computa draft-first p/
   perene/persona/macro no card, mas o `semantic_core` só força draft em perene+untrusted. Aceitável
   p/ F4 (o gate do fork é conservador); formalizar = F5.
3. **Round-trip do `prepare` no checkout** — `acervoctl prepare` por card é subprocess; em lote grande
   pode ser lento. Mitigar: preparar sob demanda / paralelizável; medir no gate.
4. **clean-portable e nomes próprios** — preservamos `focus` como texto; não removemos heurísticamente
   o nome do cliente. Documentado como limitação (F5).

## 12. Sequência do programa (contexto)
F0(spike)→F1a/F1b(MVP)→F2(Curador)→F3(Sala viva)→**C0**(condução)→**C1**(declutter+E3)→**F4 (esta)**→
F5(polish/GA/fecha #130). F5 audita a jornada completa (frase→sala→execução→**colheita→receita**), logo
**depende desta fase**. Índice: `docs/plans/2026-07-23_canvas-tarefas/00-INDEX.md`.
