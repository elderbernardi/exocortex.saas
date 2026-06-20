---
type: context
title: Wiki Schema — Shared (Barramento Cross-domain)
description: Ponte de comunicação entre Microversos isolados.
tags: []
timestamp: 2026-05-27
class: perene
created_at: 2026-05-27T04:03:03Z
last_accessed_at: 2026-05-27T04:03:03Z
---

# Wiki Schema — Shared (Barramento Cross-domain)

## Domain
Ponte de comunicação entre Microversos isolados.
Conteúdo aqui é referência cruzada — NUNCA duplicação de dados.

## Type
shared

## Loading Strategy
- `index.md` carregado quando tarefa cruza mais de 1 Microverso
- cross-refs/ carregadas sob demanda
- groups.md consultado quando scope de tarefa tem deny/allow

## Conventions
- Cross-refs são notas curtas (5-15 linhas), não documentos formais
- File names: `{microverso-a}--{microverso-b}--{tema}.md`
- YAML frontmatter obrigatório
- Dados pessoais/confidenciais NUNCA entram em cross-refs (anonymizar)

## Frontmatter (Cross-ref)
```yaml
---
title: Cross-ref Título
created: YYYY-MM-DD
updated: YYYY-MM-DD
from: [microverso-a]
to: [microverso-b]
subject: resumo em 1 linha
tags: [cross-ref]
---
```

## Rules
- Cross-refs são criadas quando uma tarefa identifica relação entre Microversos
- Cross-refs apontam para conteúdo nos Microversos, não duplicam
- Cada Microverso pode ter no máximo 1 ponteiro (1 linha) referenciando a cross-ref
- Cross-refs obsoletas → mover para _archive/ (não deletar)
