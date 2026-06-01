---
title: DocBrain CLI API
created: 2026-05-31
updated: 2026-05-31
nature: ferramentas
kind: tool
scope_mode: micro
scope_slug: hermes-setup
applies_to: [intake, parser, exocortex-setup]
authority: canonical
operational_mode: executable
stability: active
sources:
  - /home/elder/projetos/pessoal/projetob/docbrain/docs/HERMES-INTEGRATION.md
  - /home/elder/projetos/pessoal/projetob/docbrain/docs/CLI-API-CONTRACT.md
derived_from:
  - /home/elder/projetos/pessoal/projetob/docbrain
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: exocortex/docbrain-cli-api
  assumed_version: 1.0.0
  coupling: adapter-only
tags: [docbrain, cli-api, parser, intake, hermes]
---

# DocBrain CLI API

DocBrain é a engine local de parser documental para fluxos de intake do Exocórtex. O Hermes consome DocBrain por CLI API local, não por servidor HTTP.

## Workspace canônico atual

```bash
/home/elder/projetos/pessoal/projetob/docbrain
```

## Repositório

```bash
https://github.com/ProjetoBB/docBrainBB.git
```

## Health check

```bash
cd /home/elder/projetos/pessoal/projetob/docbrain
npm run --silent cli -- api health --output json
```

A resposta deve conter:

```json
{
  "ok": true,
  "api_version": "docbrain.cli.v1",
  "command": "health"
}
```

## Parse padrão para Hermes

```bash
cd /home/elder/projetos/pessoal/projetob/docbrain
npm run --silent cli -- api parse create \
  --input /abs/path/document.pdf \
  --include document,job,sections,tables \
  --reprocess-policy skip \
  --output json
```

## Request via stdin

```bash
cd /home/elder/projetos/pessoal/projetob/docbrain
printf '%s' "$REQUEST_JSON" | npm run --silent cli -- api parse create --request -
```

Payload:

```json
{
  "input": "/abs/path/document.pdf",
  "input_kind": "file",
  "include": ["document", "job", "sections", "tables"],
  "reprocess_policy": "skip",
  "llm": "auto",
  "citation": "Documento recebido pelo intake",
  "tags": ["intake"],
  "project_root": "/home/elder/projetos/pessoal/projetob/docbrain"
}
```

## Jobs

```bash
npm run --silent cli -- api parse get --document-id 'sha256:...' --latest --include document,job
npm run --silent cli -- api parse get --job-id 'sha256_...-r1' --include document,job
npm run --silent cli -- api parse list --limit 20 --status completed
npm run --silent cli -- api parse revisions --document-id 'sha256:...'
```

## Regra operacional

- Usar `reprocess-policy=skip` por padrão.
- Solicitar `raw_text` só quando necessário.
- Guardar `document_id`, `job_id` e `revision` no intake.
- Não usar `docbrain ingest` em automação Hermes, exceto quando o objetivo for escrever projeção wiki.
