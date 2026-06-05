---
title: Workflow — provisionar microverso base
created: 2026-06-05
updated: 2026-06-05
nature: workflows
kind: workflow
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
tags: [setup, microverso-base, provisionamento]
---

# Workflow — provisionar microverso base

## Trigger

Usar quando um microverso deve existir em instalações futuras do Exocórtex.

## Pré-condições

- Microverso runtime validado.
- Snapshot `before` criado.
- DRAFT de mudança no setup preparado.
- Aprovação explícita antes de aplicar patch no setup.

## Passos

1. Validar estrutura do microverso runtime.
2. Remover dados pessoais, segredos e contexto local não replicável.
3. Criar seed no source do installer.
4. Alterar setup para copiar seed só quando arquivos estiverem ausentes.
5. Excluir o microverso do rsync genérico destrutivo.
6. Validar `bash -n`.
7. Rodar instalação isolada em `mktemp -d`.
8. Rodar segunda execução e comparar checksums.
9. Testar preservação de mutação local.
10. Registrar snapshot `after`.

## Verificação

- `source/acervo/micro/{slug}` existe.
- Runtime preserva arquivos existentes.
- Segunda execução não muda checksums.
- `groups.md` inclui o microverso sem duplicidade.
