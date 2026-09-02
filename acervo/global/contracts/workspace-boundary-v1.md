---
schema: acervo/v0.2
type: contract
title: Fronteira V1 entre workspace de projeto e Acervo
description: Define workspace como superfície operacional do usuário e Acervo como autoridade de contexto, memória e promoção.
tags: [workspace, memory, acervo, boundary, architecture]
timestamp: 2026-08-15
class: perene
status: draft
created_at: 2026-08-15T19:09:29Z
nature: contracts
excrtx_type: rule
confidence: high
sources: [docs/ADR/ADR-026-workspaces-v1.md, docs/workspaces/WORKSPACE-SPEC-v1.md]
relates_to: [global/contracts/memory-routing-contract.md, global/decisions/adr-023-memory-v2-spec.md]
scope_slug: global
---

# Fronteira V1 entre workspace de projeto e Acervo

> **DRAFT:** aprovado para implementação e validação do Slice 0. Ainda não é contrato ativo do runtime.

## Regra central

Workspace é a superfície operacional de um projeto. Microverso fornece contexto. Acervo preserva memória promovida e mantém somente uma projeção reversa sem paths.

O Acervo não mantém a árvore do projeto.

## Autoridade

| Conteúdo ou ação | Autoridade |
|---|---|
| Arquivos, código, fontes, assets e entregáveis | usuário; agente opera durante tarefa explícita |
| Identidade, objetivo, vínculo e status descritivo | `.exocortex/workspace.yaml` |
| Localização física | locator local fora do Acervo |
| Projeção por microverso | `$ACERVO/global/_meta/workspaces.yaml`, sem paths |
| Contexto e memória | Acervo/microversos |
| Promoção | controle semântico do Acervo |

## Regras obrigatórias

1. Trabalhar em um arquivo não o transforma em memória.
2. O conteúdo do workspace não entra automaticamente no recall ou no catálogo do Acervo.
3. O agente pode editar arquivos do workspace quando a tarefa explícita exigir.
4. Descoberta, validação, registro, resolução e status não executam o projeto nem alteram seu payload fora de `.exocortex/`.
5. Status `proposed | active | archived` é descritivo; não é ACL, capability ou gate.
6. `workspacectl` não possui promoção, deploy, publicação ou execução de comandos do projeto.
7. Promoção usa o control plane semântico do Acervo e registra referência `workspace://` relativa.
8. Working source e deliverable permanecem no workspace.
9. `_artifacts` recebe apenas snapshot institucional por ação explícita.
10. Paths absolutos e estado local nunca entram no Acervo.
11. Vínculo de microverso no manifesto descreve contexto; não concede acesso.
12. Operações externas continuam Draft-First.

## Compatibilidade

`_tasks`, `_routines`, `_automations`, `_inbox`, `_artifacts` e WebUI Spaces permanecem legíveis. Não são convertidos em workspaces nem migrados na V1.

`$EXOCORTEX_HOME` é o Exocórtex Home/Cockpit. Não é workspace de projeto. A raiz padrão de projetos é `EXOCORTEX_WORKSPACES_HOME`, com fallback `~/workspace`.

## Referência normativa

Schema, locator, registro reverso, segurança de paths e semântica dos comandos estão em `docs/workspaces/WORKSPACE-SPEC-v1.md`.
