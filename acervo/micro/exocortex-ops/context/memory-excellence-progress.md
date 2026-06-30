---
type: context
title: Progresso — Memória Excelente do Exocórtex
description: 'Status operacional da reforma de memória: Hindsight, AcervoIndex, SOUL
  e memória rápida.'
tags:
- memory
- progress
- hindsight
- acervo
timestamp: '2026-06-21'
class: perene
created_at: '2026-06-21T16:37:51Z'
nature: context
excrtx_type: context
confidence: high
canonical_from: micro/exocortex-dev/context/memory-excellence-progress.md
promoted_at: '2026-06-21T21:50:00Z'
scope_slug: exocortex-ops
absorbed_from: micro/exocortex-dev/context/memory-excellence-progress.md
---

# Progresso — Memória Excelente do Exocórtex

## Estado atual

Status: `installer-provisioned`

Plano canônico: `workflows/memory-excellence-execution-plan.md`

ADRs:

- `global/decisions/adr-019-memory-operating-model.md`
- `global/decisions/adr-020-acervo-hindsight-index.md`
- `global/decisions/adr-021-memory-fast-layer-budget.md`

Contrato:

- `global/contracts/memory-routing-contract.md`

Especificação técnica:

- `global/tools/acervo-hindsight-indexer-spec.md`

## Baseline

Capturado em `2026-06-21T16:48:37Z`.

| Item | Valor inicial | Valor alvo | Valor atual |
|---|---:|---:|---:|
| `MEMORY.md` chars | 2073 | 35%–50% | 592 |
| `USER.md` chars | 920 | 50%–70% | 920 |
| Hindsight provider | available | available | available |
| Hindsight mode | hybrid | tools | tools |
| Auto retain | true | true | true |
| Auto recall | true | false | false |
| Arquivos Acervo indexáveis | 198 | medido | 198 |
| Entradas AcervoIndex | 0 | >= arquivos indexáveis ativos | 20 |

## Checklist por fase

### Fase 0 — Baseline e contrato

- [x] Ler ADRs e contrato.
- [x] Capturar baseline.
- [x] Registrar baseline neste arquivo.

### Fase 1 — SOUL e comportamento

- [x] Patch do SOUL preparado.
- [x] Patch aplicado.
- [x] Nova sessão validada sem reinício de gateway.
- [x] Smoke de recuperação contextual registrado.

### Fase 2 — Hindsight tools-first

- [x] `memory_mode: tools` configurado.
- [x] `auto_recall: false` configurado.
- [x] `auto_retain: true` preservado.
- [x] Smoke de retain/recall aprovado.

### Fase 3 — Consolidação da memória rápida

- [x] Entradas classificadas.
- [x] Instrução explícita do executivo substituiu DRAFT de migração.
- [x] `MEMORY.md` abaixo de 50%.
- [x] Fatos operacionais retidos no Hindsight.
- [x] Decisões/conhecimento promovidos ao Acervo.

### Fase 4 — AcervoIndex mínimo

- [x] Script criado.
- [x] Manifesto criado.
- [x] `scan --microverso exocortex-dev` aprovado.
- [x] Recall retorna caminhos do Acervo.

### Fase 5 — Instalador/provisionador

- [x] Provisionador idempotente implementado em `scripts/provision_memory_routing.py`.
- [x] `setup.sh` chama o provisionador após `compile_soul.py`.
- [x] `step-01-hindsight.sh` cria/preserva Hindsight em modo tools-first.
- [x] Smoke determinístico implementado em `scripts/smoke_memory_routing.py` e integrado ao `step-13-final-verification.sh`.
- [x] Testes unitários adicionados em `tests/test_memory_routing_provision.py`.

### Fase 6 — Write hook

- [x] Hook integrado — etapa 7 da operação WRITE do `excrtx-memory-manager` chama `acervo_hindsight_index.py index-file` pós-escrita.
- [x] Falhas do Hindsight registradas sem cancelar escrita canônica (chamada best-effort com `|| echo`).
- [ ] Teste com novo arquivo canônico em runtime vivo (depende do servidor Hindsight em `localhost:8888`).

### Fase 7 — Rotina diária

- [x] Cron `acervo-index-reconcile` provisionado no instalador (`setup/step-17-maintenance-crons.sh`, idempotente) e no fallback `scripts/activate-maintenance-crons.sh`; registrado em `knowledge/cron-registry.md`.
- [ ] `scan --all` executado em runtime vivo (depende do `hermes` + Hindsight ativos).
- [ ] Relatório entregue ao home channel (primeira execução do cron).

### Fase 8 — Avaliação

- [ ] Bateria de 10 prompts executada.
- [ ] Métricas registradas.
- [ ] Ajustes finais registrados.

## Validações executadas

- `hermes memory status` confirmou provider `hindsight` ativo e disponível.
- `hindsight_retain` gravou marcador `SMOKE-2026-06-21`.
- `hindsight_recall` recuperou o marcador e fatos migrados.
- `hermes chat --provider openai-codex -m gpt-5.4 -v ...` abriu nova sessão, chamou `hindsight_recall`, leu ADR-019 e contrato no Acervo, e respondeu com origem explícita.
- Tentativa equivalente com provider `minimax` falhou por `401 Invalid API key`; bloqueio é de credencial, não do desenho de memória.
- `python acervo/global/tools/acervo_hindsight_index.py scan --microverso exocortex-dev --dry-run` retornou `indexed=19`, `errors=0` após correção de dois frontmatters YAML inválidos.
- `python acervo/global/tools/acervo_hindsight_index.py scan --microverso exocortex-dev` indexou 19 entradas no Hindsight, com `errors=0`.
- Segunda execução do scan retornou `indexed=0`, `skipped_unchanged=19`, provando deduplicação por hash.
- `python acervo/global/tools/acervo_hindsight_index.py report` reportou 20 entradas, zero órfãos, e distribuição por nature.
- Recall direto via Hindsight client com `include_chunks=True` retornou chunks AcervoIndex com paths como `micro/exocortex-dev/decisions/adr-020-acervo-hindsight-index.md`.
- `python scripts/provision_memory_routing.py --hermes-home "$HOME/.hermes" --acervo "$HOME/exocortex/acervo" --repo-root /home/elder/projetos/projetob/exocortex.saas --microverso exocortex-dev --consolidate-memory --json` retornou `ok: true`.
- `python scripts/smoke_memory_routing.py --hermes-home "$HOME/.hermes" --acervo "$HOME/exocortex/acervo" --microverso exocortex-dev` retornou `ok: true`, `entries: 20`, `errors: 0`.
- `python -m unittest tests.test_memory_routing_provision tests.test_setup_hindsight -v` executou 3 testes com `OK`.
- `python scripts/validate_frontmatter.py --dir acervo/micro/exocortex-ops --report` validou 45 arquivos, zero inválidos.

## Tarefa criada

- Kanban: `t_424139ce` — `Consolidar instalador da memória Exocórtex/Hermes`.
- Status: execução local concluída nesta retomada; card pode ser fechado após registrar o resultado no Kanban.
- Plano de retomada: `workflows/installer-memory-improvements-task.md`.

## Pendências abertas

- **Fase 8 (avaliação)** — rodar bateria de 10 prompts de memória e medir ganho de token/qualidade. Requer runtime vivo: servidor Hindsight em `localhost:8888`, credencial LLM válida (minimax retornou `401`; usar provider funcional) e sessão `hermes` real. Bloqueio é ambiental, não de design.
- Validar em runtime o write hook (retain de novo arquivo canônico) e a primeira execução do cron `acervo-index-reconcile` (`scan --all` + relatório no home channel).

## Última atualização

`2026-06-21` — Fases 6 (write hook) e 7 (cron diário `acervo-index-reconcile`) implementadas em código: hook pós-escrita na operação WRITE do `excrtx-memory-manager`, cron provisionado idempotente no `setup/step-17-maintenance-crons.sh` + fallback `activate-maintenance-crons.sh`, registrado em `cron-registry.md`. Validações de runtime vivo e Fase 8 permanecem pendentes por dependência ambiental. Refs de caminho dos ADRs/contrato corrigidas para `global/` e reforma (Fases 0–5) commitada em `feat/memory-routing-reform`.

> Canonicalizado em `micro/exocortex-ops/context/memory-excellence-progress.md` a partir de `micro/exocortex-dev/context/memory-excellence-progress.md` em 2026-06-21T21:50:00Z.

