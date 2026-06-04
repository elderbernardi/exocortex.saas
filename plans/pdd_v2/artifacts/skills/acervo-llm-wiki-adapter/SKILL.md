---
name: acervo-llm-wiki-adapter
description: "Adapter seguro entre a skill nativa research/llm-wiki e o Acervo Cognitivo v2."
version: 1.0.0
author: Exocórtex
metadata:
  hermes:
    tags: [exocortex, acervo, llm-wiki, adapter, safety, ontology-v2]
    category: exocortex
    related_skills: [llm-wiki, acervo-manager]
---

# Acervo LLM Wiki Adapter

Use esta skill quando uma operação da LLM Wiki precisar afetar o Acervo.

## Princípio

A LLM Wiki nativa fornece mecânica. O Acervo fornece ontologia, scope e destino.

Nunca apontar `WIKI_PATH` para `~/.hermes/acervo` como forma de integração.

Fluxo obrigatório:

```text
research/llm-wiki → acervo-llm-wiki-adapter → acervo-manager → Acervo
```

## Ativar quando

- O usuário pedir ingestão, query, lint ou manutenção usando LLM Wiki e Acervo.
- Uma fonte externa deve entrar automaticamente no Acervo.
- Uma resposta da LLM Wiki deve virar conhecimento, decisão, contrato, prompt, skill, workflow ou reflexão.

## Procedimento

1. Carregar `research/llm-wiki` para obter mecânicas e cuidados upstream.
2. Carregar `exocortex/acervo-manager` para operar o Acervo.
3. Resolver scope: global, micro ou shared.
4. Traduzir categorias LLM Wiki para Ontologia Multifocal v2.
5. Preencher frontmatter v2.
6. Chamar operação WRITE do acervo-manager.
7. Atualizar `index.md` e `log.md` do escopo.
8. Para mudanças estruturais, setup, contratos ou adapter, aplicar registro auditável: `SCHEMA.md`, `index.md`, `log.md`, `contracts/`, `decisions/` e `workflows/` quando aplicável. O `log.md` deve explicitar escopo, arquivos, autoridade e impacto operacional; não usar registro genérico. Ver `references/registration-audit-pattern.md`.
9. Rodar lint ontológico quando houver alteração estrutural.

## Tradução

| LLM Wiki | Acervo v2 |
|---|---|
| entity | `knowledge/`, `nature: conhecimento`, `kind: fact/concept` |
| concept | `knowledge/`, `nature: conhecimento`, `kind: concept` |
| comparison | `decisions/` ou `knowledge/`, `kind: decision/concept` |
| query | `reflections/`, `kind: lesson`, se reutilizável |
| raw | `raw/` do escopo resolvido, imutável após captura |

## Bloqueios

- Não escrever em `macro/`.
- Não criar `entities/`, `concepts/`, `comparisons/` ou `queries/` dentro do Acervo.
- Não gerar wikilinks cross-microverso.
- Não gravar direto em `~/wiki` como fonte oficial.
- Não aceitar update upstream da LLM Wiki como mudança automática de contrato.

## Persistência automática

Conteúdo relevante entra automaticamente no Acervo, mas com `authority: derived | observed` por padrão. Só vira `canonical` quando vier de decisão explícita do executivo ou contrato já aceito.
