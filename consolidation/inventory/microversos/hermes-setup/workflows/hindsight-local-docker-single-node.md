---
title: Workflow — Hindsight Local em Docker Único (single-node)
created: 2026-06-01
updated: 2026-06-01
nature: processos
kind: workflow
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global]
authority: canonical
operational_mode: executable
stability: active
sources: [~/.hermes/setup.sh, /home/elder/projetos/pessoal/exocortex.saas/setup.sh, https://github.com/vectorize-io/hindsight]
derived_from: [workflows/hindsight-operational-memory.md]
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: exocortex-operational-memory
  assumed_version: null
  coupling: adapter-only
tags: [hindsight, docker, local, setup, memory]
---

# Workflow — Hindsight Local em Docker Único (single-node)

## Objetivo

Subir Hindsight local com persistência de dados em volume local, no mesmo host do Hermes, com operação simples e reversível.

## Topologia

- Um container: `exocortex-hindsight`
- Diretório dedicado: `~/.hermes/hindsight-local`
- Persistência: `~/.hermes/hindsight-local/data`
- API: `localhost:8888`
- UI: `localhost:9999`

## Regras operacionais

1. Um Hindsight por instância Hermes.
2. Perfis `exec` e `evol` compartilham a mesma memória (bank único do Hermes).
3. Sem exclusão automática de memória em update.
4. Exclusão só com confirmação explícita por parâmetro.

## Parâmetros de controle

- `EXOCORTEX_ENABLE_HINDSIGHT=1` ativa o fluxo.
- `EXOCORTEX_HINDSIGHT_DIR` redefine diretório base.
- `EXOCORTEX_HINDSIGHT_API_PORT` redefine porta API.
- `EXOCORTEX_HINDSIGHT_UI_PORT` redefine porta UI.
- `EXOCORTEX_HINDSIGHT_RESET_DATA=1` solicita wipe.
- `EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY` confirma wipe.

Sem os dois últimos parâmetros juntos, a memória é preservada.

## Passo a passo

1. Executar setup:

```bash
EXOCORTEX_ENABLE_HINDSIGHT=1 bash ~/.hermes/setup.sh
```

2. Verificar arquivos gerados:

- `~/.hermes/hindsight-local/docker-compose.yml`
- `~/.hermes/hindsight-local/.env`
- `~/.hermes/hindsight-local/data/`

3. Confirmar serviço ativo:

```bash
docker ps | grep exocortex-hindsight
```

4. Verificar provider:

```bash
hermes memory status
```

## Wipe controlado da memória

```bash
EXOCORTEX_ENABLE_HINDSIGHT=1 \
EXOCORTEX_HINDSIGHT_RESET_DATA=1 \
EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY \
bash ~/.hermes/setup.sh
```

## Pós-ativação esperada

- `memory.provider=hindsight`
- `memory.memory_enabled=false`
- `memory.user_profile_enabled=false`

Isso evita duplicidade com memória simples local.
