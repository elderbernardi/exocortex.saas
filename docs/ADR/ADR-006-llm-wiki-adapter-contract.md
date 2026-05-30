# ADR-006: Adapter LLM Wiki → Acervo Cognitivo

> **Status:** Aceita  
> **Data:** 2026-05-30  
> **Decisor:** @elder  
> **Contexto:** Segurança contra updates da skill nativa `research/llm-wiki`

## Contexto

A skill nativa `research/llm-wiki` do Hermes está bem integrada ao harness e fornece mecânicas maduras: `SCHEMA.md`, `index.md`, `log.md`, `raw/`, frontmatter, lint, ingest e query. O Acervo Cognitivo usa essas mecânicas, mas possui ontologia distinta: macro/global/micro/shared, microversos isolados, Natures e contratos operacionais.

## Decisão

A LLM Wiki nativa será tratada como upstream mecânico. Ela nunca escreve diretamente no Acervo.

Toda operação passa por:

```text
research/llm-wiki mechanics → acervo-llm-wiki-adapter → acervo-manager → Acervo
```

## Contratos

1. Acervo é fonte canônica.
2. `~/wiki` não é repositório oficial do Exocórtex.
3. A ontologia `entities/concepts/comparisons/queries` não é aplicada diretamente.
4. Toda categoria LLM Wiki é traduzida para diretório funcional + Nature.
5. `raw/` permanece imutável.
6. `macro/` é read-only para o adapter.
7. Wikilinks são intra-microverso.
8. Cross-domain usa `shared/cross-refs/`.
9. Updates futuros da skill `llm-wiki` não podem alterar o contrato do Acervo.

## Tradução segura

| LLM Wiki | Acervo v2 |
|---|---|
| entity | `knowledge/`, `nature: conhecimento`, `kind: fact/concept` |
| concept | `knowledge/`, `nature: conhecimento`, `kind: concept` |
| comparison | `decisions/` ou `knowledge/`, `kind: decision/concept` |
| query | `reflections/` se reutilizável; caso trivial, não persiste |
| raw | `raw/` do escopo resolvido |
| schema/index/log | preservados no escopo do Acervo |

## Consequências

- Criar skill `exocortex/acervo-llm-wiki-adapter`.
- Atualizar `acervo-manager` para Ontologia Multifocal v2.
- Adicionar lint ontológico.
- Registrar o contrato no microverso `hermes-setup`.
