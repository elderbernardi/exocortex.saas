---
type: context
title: Wiki Schema — Exocórtex Dev
description: Desenvolvimento do Exocórtex.IA
tags: []
timestamp: 2026-06-11
class: perene
created_at: 2026-06-11T03:03:32Z
last_accessed_at: 2026-06-11T03:03:32Z
---

# Wiki Schema — Exocórtex Dev

## Domain

Desenvolvimento do Exocórtex.IA

## Description

Desenvolvimento de skills, harness, estrutura do acervo, integrações e evolução do framework Exocórtex.IA.

## Type

project

## Owner

@elder

## Loading Strategy

- `index.md` carregado quando o Microverso `exocortex-dev` entra no scope da tarefa
- Natures carregadas sob demanda (por query ou por step do de desenvolvimento)
- NUNCA carregar todas as Natures de uma vez

## Isolation Rules

- Conteúdo deste Microverso não pode ser copiado para outros Microversos
- Cross-refs com outros domínios vão para `shared/cross-refs/`
- Wikilinks `[[page]]` são INTRA-microverso apenas

## Neighbors

- `exocortex-ops` (operação e manutenção da instância ativa)

## Directory Structure

Este Microverso segue a estrutura padrão de Natures:

```
exocortex-dev/
├── _meta/
│   ├── SCHEMA.md        # Este arquivo — especificação do wiki
│   ├── index.md         # Catálogo (carregado no scope)
│   └── log.md           # Registro cronológico append-only
├── context/             # Nature: context — situação atual do desenvolvimento
├── knowledge/           # Nature: knowledge — arquitetura e fatos técnicos
├── contracts/           # Nature: contracts — padrões de código e qualidade
├── decisions/           # Nature: decisions — ADRs (Architectural Decision Records)
├── workflows/           # Nature: workflows — SOPs de desenvolvimento e testes
└── _archive/            # Conteúdo obsoleto ou supersedido
```

O valor de `nature:` no frontmatter DEVE corresponder ao diretório onde o arquivo reside.

## Conventions

- File names: lowercase, hyphens, no spaces (ex: `development-standards.md`)
- YAML frontmatter obrigatório em toda página wiki
- Nomes de Natures no frontmatter devem ser válidos (ex: `nature: knowledge`)

## Frontmatter

```yaml
---
title: Título da Página
created: YYYY-MM-DD
updated: YYYY-MM-DD
nature: context | knowledge | contracts | decisions | workflows
type: fact | rule | workflow | tool | profile | lesson | context
tags: [dev, exocortex, architecture, skill, workflow]
sources: [raw/source.md]
confidence: high | medium | low
---
```

## Tag Taxonomy

- `dev`: desenvolvimento de novas features ou melhorias
- `architecture`: decisões arquiteturais e design interno
- `skill`: desenvolvimento e calibração de skills
- `workflow`: processos de testes e validação
- `standards`: padrões de código e qualidade
- `harness`: ambiente de runtime e bootstrap

## Page Thresholds

- Promover Nature: quando arquivo ultrapassa ~150 linhas → converter para diretório com `_index.md`
- Split de página wiki: quando ultrapassa ~200 linhas
- Archive: quando conteúdo é supersedido → mover para `_archive/`

## Update Policy

- Alterações locais e criação de páginas de documentação — sem aprovação extra necessária
- Alterações que afetam a estrutura do Acervo global — confirmar com o executivo
- Logar toda alteração em `_meta/log.md`
