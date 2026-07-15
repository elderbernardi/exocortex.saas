---
schema: acervo/v0.2
type: context
title: Wiki Schema — Global (Operação Universal)
description: Rules, processes, tools, and knowledge that apply to ALL Microverses.
tags: []
timestamp: 2026-05-27
class: perene
status: active
epistemic: fact
created_at: 2026-05-27T04:03:03Z
last_accessed_at: 2026-05-27T04:03:03Z
nature: _meta
---

# Wiki Schema — Global (Operação Universal)

## Domain
Rules, processes, tools, and knowledge that apply to ALL Microverses.
Esta camada NÃO é identidade (isso é macro/). É operação universal.

## Type
global

## Loading Strategy
- `index.md` é carregado no BOOT de toda sessão (junto com macro/)
- Páginas individuais são carregadas SOB DEMANDA quando a tarefa precisa
- NUNCA carregar tudo de uma vez — usar index para localizar

## Conventions
- File names: lowercase, hyphens, no spaces
- YAML frontmatter obrigatório em toda página wiki
- Tags devem constar na taxonomia abaixo
- Nature como arquivo único até ~150 linhas; após, promover para diretório
- Split de página wiki em ~200 linhas

## Frontmatter
```yaml
---
title: Título da Página
created: YYYY-MM-DD
updated: YYYY-MM-DD
nature: context | knowledge | contracts | workflows | tools | reflections
type: rule | workflow | tool | fact | lesson
tags: [from taxonomy below]
sources: [raw/documents/source.md]
confidence: high | medium | low
---
```

## Tag Taxonomy
- Scope: regra-global, workflow-global, tool-universal
- Domain: comunicacao, qualidade, seguranca, compliance
- Type: instruction, process, tool, knowledge, reflection

## Page Thresholds
- Criar página: quando regra/processo é referenciado em 2+ Microversos
- Promover Nature: quando arquivo ultrapassa ~150 linhas → converter para diretório
- Split de página: quando ultrapassa ~200 linhas
- Archive: quando conteúdo é supersedido → mover para _archive/

## Update Policy
- Alterações em global/ afetam TODOS os Microversos
- Confirmar com o executivo antes de alterar regras globais
- Logar toda alteração em log.md
