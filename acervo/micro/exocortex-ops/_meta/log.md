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
