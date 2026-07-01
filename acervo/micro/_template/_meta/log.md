---
type: context
title: "{{DOMAIN_NAME}} — Log"
description: "Registro cronológico append-only do microverso {{DOMAIN_NAME}}"
tags: [log, meta]
timestamp: "{{CREATED_DATE}}"
class: perene
created_at: "{{CREATED_DATE}}T00:00:00Z"
nature: context
---

# {{DOMAIN_NAME}} — Log

> Registro cronológico de operações neste Microverso. Append-only.
> Format: `## YYYY-MM-DD` seguido de bullets `- CREATED:`/`- UPDATED:`/`- ARCHIVED:`.
> Actions: create, update, ingest, archive, lint, promote.
> Rotacionar quando exceder 500 entradas: renomear para log-YYYY.md.

## {{CREATED_DATE}}
- CREATED: micro/{{DOMAIN_SLUG}}/ (perene) — microverso inicializado a partir de `_template/`.
- CREATED: micro/{{DOMAIN_SLUG}}/_meta/ (perene) — estrutura canônica de metadados criada.
- UPDATED: micro/{{DOMAIN_SLUG}}/contracts/exocortex-hermes-identity.md (perene) — contrato local de identidade Exocórtex sobre Hermes aplicado.
