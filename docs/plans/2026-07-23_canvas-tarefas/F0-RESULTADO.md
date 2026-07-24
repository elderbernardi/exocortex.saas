# F0-RESULTADO — Canvas de Tarefas (spike)

> Resultado do spike F0 (meta issue [#130](https://github.com/elderbernardi/exocortex.saas/issues/130), fase [#131](https://github.com/elderbernardi/exocortex.saas/issues/131)). Branch: `collab/canvas-tarefas` no fork `hermes-webui`. Todas as seções trazem output bruto — nada resumido sem a evidência ao lado.

## 1. Baseline vs suíte final

Comando (idêntico nas duas corridas): `python3 -m pytest tests/ -q -p no:cacheprovider 2>&1 | tail -3`

**T0 (baseline, antes do spike):**
```
12 failed, 13004 passed, 101 skipped, 1 xfailed, 2 xpassed, 9 warnings, 34 subtests passed in 446.32s
```

**Agora (após as 8 tasks do spike, branch `collab/canvas-tarefas`):**
```
12 failed, 13028 passed, 101 skipped, 1 xfailed, 2 xpassed, 9 warnings, 34 subtests passed in 431.97s (0:07:11)
```

**Veredito: sem regressão.** `failed` permanece em **12** (mesmos 12 nomes, listados abaixo — nenhum é dos módulos `canvas_*`); `passed` sobe **13004 → 13028 (+24)**, exatamente os 24 testes novos do spike (`test_canvas_store.py` 7 + `test_canvas_validate.py` 6 + `test_canvas_enquadrador.py` 5 + `test_canvas_routes.py` 6 = 24; o F0-PLANO listava contagens por tarefa somando 16 — os fixes das reviews elevaram o total real a 24). `skipped`/`xfailed`/`xpassed`/`subtests` idênticos.

12 falhas pré-existentes (env-sensíveis, já documentadas em rounds anteriores do SDD — nenhuma nova, nenhuma no escopo do canvas):
```
FAILED tests/test_issue4685_post_compression_context_metering.py::test_post_compression_estimate_uses_compressor_budget_counter_without_metadata_estimators
FAILED tests/test_tls_aware_probe.py::test_helper_self_signed_warns_and_succeeds
FAILED tests/test_tls_aware_probe.py::test_helper_insecure_optin_is_silent
FAILED tests/test_workspace_git.py::test_git_fetch_pull_and_push_with_upstream
FAILED tests/test_workspace_git.py::test_git_fetch_pull_and_push_skip_repo_local_remote_helpers_when_destructive_mode_enabled
FAILED tests/test_workspace_git.py::test_git_fetch_skips_repo_local_remote_helpers_without_destructive_mode
FAILED tests/test_workspace_git.py::test_git_branches_lists_local_remote_and_upstream
FAILED tests/test_workspace_git.py::test_git_checkout_local_new_remote_dirty_and_invalid_refs
FAILED tests/test_workspace_git.py::test_git_pull_skips_repo_local_hooks_when_destructive_mode_enabled
FAILED tests/test_workspace_git.py::test_git_fetch_skips_repo_local_reference_transaction_hook_without_destructive_mode
FAILED tests/test_workspace_git.py::test_git_pull_blocks_repo_local_filters_when_destructive_mode_enabled
FAILED tests/test_xsession_wakeup_misroute.py::test_turn_identity_binder_restores_previous_value
```

Suíte isolada dos 4 módulos canvas (evidência complementar):
```
$ python3 -m pytest tests/test_canvas_store.py tests/test_canvas_validate.py tests/test_canvas_enquadrador.py tests/test_canvas_routes.py -q -p no:cacheprovider
Running 24 items in this shard
........................                                                 [100%]
24 passed in 3.00s
```

**Nota de transparência (reverificação pós-interrupção de sessão):** duas corridas subsequentes da suíte completa (ainda **sem nenhuma mudança de código** desta task — só a entrada de docs do MOD-011 em `EXOCRTX_MODIFICATIONS.md`) produziram `13 failed, 13027 passed` em vez de `12 failed, 13028 passed`. A 13ª falha, `tests/test_credential_pool_providers.py::test_custom_provider_detected_by_get_available_models`, **passa isoladamente** (`1 passed in 4.90s`) e mexe em cache global de config (`config._CREDENTIAL_POOL_CACHE`, `config._cfg_mtime`) não relacionado a nenhum módulo `canvas_*` — classificando-se como flake de isolamento/ordem de teste pré-existente na suíte (mesma categoria "env-sensível" das 12 falhas documentadas), não uma regressão introduzida pelo spike — mas sem descartar por completo o mecanismo: esta task acrescentou 24 arquivos de teste ao repositório (o spike), o que altera a ordem de coleta do pytest, então existe em princípio um mecanismo de dependência de ordem entre módulos capaz de produzir esse tipo de flake; a classificação acima repousa em corridas de código **IDÊNTICO** (sem qualquer mudança de `.py` nesta task) que produziram tanto 12F quanto 13F, mais o passe isolado do teste em questão — não na alegação de que nenhum mecanismo exista. `passed` some 1 a menos (13027 vs 13028) exatamente pela falha ter capturado esse teste em vez de contá-lo como sucesso — a contagem de testes novos do canvas (24) permanece intacta e verificada isoladamente acima.

## 2. E2E com stub (gate (a) da issue F0)

Servidor local (`./ctl.sh start`) com `CANVAS_LLM_CMD` apontando (caminho **absoluto**, ver §4) para `tests/fixtures/stub_llm_ok.py`.

**curl (sanidade da API/SSE):**
```
$ curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8787/static/canvas-dev.html
200

$ timeout 8 curl -sN "http://127.0.0.1:8787/api/canvas/stream?canvas_id=$CID"
event: canvas_snapshot
data: {"canvas_id": "canvas_20260724_161305_renegociar-contrato-com-o-cliente-alfa-a", "focus": "", ... "vector": "evolucao", "intent_type": "explorar", ...}

event: canvas_delta
data: [{"op": "replace", "path": "/focus", "value": "Renegociar contrato Alfa"}, {"op": "replace", "path": "/vector", "value": "execucao"}, {"op": "replace", "path": "/intent_type", "value": "produzir"}, {"op": "add", "path": "/gaps/-", "value": "Teto de desconto?"}]

event: canvas_done
data: {"valid": true, "errors": []}
```

**Browser (Playwright MCP)** — frase real digitada: `renegociar contrato com o cliente Alfa até sexta`. Zonas renderizadas: Foco = "Renegociar contrato Alfa"; Vetor = "execucao · produzir"; Microverso âncora = "—" (esperado, stub retorna `microverso_primary: null`); Lacunas = "Teto de desconto?". Linha de status observada ao final (texto exato, citado da Task 5):

> **"✓ canvas válido (schema v0.4)"**

Screenshot (fullPage) salvo em `hermes-webui/.superpowers/sdd/t5-canvas-dev.png` — **este caminho é git-ignorado** (diretório `.superpowers/` fica fora do controle de versão do fork), então o arquivo não é rastreável via link de repositório; a citação da linha de status acima + o transcript SSE/curl bruto acima são a evidência reproduzível em texto. Fonte completa do transcript: `hermes-webui/.superpowers/sdd/task-5-report.md`.

**Caveat de transparência para o gate — leia antes de aprovar:** o screenshot `t5-canvas-dev.png` mostra conteúdo vindo do **STUB** (`tests/fixtures/stub_llm_ok.py`), não de uma resposta de LLM real. A validade do pipeline com LLM real **está comprovada**, mas por outra evidência: a tabela de latência da §3 (3/3 chamadas com `valido=True`), rodada através do **MESMO pipeline** (mesmos endpoints SSE, mesma validação `canvas_validate`) — só que sem captura de browser nessa corrida com LLM real. Ou seja: a prova visual (screenshot) é stub; a prova de correção fim-a-fim com LLM real é a tabela de latência, não um screenshot.

## 3. Latência real (LLM real, `deepseek-v4-pro`)

Script: `scripts/spike_canvas_latency.py`. Seam: `CANVAS_LLM_CMD=python3 .../scripts/spike_llm_cmd.py`, `CANVAS_LLM_MODEL=deepseek-v4-pro` (ver §5 — override obrigatório).

| Frase (truncada) | first_delta | done | válido |
|---|---|---|---|
| "Preparar ofício de renegociação do contrato " | 18.5s | 18.5s | True |
| "Estou pensando em como estruturar o lançamen" | 18.4s | 18.4s | True |
| "Revise as pendências do microverso exocortex" | 13.4s | 13.4s | True |

3/3 válidas (≥2/3 exigido pelo brief). `first_delta == done` nas 3 porque o seam `spike_llm_cmd.py` faz uma chamada bloqueante **não-streaming** ao provider — a resposta inteira só chega depois que o LLM termina de gerar, então `canvas_delta` e `canvas_done` disparam juntos, no fim da latência total.

## 4. Invocação (achados da investigação T3/Step 1)

Grep dirigido em `api/streaming.py`, `api/config.py`, `api/providers.py` por helpers de completion single-shot (`def .*complete`, `def .*chat(`, `def ask_`, `_chat_completion`): nenhum helper reutilizável de invocação single-shot foi encontrado. Existe `run_conversation` (orquestração completa, não um helper simples) e callbacks de tool-call (`_record_live_tool_complete`, `on_tool_complete`), não invocação de LLM.

**Conclusão**: não há seam in-process pronto para reuso; o seam externo `CANVAS_LLM_CMD` (subprocess) foi a escolha correta para o spike. A integração definitiva com o runtime in-process fica para a F1, e é o gatilho natural para reavaliar streaming token-a-token (ver Consequências da ADR-CT-04).

## 5. ADRs decididas

- **[ADR-CT-04 — Invocação do enquadrador](adr/ADR-CT-04-invocacao-enquadrador.md)** — `status: decidida`. Decisão: **(b) job + poll**. `p50(done)=18.4s` (≤20s, OK) mas `first_delta` nunca ≤8s nas 3 frases (mín. 13.4s) — a regra exige as duas condições simultaneamente e falha na de `first_delta`, então cai no "caso contrário" da regra escrita.
- **[ADR-CT-05 — Vanilla JS vs ilha Preact](adr/ADR-CT-05-vanilla-vs-ilha.md)** — `status: decidida`. Decisão: **vanilla JS** na F1. `static/canvas-tarefas.js` = 80 linhas (≤~400) e render stateless (uma variável global `canvas`, `applyPatch()` + re-render total), zero bugs de sincronização observados no E2E nem na corrida com LLM real. Gatilho de migração para ilha Preact registrado na própria ADR (≥3 stores mutáveis interdependentes OU ~900 linhas).

## 6. Achados de framework (obrigatórios)

1. **Drift `vetor` × `vector`, duas camadas núcleo/documento.** O schema oficial `$ACERVO/global/tools/harness/canvas_schema.py` (`CANVAS_SCHEMA`, flat, `additionalProperties: False`) usa a chave **`vetor`**. O template `$ACERVO/global/templates/harness-v0.4/canvas.yaml` (documento rico, aninhado — `user_intention`, `dominant_entity`, `task_candidate`, `promotion_candidates`, etc.) usa a chave **`vector`**. O spike resolveu isso com **duas camadas explícitas**: o "núcleo" (schema v0.4, `vetor`/`intent_type`/`focus`/...) validado por `canvas_validate.validate_core`, mapeado para o "documento" (template rico) por `canvas_store.core_to_patch` (`vetor→/vector`, `microverso_primary→/microversos/primary`, etc.). Funcionou para o spike, mas é uma tradução manual campo-a-campo que só cobre os campos do núcleo — **recomendação: unificar em canvas v0.5 durante a F1** (escolher um nome único de campo e eliminar a camada de tradução, ou formalizar as duas camadas como contrato estável se a distinção núcleo/documento for intencional).
2. **Enum de `intent_type` divergente.** Schema oficial: 5 valores (`explorar, decidir, produzir, revisar, manter`). Template: 8 valores (os mesmos 5 + `publicar, ingestao, outro`). `validate_core` valida contra os 5 do schema; se o enquadrador (ou uma versão futura) usar `publicar`/`ingestao`/`outro`, a validação do núcleo rejeita um valor que o documento-template considera válido. **Recomendação: unificar o enum em canvas v0.5 durante a F1** (mesma decisão do item 1, mesmo dono).
3. **`CANVAS_LLM_CMD` exige caminho absoluto.** O subprocess do enquadrador roda com cwd = diretório do agente Hermes (`~/.hermes/hermes-agent`), não a raiz do repo `hermes-webui`. Um `CANVAS_LLM_CMD` relativo (ex.: `python3 scripts/spike_llm_cmd.py`, como o F0-PLANO originalmente ilustrava) resolve para o caminho errado e falha **silenciosamente** — o enquadrador reporta `canvas_done {"valid": false, "errors": [...]}`, sem nunca emitir `canvas_delta`, o que é fácil de diagnosticar erroneamente como bug de schema/LLM em vez de path. Descoberto na Task 5, contornado com caminho absoluto em todas as tasks seguintes (5 e 6). Recomendação para F1: o servidor resolver `CANVAS_LLM_CMD` relativo à raiz do próprio repo, ou documentar o requisito de caminho absoluto de forma visível (`ctl.sh`/README).
4. **Modelo default do seam desatualizado.** `scripts/spike_llm_cmd.py` usa `deepseek-chat` como default de `CANVAS_LLM_MODEL`. O provider atual do ecossistema (DeepSeek) só aceita `deepseek-v4-pro` ou `deepseek-v4-flash` — `deepseek-chat` retorna `HTTP 400 Bad Request` ("The supported API model names are deepseek-v4-pro or deepseek-v4-flash..."). A Task 6 precisou setar `CANVAS_LLM_MODEL=deepseek-v4-pro` explicitamente para a medição de latência real funcionar. Não corrigido no seam (fora do escopo do commit da Task 3, já commitado); sinalizado aqui para follow-up em F1.

## 7. Pendências deliberadas

Nenhuma ação prescrita no F0-PLANO ficou sem execução — as 8 tasks (T0–T7) foram completadas em sequência, incluindo os fix-reports de revisão (guard de validação no enquadrador, cobertura de retry, non-mkdir no read-path, cobertura do branch de template, guard de thread + sweep de streams não-abertos no dispatcher). Único item não corrigido *dentro do próprio spike* — por estar fora do escopo do commit que o introduziu — é o achado 4 acima (modelo default do seam); está registrado como follow-up explícito para a F1, não como pendência esquecida.

`PENDING:` nenhuma.

## 8. Arquivos e commits

Ver entrada MOD-011 em `hermes-webui/EXOCRTX_MODIFICATIONS.md` para a lista completa de arquivos. Branch `collab/canvas-tarefas`, commits T0→T7:
```
96d78892 feat(canvas-f0): server-side canvas store in $ACERVO/_tasks (MOD-011 spike)
3c1a8b14 fix(canvas-f0): no mkdir on read path; cover template-load branch
b9f8542b feat(canvas-f0): core validation against official canvas schema v0.4
d287854e fix(canvas-f0): validate_core tolerates non-string enum values from malformed LLM output
1b383333 feat(canvas-f0): enquadrador turn (phrase -> validated canvas core) behind LLM seam
43170026 fix(canvas-f0): guard first validation like retry; cover retry branch
85dcf44a feat(canvas-f0): /api/canvas prefix dispatch with SSE snapshot/delta/done
f3327c9d fix(canvas-f0): gate deltas on validity; guard enquadrador thread; sweep unopened streams
271d2b1c feat(canvas-f0): dev page rendering canvas zones from SSE snapshot+deltas
50fe8496 feat(canvas-f0): latency measurement script
```
+ o commit final desta task (MOD-011 no `EXOCRTX_MODIFICATIONS.md`).
