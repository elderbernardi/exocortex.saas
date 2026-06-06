# DRAFT Issue — NotebookLM bloqueado por auth HTTP 400 e ausência de uv

## Features

EX-28 — NotebookLM Router
EX-29 — NotebookLM Ops

## Prioridade

P1

## Comportamento observado

- `nlm --version`: 0.5.16
- `nlm login --check`: HTTP 400 Bad Request
- `nlm notebook list --title`: HTTP 400
- `hermes mcp test notebooklm`: passa, mas só prova discovery/transporte.
- `uv` ausente no PATH, bloqueando upgrade oficial do pacote.

## Impacto

NotebookLM parece instalado, mas não está operacional. MCP discovery gera falso positivo se o harness não testa auth real.

## Critérios de aceite

- [ ] Setup garante `uv` ou usa caminho absoluto disponível.
- [ ] `nlm` atualizado para versão compatível.
- [ ] Harness exige `nlm login --check` e operação real mínima.
- [ ] Output diferencia MCP discovery de auth operacional.
