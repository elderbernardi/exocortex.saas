---
schema: acervo/v0.2
type: workflow
title: Inventário de Microversos
description: 1. Listar diretórios em `~/.hermes/acervo/micro`.
tags: [microverso, inventory, acervo]
timestamp: 2026-06-05
class: volátil
status: active
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
excrtx_type: workflow
nature: workflows
sources: ['conversation:microverso-inventory']
confidence: high
created: 2026-06-05
---

# Inventário de microversos

## Procedimento

1. Listar diretórios em `~/.hermes/acervo/micro`.
2. Ignorar `_template` como domínio ativo.
3. Ler `_meta/SCHEMA.md` e `_meta/index.md` de cada microverso ativo.
4. Reportar tipo, escopo, maturidade e lacunas.
5. Não carregar conteúdo interno profundo sem necessidade.

## Maturidade

- Estrutural: tem diretórios e schema.
- Operacional: tem workflows/skills/tools usáveis.
- Vivo: tem logs, decisões, reflexões e cross-refs produzidos por uso real.
