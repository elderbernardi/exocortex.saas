---
type: knowledge
title: Registro de Integrações Operacionais
description: 'Uso esperado: parser local de documentos para workflows de intake.'
tags: [integration, docbrain, notebooklm, mcp]
timestamp: 2026-06-05
class: volátil
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
excrtx_type: fact
nature: knowledge
sources: ['conversation:docbrain-check', 'command:hermes-tools-list']
confidence: high
created: 2026-06-05
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
