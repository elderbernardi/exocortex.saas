# DRAFT Issue — OAuth MCP não tem fixture/alvo canônico para dogfood end-to-end

## Feature

EX-26 — OAuth MCP

## Prioridade

P2

## Comportamento observado

O ambiente possui MCP `notebooklm` via stdio sem auth MCP. `hermes mcp test notebooklm` passou, mas isso não exercita OAuth remoto.

Sem endpoint OAuth remoto/provedor configurado, o teste fica BLOCKED.

## Impacto

A feature pode estar documentada, mas não há como validar integração OAuth real em pós-provisionamento.

## Critérios de aceite

- [ ] Definir provedor OAuth MCP canônico de teste ou mock local.
- [ ] Harness diferencia stdio/no-auth de HTTP/OAuth.
- [ ] Teste end-to-end valida list, test, auth callback e sessão real.
