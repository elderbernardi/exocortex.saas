---
type: context
title: Índice — exocortex-ops
description: Microverso canônico para setup, operação, manutenção, diagnóstico, integrações, memória, profiles, tools, MCPs, self-...
tags: [index, ops, setup]
timestamp: 2026-06-05
class: perene
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
nature: meta
kind: index
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
created: 2026-06-05
---

# exocortex-ops

Microverso canônico para setup, operação, manutenção, diagnóstico, integrações, memória, profiles, tools, MCPs, self-check e auditoria de drift do Exocórtex sobre Hermes Agent.

## Estado

- Status: active.
- Base provisionável: draft em preparação.
- Snapshot funcional: `_meta/snapshots/2026-06-05-1442-before-base-provisioning.md`.
- DRAFT de setup: `_meta/drafts/setup-provision-exocortex-ops-2026-06-05.md`.

## Arquivos centrais

### Context
- `context/current-state.md`
- `_meta/provision-manifest.md`
- `_meta/drift-register.md`

### Knowledge
- `knowledge/runtime-map.md`
- `knowledge/memory-providers.md`
- `knowledge/integration-registry.md`
- `knowledge/profile-registry.md`
- `knowledge/mcp-registry.md`
- `knowledge/cron-registry.md`
- `knowledge/version-matrix.md`

### Contracts
- `contracts/operating-boundaries.md`
- `contracts/profile-isolation.md`
- `contracts/canonical-path-policy.md`
- `contracts/draftfirst-change-policy.md`
- `contracts/secret-handling-policy.md`
- `contracts/memory-authority-policy.md`
- `contracts/runtime-verification-policy.md`
- `contracts/rollback-policy.md`

### Workflows
- `workflows/self-check.md`
- `workflows/runtime-drift-audit.md`
- `workflows/microverso-inventory.md`
- `workflows/setup-change-draftfirst.md`
- `workflows/base-microverse-provisioning.md`
- `workflows/post-change-validation.md`
- `workflows/incident-response.md`

### Tools
- `tools/hermes-cli.md`
- `tools/docbrain.md`
- `tools/notebooklm.md`

### Templates
- `templates/ops-decision.md`
- `templates/drift-report.md`
- `templates/runtime-snapshot.md`
- `templates/change-draft.md`
- `templates/healthcheck-report.md`

### Decisions
- `decisions/create-exocortex-ops.md`
- `decisions/provision-as-base-microverse.md` (DRAFT)

### Persona
- `persona/ops-steward.md`

## Contratos bloqueantes

Antes de qualquer mudança operacional sensível, consultar:

1. `contracts/draftfirst-change-policy.md`
2. `contracts/secret-handling-policy.md`
3. `contracts/runtime-verification-policy.md`
4. `contracts/rollback-policy.md`
5. `contracts/profile-isolation.md`

## Próxima ação operacional

Aplicar o DRAFT de provisionamento só após aprovação explícita do executivo. Até lá, o setup executável permanece intacto.
