
---
title: Workflow — Setup Replicável do Exocórtex
created: 2026-05-30
updated: 2026-05-30
nature: processos
kind: workflow
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global]
authority: canonical
operational_mode: executable
stability: active
sources: [~/.hermes/setup.sh]
derived_from: [ontology-v2-migration]
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: autonomous-ai-agents/hermes-agent
  assumed_version: null
  coupling: adapter-only
tags: [setup, replicability, hermes, exocortex]
---

# Workflow — Setup Replicável do Exocórtex

1. Criar as 4 camadas do Acervo.
2. Criar diretórios funcionais v2 em `global/`, `shared/`, `_template/` e microversos base.
3. Instalar skills do bundle Exocórtex.
4. Validar `acervo-manager` e `acervo-llm-wiki-adapter`.
5. Verificar profiles `exec` e `evol`.
6. Rodar lint estrutural.
7. Para entrada, instalar o Personal Intake Workspace: `_inbox/`, contrato, ferramenta `intake_ingest.py`, skill e documentação do microverso `hermes-setup`.
8. Para superfícies amigáveis, preservar também o `apps/intake_control_plane/` no projeto como referência executável de server + dropzone.
9. Para artefatos finais, usar o Personal Artifact Workspace: pacote em `_artifacts/`, exports no Drive privado, manifest/receipt no Acervo e Draft-First para compartilhamento externo.
