
---
title: Decisão — Personal Intake Workspace
author: Exocórtex
created: 2026-05-30
updated: 2026-05-30
nature: conhecimento
kind: decision
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global, exocortex, hermes, acervo]
authority: canonical
operational_mode: advisory
stability: active
sources:
  - /home/elder/.hermes/acervo/global/contracts/personal-intake-workspace.md
  - /home/elder/.hermes/skills/exocortex/personal-intake-workspace/SKILL.md
  - /home/elder/projetos/pessoal/exocortex.saas/docs/ADR/ADR-008-personal-intake-workspace.md
derived_from:
  - personal-intake-workspace-mvp
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: exocortex/personal-intake-workspace
  assumed_version: 1.0.0
  coupling: adapter-only
tags: [intake, inbox, ingestion, multichannel, reproducibility]
---

# Decisão — Personal Intake Workspace

## Decisão

O Exocórtex-Hermes recebe bruto por `_inbox/` e só depois promove para o Acervo semântico.

## Modelo adotado

```text
~/.hermes/acervo/_inbox/{intake_id}/
├── original/
├── derived/
├── manifest.json
├── routing.json
└── log.json
```

Essa área é operacional. Não substitui `knowledge/`, `contracts/`, `context/` nem `_artifacts/`.

## Arquitetura

O caminho respeita a separação do produto:

```text
USER -> GUI -> SERVER -> HERMES
```

O servidor recebe e normaliza. O Hermes interpreta, triageia e promove.

## Relação com workspaces existentes

- `_inbox/` é entrada.
- o Acervo semântico é memória curada.
- `_artifacts/` é saída final publicável.

## Política de segurança estrutural

- bruto não entra direto no Acervo semântico;
- original sempre é preservado;
- canal não decide workflow;
- ZIP, áudio e vídeo exigem revisão adicional antes de promoção automática.
