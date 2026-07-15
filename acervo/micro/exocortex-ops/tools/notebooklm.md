---
schema: acervo/v0.2
type: tool
title: NotebookLM MCP
description: O MCP server `notebooklm` aparece configurado com tools habilitadas.
tags: [notebooklm, mcp, research]
timestamp: 2026-06-05
class: volátil
status: active
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
excrtx_type: tool
nature: tools
sources: ['command:hermes-tools-list']
confidence: high
created: 2026-06-05
---

# NotebookLM MCP

## Estado inicial observado

O MCP server `notebooklm` aparece configurado com tools habilitadas.

## Uso esperado

- Criar/listar notebooks.
- Adicionar fontes.
- Consultar fontes existentes.
- Fazer research web/drive quando solicitado.
- Gerar e baixar artefatos quando aprovado.

## Regra

Operações que compartilham, exportam ou alteram artefatos externos seguem Draft-First quando houver impacto fora do ambiente local.
