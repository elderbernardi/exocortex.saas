---
title: Snapshot funcional — antes de provisionar exocortex-ops como microverso base
created: 2026-06-05
updated: 2026-06-05
nature: context
kind: snapshot
scope_slug: exocortex-ops
authority: observed
stability: active
lifecycle_state: observed
snapshot_phase: before
snapshot_reason: base-microverse-provisioning
confidence: high
tags: [snapshot, ops, runtime, setup, drift]
---

# Snapshot funcional — antes de provisionar exocortex-ops como microverso base

## Escopo
- Motivo: capturar o estado funcional antes de preparar o provisionamento replicável do microverso `exocortex-ops`.
- Data/hora: 2026-06-05 14:42 -0300.
- Profile Hermes ativo observado: `default`.
- Modelo reportado pelo `hermes profile list`: `gpt-5.4`.
- Modelo operacional informado pelo runtime da sessão: `gpt-5.5` via OpenAI Codex.
- Hermes version: `Hermes Agent v0.15.1 (2026.5.29)`.
- HERMES_HOME presumido: `/home/elder/.hermes`.
- Acervo canônico: `/home/elder/exocortex/acervo`.
- Alias observado: `/home/elder/.hermes/acervo` resolve para `/home/elder/exocortex/acervo`.

## Estado do Acervo
- `micro/exocortex-ops` existe no runtime.
- `micro/exocortex-ops` ainda não existe no source do installer em `/home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-ops`.
- `shared/knowledge/groups.md` já inclui `exocortex-ops` em `DOMAINS` e `OPS`.
- Estrutura v2 observada: `_meta/`, `context/`, `knowledge/`, `contracts/`, `prompts/`, `skills/`, `workflows/`, `tools/`, `templates/`, `decisions/`, `reflections/`, `persona/`, `raw/`, `_archive/`.

## Arquivos observados no microverso
```text
_archive/.gitkeep
context/current-state.md
contracts/canonical-path-policy.md
contracts/operating-boundaries.md
contracts/profile-isolation.md
decisions/create-exocortex-ops.md
knowledge/integration-registry.md
knowledge/memory-providers.md
knowledge/runtime-map.md
_meta/index.md
_meta/log.md
_meta/SCHEMA.md
microverso.yaml
persona/ops-steward.md
prompts/ops-healthcheck.md
raw/.gitkeep
reflections/initial-gap-analysis.md
skills/ops-maintenance-routing.md
templates/drift-report.md
templates/ops-decision.md
tools/docbrain.md
tools/hermes-cli.md
tools/notebooklm.md
workflows/microverso-inventory.md
workflows/runtime-drift-audit.md
workflows/self-check.md
workflows/setup-change-draftfirst.md
```

## Estado Hermes
- Profiles observados:
  - `default`: running.
  - `manut`: stopped.
- MCPs observados:
  - `notebooklm`: enabled, transport `notebooklm-mcp`, tools `all`.
- Memória observada:
  - Built-in: active.
  - Provider externo: none.
  - Plugins instalados: byterover, hindsight, holographic, honcho, mem0, openviking, retaindb, supermemory.

## Setup
- Script auditado: `/home/elder/projetos/projetob/exocortex.saas/setup.sh`.
- `bash -n` do script atual: OK.
- `git status --short` no source do installer: limpo no momento da captura.
- Risco detectado: Step 3 usa `rsync -a` genérico para instalar o Acervo. Se `exocortex-ops` entrar no source sem exceção, o setup pode sobrescrever evolução local do microverso runtime.
- Mitigação proposta: excluir `micro/exocortex-ops/***` do rsync genérico e provisionar o seed com `rsync --ignore-existing`.

## Drift conhecido
| Área | Esperado | Observado | Severidade | Próxima ação |
|---|---|---|---|---|
| Installer | Seed `acervo/micro/exocortex-ops` presente | Source ainda não contém o microverso | SEV2 | Preparar DRAFT de patch, sem aplicar |
| Setup | Preservar evolução runtime | `rsync -a` genérico pode sobrescrever destino | SEV1 | Alterar setup só após aprovação explícita |
| DocBrain | Skill/docs alinhadas ao runtime | Runtime funcional em `/home/elder/exocortex/tools/docbrain`, com drift documental anterior | SEV2 | Corrigir documentação em tarefa própria |
| Modelo | Identidade operacional gpt-5.5 | `hermes profile list` ainda mostra gpt-5.4 | SEV2 | Auditar config/model em manutenção separada |

## Comandos executados
```bash
date '+%F %H:%M %z'
hermes --version
hermes profile list
hermes mcp list
hermes memory status
realpath /home/elder/.hermes/acervo
find /home/elder/.hermes/acervo/micro/exocortex-ops -type f | sort
bash -n /home/elder/projetos/projetob/exocortex.saas/setup.sh
cd /home/elder/projetos/projetob/exocortex.saas && git status --short
```
