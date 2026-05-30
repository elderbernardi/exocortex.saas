# ADR-004: Integração LLM Wiki no Acervo Cognitivo

> **Status:** Aceita
> **Data:** 2026-05-26
> **Decisor:** @elder
> **Contexto:** Sessão PDD P2_MEMORY — alinhamento com skill nativa do Hermes

---

## Contexto

O Hermes Agent possui a skill nativa `llm-wiki` (v2.1.0), baseada no padrão de Andrej Karpathy. Essa skill implementa um sistema de wiki pessoal com 3 layers: raw (fontes imutáveis), wiki (páginas compiladas), schema (convenções). O Acervo Cognitivo do Exocórtex tem propósito similar, mas organizado pelas 7 Natures em vez das categorias entity/concept/comparison/query da LLM Wiki.

A decisão é: como alinhar as mecânicas da LLM Wiki (que são robustas) com a ontologia do Exocórtex (que é semântica para o executivo).

## Decisão

Adotar as **mecânicas** da LLM Wiki mantendo a **ontologia** do Exocórtex:

### Mecânicas Adotadas da LLM Wiki

| Mecânica | Implementação no Acervo |
|---|---|
| `SCHEMA.md` | Cada Microverso e `global/` tem SCHEMA com domínio, convenções, taxonomia |
| `index.md` | Catálogo de conteúdo por Microverso (carregado no boot do scope) |
| `log.md` | Log append-only de operações, isolado por Microverso |
| `raw/` | Fontes brutas imutáveis por Microverso |
| `_archive/` | Páginas supersedidas (archiving, não delete) |
| YAML frontmatter | Em toda página wiki (title, created, updated, nature, type, tags, sources, confidence) |
| Wikilinks `[[page]]` | Referências **intra-Microverso** apenas |
| Lint/audit | Orphan pages, broken links, stale content, contradictions |
| Drift detection | sha256 no frontmatter de raw para detectar mudanças |

### Ontologia Mantida do Exocórtex

| Exocórtex | LLM Wiki equivalente |
|---|---|
| 7 Natures (contexto, conhecimento, instrucoes, persona, processos, ferramentas, reflexoes) | entities, concepts, comparisons, queries |
| Microversos (por workspace) | Uma wiki por domínio |
| Macroverso (identidade) | Sem equivalente (nova camada) |
| `global/` (operação universal) | Sem equivalente (nova camada) |
| `shared/cross-refs/` | Sem equivalente (wikilinks cruzam wikis no Karpathy; aqui são proibidos cross-wiki) |

### Diferença Fundamental

- **LLM Wiki original:** Uma wiki monolítica com cross-refs internos livres
- **Acervo Cognitivo:** Múltiplas wikis isoladas (Microversos) com cross-refs apenas via `shared/`

## Alternativas Rejeitadas

1. **Adotar LLM Wiki pura** — Rejeitada porque perde isolamento de contexto (uma wiki monolítica polui tudo).
2. **Ignorar LLM Wiki** — Rejeitada porque as mecânicas (index, log, raw, frontmatter, lint) são maduras e testadas.
3. **Substituir Natures por categorias da wiki** — Rejeitada porque as 7 Natures mapeiam diretamente para capacidades do Harness (PRD §3.1).

## Consequências

- Cada Microverso é uma "mini LLM Wiki" com frontmatter, index, log e raw
- A skill `exocortex-search` opera como a Query da LLM Wiki, mas com scope de Microverso
- Lint/audit pode ser implementado como extensão da LLM Wiki lint
- `raw/` é imutável em todo o Acervo (sem exceção)

## Referências

- Skill LLM Wiki: `~/.hermes/skills/research/llm-wiki/SKILL.md`
- Karpathy LLM Wiki: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Hermes Release: `docs/hermes-agent-kwon/hermes-agent/RELEASE_v0.8.0.md` (llm-wiki introduzida)
- PRD §3.1: `docs/PRD/PRD_dev_v1.md` (7 Natures mapeadas ao Harness)


## Atualização 2026-05-30

ADR-006 define que a LLM Wiki nativa só integra o Acervo via adapter seguro.
