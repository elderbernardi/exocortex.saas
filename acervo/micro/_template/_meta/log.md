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
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: create, update, ingest, archive, lint, promote
> Rotacionar quando exceder 500 entradas: renomear para log-YYYY.md

## [{{CREATED_DATE}}] create | Microverso initialized
- Created from _template/ by exocortex-new-microverso
- 11 Natures initialized as directories
- Onboarding: pending
- [2026-06-01T21:06:19-03:00] Contrato local de identidade Exocórtex sobre Hermes aplicado em `contracts/exocortex-hermes-identity.md`.
