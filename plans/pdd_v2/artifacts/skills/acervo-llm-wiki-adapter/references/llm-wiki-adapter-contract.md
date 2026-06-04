# Contrato LLM Wiki Adapter

A LLM Wiki nativa é upstream mecânico. O Acervo é fonte canônica.

Fluxo obrigatório:

```text
research/llm-wiki → acervo-llm-wiki-adapter → acervo-manager → Acervo
```

Bloqueios:

- Não apontar `WIKI_PATH` para `~/.hermes/acervo`.
- Não criar `entities/`, `concepts/`, `comparisons/` ou `queries/` dentro do Acervo.
- Não escrever em `macro/`.
- Não gerar wikilinks cross-microverso.
- Não tratar updates upstream como alteração automática do contrato.
