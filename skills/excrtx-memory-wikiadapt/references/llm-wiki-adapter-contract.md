# LLM Wiki Adapter Contract

The native LLM Wiki is an upstream mechanism. The Acervo is the canonical source.

Mandatory flow:

```text
research/llm-wiki → acervo-llm-wiki-adapter → acervo-manager → Acervo
```

Blocks:

- Don't point `WIKI_PATH` to `~/.hermes/acervo`.
- Don't create `entities/`, `concepts/`, `comparisons/`, or `queries/` inside the Acervo.
- Don't write to `macro/`.
- Don't generate cross-microverso wikilinks.
- Don't treat upstream updates as automatic contract changes.
