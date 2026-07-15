---
schema: acervo/v0.2
type: contract
title: Constantes do Lifecycle de Memória
description: Single source of truth for memory lifecycle thresholds (quarantine, purge, page sizes, fast-layer budgets).
tags: [memory, lifecycle, quarantine, contract, constants]
timestamp: 2026-07-04
class: perene
status: active
created_at: 2026-07-04T00:00:00Z
nature: contracts
excrtx_type: rule
confidence: high
scope_slug: global
---

# Constantes do Lifecycle de Memória

Fonte canônica única dos thresholds numéricos do lifecycle do Acervo. Estes
valores eram restatados em três skills (`excrtx-memory-manager`,
`excrtx-memory-syndic`, `excrtx-memory-quarantine`); a partir deste contrato,
o valor definido aqui é o que vale.

## Tabela de Constantes

| Constante | Valor | Definição | Usada por | ADR |
|---|---|---|---|---|
| `STALE_VOLATILE_QUARANTINE_DAYS` | **90 dias** | Arquivo `class: volátil` com `last_accessed_at` mais antigo que 90 dias vira candidato a quarentena (stale volatile) | `excrtx-memory-syndic`, `excrtx-memory-quarantine`, `excrtx-memory-manager` | ADR-015, ADR-018 |
| `LONG_DEPRECATED_QUARANTINE_DAYS` | **180 dias** | Arquivo `deprecated: true` com `deprecated_at` mais antigo que 180 dias vira candidato a quarentena (long-deprecated) | `excrtx-memory-syndic`, `excrtx-memory-quarantine` | ADR-014, ADR-015, ADR-018 |
| `QUARANTINE_PURGE_WINDOW_DAYS` | **30 dias** | Janela de quarentena: `quarantine_expires_at = quarantined_at + 30 dias`; sem restore nesse período, o arquivo é purgado (irreversível) | `excrtx-memory-quarantine`, `excrtx-memory-syndic` | ADR-015 |
| `PAGE_PROMOTE_LINES` | **~150 linhas** | Nature-arquivo que ultrapassa ~150 linhas promove para diretório com `_index.md` | `excrtx-memory-manager` | ADR-003 |
| `PAGE_SPLIT_LINES` | **~200 linhas** | Página wiki individual que ultrapassa ~200 linhas deve ser dividida em 2+ páginas | `excrtx-memory-manager` | ADR-003, ADR-004 |
| `MEMORY_MD_BUDGET_CHARS` | **2200 chars** | Orçamento máximo do `MEMORY.md` (fast layer) | fast layer / rotinas de consolidação | ADR-021 |
| `USER_MD_BUDGET_CHARS` | **1375 chars** | Orçamento máximo do `USER.md` (fast layer) | fast layer / rotinas de consolidação | ADR-021 |

## Regra de Referência

- As skills **DEVEM referenciar este contrato** em vez de restatar os valores
  numéricos em seus próprios corpos. Menções existentes são apenas ilustrativas
  e apontam para cá como fonte canônica.
- **Ao alterar qualquer constante:** atualizar o valor **aqui** (única edição
  numérica necessária) e registrar a mudança no log append-only
  (`global/_meta/log.md`), com valor anterior, novo valor e motivo.
- Em caso de divergência entre um valor citado numa skill/doc e este contrato,
  **este contrato vence** (Regra de Autoridade: contratos do Acervo).
