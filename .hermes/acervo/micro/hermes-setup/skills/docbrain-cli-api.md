---
title: Skill — DocBrain CLI API
created: 2026-05-31
updated: 2026-05-31
nature: processos
kind: skill
scope_mode: micro
scope_slug: hermes-setup
applies_to: [intake, parser, exocortex-setup]
authority: canonical
operational_mode: executable
stability: active
sources:
  - ~/.hermes/skills/exocortex/docbrain-cli-api/SKILL.md
  - /home/elder/projetos/pessoal/projetob/docbrain/docs/HERMES-INTEGRATION.md
  - /home/elder/projetos/pessoal/projetob/docbrain/docs/EXOCORTEX-INSTALLATION.md
derived_from:
  - docbrain-cli-api
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
tags: [skill, docbrain, hermes, cli-api, parser]
---

# Skill — DocBrain CLI API

A skill local `exocortex/docbrain-cli-api` foi criada para ensinar esta instância Hermes a operar o DocBrain como parser engine local.

## Local

```bash
~/.hermes/skills/exocortex/docbrain-cli-api/SKILL.md
```

## Conteúdo operacional

A skill registra:

- workspace canônico do DocBrain;
- health check;
- parse padrão;
- request via stdin;
- query de jobs e revisões;
- política de key compartilhada com Hermes;
- instalação em novos Exocórtex;
- validação com `npx vitest run --pool=forks`;
- pitfalls de automação.

## Regra

Quando a tarefa envolver DocBrain, intake documental, parser engine ou setup reprodutível, carregar `exocortex/docbrain-cli-api` antes de operar.

## Observação

A skill local existe no runtime desta instância. Para novas instalações, ela precisa estar presente no bundle Exocórtex ou ser recriada pelo setup que materializa as skills locais.
