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

## Directory Structure

Cada Microverso instanciado segue esta estrutura de diretórios:

```
{slug}/
├── _meta/
│   ├── SCHEMA.md        # Este arquivo — especificação do wiki
│   ├── index.md         # Catálogo (carregado no scope)
│   └── log.md           # Registro cronológico append-only
├── context/             # Nature: context — situação atual do domínio
├── knowledge/           # Nature: knowledge — fatos e dados
├── contracts/           # Nature: contracts — regras e contratos
├── prompts/             # Nature: prompts — prompts reutilizáveis
├── persona/             # Nature: persona — voz, tom e estilo
├── workflows/           # Nature: workflows — SOPs e processos
├── skills/              # Nature: skills — capacidades encapsuladas
├── tools/               # Nature: tools — ferramentas e integrações
├── templates/           # Nature: templates — modelos (emails, docs)
├── decisions/           # Nature: decisions — decisões arquiteturais (ADR)
├── reflections/         # Nature: reflections — lições aprendidas
├── raw/                 # Fontes brutas (NUNCA modificadas)
└── _archive/            # Conteúdo supersedido
```

Cada diretório de Nature contém pelo menos um `_seed.md` (template inicial).
O valor de `nature:` no frontmatter DEVE corresponder ao diretório onde o arquivo reside (ex: arquivo em `prompts/` → `nature: prompts`).

## Conventions

- File names: lowercase, hyphens, no spaces
- YAML frontmatter obrigatório em toda página wiki
- Tags devem constar na taxonomia abaixo
- Nature como diretório contendo um ou mais arquivos; novas páginas são criadas no diretório correspondente
- Quando um diretório de Nature ultrapassa ~200 linhas totais, considerar split em múltiplos arquivos

## Frontmatter

```yaml
---
title: Título da Página
created: YYYY-MM-DD
updated: YYYY-MM-DD
nature: context | knowledge | contracts | prompts | persona | workflows | skills | tools | templates | decisions | reflections
type: fact | rule | workflow | tool | profile | lesson | context
tags: [from taxonomy below]
sources: [raw/source.md]
confidence: high | medium | low
---
```

## Tag Taxonomy

<!-- Customize per domain. Starting defaults: -->

- Nature: context, knowledge, contracts, prompts, persona, workflows, skills, tools, templates, decisions, reflections
- Priority: critico, importante, referencia

## Page Thresholds

- Promover Nature: quando arquivo ultrapassa ~150 linhas → converter para diretório com \_index.md
- Split de página wiki: quando ultrapassa ~200 linhas
- Archive: quando conteúdo é supersedido → mover para \_archive/

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
