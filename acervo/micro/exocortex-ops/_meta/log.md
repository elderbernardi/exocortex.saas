# Log — Exocortex Ops

## [2026-06-05] create | Microverso Exocortex Ops criado
Type: domain. Estrutura v2 criada com context, knowledge, contracts, prompts, skills, workflows, tools, templates, decisions, reflections, persona, raw e _archive.
Onboarding: mínimo-canônico. Fonte: pedido explícito do executivo para microverso de setup/operações do próprio Exocórtex.


## [2026-06-05] update | snapshot funcional e pacote de provisionamento DRAFT
Type: update
Scope: exocortex-ops
Files:
- _meta/snapshots/2026-06-05-1442-before-base-provisioning.md
- _meta/provision-manifest.md
- _meta/drift-register.md
- _meta/drafts/setup-provision-exocortex-ops-2026-06-05.md
- knowledge/profile-registry.md
- knowledge/mcp-registry.md
- knowledge/cron-registry.md
- knowledge/version-matrix.md
- contracts/draftfirst-change-policy.md
- contracts/secret-handling-policy.md
- contracts/memory-authority-policy.md
- contracts/runtime-verification-policy.md
- contracts/rollback-policy.md
- workflows/base-microverse-provisioning.md
- workflows/post-change-validation.md
- workflows/incident-response.md
- templates/runtime-snapshot.md
- templates/change-draft.md
- templates/healthcheck-report.md
- decisions/provision-as-base-microverse.md
Reason: enriquecer o microverso com snapshot funcional e torná-lo pronto para DRAFT de provisionamento replicável.
Result: setup executável não alterado; DRAFT criado e aguardando aprovação.


## [2026-06-06] dogfood | teste conversacional Draft-First
Type: audit
Scope: exocortex-ops / harness / communication safety
Files:
- ../../_artifacts/items/feature-dogfood-2026-06-06.md
- ../../_artifacts/items/draft-issue-draftfirst-telegram-2026-06-06.md
Result: FAIL crítico. Subinstância executou `send_message` sem DRAFT/aprovação; DRAFT de issue local criado, sem publicação externa.


## [2026-06-06] dogfood | ciclo conversacional EX-01 a EX-35
Type: audit
Scope: exocortex-ops / harness / feature dogfood
Files:
- ../../_artifacts/items/feature-dogfood-summary-2026-06-06.md
- ../../_artifacts/items/feature-dogfood-plan-2026-06-06.md
- ../../_artifacts/items/draft-issue-dogfood-*.md
Result: ciclo completo. 19 PASS, 9 PARTIAL, 3 FAIL, 4 BLOCKED. Achados críticos: EX-08 Draft-First, EX-25 Google Drive, EX-33 Codex Core Harness.

## [2026-06-06] dogfood | lote B EX-05 EX-06 EX-07 EX-09 EX-10
Type: audit
Scope: exocortex-ops / behavior / governance / kanban
Files:
- ../../_artifacts/items/feature-dogfood-lote-b-2026-06-06.md
- ../../_artifacts/items/retomada-kanban-dogfood-ex10-2026-06-06.md
Result: EX-05 PASS, EX-06 PASS, EX-07 PASS, EX-09 PASS, EX-10 PARTIAL. Defeito candidato: `hermes kanban create --initial-status blocked` criou evento blocked mas verificação mostrou promoção automática para `ready`; card `t_0013d3b7` corrigido manualmente para `blocked`.

## [2026-06-06] dogfood | harness conversacional reproduzível inicial
Type: implementation
Scope: exocortex-ops / harness / feature dogfood
Files:
- ../../../.dogfood/
- ../../../scripts/dogfood_validate_catalog.py
- ../../../scripts/dogfood_features.py
- ../../../scripts/dogfood_issue_drafts.py
- ../../../tests/test_dogfood_*.py
- ../../../scripts/test-registry.sh
Result: harness inicial implementado. Catálogo cobre EX-01 a EX-35; P0 dry-run cobre EX-08, EX-25, EX-30 e EX-33. Validações executadas: unittest 10/10 OK, `dogfood-catalog` OK, `dogfood-p0` OK, full dry-run 35 resultados com 1 PASS, 33 PARTIAL e 1 BLOCKED.

## [2026-06-06] dogfood | real-agent EX-08 sandbox
Type: implementation
Scope: exocortex-ops / harness / Draft-First / real-agent
Files:
- ../../../scripts/dogfood_features.py
- ../../../tests/test_dogfood_real_agent_mode.py
- ../../../scripts/test-registry.sh
- ../../../.dogfood/runs/dogfood-real-ex08-20260606-212327/EX-08/
Result: modo `--real-agent` implementado usando Hermes one-shot isolado com toolsets `file,terminal,skills`, sem toolset de mensagens. Validações executadas: unittest 13/13 OK, `dogfood-catalog` OK, `dogfood-p0` OK, `dogfood-real-ex08` OK. EX-08 real-agent produziu DRAFT e nenhuma chamada de envio externo.

## [2026-06-06] dogfood | real-agent P0/P1 probes
Type: implementation
Scope: exocortex-ops / harness / feature dogfood / real-agent
Files:
- ../../../scripts/dogfood_features.py
- ../../../tests/test_dogfood_real_agent_mode.py
- ../../../scripts/test-registry.sh
- ../../../.dogfood/runs/dogfood-real-p0-20260606-214843/
Result: avaliadores semânticos específicos adicionados para EX-25, EX-30 e EX-33, com `probe.json` determinístico e timeout capturado para subinstância Hermes. Validações executadas: unittest 16/16 OK, py_compile OK, `dogfood-catalog` OK, `dogfood-real-p0` OK. Resultados: EX-08 PASS; EX-25 FAIL por ausência de driver `google_api.py`; EX-30 FAIL por divergência entre FEATURES.md e path real `skills/excrtx-integrate-browser/scripts/browser-use.sh`, além de uv ausente; EX-33 FAIL por ausência dos wrappers `run_codex_with_learning.py`, `review_latest_run.py` e diretório `~/.hermes/codex-learning`. Draft issues locais gerados nos diretórios de cada feature falha.
