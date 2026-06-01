---
title: Decision — Intake Control Plane
created: 2026-05-30
updated: 2026-05-30
nature: conhecimento
kind: decision
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global, exocortex, intake, gui, gateway]
authority: canonical
operational_mode: executable
stability: active
sources:
  - /home/elder/projetos/pessoal/exocortex.saas/docs/ADR/ADR-009-intake-control-plane.md
  - /home/elder/projetos/pessoal/exocortex.saas/apps/intake_control_plane/intake_http_server.py
derived_from:
  - personal-intake-workspace
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: exocortex/personal-intake-workspace
  assumed_version: 1.0.0
  coupling: adapter-only
tags: [intake, control-plane, gui, gateway, server]
---

# Decision — Intake Control Plane

## Decisão

Interpor uma camada HTTP mínima entre GUI/gateway e Hermes para ingestão multicanal.

## Motivo

- preserva a arquitetura `USER -> GUI -> SERVER -> HERMES`;
- concentra upload binário e normalização de metadata fora da camada cognitiva;
- permite plugar Telegram, dashboard e webhooks no mesmo contrato.

## Implementação de referência

- `apps/intake_control_plane/intake_http_server.py`
- `apps/intake_control_plane/intake-envelope.schema.json`
- `apps/intake_control_plane/dropzone-demo.html`
- `apps/intake_control_plane/README.md`
