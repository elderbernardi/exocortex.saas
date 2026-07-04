---
schema: acervo/v0.2
type: contract
title: Estrutura Canônica de Diretórios de Microverso
description: Estrutura canônica de diretórios de microverso — 11 natures + 3 infra = 14 diretórios. Contrato normativo.
tags: [exocortex, microverso, directory-structure, canonical, natures, excrtx-v1]
timestamp: 2026-06-21
class: perene
status: active
created_at: 2026-06-21T00:00:00Z
nature: contracts
excrtx_type: rule
kind: contract
scope_mode: global
scope_slug: null
authority: canonical
operational_mode: blocking
stability: stable
sources: [issue-89, issue-87, issue-88, MV-PACK-2]
---

# Estrutura Canônica de Diretórios de Microverso

Todo microverso no Acervo Cognitivo segue **uma única** estrutura de diretórios.
Não há variação por tipo (`client`, `project`, `domain`, `role`), maturidade ou
tamanho. A estrutura é a mesma para o `_template/` e para todos os microversos
instanciados.

## Árvore canônica (14 diretórios)

```
{slug}/
├── _meta/                 # Infraestrutura do microverso (3 arquivos obrigatórios)
│   ├── SCHEMA.md          #   Especificação do wiki (OKF v0.1, perene)
│   ├── index.md           #   Catálogo de todas as páginas (carregado no scope)
│   └── log.md             #   Registro cronológico append-only
│
├── context/               # Nature 1  — Situação atual, prioridades, stakeholders
├── knowledge/             # Nature 2  — Fatos, métricas, referências
├── contracts/             # Nature 3  — Regras condicionais (WHEN/THEN)
├── prompts/               # Nature 4  — Prompts reutilizáveis
├── persona/               # Nature 5  — Voz, tom, estilo de comunicação
├── workflows/             # Nature 6  — SOPs, processos, fluxos de trabalho
├── skills/                # Nature 7  — Capacidades encapsuladas
├── tools/                 # Nature 8  — Ferramentas, MCPs, APIs, integrações
├── templates/             # Nature 9  — Modelos (emails, docs, slides)
├── decisions/             # Nature 10 — Decisões arquiteturais (ADR)
├── reflections/           # Nature 11 — Lições aprendidas, post-mortems
│
├── raw/                   # Fontes brutas (imutáveis — nunca editadas)
└── _archive/              # Conteúdo supersedido (não-indexado, não-carregado)
```

**Total: 11 natures + 3 diretórios de infraestrutura = 14 diretórios.**

Cada diretório de Nature contém pelo menos um `_seed.md`. O valor da chave
`nature:` no frontmatter YAML de cada arquivo DEVE corresponder ao diretório
onde o arquivo reside.

## Natures (11)

Estas são as **únicas** classificações de conteúdo reconhecidas. Nenhuma skill
pode referenciar uma contagem ou lista diferente.

| # | Nature | Semântica | Quando ler | Quando escrever |
|---|--------|-----------|------------|-----------------|
| 1 | `context` | Situação atual, prioridades, stakeholders | Início de tarefa no domínio | Mudança de cenário |
| 2 | `knowledge` | Fatos, métricas, referências | Pergunta factual | Novo dado confirmado |
| 3 | `contracts` | Regras condicionais (WHEN/THEN) | Antes de ações no domínio | Nova regra do executivo |
| 4 | `prompts` | Prompts reutilizáveis | Tarefa repetitiva | Novo prompt validado |
| 5 | `persona` | Voz, tom, estilo | Ao comunicar no domínio | Novo perfil de audiência |
| 6 | `workflows` | SOPs, processos | Tarefa recorrente | Novo workflow aprovado |
| 7 | `skills` | Capacidades encapsuladas | Tarefa especializada | Nova skill criada |
| 8 | `tools` | MCPs, APIs, integrações | Tarefa com ferramenta | Nova integração |
| 9 | `templates` | Modelos (emails, docs) | Output padronizado | Novo template aprovado |
| 10 | `decisions` | Decisões arquiteturais (ADR) | Mudança estrutural | Decisão tomada |
| 11 | `reflections` | Lições aprendidas | Início de tarefa similar | Após incidente/aprendizado |

## Diretórios de infraestrutura (3)

| Dir | Função | Modificável | Indexado |
|-----|--------|-------------|----------|
| `_meta/` | SCHEMA.md + index.md + log.md | Sim (log é append-only) | Não (meta, não conteúdo) |
| `raw/` | Fontes brutas (PDFs, CSVs, capturas) | **Nunca** | Não |
| `_archive/` | Conteúdo supersedido | Não (só entrada) | Não |

## Regras de isolamento

- **Conteúdo de um microverso NUNCA é copiado para outro.** Use `shared/cross-refs/`.
- **Wikilinks `[[page]]` são intra-microverso** — não cruzam fronteiras de slug.
- **`raw/` é imutável.** Nenhuma operação de write, patch ou promote atua sobre `raw/`.

## Relação com OKF e empacotamento

- Esta estrutura é a **fonte da verdade** para o gate OKF no export (`microverso_package.py`).
- No empacotamento (`.mvpkg`): `raw/` é incluído apenas com `--include-raw`; `_archive/` nunca.
- `_meta/` é incluído no pacote, mas `last_accessed_at` é removido no export.
- O manifesto `microverso.yaml` (`excrtx/v1`) referencia esta estrutura via chave `tree:`.

## Skills que referenciam esta estrutura

Todas as skills abaixo DEVEM estar alinhadas com esta especificação:

| Skill | O que referencia |
|-------|-----------------|
| `excrtx-memory-manager` | Lista e semântica das 11 Natures |
| `excrtx-memory-newmicro` | Criação de microverso (cópia do `_template/`) |
| `excrtx-memory-mvsetup` | Provisionamento de microversos base |
| `excrtx-memory-mvexport` | Empacotamento limpo (exclusão de `raw/`, `_archive/`) |
| `excrtx-memory-mvinstall` | Instalação e validação de estrutura |

Qualquer desalinhamento entre uma skill e este contrato é um **defeito** da skill,
não uma exceção à estrutura.

## Versionamento

- **Versão atual:** `excrtx/v1` (alinhada com o schema `microverso.yaml`).
- Este contrato é `class: perene` — mudanças exigem ADR e atualização de todas as skills.
