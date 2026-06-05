---
title: Registro de Integrações Operacionais
created: 2026-06-05
updated: 2026-06-05
nature: knowledge
type: fact
tags: [integration, docbrain, notebooklm, mcp]
sources: [conversation:docbrain-check, command:hermes-tools-list]
confidence: high
---

# Registro de integrações operacionais

## DocBrain

- Uso esperado: parser local de documentos para workflows de intake.
- Modo de consumo: CLI API, não serviço HTTP.
- Runtime funcional observado: `/home/elder/exocortex/tools/docbrain`.
- Health check funcional observado: `npm run --silent cli -- api health --output json`.
- Drift observado: skill apontava para path canônico inexistente neste ambiente.

## NotebookLM

- MCP server `notebooklm` observado como configurado.
- Uso esperado: pesquisa, notebooks, fontes e artefatos NotebookLM quando adequado.

## Regra

Integrações devem ter três camadas registradas quando amadurecem:
1. estado/runtime real;
2. skill operacional;
3. workflow reproduzível no acervo/setup.
