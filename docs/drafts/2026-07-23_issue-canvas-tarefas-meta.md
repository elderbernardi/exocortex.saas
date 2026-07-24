# [META][P1] Canvas de Tarefas — enquadramento conduzido pelo agente, do intento à sessão (Hermes WebUI)

> Promover o Canvas Cognitivo (EX-06) de bloco interno de trace a **superfície primária da WebUI**: o executivo declara o intento em uma frase; um agente de UI monta a sala de trabalho inteira — vetor, microversos, itens do acervo, critério de pronto — e conduz a execução com HITL cirúrgico. Cada sala bem enquadrada pode ser canonizada de volta ao Acervo. O sistema melhora a cada uso.

## 1. Visão & porquê

O framework já modela tudo o que esta UX precisa — e nada disso tem superfície visual hoje:

- **EX-06** define que *a Tarefa é a sala* (microverso nunca é sala) e extrai de cada input um canvas estruturado: focus, vetor, intent_type, gaps, âncoras de microverso com sharing constraints, personas, artefatos esperados, candidatos a promoção.
- O harness v0.4 persiste esse canvas (`acervo/global/templates/harness-v0.4/canvas.yaml`), valida (`acervo/global/tools/harness/canvas_schema.py`) e registra tarefas (`register_task_from_canvas.py` → `$ACERVO/_tasks/{task_id}/`).
- **`_tasks/` do acervo vivo está VAZIO.** O trilho existe; falta a UX que o alimente.

O problema que esta iniciativa ataca não é estético: é o **enquadramento**. O maior desperdício em trabalho humano-agente está no vão entre o que a pessoa quer (ampliado pelas possibilidades do agente, que ela não conhece por inteiro) e o que o agente entende para executar. A resposta do mercado em 2026 (Claude Cowork, plan-mode, padrões "clarify-or-act") converge para o que EX-05/EX-06 já prescrevem: co-construção de intenção antes e durante a execução. Nossa vantagem: temos o modelo de dados, o acervo e a governança prontos — falta a sala.

**Atualização de doutrina (formal):** os docs `docs/plans/2026-07-03_memory-v2-spec/09-human-interface.md` ("no new UI required") e `skills/excrtx-harness-kanban/references/mission-control-ui-todo.md` (preferir soluções prontas) ficam **atualizados por esta issue**: o Canvas de Tarefas é o cockpit desktop do executivo/operador, complementar ao Telegram (EX-35 permanece: Telegram = executivo em movimento; WebUI/Studio = trabalho de mesa). A preferência por reuso permanece — a implementação reusa Acervo Studio, kanban bridge, clarify, goals e o harness v0.4 inteiro.

## 2. Princípios de design

| # | Princípio | Fonte |
|---|---|---|
| P1 | **O agente conduz; HITL em 3 classes apenas**: (1) gap que só o executivo responde; (2) decisão que muda o rumo (vetor ambíguo, conflito de sharing constraints, gate Draft-First); (3) intervenção com ganho claro no resultado. O workflow completo é longo demais para o humano operar — o sistema reduz atrito. | Diretriz do owner (2026-07-23) |
| P2 | **Zonas estruturadas, não canvas infinito.** Lição HCI da pesquisa: freeform confunde não-técnicos. O canvas EX-06 já tem estrutura — a UI a projeta. | Pesquisa 2026 |
| P3 | **Launch now, refine later.** Sala lançável com gaps abertos (viram premissas explícitas). Nada bloqueia por padrão. | P1 |
| P4 | **Todo item do acervo aplicado é citado** (path clicável) e rastreável. Nunca inventar para preencher gap — marcar "desconhecido". | EX-06, EX-49 |
| P5 | **Governança preservada**: Draft-First (EX-08), risk gate (perene/persona/macro = DRAFT-first), trust gate (web = untrusted), sharing firewall `allow > deny`, anti-slop ≥35/50, `.quarantine` invisível. | SOUL_SEED |
| P6 | **PT-BR na interface; estética "Calm Console"** (`hermes-webui/DESIGN.md`): tool traces como metadado silencioso, um acento por vez. | Convenções |
| P7 | **Rebase-safety**: arquivos novos + prefix dispatch; `routes.py`/`ui.js`/`style.css` quase intocados; catálogo MOD-NNN atualizado. | EXOCRTX_MODIFICATIONS.md |
| P8 | **A Web UI nativa fica intocada.** O Canvas de Tarefas vive no **Acervo Studio** (MOD-010), que evolui de cockpit de curadoria para cockpit de trabalho. Integração com o chat nativo só via contrato de sessão (staged context), nunca acoplamento DOM. | Decisão do owner |
| P9 | **Canvas verificável e editável in loco**: clique-e-edita em qualquer campo; badge de validação contra `canvas_schema.py`; distinção visual explícito×inferido; preview diff-able do brief compilado antes do launch. | Decisão do owner |
| P10 | **A condução segue o loop fable-method** (think/act/prove) com thresholds mecânicos — os hard bounds do método são os gatilhos de HITL. | Insumo do owner |
| P11 | **O contexto da tarefa é sagrado**: acompanhamento, busca no acervo e pesquisa vivem no **Curador** (agente paralelo). A Sala só retém o destilado. | Diretriz do owner |

## 3. Jornada-alvo

**Átrio** (lobby do Studio): board kanban das salas vivas (reusa `api/kanban_bridge.py` + dispatcher) · galeria de **receitas de sala** (templates canonizados) · um único campo: *"o que vamos fazer?"* (texto/voz).

1. O executivo escreve UMA frase. O enquadrador (turno estruturado do Hermes, validado por `canvas_schema.py`) **monta o canvas em streaming** diante dele: vetor classificado com confiança (EX-05), microverso âncora + apoios com badges de constraint, itens do acervo sugeridos pelo Curador (com path), artefatos esperados, **critério de pronto com verificação nomeada**, gaps como cartões de pergunta.
2. Vetor ambíguo? Um cartão de 3 botões — *executar / explorar / manter* (a pergunta canônica do EX-05). Só aparece se ambíguo.
3. Cada **cartão de gap** traz: a pergunta, por que importa, e o default que o agente assume se ignorado ("assumirei X"). Ações: responder · aceitar default · "não sei → vire subtarefa de descoberta". Fila não-modal.
4. **Lançar**: o canvas compila num brief estruturado (analogia deliberada com `compile_soul.py`) → `register_task_from_canvas.py` cria `_tasks/{id}/` → sessão Hermes nasce com o brief como contexto de abertura (staged context, ponte MOD-008/Studio) → vínculos sessão↔tarefa↔goal em `links.yaml`.
5. **Sala viva**: eventos da execução atualizam o canvas — artefatos produzidos viram cards; ações externas viram cartões de aprovação Draft-First; `clarify` vira gap card; estado kanban muda. O executivo pilota por steering, não babysitting.
6. **Checkout**: passe de juiz (verificação por execução/diff, nunca lendo o relatório) → report outcome-first → **colheita**: candidatos a canonização aprovados em lote → sala arquivada ou canonizada como receita.

Mock (evolução do bloco 🧠 do EX-06 para zonas de UI):

```
┌─ SALA · Ofício de renegociação — Cliente Alfa ────────────── [⚡ Execução ▾] ─┐
│                                                                              │
│  FOCO  Renegociar contrato com Cliente Alfa até sexta                        │
│  PRONTO QUANDO  ofício .docx aprovado pelo executivo + registrado no Drive   │
│                 verificação: manifest do artefato + receipt SHA-256          │
│                                                                              │
│  🌍 MICROVERSOS          📚 ACERVO APLICADO         🎭 PERSONAS              │
│  âncora: cliente-alfa    ✓ templates/oficio.md      redator: institucional   │
│  apoio: juridico 🔒      ✓ knowledge/historico-     avaliador: crítico       │
│  (deny ALL, allow        renovacoes.md              [+ sugerir]              │
│  gabinete)               [+ Curador sugere 2…]                               │
│                                                                              │
│  ⚠ LACUNAS (2)                        📦 ARTEFATOS ESPERADOS                 │
│  • Teto de desconto? [responder]      • oficio-renegociacao.docx             │
│    default: manter tabela vigente     • resumo-1-pagina.md                   │
│  • Prazo de vigência? [→ descobrir]                                          │
│                                                                              │
│  🧺 COLHEITA (3 pendentes)            ▶ LANÇAR SESSÃO   [preview do brief]   │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 4. Modelo de domínio

- **Fonte da verdade: `canvas.yaml` (harness v0.4)** — o canvas da UI é uma projeção editável deste objeto; estado server-side em `_tasks/{id}/`, mutações por JSON Patch.
- **Extensões propostas (canvas v0.5 / EX-06 v3)**, vindas do loop de condução: `shape` (question|task|plan-first — complementa o vetor, não o substitui), `done_criteria` + `verification` nomeada (**o campo que falta hoje**; "não consigo nomear verificação" → gap card), `scope` (superfícies a tocar; expansão = surprise), `assumptions[]` (load-bearing, checáveis), `authorization[]` (AUTH com as palavras exatas do executivo para cada ação externa — operacionaliza EX-08 com rastro citável).
- **Task**: `task.yaml` (lifecycle implicit→candidate→registered→active→blocked→ready→completed→maintained→archived) + `events.log` + `links.yaml` (sessão WebUI, goal, artefatos).
- **Acervo → UI** (natures do acervo vivo, 2026-07-23: knowledge 30 · contracts 25 · workflows 24 · decisions 17 · context 15 · templates 14 · persona 8 · skills 8 · tools 7 · reflections 7 · prompts 6, em 12 microversos): personas → zona Personas (sugeridas/explícitas/avaliadoras); templates/prompts/workflows/skills/knowledge → trilho Acervo Aplicado; decisions → zona de decisões tocadas/pendentes. Memory-v2 (episodes/entities/intentions) = extensão futura, não dependência.
- **"Estratégia"** não é nature: entra como persona (ex. `strategist.md`) ou workflow — a UI não inventa taxonomia nova.

## 5. Requisitos funcionais por épico

**E1 · Átrio** — board de salas sobre o kanban existente; galeria de receitas; intake de uma frase; estados vazios ensinam o método (primeiro uso = onboarding da mecânica).

**E2 · Enquadrador** — turno estruturado do Hermes que emite canvas JSON válido (`canvas_schema.py`) em streaming; classificação de vetor com confiança; extração de gaps/assumptions; proposta de done_criteria com verificação nomeada; re-enquadramento incremental a cada edição/resposta do executivo (canvas nunca congela — regra EX-06 "stale canvas").

**E3 · Canvas UI** — zonas fixas (Foco/Pronto, Vetor, Microversos, Acervo, Personas, Gaps, Artefatos, Colheita, Next moves); edição in loco de todo campo com persistência por delta + re-validação; badges: validade de schema, origem citada, explícito×inferido, constraint de sharing; **preview do brief compilado** (diff-able) antes do launch.

**E4 · Curador (agente paralelo, semântica A2A)** — segundo agente Hermes com contexto próprio e persistente: (a) busca no acervo via `acervoctl retrieve/posture` (budgetada, citada); (b) sugestão de skills/personas/templates/workflows com **memória viva das capacidades por microverso** (índice derivado de `_meta/index.md` + `catalog.sqlite`, refrescado e persistido no acervo); (c) pesquisa externa via Hermes (last30days, agent-reach, firecrawl) para propor soluções a agregar. Contrato executor↔curador com semântica A2A (Task/Message/Artifact + estados, updates streamados), **in-process primeiro** (padrão worker/dispatcher do kanban), upgradeable a A2A real HTTP quando o multi-container (`agent-api-contract.md`) chegar. **Higiene de contexto: a Sala recebe só artefatos destilados** ("3 skills sugeridas + por quês + paths"), nunca trilhas de busca. Sugestões proativas chegam como cards (aceitar/dispensar = HITL classe 3).

**E5 · Gaps & HITL** — generalização do padrão `api/clarify.py`: cartões com pergunta/por quê/default; fila não-modal; respostas re-enquadram o canvas; **hard bounds do método como gatilhos mecânicos** (3 ciclos de verify falhos → devolve com hipótese; 2 lookups infrutíferos → para; fit gate "só inferência" → hand-back honesto, nunca fantasia).

**E6 · Compile & Launch** — canvas → brief estruturado → `register_task_from_canvas.py` + `POST /api/session/new` + staged context + model/profile/vetor; postura da sessão configurada pelo vetor (Evolução = socrática; Execução = artefato + quality gates; Manutenção = perfil `manut`).

**E7 · Sala viva** — assinatura dos eventos da sessão: artefatos → cards com manifest; ações externas → cartões Draft-First com AUTH (palavras exatas); linhas INTENT/TWINS/PENDING do método → **trace cards clicáveis** (P9); surprise → card de achado principal com ordem de autoridade (executivo > spec > tests > código); estado kanban sincronizado.

**E8 · Colheita & canonização** — durante a execução, `promotion_candidates` (conhecimento/decisões/reflexões) e artefatos intermediários acumulam na **bandeja de colheita** (cada card: destino microverso/nature proposto, classe de gate risk/trust, diff sob demanda). HITL em lote no **checkout de fechamento**: aprovar tudo · revisar item a item · rejeitar — 1 momento, não N interrupções. Execução via `acervoctl new-object/commit-write` (propose-then-approve; ADR-022). **Canvas → receita**: transformação clean-portable (analogia EX-58): remove instância, preserva estrutura (vetor, slots de microverso, personas, perguntas de intake derivadas dos gaps, artefatos esperados, verificação) → acervo (nature `templates`/`workflows`, OKF v0.2) → galeria do Átrio.

**E9 · Contrato de eventos (AG-UI-inspired)** — taxonomia mapeada sobre `docs/rfcs/session-sse-contract-v1.md`: snapshot/delta (JSON Patch RFC 6902) para o canvas; interrupt/resume para gaps e aprovações; activity para PLAN/SEARCH; **sem adotar SDK** (constraint vanilla/no-build); tabela de correspondência AG-UI ↔ eventos nossos documentada para interop futura.

**E10 · Harness de condução (fable-method)** — a Sala executa o loop *classify → define done → evidence → decide → act → verify → report*: fases visíveis discretamente (nunca narradas no output — regra do método); triviality gate (input trivial não gera canvas — regra EX-06 preservada); fable-judge no checkout (verificação por execução/diff); report outcome-first com caveats honestos. ADR decide: port como skills `excrtx-conduct-*` (compiled_rules → SOUL_SEED, EX-IDs + dogfood) vs metodologia de referência do enquadrador. Licença MIT compatível.

## 6. Requisitos não-funcionais

- **Stack**: sem build step; se o estado da UI justificar, ilha Preact IIFE pré-bundlada (caminho já previsto no RFC do Studio) — decisão no spike F0.
- **Single-user honesto**: paralelismo real só via padrão worker/dispatcher; nunca duas `run_conversation` concorrentes no mesmo processo sem o padrão existente.
- **Latência percebida**: canvas começa a aparecer < 2s após o intake (streaming de campos conforme o enquadrador emite).
- **Custo LLM**: enquadrador e Curador podem usar o LLM role `auxiliar` (mais barato); orçamento de retrieval sempre explícito (`--budget`).
- **Segurança**: writes só pelas superfícies semânticas (`acervoctl`/MCP `acervo`); `.quarantine` bloqueado; sharing firewall `allow > deny` validado server-side (`acervo_validate_scope`); nenhum segredo no canvas.
- **A11y**: navegação por teclado em todos os cards; a fila de gaps operável sem mouse.
- **i18n**: PT-BR primário (catálogo `static/i18n.js` já traduzido — MOD-006).

## 7. ADR-candidatas (decidir em F0/F1)

1. **Superfície = Acervo Studio** (ratificada pelo owner nesta issue; Web UI nativa intocada).
2. **AG-UI como blueprint semântico, sem SDK** — taxonomia própria compatível, sobre SSE.
3. **Estado do canvas server-side** em `_tasks/` + deltas JSON Patch (cliente nunca é fonte da verdade).
4. **Invocação do enquadrador**: turno estruturado síncrono vs job+poll — spike F0 (questão já aberta no RFC do Studio §6.2).
5. **fable-method**: port `excrtx-conduct-*` vs referência metodológica do enquadrador.
6. **Curador**: semântica A2A in-process (worker/dispatcher) agora → A2A real HTTP no multi-container; um Curador singleton do Átrio vs um por sala.
7. **canvas.yaml v0.5**: shape, done_criteria/verification, scope, assumptions, authorization (retrocompatível com v0.4).

## 8. Roadmap (alto nível — plano de execução detalhado vem após revisão desta issue)

| Fase | Entrega | Gate |
|---|---|---|
| **F0 · Spike** | Enquadrador emite canvas JSON válido em streaming; deltas sobre SSE; decisão vanilla vs ilha Preact; decisão sync vs job+poll | canvas de exemplo renderizado a partir de 1 frase real |
| **F1 · MVP Sala** | Átrio mínimo + canvas verificável/editável + done_criteria + Compile & Launch | 1 frase → sala lançada → sessão com brief; `_tasks/` populado |
| **F2 · Curador** | Assistência paralela (acervo + memória de capacidades + pesquisa), contrato A2A-inspired, cards proativos | sugestões citadas aplicáveis em 1 clique; contexto da sessão não cresce com a busca |
| **F3 · Sala viva** | Loop de condução + bounds + trace cards + Draft-First/AUTH cards + kanban sync | execução real com ≤ HITL das 3 classes |
| **F4 · Colheita & canonização** | Bandeja + checkout em lote + fable-judge + canvas→receita + galeria | 1 sala real canonizada como receita reutilizada |
| **F5 · Polish** | a11y, i18n, docs, calibração (EX-ID + dogfood), UPSTREAM-SYNC | dogfood PASS; auditoria interativa GO |

## 9. Riscos & mitigações

- **Upstream drift** (~600 commits à frente): arquivos novos + prefix dispatch + `UPSTREAM-SYNC.md`; zero linhas novas em hot zones.
- **Monólitos** (`ui.js` ~950KB, `routes.py` ~1.1MB): não tocar; tudo em módulos novos (padrão Studio).
- **Concorrência single-user**: Curador e sessões paralelas só via dispatcher/worker; documentar limite na UI (fila, não paralelismo silencioso).
- **Custo/latência de dois agentes**: role auxiliar p/ Curador; retrieval budgetado; cache do índice de capacidades.
- **Scope creep**: fases gated; F1 não depende de E4/E8/E10 completos.
- **Fricção nova > fricção antiga** (o risco real de UX): medir — tempo intake→launch alvo < 60s no caminho feliz; se o canvas atrasar o usuário experiente, o bypass "lançar direto" (triviality gate) resolve.

## 10. Questões abertas

1. Naming final das superfícies (Átrio/Sala/Colheita/Receitas) — validar com o executivo no F1.
2. Handoff Telegram ↔ Sala (começar no bolso, continuar na mesa) — fase futura?
3. Multi-sessão paralela por sala na v1 ou fila?
4. Gatilho objetivo para migrar de vanilla a ilha Preact.
5. Profundidade do port fable-method na v1 (4 skills ou só method+judge?).
6. Persistência da memória viva do Curador: `global/knowledge` vs `_meta`/catalog derivado.
7. Curador singleton do Átrio vs instância por sala.

## 11. Governança & rastreamento

- Implementação = **COLLAB** (umbrella `projetob`): change record em `.harness/changes/`, branch `collab/canvas-tarefas`, e criação do contrato hoje inexistente `.harness/contracts/exocortex-hermes-webui.md` (superfícies: provisionamento, canvas.yaml v0.5, contrato de eventos, endpoints `/api/canvas/*`).
- Fork: novos MODs (MOD-011+) catalogados em `hermes-webui/EXOCRTX_MODIFICATIONS.md`.
- Skills novas/evoluídas (enquadrador, curador, conduct-*) ganham EX-ID + cenário dogfood + `compile_soul.py`.
- Esta issue é o épico-mãe; issues-filhas por fase (F0…F5) serão abertas com o plano de execução.

## 12. Referências

**Internas** — EX-05 `skills/excrtx-behavior-vetor/` · EX-06 `skills/excrtx-behavior-canvas/` (v2.0) · harness v0.4 `acervo/global/templates/harness-v0.4/{canvas,task,routine,automation}.yaml` · `acervo/global/tools/harness/{canvas_schema.py,register_task_from_canvas.py,auditor_canvas_validator.py}` · ADR-022 + `scripts/{acervoctl.py,acervo_mcp_server.py,acervo_semantic_core.py}` · memory-v2 `docs/plans/2026-07-03_memory-v2-spec/` (esp. 09-human-interface) · EX-35 `skills/excrtx-harness-surfaces/` · mission-control `skills/excrtx-harness-kanban/references/mission-control-ui-todo.md`.

**Fork (hermes-webui)** — `docs/rfcs/acervo-studio.md` · `docs/rfcs/session-sse-contract-v1.md` · `docs/architecture/{agent-api-contract,unified-session-db}.md` · `api/{acervo_studio*.py,kanban_bridge.py,clarify.py,goals.py,streaming.py}` · `EXOCRTX_MODIFICATIONS.md` (MOD-001…010) · `DESIGN.md` · `ROADMAP.md` (#1255, #719).

**Externas** — [AG-UI](https://docs.ag-ui.com/introduction) ([repo](https://github.com/ag-ui-protocol/ag-ui/)) · [A2A v1.0 — visão técnica](https://tyk.io/learning-center/a2a-protocol-architecture-and-technical-specification/) · [Claude Cowork](https://claude.com/blog/cowork-web-mobile) ([help](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)) · [GLM Slide/Poster Agent](https://docs.z.ai/guides/agents/slide) · [tldraw agent-template](https://github.com/tldraw/agent-template) · [Flowith canvas-cowork](https://github.com/flowith-ai/canvas-cowork) · [fable-method](https://github.com/Sahir619/fable-method) (loop de condução think/act/prove, MIT, evals adversariais em `eval/`) · padrões intent-framing: [co-constructing intent](https://uxdesign.cc/lifting-the-fog-co-constructing-intent-with-ai-agents-fbb503599ac0), [prompt augmentation (Nielsen)](https://jakobnielsenphd.substack.com/p/prompt-augmentation), [Smashing — agentic UX patterns](https://www.smashingmagazine.com/2026/02/designing-agentic-ai-practical-ux-patterns/).
