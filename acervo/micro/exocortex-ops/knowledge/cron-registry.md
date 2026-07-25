---
schema: acervo/v0.2
type: knowledge
title: Registro de cron jobs
description: Registro de cron jobs canônicos do microverso, incluindo a reconciliação diária do AcervoIndex e o despachante autônomo de notícias.
tags: [cron, automacao, manutencao]
timestamp: 2026-06-05
class: volátil
status: active
epistemic: fact
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-07-24T00:00:00Z
updated: 2026-07-24
nature: knowledge
kind: registry
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
created: 2026-06-05
---

# Registro de cron jobs

## Crons canônicos

### acervo-index-reconcile (ADR-020)

| Campo | Valor |
|---|---|
| job_id | Atribuído na ativação (`hermes cron list` após `scripts/activate-maintenance-crons.sh`) |
| schedule | `0 5 * * *` (diário 05:00 GMT-3) |
| script | `python "$ACERVO/global/tools/acervo_hindsight_index.py" scan --all` + `report` |
| profile/workdir | perfil `manut` (persona síndico), workdir = Acervo |
| side effects | Indexa ponteiros do Acervo no Hindsight (rede → localhost:8888); escreve manifesto `global/tools/state/acervo_hindsight_index.json`; envia relatório ao home channel. **Não apaga** entradas Hindsight. |
| approval | Reforma Memory Excellence (Fases 6–7); ver `workflows/memory-excellence-execution-plan.md` |
| rollback | `hermes cron delete acervo-index-reconcile` (ou pausar via `hermes cron`); a indexação é idempotente e não-destrutiva |

### memory-eval-live-monthly (Phase 6)

| Campo | Valor |
|---|---|
| job_id | `f0289a5c897e` |
| schedule | `0 5 1 * *` (dia 1, 05:00 GMT-3) |
| script | `bash scripts/run-memory-live-eval.sh "$ACERVO" "$EXOCORTEX_MEMORY_EVAL_QUESTIONS"` |
| profile/workdir | perfil default, workdir = repo do installer |
| side effects | Gera report `tests/memory-eval/report/live-*.{json,md}`; fora do fixture, materializa knowledge canônico no Acervo alvo via `file_memory_eval_knowledge.py`; envia resumo ao home channel. |
| approval | Reforma memory-v2 — Phase 6 live eval |
| rollback | `hermes cron delete memory-eval-live-monthly` |

### memory-learning-loops-monthly (Phase 6 — H7/H12)

| Campo | Valor |
|---|---|
| job_id | `e127f4a26b2e` |
| schedule | `15 5 1 * *` (dia 1, 05:15 GMT-3) |
| script | `python3 scripts/report_memory_learning_loops.py --acervo-root "$ACERVO" --format markdown --window-days 30` |
| profile/workdir | perfil default, workdir = repo do installer |
| side effects | Leitura do Acervo + `consolidation-scan`; sem mutações canônicas. Entrega resumo de H7 (ratio de correções pós auto-commit) e H12 (use-decay) ao home channel. |
| approval | Reforma memory-v2 — Phase 6 learning loop reporting |
| rollback | `hermes cron delete memory-learning-loops-monthly` |

### news-producer-dispatch (docs/plans/2026-07-24_noticias-producer-skill)

| Campo | Valor |
|---|---|
| job_id | Atribuído na ativação (`hermes cron list` após `hermes cron create --name news-producer-dispatch ...`) |
| schedule | `0 6 * * *` (diário 06:00 GMT-3) — cadência do SO ≤ menor `cadence` de `config/noticias.toml` (hoje `weekly` em todas as áreas monitoradas); diário é suficiente |
| script | Sessão Hermes carrega a skill `excrtx-news-sales-ai` em **Modo A (autônomo, macro)**: `python3 skills/excrtx-news-sales-ai/scripts/news_dispatch.py --config skills/excrtx-news-sales-ai/config/noticias.toml --state "$NEWS_CADENCE_STATE" --now $(date +%s)` lista as áreas vencidas; para cada área o agente roda pesquisa (`excrtx-research-cpg-brasil`) → `build_dossier.py` → curadoria (modelo + `excrtx-quality-antislop`) → guard (`scripts/news_guard.py`, read-before-write) → publish via MCP `sales-ai.publish_noticia` (escopo=macro) → `news_dispatch.py --mark <slug> --now $(date +%s)` → `expire_noticia` para itens vencidos |
| profile/workdir | perfil default, workdir = repo do installer (`exocortex.saas/`) |
| side effects | Publica em `noticias_publicas` via MCP `sales-ai` (DataBrain-free, `use_docbrain=false`); escreve `last_run_at` por área em `NEWS_CADENCE_STATE`; expira itens vencidos via `expire_noticia`. **Não** sobe o harness DataBrain como processo ativo. |
| approval | Gate de ação externa recorrente via `excrtx-govern-draftfirst` na criação do cron (DRAFT → aprovação explícita); uma vez vivo, cada disparo publica autonomamente — **o despachante (`news_dispatch.py`), não o cron do SO, é o árbitro real de qual área roda em cada disparo**. Ver `docs/plans/2026-07-24_noticias-producer-skill/design.md` §5. |
| ativação | ⏳ **PENDENTE — executar na instância Hermes de runtime (não no host de dev).** Runbook de handoff passo-a-passo (creds, MCP wiring, smoke dry-run, publish, criação do cron): `skills/excrtx-news-sales-ai/ACTIVATION.md`. |
| rollback | `hermes cron delete news-producer-dispatch`; o estado de cadência em `NEWS_CADENCE_STATE` é preservado (pausar/retomar não perde `last_run_at`) |

## Regra

Todo cron recorrente deve registrar:

| Campo | Exigência |
|---|---|
| job_id | ID real retornado por `cronjob list` |
| schedule | Cron expression ou intervalo |
| prompt/script | Conteúdo completo ou path |
| profile/workdir | Escopo de execução |
| side effects | Envio, escrita, rede, alteração de estado |
| approval | Link ou referência ao DRAFT aprovado |
| rollback | Como pausar/remover |

Cron jobs não podem criar outros cron jobs em execução autônoma.
