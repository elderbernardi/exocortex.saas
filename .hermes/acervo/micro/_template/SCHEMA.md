# Wiki Schema — Microverso Template

## Domain
{{DOMAIN_NAME}}

## Description
{{DOMAIN_DESCRIPTION}}

## Type
{{micro_type}}
<!-- Options: client | project | domain | role -->

## Owner
@elder

## Loading Strategy
- `index.md` carregado quando Microverso entra no scope da tarefa
- Natures carregadas sob demanda (por query ou por step do workflow)
- NUNCA carregar todas as Natures de uma vez

## Isolation Rules
- Conteúdo deste Microverso NÃO pode ser copiado para outros Microversos
- Cross-refs vão para shared/cross-refs/ com ponteiro mínimo aqui
- Wikilinks [[page]] são INTRA-microverso apenas

## Neighbors
<!-- Microversos que frequentemente interagem com este. Exemplo:
- cliente-alfa (via shared/cross-refs/)
-->

## Conventions
- File names: lowercase, hyphens, no spaces
- YAML frontmatter obrigatório em toda página wiki
- Tags devem constar na taxonomia abaixo
- Nature como arquivo único até ~150 linhas; após, promover para diretório

## Frontmatter
```yaml
---
title: Título da Página
created: YYYY-MM-DD
updated: YYYY-MM-DD
nature: contexto | conhecimento | instrucoes | persona | processos | ferramentas | reflexoes
type: fact | rule | workflow | tool | profile | lesson | context
tags: [from taxonomy below]
sources: [raw/source.md]
confidence: high | medium | low
---
```

## Tag Taxonomy
<!-- Customize per domain. Starting defaults: -->
- Nature: contexto, conhecimento, instrucoes, persona, processos, ferramentas, reflexoes
- Priority: critico, importante, referencia

## Page Thresholds
- Promover Nature: quando arquivo ultrapassa ~150 linhas → converter para diretório com _index.md
- Split de página wiki: quando ultrapassa ~200 linhas
- Archive: quando conteúdo é supersedido → mover para _archive/

## Style Override (DESIGN.md)

- Arquivo `DESIGN.md` é **OPCIONAL** neste Microverso
- Ausência = herda 100% de `global/DESIGN.md`
- Presença = declara APENAS tokens que diferem do global
- Frontmatter DEVE conter `extends: global`
- Formato: Google DESIGN.md (YAML tokens + markdown prosa)
- Criação guiada por `brandkit` via `exocortex-design-system`

## Update Policy
- Alterações locais — sem aprovação extra necessária
- Alterações que afetam global/ — confirmar com executivo
- Logar toda alteração em log.md
