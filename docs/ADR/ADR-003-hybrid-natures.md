# ADR-003: Natures Híbridas (Arquivo → Diretório)

> **Status:** Supersedida por ADR-007
> **Data:** 2026-05-26
> **Decisor:** @elder
> **Contexto:** Sessão PDD P2_MEMORY — otimização de context loading

---

## Contexto

Cada Microverso tem 7 Natures (contexto, conhecimento, instrucoes, persona, processos, ferramentas, reflexoes). A implementação original (P2 prompts 006-010) usava 1 arquivo `.md` por Nature. Com o alinhamento à LLM Wiki, surge a questão: cada Nature deve ser um diretório com páginas wiki desde o início?

O problema: um Microverso novo com 7 diretórios vazios + `_index.md` cada = overhead sem benefício. Mas um arquivo único de 500 linhas de conhecimento = contexto pesado para carregar inteiro quando se busca 1 métrica.

## Decisão

Natures começam como **arquivo único** e **promovem para diretório** quando ultrapassam ~150 linhas.

### Estado Inicial (Microverso novo)

```
micro/{slug}/
├── conhecimento.md       ← 30 linhas: read_file direto
├── instrucoes.md         ← 15 linhas: read_file direto
└── ...
```

### Após Promoção (Nature cresceu)

```
micro/{slug}/
├── conhecimento/          ← Promovido
│   ├── _index.md          ← Catálogo leve
│   ├── metricas-q3.md     ← Página wiki
│   └── contratos.md       ← Página wiki
├── instrucoes.md          ← Ainda arquivo (pequeno)
└── ...
```

### Threshold

- **~150 linhas** para promoção de Nature (arquivo → diretório)
- **~200 linhas** para split de página wiki (página → 2 páginas)

### Mecânica de Promoção

1. Agente detecta que Nature file > ~150 linhas
2. Cria diretório com mesmo nome
3. Extrai seções do arquivo original em páginas separadas
4. Cria `_index.md` com catálogo
5. Remove arquivo original
6. Atualiza `index.md` do Microverso
7. Loga em `log.md`

## Alternativas Rejeitadas

1. **Sempre diretório** — Rejeitada porque overhead de diretório vazio + _index.md não compensa para Microversos novos ou Natures pequenas.
2. **Sempre arquivo** — Rejeitada porque arquivos de 500+ linhas degradam performance de context loading.
3. **Threshold fixo (ex: 100 linhas)** — Rejeitada em favor de ~150 como sweet spot (suficiente para conteúdo denso, mas antes de ficar pesado).

## Consequências

- Nature skills precisam de lógica dual: detectar se Nature é arquivo ou diretório
- Nova skill `nature-promote` (ou lógica embutida) para executar promoção
- `exocortex-search` precisa buscar em ambos os formatos
- Context loading otimizado: arquivo = lê tudo; diretório = lê _index.md, depois página específica

## Referências

- LLM Wiki: `~/.hermes/skills/research/llm-wiki/SKILL.md` §Page Thresholds
- Plano: `artifacts/plan_wiki_alignment.md` v3


## Supersedida

Em 2026-05-30, a Ontologia Multifocal v2 substituiu a mecânica de Natures como arquivos/diretórios. Natures permanecem como frontmatter semântico; diretórios funcionais passam a ser a estrutura operacional.
