---
title: Decisão — Personal Artifact Workspace
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
  - /home/elder/.hermes/acervo/global/contracts/personal-artifact-workspace.md
  - /home/elder/.hermes/skills/exocortex/personal-artifact-workspace/SKILL.md
  - /home/elder/projetos/pessoal/exocortex.saas/plans/pdd_v2/ARTIFACT_WORKSPACE.md
derived_from:
  - personal-artifact-workspace-mvp
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: exocortex/personal-artifact-workspace
  assumed_version: 1.0.1
  coupling: adapter-only
tags: [artifacts, drive, publishing, reproducibility, pdd-v2]
---

# Decisão — Personal Artifact Workspace

## Decisão

O Exocórtex-Hermes publica artefatos finais por um pacote operacional no Acervo e usa o Drive como ferramenta de entrega privada ao usuário.

O Acervo não sincroniza integralmente com Drive. O Drive não vira memória. O Drive recebe exports finais para consumo humano.

## Modelo adotado

```text
~/.hermes/acervo/_artifacts/{artifact_id}/
├── source/
├── assets/
├── exports/
├── manifest.json
└── receipt.{provider}.json
```

O pacote preserva fonte, assets, exports e rastreabilidade. O microverso registra páginas semânticas apenas quando o artefato tem valor cognitivo.

## Provider inicial

Google Drive via OAuth local do Hermes, usando a skill `productivity/google-workspace`.

Composio fica como fallback ou conector opcional. Ele não é dependência do harness base.

## Política de segurança

Upload privado para o Drive do próprio usuário é entrega pessoal quando o usuário pediu o artefato.

Exigem Draft-First:

- link público;
- compartilhamento com turma, terceiros, organização ou domínio;
- envio por email ou mensagem;
- publicação em site, release ou documento colaborativo;
- conversão para formato colaborativo quando a conversão alterar semântica, layout ou permissões.

## Relação com PDD v2

A decisão nasceu depois da graduação P5_PRODUCTION. O PDD v2 registra a capacidade em `ARTIFACT_WORKSPACE.md` como addendum pós-graduação.

Ela não altera a linha histórica dos 27 prompts. Deve entrar na próxima golden image quando o provider publicar com receipt válido em ambiente limpo.
