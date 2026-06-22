---
type: context
title: Handoff Log — Reforma de Memória do Exocórtex
description: Registro entre tarefas para agentes menores executarem a reforma de memória
  sem perda de contexto.
tags:
- memory
- handoff
- agents
- progress
timestamp: '2026-06-21'
class: volátil
created_at: '2026-06-21T16:37:51Z'
nature: context
excrtx_type: context
confidence: high
canonical_from: micro/exocortex-dev/context/memory-excellence-handoff-log.md
promoted_at: '2026-06-21T21:50:00Z'
scope_slug: exocortex-ops
absorbed_from: micro/exocortex-dev/context/memory-excellence-handoff-log.md
---

# Handoff Log — Reforma de Memória do Exocórtex

## Protocolo obrigatório

Cada agente que executar uma fase deve adicionar uma entrada no formato:

```markdown
## YYYY-MM-DDTHH:MM:SSZ — Agente/Nome — Fase

- Estado: done|blocked|partial
- Arquivos alterados:
- Comandos/validações executadas:
- Decisões tomadas:
- Pendências:
- Próximo agente recomendado:
```

## 2026-06-21T16:37:51Z — Exocórtex — Planejamento inicial

- Estado: done
- Arquivos alterados:
  - `decisions/adr-019-memory-operating-model.md`
  - `decisions/adr-020-acervo-hindsight-index.md`
  - `decisions/adr-021-memory-fast-layer-budget.md`
  - `contracts/memory-routing-contract.md`
  - `tools/acervo-hindsight-indexer-spec.md`
  - `workflows/memory-excellence-execution-plan.md`
  - `context/memory-excellence-progress.md`
  - `context/memory-excellence-handoff-log.md`
- Comandos/validações executadas:
  - `hermes memory status` executado em diagnóstico anterior: provider `hindsight` disponível.
  - Hindsight recall/reflect confirmaram presença de contexto sobre a arquitetura proposta.
  - Estrutura do microverso `exocortex-dev` inspecionada.
- Decisões tomadas:
  - Hindsight será memória operacional semântica.
  - Acervo será fonte canônica.
  - Hindsight indexará ponteiros do Acervo, não cópias integrais.
  - `MEMORY.md` será reduzido para bootstrap mínimo.
- Pendências:
  - Atualizar `SOUL.md` com regra de recuperação.
  - Configurar Hindsight para `memory_mode: tools` após aprovação operacional.
  - Consolidar `MEMORY.md` com DRAFT antes de remover entradas.
  - Implementar indexador e rotina diária.
- Próximo agente recomendado:
  - Agente A — Baseline e SOUL.

## 2026-06-21T16:55:29Z — Exocórtex — Execução das Fases 0 a 3

- Estado: done
- Arquivos alterados:
  - `~/.hermes/SOUL.md`
  - `~/.hermes/hindsight/config.json`
  - `~/.hermes/memories/MEMORY.md`
  - `context/memory-excellence-progress.md`
  - `context/memory-excellence-handoff-log.md`
  - `context/current-state.md`
- Comandos/validações executadas:
  - `hermes memory status`
  - leitura de `~/.hermes/SOUL.md`, `~/.hermes/memories/MEMORY.md`, `~/.hermes/memories/USER.md`, `~/.hermes/hindsight/config.json`
  - contagem de arquivos indexáveis do Acervo: `198`
  - `hindsight_retain` com marcador `SMOKE-2026-06-21 memória tools-first aplicada`
  - `hindsight_recall` recuperando o marcador e fatos operacionais migrados
  - `hermes chat --provider openai-codex -m gpt-5.4 -v ...` validando nova sessão com `hindsight_recall` + leitura de ADR-019 e contrato
  - tentativa equivalente com `minimax` falhou por `401 Invalid API key`
- Decisões tomadas:
  - Regra de memória foi promovida ao `SOUL.md`: Hindsight recupera; Acervo confirma; `session_search` prova; memória rápida só inicializa.
  - Hindsight passou para `memory_mode: tools` com `auto_recall: false` e `auto_retain: true` preservado.
  - `MEMORY.md` foi consolidado para 4 invariantes de bootstrap, reduzindo o uso para 592/2200 chars.
  - Fatos operacionais removidos da memória rápida foram retidos no Hindsight.
  - A instrução explícita do executivo para “executar o plano” substituiu a etapa de DRAFT de migração.
- Pendências:
  - Implementar AcervoIndex mínimo e manifesto.
  - Integrar write hook para indexação/retain pós-escrita.
  - Rodar bateria final de prompts e medir ganho de token.
- Próximo agente recomendado:
  - Agente B — AcervoIndex mínimo.

## 2026-06-21T21:13:33Z — Exocórtex — Fase 4 e tarefa do instalador

- Estado: done
- Arquivos alterados:
  - `acervo/global/tools/acervo_hindsight_index.py`
  - `acervo/global/tools/state/acervo_hindsight_index.json`
  - `context/memory-excellence-progress.md`
  - `context/memory-excellence-handoff-log.md`
  - `context/current-state.md`
  - `workflows/installer-memory-improvements-task.md`
  - `_meta/index.md`
  - `_meta/log.md`
  - `global/_meta/index.md`
  - `global/_meta/log.md`
- Comandos/validações executadas:
  - `python -m py_compile acervo/global/tools/acervo_hindsight_index.py`
  - `python acervo/global/tools/acervo_hindsight_index.py scan --microverso exocortex-dev --dry-run`
  - `python acervo/global/tools/acervo_hindsight_index.py scan --microverso exocortex-dev`
  - `python acervo/global/tools/acervo_hindsight_index.py report`
  - `hindsight_recall` e recall direto via Hindsight client com `include_chunks=True`
  - `hermes kanban create ...` seguido de `reclaim` e `block` para evitar execução automática
- Decisões tomadas:
  - O AcervoIndex mínimo fica em camada global porque serve todos os microversos.
  - O manifesto local fica em `acervo/global/tools/state/acervo_hindsight_index.json`.
  - O card de consolidação do instalador foi criado como Kanban `t_424139ce` e bloqueado para retomada posterior.
- Pendências:
  - Consolidar instalador/provisionador conforme `workflows/installer-memory-improvements-task.md`.
  - Integrar write hook.
  - Criar rotina diária de `scan --all`.
  - Rodar bateria final de 10 prompts.
- Próximo agente recomendado:
  - Agente Installer — Consolidar instalador da memória (`t_424139ce`).

## 2026-06-21T21:34:25Z — Exocórtex — Consolidação do instalador de memória

- Estado: done
- Arquivos alterados:
  - `/home/elder/projetos/projetob/exocortex.saas/setup.sh`
  - `/home/elder/projetos/projetob/exocortex.saas/setup/step-01-hindsight.sh`
  - `/home/elder/projetos/projetob/exocortex.saas/setup/step-13-final-verification.sh`
  - `/home/elder/projetos/projetob/exocortex.saas/scripts/provision_memory_routing.py`
  - `/home/elder/projetos/projetob/exocortex.saas/scripts/smoke_memory_routing.py`
  - `/home/elder/projetos/projetob/exocortex.saas/tests/test_memory_routing_provision.py`
  - `/home/elder/projetos/projetob/exocortex.saas/acervo/global/tools/acervo_hindsight_index.py`
  - `context/memory-excellence-progress.md`
  - `context/memory-excellence-handoff-log.md`
  - `_meta/log.md`
- Comandos/validações executadas:
  - `python -m py_compile scripts/provision_memory_routing.py scripts/smoke_memory_routing.py acervo/global/tools/acervo_hindsight_index.py`
  - `python -m unittest tests.test_memory_routing_provision tests.test_setup_hindsight -v` → 3 testes `OK`
  - `python scripts/provision_memory_routing.py --hermes-home "$HOME/.hermes" --acervo "$HOME/exocortex/acervo" --repo-root /home/elder/projetos/projetob/exocortex.saas --microverso exocortex-dev --consolidate-memory --json` → `ok: true`
  - `python scripts/smoke_memory_routing.py --hermes-home "$HOME/.hermes" --acervo "$HOME/exocortex/acervo" --microverso exocortex-dev` → `ok: true`, 20 entradas, zero erros
  - `python scripts/validate_frontmatter.py --dir acervo/micro/exocortex-ops --report` → 45 válidos, 0 inválidos
- Decisões tomadas:
  - O provisionamento de memória fica em script Python idempotente separado para facilitar smoke test e reuso no setup.
  - `setup.sh` executa o provisionador depois do `compile_soul.py`, garantindo que o protocolo de memória permaneça fora do bloco compilado.
  - `step-13-final-verification.sh` roda smoke determinístico local; o smoke conversacional permanece opcional por depender de provider externo.
- Pendências:
  - Integrar write hook.
  - Criar rotina diária `scan --all`.
  - Rodar bateria final de prompts para medir economia e qualidade.
- Próximo agente recomendado:
  - Agente Hook — indexação/retain em escrita canônica.

> Canonicalizado em `micro/exocortex-ops/context/memory-excellence-handoff-log.md` a partir de `micro/exocortex-dev/context/memory-excellence-handoff-log.md` em 2026-06-21T21:50:00Z.

