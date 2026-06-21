---
type: knowledge
title: Acervo Cognitivo — Exocórtex.IA
description: Sistema de memória estruturada do Exocórtex, baseado em LLM Wiki (Karpathy).
tags: []
timestamp: 2026-05-27
class: volátil
created_at: 2026-05-27T04:03:03Z
last_accessed_at: 2026-05-27T04:03:03Z
---

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
│   ├── _meta/
│   │   ├── SCHEMA.md           #    Convenções da camada global
│   │   ├── index.md            #    Catálogo (carregado no boot)
│   │   ├── log.md              #    Log append-only
│   │   └── DESIGN.md           #    Tokens visuais globais
│   ├── context/                #    Situação e prioridades universais
│   ├── knowledge/              #    Compliance, legal, fatos universais
│   ├── contracts/              #    Regras e contratos universais
│   ├── workflows/              #    Workflows globais
│   ├── tools/                  #    Tools em todo contexto
│   ├── reflections/            #    Lições transversais
│   ├── raw/{articles,docs,assets}  # Fontes brutas universais
│   └── _archive/               #    Páginas supersedidas
│
├── micro/                      # 🔬 Domínios Isolados (WIKI — por scope)
│   ├── _template/              #    Template wiki completo
│   │   ├── _meta/ (SCHEMA, index, log)
│   │   └── {7 Nature directories com _seed.md + contracts/, raw/, _archive/}
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
Toda operação sobre o acervo (read, write, promote, search, scope) é feita via **`excrtx-memory-manager`** (ADR-005).
As 7 Natures são classificação de dados — a semântica é definida por SCHEMA + frontmatter.

## Lifecycle de Memória (OKF v0.1)

Cada arquivo do Acervo carrega frontmatter YAML alinhado ao [Open Knowledge Format v0.1](docs/plans/2026-06-19_acervo-lifecycle-okf/SCHEMA.md). Os campos obrigatórios são:

- **OKF canonical**: `type` (concept type), `title`, `description`, `tags`, `timestamp`
- **Acervo extension**: `class` (`perene` | `volátil`), `created_at`, `last_accessed_at`

### Classes de Permanência

| Classe | Exemplos | Comportamento |
|--------|----------|--------------|
| `perene` | decisions, contracts, persona, identity | Nunca auto-deprecado ou quarentinado |
| `volátil` | knowledge, context, workflows, prompts | Candidato a deprecação (contradição) e quarentena (inatividade) |

### Diretório de Quarentena

```
acervo/.quarantine/   # Arquivos aguardando purge (janela de 30 dias — ADR-015)
                      # Espelha a estrutura do acervo para facilitar restore
                      # .purge_log: log append-only de operações de purge
```

Nenhum arquivo é deletado diretamente. Fluxo: **deprecação → quarentena (30 dias) → purge**.

### Skills do Lifecycle

| Skill | Quando usar |
|-------|------------|
| `excrtx-memory-deprecate` | WRITE: detecta contradição com arquivo volátil existente e depreca o predecessor (ADR-016) |
| `excrtx-memory-quarantine` | Mover arquivo para `.quarantine/`, restaurar, ou purgar após expiração (ADR-015) |
| `excrtx-memory-syndic` | Ciclo autônomo semanal: scan → quarentena → purge, executado pelo cron `maintenance-weekly` (ADR-018) |

### Validação e Migração

```bash
# Validar frontmatter de arquivo ou diretório (exit 0 = OK, exit 1 = ERROR)
python3 scripts/validate_frontmatter.py --file <path>
python3 scripts/validate_frontmatter.py --dir $ACERVO --report

# Migrar arquivos com schema legado para OKF v0.1
python3 scripts/migrate_frontmatter.py --dry-run --dir $ACERVO
python3 scripts/migrate_frontmatter.py --dir $ACERVO
```

Referência completa do schema: `docs/plans/2026-06-19_acervo-lifecycle-okf/schema-spec.md`

## Export / Import de Microversos (formato `.mvpkg`)

Um microverso pode ser empacotado num pacote portátil e autossuficiente (Docker-like):
*"se roda no meu Exocortex, roda no seu"*. O pacote carrega dados cognitivos,
skills embutidas, pins de dependências e configs de integração, com manifesto
`microverso.yaml` (`excrtx/v1`) e `MANIFEST.sum` de integridade.

```bash
# Export → pacote .mvpkg.tar.gz (clean-portable: remove last_accessed_at, exclui
# quarantine/_archive/raw, descarta deprecated, valida o gate OKF)
python3 $ACERVO/global/tools/microverso_package.py --microverso <slug> --out <dir> --tar

# Import (dir, .tar.gz ou git URL): integridade → manifesto → gate OKF →
# preflight de compat → skills (resolução de colisão) → merge seguro → registro
python3 $ACERVO/global/tools/microverso_install.py <pkg> [--install-deps] [--update-skills]
```

Skills (`excrtx-memory-mvexport`, `excrtx-memory-mvinstall`) embrulham essas
ferramentas. Especificação completa do formato:
`global/contracts/microverso-package-spec.md`. Registro de microversos instalados:
`global/_meta/microversos.yaml` (append-only).

## ADRs

- [ADR-001: 4 Camadas](../projetos/pessoal/exocortex.saas/docs/ADR/ADR-001-four-layer-acervo.md)
- [ADR-002: Isolamento de Contexto](../projetos/pessoal/exocortex.saas/docs/ADR/ADR-002-context-isolation.md)
- [ADR-003: Natures Híbridas](../projetos/pessoal/exocortex.saas/docs/ADR/ADR-003-hybrid-natures.md)
- [ADR-004: LLM Wiki Alignment](../projetos/pessoal/exocortex.saas/docs/ADR/ADR-004-llm-wiki-alignment.md)
- [ADR-005: Consolidar Skills](../projetos/pessoal/exocortex.saas/docs/ADR/ADR-005-consolidate-nature-skills.md)
