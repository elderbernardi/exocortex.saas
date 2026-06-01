# Wiki Schema — Hermes Setup

## Domain
Setup, replicabilidade e evolução do harness Hermes/Exocórtex.

## Type
project

## Ontology Model
Este escopo usa a Ontologia Multifocal v2 do Acervo Cognitivo.

A estrutura de diretórios é funcional para o harness Hermes. As Natures continuam como vocabulário semântico no frontmatter, nos índices e no lint.

### Functional Directories
- `context/` — contexto carregável do domínio.
- `knowledge/` — fatos, conceitos, referências e métricas.
- `contracts/` — regras, políticas e guardrails bloqueantes.
- `prompts/` — prompts reutilizáveis e padrões de invocação.
- `skills/` — skills Hermes ou especificações de skills do domínio.
- `workflows/` — playbooks, checklists e rotas de tool calling.
- `tools/` — ferramentas, MCPs, scripts e conectores.
- `templates/` — modelos de documentos e artefatos.
- `decisions/` — ADRs, decisões arquiteturais e escolhas reversíveis.
- `reflections/` — lições aprendidas, pós-mortems e sínteses evolutivas.
- `persona/` — tom, vocabulário e comportamento específico do domínio.

### Nature Vocabulary
- `contexto`: situação, cenário, prioridade, restrição local.
- `conhecimento`: fatos, conceitos, decisões e referências.
- `instrucoes`: contratos, regras, políticas e preferências normativas.
- `processos`: workflows, prompts, skills, playbooks e procedimentos.
- `ferramentas`: tools, MCPs, scripts e integrações.
- `persona`: voz, estilo, público e comportamento.
- `reflexoes`: aprendizados, revisões, hipóteses e sínteses.

## Required Frontmatter v2
```yaml
---
title: Título Descritivo
created: YYYY-MM-DD
updated: YYYY-MM-DD
nature: contexto | conhecimento | instrucoes | processos | ferramentas | persona | reflexoes
kind: context | fact | concept | decision | contract | rule | workflow | prompt | skill | tool | template | profile | lesson | event
scope_mode: macro | global | micro | shared
scope_slug: hermes-setup
applies_to: []
authority: canonical | derived | draft | observed | external
operational_mode: read_only | advisory | executable | blocking | template
stability: experimental | active | stable | deprecated
sources: []
derived_from: []
confidence: high | medium | low
promotion_policy: none | candidate-global | candidate-shared | promoted
upstream:
  source_skill: null
  assumed_version: null
  coupling: none | adapter-only | direct
tags: []
---
```

## Path Contracts
- Arquivos em `contracts/` DEVEM usar `kind: contract | rule` e `operational_mode: blocking | advisory`.
- Arquivos em `skills/` DEVEM usar `kind: skill` e `operational_mode: executable | advisory`.
- Arquivos em `prompts/` DEVEM usar `kind: prompt`.
- Arquivos em `decisions/` DEVEM usar `kind: decision`.
- Arquivos em `tools/` DEVEM usar `kind: tool`.
- `raw/` é imutável.
- `_archive/` recebe conteúdo supersedido ou legado.
- Wikilinks `[[page]]` são intra-microverso; cross-domain usa `shared/cross-refs/`.

## Legacy Policy
Arquivos flat de Nature (`contexto.md`, `processos.md`, etc.) estão descontinuados. Conteúdo legado deve ser migrado para diretórios funcionais e o original arquivado em `_archive/legacy-flat-natures/`.

## LLM Wiki Adapter Policy
A skill nativa `research/llm-wiki` é upstream mecânico. Ela nunca escreve diretamente neste escopo. Qualquer ingest, query ou lint vindo da LLM Wiki passa por `exocortex/acervo-llm-wiki-adapter` e depois por `exocortex/acervo-manager`.
