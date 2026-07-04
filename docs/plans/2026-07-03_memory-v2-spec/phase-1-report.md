# Phase 1 — Execution Report

> **Executed:** 2026-07-04 · **Status:** ✅ complete (installer + live) · ADR-023 **accepted** pelo executivo em 2026-07-04

## Delivered

| Item | Result |
|---|---|
| `scripts/migrate_frontmatter_v2.py` | v1→v0.2: schema, status (derivação + normalização `accepted→active`/`proposed→draft`), **type alinhado ao diretório**, epistemic default sobre o type final, confidence remap conservador, nature derivada; nunca inventa proveniência; idempotente por gate de `schema`. 26 testes |
| `scripts/validate_frontmatter.py` v2 | Despacho por versão: arquivos v0.2 → regras V2-0xx (type enum 16, type↔dir, status enum, Tier-1 epistêmico, pares superseded/deprecated/quarantined, **trust gate de segredos V2-060**, Tier-2 formats); v1 intacto + WARN V2-000 "não migrado". 49 testes, zero regressão |
| `acervo_catalog.py` + `acervoctl reindex/doctor` | catalog.sqlite derivado (objects+links+FTS5, reconstruível, gitignorado); doctor: links quebrados, pareamento de supersedência, type↔dir, drift. `canonical_from` quebrado = WARN (proveniência histórica). 8 testes |
| `tests/memory-eval/` fixture | 44 objetos v0.2 válidos (executiva fictícia, 3 microversos) com material plantado: armadilha de contaminação (R$ 47,20 vs 52,80/ton), cadeia superseded v1→v2→v3, conflito aberto (12.000 vs 15.000 m²), par temporal Q1/Q2, stale ×2, 3 episódios/3 intenções/decisão com alternativas + `PLANTED.yaml` + **25 perguntas-ouro** (`golden/questions.yaml`), zero paths pendurados |
| **Installer acervo** | 162/162 migrados · validador exit 0 · doctor 0 erros |
| **Acervo vivo** | 234/234 migrados (commit `c1113df`) · 5 correções V-070 reais · `_ops_snapshots/` congelado revertido + excluído das 3 ferramentas · validador exit 0 · catalog 222 objetos · doctor 0 erros |

## Aceite ADR-023 Fase 1

- [x] Migração v0.2 aplicada (installer + vivo, idempotente)
- [x] Catalog reconstrói de arquivos (`acervoctl reindex`)
- [x] `acervoctl doctor` limpo (0 erros; warnings = proveniência histórica/exemplos de sintaxe)

## Incidentes reais encontrados e resolvidos durante a execução

1. Migração inicial não convertia `type` nem normalizava `status` legado → validador v2 teria falhado em massa; migrador estendido + 4 testes.
2. Doctor divergia do validador nas isenções (`_meta`, `cross-refs`) → alinhado.
3. `_ops_snapshots/` (só no vivo) foi migrado indevidamente → revertido via git e excluído em ponto único (`SKIP_PARTS`).
4. 5 arquivos vivos com `timestamp` bumpado sem `created_at` (V-070 legítimo) → corrigidos.

## Próximo

Phase 2 (ingestão segura + verbos de conflito + tipos episode/entity/intention em produção) — exige atualizar `excrtx-memory-manager` e o control plane. Phase 3 (retrieval híbrido) pode usar o fixture + goldens já prontos, incluindo o experimento H2.
