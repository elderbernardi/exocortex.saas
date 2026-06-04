# Acervo Cognitivo — Exocórtex.IA

> Sistema de memória estruturada do Exocórtex, baseado em LLM Wiki (Karpathy).
> 4 camadas com loading seletivo para performance de contexto.

## Arquitetura

```
acervo/
├── macro/                      # 🧠 Identidade (FLAT — sempre carregado)
│   ├── soul.md                 #    Quem sou, propósito
│   ├── valores.md              #    Princípios de decisão
│   └── estilo.md               #    Tom e voz do executivo
│
├── global/                     # 🌐 Operação Universal (WIKI — index no boot)
│   ├── SCHEMA.md               #    Convenções da camada global
│   ├── index.md                #    Catálogo (carregado no boot)
│   ├── log.md                  #    Log append-only
│   ├── raw/{articles,docs,assets}  # Fontes brutas universais
│   ├── _archive/               #    Páginas supersedidas
│   ├── instrucoes.md           #    Regras universais
│   ├── processos.md            #    Workflows globais
│   ├── ferramentas.md          #    Tools em todo contexto
│   ├── conhecimento.md         #    Compliance, legal
│   └── reflexoes.md            #    Lições transversais
│
├── micro/                      # 🔬 Domínios Isolados (WIKI — por scope)
│   ├── _template/              #    Template wiki completo
│   │   ├── SCHEMA.md, index.md, log.md
│   │   ├── raw/, _archive/
│   │   └── {7 Nature files com frontmatter}
│   └── {slug}/                 #    Microverso instanciado
│
└── shared/                     # 🔗 Ponte Cross-domain
    ├── SCHEMA.md               #    Convenções de cross-ref
    ├── index.md                #    Catálogo de cross-refs
    ├── log.md                  #    Log cross-domain
    ├── glossario.md            #    Vocabulário comum
    ├── groups.md               #    Aliases: ALL, CLIENTS, PROJECTS
    └── cross-refs/             #    Referências cruzadas pragmáticas
```

## Loading Strategy

| Camada | Quando Carrega | O que Carrega |
|---|---|---|
| `macro/` | SEMPRE (toda sessão) | 3 arquivos inteiros (~100 linhas) |
| `global/` | BOOT | Apenas `index.md` (~30 linhas); páginas sob demanda |
| `micro/{slug}/` | Quando scope ativa | Apenas `index.md`; Natures sob demanda |
| `shared/` | Quando tarefa cruza domínios | `groups.md` para resolver scope; cross-refs sob demanda |

## Regras Fundamentais

### Imutabilidade
`raw/` em qualquer camada NUNCA é modificado. Conteúdo obsoleto → `_archive/`.

### Isolamento
Conteúdo específico de A não entra em B. Cross-refs vão para `shared/`.
Wikilinks `[[page]]` são INTRA-microverso apenas.

### Firewall
Tarefas têm acesso aberto por padrão. Para restringir:
```yaml
scope:
  deny: [ALL]
  allow: [cliente-acme]  # Allow sobrescreve deny. SEMPRE.
```

### Natures Híbridas
Começam como arquivo. Quando ultrapassam ~150 linhas → promovem para diretório com `_index.md`.

### Skill Unificada
Toda operação sobre o acervo (read, write, promote, search, scope) é feita via **`acervo-manager`** (ADR-005).
As 7 Natures são classificação de dados — a semântica é definida por SCHEMA + frontmatter.

## ADRs

- [ADR-001: 4 Camadas](../projetos/pessoal/exocortex.saas/docs/ADR/ADR-001-four-layer-acervo.md)
- [ADR-002: Isolamento de Contexto](../projetos/pessoal/exocortex.saas/docs/ADR/ADR-002-context-isolation.md)
- [ADR-003: Natures Híbridas](../projetos/pessoal/exocortex.saas/docs/ADR/ADR-003-hybrid-natures.md)
- [ADR-004: LLM Wiki Alignment](../projetos/pessoal/exocortex.saas/docs/ADR/ADR-004-llm-wiki-alignment.md)
- [ADR-005: Consolidar Skills](../projetos/pessoal/exocortex.saas/docs/ADR/ADR-005-consolidate-nature-skills.md)
