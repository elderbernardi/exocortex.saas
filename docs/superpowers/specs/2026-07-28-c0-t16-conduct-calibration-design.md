# C0 — Fechar o gate T16 ao vivo: calibração das skills de condução (design)

> Mini-fase do programa **Canvas de Tarefas** (meta issue elderbernardi/exocortex.saas#130). Executada ANTES de C1/C2/C3 por decisão do owner (de-riscar o maior item em aberto primeiro). Método leve (calibração de skill + fiação mínima), não o workflow pesado de design/SDD.

## 1. Contexto e problema

F3 (Sala viva) shipou a engenharia: o observer (`api/canvas_sala.py`) segue `$ACERVO/_tasks/<task_id>/conduct.jsonl`, o reducer (`api/sala_reducer.py`) traduz cada linha em eventos `sala_*`, e o Cockpit renderiza cards. As skills de método `excrtx-conduct-loop` (EX-60) e `excrtx-conduct-bounds` (EX-61) chegam à sessão lançada via SOUL (ADR-CT-07).

O gate T16 ficou **parcial** (`docs/sala/F3-GATE-PROOF.md`, 2026-07-27): a SOUL *governa o raciocínio* do agente lançado (ele classifica vetor, reconhece Draft-First EX-08, busca evidência, pergunta-quando-bloqueado), MAS **narra as fases em PT-BR na resposta** ("Classificação:", "Definição de pronto:") em vez de rodar `printf … >> conduct.jsonl`. Resultado: 0 linhas escritas → `n_events:0` → **0 cards na Sala**. O grep anti-narração só pega tokens EN exatos, então nem sinalizou.

**Objetivo do C0:** fechar o gate T16 AO VIVO — uma sessão real conduzida produz **≥1 card na Sala + ≥1 Draft-First AUTH** (não injetado) — calibrando as skills para o agente ESCREVER o `conduct.jsonl`, e corrigindo os riscos adjacentes que a varredura de risco expôs.

## 2. Decisões do owner (vinculantes)

| # | Decisão | Consequência |
|---|---|---|
| OD-C0-1 | Skills-only puro como abordagem; **se a calibração honesta não fechar o gate, PARAR e re-decidir** (sem backstop no observador, sem tool nova) | Não ressuscitar o journal-tail cortado no F3; não cunhar `conduct_append` tool |
| OD-C0-2 | Processo **leve** (calibração + fiação mínima), não design/SDD multiagente | Spec curta → editar → gate iterando → merge owner-gated |
| OD-C0-3 | **Injetar `task_id` no brief** (1 linha no fork) — a skill só LÊ | C0 deixa de ser 100% skills-only; ganha 1 mudança aditiva no fork (MOD) |
| OD-C0-4 | Gate **fixo em DeepSeek isolado** até haver build completo; **em prod a sala segue o modelo default da sessão** (não pinar) | Gate prova o mecanismo no DeepSeek; alinhamento do modelo de prod = nota F5/go-live (comportamento atual já herda o default) |

## 3. Achados da varredura de risco (4 investigadores read-only, tips de origin + runtime real)

- **A (viabilidade do append) — VIÁVEL.** A sessão lançada tem o `terminal` tool ativo e desbloqueado (`printf >>` num `_tasks/.../conduct.jsonl` não casa padrão sensível → roda sem HITL); `$ACERVO` está no env herdado (`tools/environments/local.py` passa-through, não é credencial); o dir `_tasks/<task_id>/` existe no launch (criado por `register_task_from_canvas.py` antes do `/api/chat/start`); `>>` cria o arquivo (sem `mkdir`). **Furo único:** o agente **não sabe o `task_id`** (gerado depois do brief) — derivável de `$HERMES_SESSION_ID` via `links.yaml`, mas frágil → resolvido por OD-C0-3 (injetar no brief).
- **B (truncamento da SOUL).** `load_soul_md` trunca head(70%)+tail(20%) char-based; cap = `context_length × 4 × 0.06` (piso 20K). Caso observado 128K → cap 30.720, head 21.504. SOUL atual 25.111 chars; bloco conduct em 14.434–16.019 (`NEVER narrate` em 15.687, dentro do head). **Orçamento: adicionar ≤ ~5.000 chars (teto duro ~5.600)** ao conjunto conduct-loop+bounds. **Blocker latente:** se `context_length` resolver ≤64K, cap cai a 20K (head 14K) e o bloco conduct (começa 14.434) cai fora inteiro → **fixar `context_length`/`context_file_max_chars` no config do smoke**. **C-S1:** o regex do compile captura linhas indentadas não-vazias → **linha em branco (ou só espaços) trunca silenciosamente**; manter `|`; chars especiais (`'"`/`>>`/`%s`) são seguros.
- **C (fiação observer→card).** Pipeline sólido, path bate exatamente. Todo tipo de frame tem handler. **Refinamentos:** (1) as skills só soletram os campos do frame `phase`; os demais (`artifact`/`trace`/`next_move`/`draft`/`surprise`) o reducer lê campos específicos (`draft_text`, `path`/`atype`, `text`, `query_sig`, `hypothesis`/`tried`/`output`, `subject`/`code`/`check`/`spec`/`resolution`) que o `compiled_rules` não especifica → card vazio se ausentes; **fixar o schema de campos por tipo na calibração**. (2) o grep anti-narração **não tem casa committada** — é prosa em `F3-PLANO.md` Task 16 Step 4; só EN. AUTH card + `choice:"once"` confirmados no código. `verify`/`search` só geram card ao bater o bound (por design). Replay/dedup não sujam 1 sessão limpa.
- **D (blast radius do provisionamento).** O `cp` do step-07 apaga o onboarding em **qualquer** re-`setup.sh` (CRÍTICO, bug geral); `step-04` (`macro/` via rsync sem `--ignore-existing`) e `step-05` (profiles) idem. **O comando de GA do F5 (`EXOCORTEX_ENABLE_HERMES_WEBUI=1 bash setup.sh`) dispararia o clobber.** Receita segura = `compile_soul.py --soul $HERMES_HOME/SOUL.md` (cirúrgico — só troca o bloco COMPILED_RULES), **não documentada em lugar nenhum**; docs apontam pro step-07 destrutivo (ADR-CT-07, FEATURES, F3-PLANO, INSTALL).

## 4. Escopo

### Dentro do C0

1. **Calibrar `excrtx-conduct-loop` + `excrtx-conduct-bounds`** (exocortex/skills), reforçando o `compiled_rules:` (add ≤ ~5K chars, regra C-S1):
   - O append shell é o **primeiro ato imperativo de cada fase**; rodar um `terminal` real, **nunca narrar** (reforço em PT-BR além de EN).
   - **`task_id`**: resolver UMA vez no início da sessão lendo do brief (injetado por OD-C0-3), cachear, usar path absoluto `$ACERVO/_tasks/$TID/conduct.jsonl`; **self-verify** (`wc -l`) após o 1º append pra um erro de path aparecer cedo.
   - **Schema de campos por tipo de frame** fixado (para os cards não virem vazios — achado C): `artifact{atype,title,path,tool}`, `trace{kind,title,evidence}`, `next_move{text}`, `draft{action,draft_text}`, `verify{subject,ok,tried,output,hypothesis}`, `search{query,query_sig,empty}`, `surprise{subject,code,check,spec,resolution}`.
   - Recompilar `SOUL_SEED.md` (`compile_soul.py`); verificar `## Conduct Loop`/`## Conduct Bounds` presentes + a cauda `NEVER narrate` sobrevive (prova anti-truncamento C-S1).
2. **Injetar `task_id` no brief** (fork) — 1 linha aditiva em `_handle_launch`/`compile_brief` (`api/canvas_tarefas.py`/`api/canvas_brief.py`); catalogar MOD-NNN em `EXOCRTX_MODIFICATIONS.md`.
3. **Alargar o grep anti-narração pra PT-BR** em `F3-PLANO.md` Task 16 Step 4 (add branches `Classifica[çc][ãa]o:`/`Defini[çc][ãa]o de pronto:`/`^\s*Fase:`); nota inline "promover a script/teste committado = F5".
4. **Corrigir os docs de propagação** para o caminho cirúrgico `compile_soul.py --soul $HERMES_HOME/SOUL.md`, com aviso de que o `cp`/step-07 é destrutivo num install personalizado (só válido em `$HERMES_HOME` isolado de smoke): ADR-CT-07 (`## Consequências` + Evidência-3), `FEATURES.md` (EX-60 ~604 / EX-61 ~614), `F3-PLANO.md` (~40, ~71), `INSTALL.md` (~443-450, aviso). Notar `.harness/changes/…canvas-f3….md` (umbrella) + a descrição da cadeia em `EXOCRTX_MODIFICATIONS.md` (fork, ~linha 142) como follow-up documental (anotar, não reescrever trilha de auditoria).
5. **Fixar `context_length`/`context_file_max_chars`** no `config.yaml` do smoke isolado (remove a ambiguidade B2; o caso 128K já passa mas é barato travar).
6. **Re-rodar o gate ao vivo** (smoke DeepSeek isolado :8792, prod :8787 + acervo real INTOCADOS), 1 sessão limpa, cenário canônico ("ofício de renegociação — Cliente Alfa"), iterando a calibração até sair **≥1 card na Sala + ≥1 Draft-First AUTH** de sessão REAL conduzida. Registrar em `docs/sala/F3-GATE-PROOF.md` (atualizar de PARCIAL → COMPLETO).

### Fora do C0 (deferido, documentado)

- **F5 (código):** step-07 idempotente (seed SOUL só se ausente; senão compile cirúrgico; nunca `cp` sobre SOUL com seção de onboarding) + `step-04` (`macro/`) + `step-05` (profiles) — torna o comando de GA seguro; promover o grep anti-narração a script/teste committado; cenários dogfood `EX-60.yaml`/`EX-61.yaml` + `calibrate-hermes.sh`; teste fixando `choice:"once"`; **alinhamento do modelo de prod da sala** (herdar o default selecionado da sessão).
- **Nova issue:** bug de idempotência de provisionamento (step-07 + step-04 `macro/` + step-05 profiles) — destrói estado do usuário em qualquer re-provisionamento, independente do conduct.

### Não-objetivos

Nenhuma feature de UI nova (isso é C1); nenhum backstop de síntese de frames a partir de narração (vetado, OD-C0-1); não pinar o modelo da sala em prod (OD-C0-4).

## 5. Gate de saída (C0)

Ao vivo, num smoke DeepSeek isolado (prod + acervo intocados, pid :8787 verificado antes/depois), 1 sessão real conduzida a partir de uma frase:
1. **≥1 card na Sala** renderizado a partir de linhas `conduct.jsonl` que **o próprio agente escreveu** (não injetadas) — verificável por `n_events>0` + screenshot Playwright.
2. **≥1 Draft-First AUTH** via card (o agente declarou uma ação externa como `{"t":"draft",…}` e ela virou card de autorização com as palavras verbatim).
3. O grep anti-narração (agora PT-BR) roda sobre `.messages[]` reais e retorna **vazio** (o agente não narrou a fase).

**Se, após calibração honesta, o gate não fechar → PARAR e trazer o achado + opções ao owner** (OD-C0-1). Não improvisar.

## 6. Guardrails e governança

- **Zona quente intocada:** `static/{ui,messages,sessions,panels,boot}.js`, `style.css`, `index.html`; `routes.py` = 0 linhas (endpoints por forward). A injeção do `task_id` fica em `api/canvas_*.py` (fork-owned). Invariante: não perturbar o upstream nesquena; zero build step; sem dep JS/npm.
- **Checkout compartilhado:** todo trabalho em **worktree isolada** (scratchpad), branch `collab/canvas-c0` cortada dos **tips de origin**; verificar a branch no mesmo comando composto do commit; **nunca `git add -A`** (paths explícitos). Merge via worktree **DETACHED** no tip do ORIGIN → `--no-ff` → push, **owner-gated**.
- **Runner keyless:** `cd <worktree> && /home/elder/projetos/projetob/hermes-webui/.venv/bin/python -m pytest <arquivos> -q` (PYTHONPATH=worktree). Skills keyless: `skill_judge.py --skill … --d1-only`; `compile_soul.py` (block scalar `|`, guard C-S1).
- **Smoke DeepSeek isolado:** `HERMES_HOME` = `cp ~/.hermes/config.yaml` + override `model.provider=deepseek` + `model.default=deepseek-v4-pro` + `model.base_url=https://api.deepseek.com/v1` + `model.api_mode=openai_chat_completions` + `providers.deepseek.base_url` + `DEEPSEEK_API_KEY` (de `databrain/.env`) + **fixar `context_length`/`context_file_max_chars`**; `SOUL.md` = `compile_soul.py --soul <isolado>/SOUL.md` (cirúrgico); `ACERVO` isolado. Server `server.py` `HERMES_WEBUI_PORT=8792 SALA_ENABLE=1` + venv do hermes-agent + `PYTHONPATH=<worktree>`. **Prod :8787 (pid antes/depois) + acervo real INTOCADOS.**
- **COLLAB 3-repos (commits separados por repo):** exocortex = skills conduct + ADR-CT-07 + FEATURES + `F3-PLANO.md` (inclui o grep anti-narração) + INSTALL; fork = injeção `task_id` no brief (MOD-NNN, próximo número livre); umbrella = change-record no `.harness/changes/` (aditivo; superfície §(a)–(g) inalterada — brief interno não é contrato). Provas P1–P11 e guardrails do método (Draft-First EX-08, EX-49) valem.

## 7. Sequência do programa (contexto)

C0 (esta spec) → **C1** (drift E3 + des-burocratizar Cockpit, dobrado c/ reintegração do Curador) → **C2** (F4 Colheita/E8) → **C3** (F5 Polish/GA: a11y, i18n, dogfood, docs, `sources.lock`, auditoria G0–G5, fechar #130). A calibração conduct saiu do C3 (virou C0).
