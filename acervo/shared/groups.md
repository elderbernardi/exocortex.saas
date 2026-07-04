---
schema: acervo/v0.2
type: knowledge
title: Groups — Aliases de Microversos
description: Registro canônico único de grupos de microversos para resolução de scope (ALL, DOMAINS, PROJECTS, ROLES, CRIACAO).
tags: [groups, scope, aliases, microversos]
timestamp: 2026-06-21
class: perene
status: active
epistemic: fact
created_at: 2026-06-21T00:00:00Z
last_accessed_at: 2026-07-04T00:00:00Z
nature: knowledge
---

# Groups — Aliases de Microversos

> **Fonte única (canônica):** este arquivo é o único registro de grupos de microversos.
> Supersede `shared/knowledge/groups.md` (deprecado em 2026-07-04; taxonomia ALL/CLIENTS/PROJECTS obsoleta).
> Fonte: listagem automática de `acervo/micro/` (exclui `_template/`).
> Atualizado: 2026-07-04. 5 microversos ativos.

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

## ROLES
Microversos que representam papéis ou contextos institucionais do executivo:
- (nenhum ativo no momento)

## CRIACAO
Microversos com capacidade criativa (produção, design, narrativa):
- estudio-criativo

---

**Slugs removidos em 2026-07-04** (não existem em `acervo/micro/`): `sales-ai`, `gabinete`.
Reintroduzir apenas quando o microverso for instalado fisicamente (registro em `global/_meta/microversos.yaml`).

**Resolução de scope:** `ALL` resolve todos. Grupos nomeados filtram por tipo.
`allow` sempre sobrescreve `deny`. Grupos são definidos por `type` no `microverso.yaml` de cada microverso.
