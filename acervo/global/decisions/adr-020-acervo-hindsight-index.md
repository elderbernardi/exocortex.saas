---
type: decision
title: ADR-020 — Hindsight como Índice Semântico do Acervo
description: 'Define o AcervoIndex: Hindsight armazena ponteiros semânticos para arquivos
  canônicos do Acervo, não cópias integrais.'
tags:
- memory
- hindsight
- acervo
- semantic-index
- retrieval
timestamp: '2026-06-21'
class: perene
created_at: '2026-06-21T16:37:51Z'
nature: decisions
excrtx_type: decision
confidence: high
status: accepted
canonical_from: micro/exocortex-dev/decisions/adr-020-acervo-hindsight-index.md
promoted_at: '2026-06-21T21:50:00Z'
scope_slug: global
---

# ADR-020 — Hindsight como Índice Semântico do Acervo

## Status

Accepted.

## Contexto

O Acervo contém conhecimento canônico, mas o agente nem sempre sabe onde procurar. O Hindsight resolve busca semântica, mas não deve virar cópia paralela do Acervo.

## Decisão

Criar o conceito de `AcervoIndex` no Hindsight.

Cada arquivo canônico do Acervo vira uma entrada curta no Hindsight com:

```text
AcervoIndex
path: micro/exocortex-dev/decisions/example.md
microverso: exocortex-dev
nature: decisions
title: Título canônico
tags: [tag1, tag2]
status: active
class: perene|volátil
hash: sha256:...
summary: Resumo curto do conteúdo e da decisão/conhecimento.
```

O Hindsight guarda **ponteiro + resumo + metadados**. O conteúdo integral continua no Acervo.

## Escopo indexável

Indexar:

- `context/`
- `knowledge/`
- `decisions/`
- `reflections/`
- `contracts/`
- `tools/`
- `workflows/`

Excluir:

- `raw/`
- `_archive/`
- `.quarantine/`
- arquivos `deprecated: true`
- manifests temporários
- outputs de artefatos, salvo quando promovidos a conhecimento ou decisão

## Fluxo de recuperação

```text
Pergunta do executivo
  → hindsight_recall(query)
  → retornar candidatos AcervoIndex
  → ler 1-3 arquivos canônicos no Acervo
  → responder citando origem
```

## Atualização do índice

Dois gatilhos devem coexistir:

1. **Write hook** — após escrita canônica no Acervo, indexar o arquivo alterado.
2. **Rotina diária** — varrer arquivos canônicos, comparar hash, reindexar drift e reportar órfãos.

## Política de conflito

Se Hindsight e Acervo divergirem:

1. Ler arquivo no Acervo.
2. Verificar `deprecated`, `class`, `last_accessed_at` e `updated`.
3. Tratar Acervo como verdade atual.
4. Usar Hindsight apenas para localizar candidatos.

## Critérios de aceite

- [ ] Busca por tema recupera candidatos com `path` do Acervo.
- [ ] O agente lê o arquivo canônico antes de responder sobre decisão ou conhecimento.
- [ ] Entradas `deprecated` e `.quarantine` não entram no índice ativo.
- [ ] Rotina diária reporta novos, alterados, órfãos e erros.

> Canonicalizado em `global/decisions/adr-020-acervo-hindsight-index.md` a partir de `micro/exocortex-dev/decisions/adr-020-acervo-hindsight-index.md` em 2026-06-21T21:50:00Z.

