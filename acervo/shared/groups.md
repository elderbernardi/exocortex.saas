---
type: knowledge
title: Groups — Aliases de Microversos
description: Agrupamento de microversos por tipo para resolução de scope (ALL, DOMAINS, PROJECTS, ROLES, CRIACAO).
tags: [groups, scope, aliases, microversos]
timestamp: 2026-06-21
class: perene
created_at: 2026-06-21T00:00:00Z
last_accessed_at: 2026-06-21T00:00:00Z
nature: knowledge
---

# Groups — Aliases de Microversos

> Fonte: listagem automática de `acervo/micro/` (exclui `_template/`).
> Atualizado: 2026-06-21. 7 microversos ativos.

## ALL
Resolvido automaticamente via `ls -1 $ACERVO/micro/ | grep -v '^_'`.
Inclui todos os microversos instanciados. `_template/` é excluído (molde, não instância).

## DOMAINS
Domínios transversais de conhecimento e operação:
- estudio-criativo
- excrtx
- exocortex-ops

## PROJECTS
Projetos com escopo, prazo e entregáveis definidos:
- exocortex-dev
- comercial
- sales-ai

## ROLES
Microversos que representam papéis ou contextos institucionais do executivo:
- gabinete

## CRIACAO
Microversos com capacidade criativa (produção, design, narrativa):
- estudio-criativo

---

**Resolução de scope:** `ALL` resolve todos. Grupos nomeados filtram por tipo.
`allow` sempre sobrescreve `deny`. Grupos são definidos por `type` no `microverso.yaml` de cada microverso.
