---
title: Decisão — promover exocortex-ops a microverso base provisionável
created: 2026-06-05
updated: 2026-06-05
nature: decisions
kind: decision
scope_slug: exocortex-ops
authority: draft
stability: draft
lifecycle_state: drafted
decision_id: OPS-DEC-2026-06-05-001
tags: [decision, setup, microverso-base]
---

# Decisão — promover exocortex-ops a microverso base provisionável

## Status

DRAFT. Ainda exige aprovação antes de alterar o setup executável.

## Contexto

`exocortex-ops` existe no runtime e organiza setup, operação, manutenção, diagnóstico, integrações, memória, profiles, tools, MCPs, self-check e auditoria de drift do Exocórtex sobre Hermes Agent.

O source do installer ainda não contém `acervo/micro/exocortex-ops`. O setup atual copia o Acervo com `rsync -a`, o que pode sobrescrever evolução local caso o microverso seja adicionado ao source sem proteção.

## Decisão proposta

Promover `exocortex-ops` a microverso base provisionável.

## Consequências

- Novas instalações já terão um domínio operacional canônico.
- O setup precisará tratar `exocortex-ops` com política de preservação.
- Evolução runtime não será revertida por reexecução do setup.

## Reversibilidade

Alta. Remover o seed do source e a etapa de provisionamento do setup reverte a promoção. O runtime existente deve permanecer preservado.

## Aprovação

Pendente.
