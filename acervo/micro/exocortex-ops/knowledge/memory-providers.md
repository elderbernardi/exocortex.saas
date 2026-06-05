---
title: Providers de Memória
created: 2026-06-05
updated: 2026-06-05
nature: knowledge
type: fact
tags: [memory, providers, hindsight]
sources: [command:hermes-memory-status]
confidence: high
---

# Providers de memória

## Estado inicial observado

- Built-in memory: sempre ativo.
- Provider externo ativo: nenhum no momento da verificação.
- Hindsight: plugin instalado, mas não ativo.

## Providers instalados observados

- byterover
- hindsight
- holographic
- honcho
- mem0
- openviking
- retaindb
- supermemory

## Política operacional

- Ativar ou trocar provider de memória é mudança de configuração; deve ser tratada como ação sensível.
- Se envolver instalação, credenciais, migração ou retenção externa, usar DRAFT e aguardar aprovação explícita.
- Não registrar segredos neste microverso.
