# ADR-001: Arquitetura de 4 Camadas do Acervo Cognitivo

> **Status:** Aceita
> **Data:** 2026-05-26
> **Decisor:** @elder
> **Contexto:** Sessão PDD P2_MEMORY — alinhamento com LLM Wiki

---

## Contexto

O Acervo Cognitivo original (P2_MEMORY prompts 006-010) foi implementado com 3 camadas: `macro/`, `micro/`, `shared/`. Durante o alinhamento com a skill nativa `llm-wiki` do Hermes (baseada no padrão Karpathy), identificamos dois gaps:

1. **Artefatos universais** (regras, processos, ferramentas que valem em todo contexto) não tinham lugar definido. Colocá-los no `macro/` inflaria o contexto que é **sempre carregado inteiro**.
2. **A estrutura interna dos Microversos** não tinha mecânicas de wiki (index, log, raw, frontmatter, wikilinks) que permitem acúmulo composto de conhecimento.

## Decisão

Adotar 4 camadas com loading seletivo:

| Camada | Propósito | Loading |
|---|---|---|
| `macro/` | Identidade (quem sou) | **Sempre inteiro** — 3 arquivos flat |
| `global/` | Operação universal (como opero em tudo) | **Index no boot**, páginas sob demanda |
| `micro/{slug}/` | Domínios isolados | **Por scope da tarefa** |
| `shared/` | Ponte cross-domain | **Quando tarefa cruza domínios** |

## Alternativas Rejeitadas

1. **Universais no `macro/`** — Rejeitada porque `macro/` é carregado inteiro em toda sessão. Universais crescem sem limite → contexto inflado.
2. **Universais no `shared/`** — Rejeitada porque `shared/` é semanticamente um barramento de cross-refs, não um repositório operacional.
3. **Manter 3 camadas** — Rejeitada porque universais ficariam sem lugar definido, gerando decisões ad-hoc.

## Consequências

- Todo Microverso e `global/` ganham estrutura wiki (SCHEMA, index, log, raw, _archive)
- Skills de Nature precisam ser atualizadas para operar sobre a nova estrutura
- `exocortex-new-microverso` precisa gerar a estrutura wiki completa
- `exocortex-search` precisa buscar em 4 camadas com prioridade

## Referências

- PRD: `docs/PRD/PRD_dev_v1.md` §11 (LLM Wiki File System)
- Skill: `~/.hermes/skills/research/llm-wiki/SKILL.md`
- Karpathy: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
