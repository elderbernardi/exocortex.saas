---
title: Manifesto de provisionamento — exocortex-ops
created: 2026-06-05
updated: 2026-06-05
nature: context
kind: provision-manifest
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
tags: [setup, provisionamento, microverso-base, idempotencia]
---

# Manifesto de provisionamento — exocortex-ops

## Objetivo

Declarar o conjunto mínimo que um setup replicável deve criar para que `exocortex-ops` exista como microverso base do Exocórtex.

## Diretórios obrigatórios

```text
context/
knowledge/
contracts/
prompts/
skills/
workflows/
tools/
templates/
decisions/
reflections/
persona/
_meta/
_meta/snapshots/
_meta/drafts/
_meta/indices/
raw/
_archive/
```

## Arquivos mínimos

```text
microverso.yaml
_meta/SCHEMA.md
_meta/index.md
_meta/log.md
context/current-state.md
knowledge/runtime-map.md
knowledge/memory-providers.md
knowledge/integration-registry.md
contracts/operating-boundaries.md
contracts/profile-isolation.md
contracts/canonical-path-policy.md
contracts/draftfirst-change-policy.md
contracts/secret-handling-policy.md
contracts/memory-authority-policy.md
contracts/runtime-verification-policy.md
contracts/rollback-policy.md
workflows/self-check.md
workflows/runtime-drift-audit.md
workflows/microverso-inventory.md
workflows/setup-change-draftfirst.md
workflows/base-microverse-provisioning.md
workflows/post-change-validation.md
tools/hermes-cli.md
tools/docbrain.md
tools/notebooklm.md
templates/ops-decision.md
templates/drift-report.md
templates/runtime-snapshot.md
templates/change-draft.md
templates/healthcheck-report.md
persona/ops-steward.md
raw/.gitkeep
_archive/.gitkeep
```

## Política de overwrite

- O setup pode criar diretórios ausentes com `mkdir -p`.
- O setup pode copiar arquivos seed ausentes.
- O setup não pode sobrescrever arquivos existentes em `$ACERVO/micro/exocortex-ops`.
- Atualizações futuras devem entrar como migração, diff ou DRAFT de mudança.

## Critérios de aceite

- `bash -n setup.sh` retorna OK.
- Instalação isolada cria `micro/exocortex-ops`.
- Segunda execução preserva checksums de arquivos existentes.
- Mutação local de arquivo semântico sobrevive a nova execução.
- `shared/knowledge/groups.md` contém `exocortex-ops` em `DOMAINS` e `OPS` sem duplicidade.
