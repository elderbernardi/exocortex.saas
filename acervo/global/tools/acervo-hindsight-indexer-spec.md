---
type: knowledge
title: Especificação — Acervo Hindsight Indexer
description: Especificação técnica do indexador que cria ponteiros semânticos do Acervo
  no Hindsight.
tags:
- memory
- acervo
- hindsight
- indexer
- tooling
timestamp: '2026-06-21'
class: perene
created_at: '2026-06-21T16:37:51Z'
nature: tools
excrtx_type: tool
confidence: high
canonical_from: micro/exocortex-dev/tools/acervo-hindsight-indexer-spec.md
promoted_at: '2026-06-21T21:50:00Z'
scope_slug: global
---

# Especificação — Acervo Hindsight Indexer

## Objetivo

Criar um indexador local que registra no Hindsight ponteiros semânticos para arquivos canônicos do Acervo.

## Interface proposta

```bash
python acervo/global/tools/acervo_hindsight_index.py scan --microverso exocortex-dev
python acervo/global/tools/acervo_hindsight_index.py scan --all
python acervo/global/tools/acervo_hindsight_index.py index-file /abs/path/file.md
python acervo/global/tools/acervo_hindsight_index.py report
```

## Manifesto local

Manter estado local em:

```text
$ACERVO/global/tools/state/acervo_hindsight_index.json
```

Formato:

```json
{
  "version": 1,
  "indexed_at": "2026-06-21T16:37:51Z",
  "entries": {
    "micro/exocortex-dev/decisions/adr-019-memory-operating-model.md": {
      "sha256": "...",
      "hindsight_document_id": "optional",
      "last_indexed_at": "...",
      "status": "active"
    }
  }
}
```

## Extração por arquivo

Para cada `.md` elegível:

1. Ler frontmatter YAML.
2. Rejeitar se `deprecated: true`.
3. Rejeitar se caminho contém `raw/`, `_archive/` ou `.quarantine/`.
4. Calcular `sha256` do arquivo.
5. Se hash não mudou, pular.
6. Gerar resumo curto:
   - usar `description` se existir;
   - complementar com primeiro parágrafo ou headings principais;
   - limitar entrada a aproximadamente 1.000 caracteres.
7. Chamar `hindsight_retain` com contexto `AcervoIndex` e tags: `acervo`, microverso, nature e tags do arquivo.
8. Atualizar manifesto local.

## Registro no Hindsight

Conteúdo sugerido:

```text
AcervoIndex
path: micro/exocortex-dev/decisions/adr-019-memory-operating-model.md
microverso: exocortex-dev
nature: decisions
title: ADR-019 — Modelo Operacional de Memória do Exocórtex
tags: [memory, hindsight, acervo]
class: perene
status: active
sha256: ...
summary: Define Hindsight como memória operacional semântica, Acervo como fonte canônica e memória rápida como bootstrap mínimo.
```

## Write hook

O write hook deve chamar `index-file` somente depois de:

1. frontmatter válido;
2. semantic revision executada;
3. escrita concluída;
4. index/log do microverso atualizados.

## Rotina diária

A rotina diária executa `scan --all` e produz relatório com:

- novos indexados;
- alterados reindexados;
- arquivos ignorados por lifecycle;
- entradas órfãs no manifesto;
- erros por arquivo.

## Critérios de aceite

- [ ] Rodar `scan --microverso exocortex-dev` sem erro.
- [ ] Criar entradas recuperáveis por `hindsight_recall`.
- [ ] Não indexar `raw/`, `_archive/`, `.quarantine/` ou `deprecated`.
- [ ] Pular arquivos sem mudança de hash.
- [ ] Produzir relatório de reconciliação.

> Canonicalizado em `global/tools/acervo-hindsight-indexer-spec.md` a partir de `micro/exocortex-dev/tools/acervo-hindsight-indexer-spec.md` em 2026-06-21T21:50:00Z.

