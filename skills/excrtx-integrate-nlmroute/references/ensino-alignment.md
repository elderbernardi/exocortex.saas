# Alinhamento com padrão do workspace de ensino (NLM)

## Decisões operacionais validadas

1. **CLI-first**: usar `nlm` como rota padrão para operações de conhecimento.
2. **Fallback MCP**: usar `notebooklm-mcp` apenas quando a rota CLI não for viável.
3. **Instalação oficial**: `uv tool install notebooklm-mcp-cli`.
4. **Verificação de auth no runtime atual**: `nlm login --check`.
   - Não usar `nlm auth status` neste ambiente.

## Fluxo mínimo recomendado

```bash
nlm --version
nlm login --check
nlm notebook create "<tema>"
nlm research start "<tema e foco>" --source web --mode fast --notebook-id <id> --auto-import
nlm source list <id> --full
nlm notebook query <id> "<pergunta principal>" --json
```

## Troubleshooting observado no runtime

- Se `nlm login --check` retornar `HTTP 400 Bad Request`, não assumir imediatamente que o MCP está saudável só porque `hermes mcp test notebooklm` conecta.
- `hermes mcp test` confirma transporte stdio e descoberta de tools; não valida operação autenticada.
- Ordem recomendada de reparo:
  1. recarregar tokens locais;
  2. repetir `nlm login --check`;
  3. refazer `nlm login`;
  4. se a CLI estiver defasada em relação ao release atual, atualizar `notebooklm-mcp-cli` pela via oficial (`uv tool upgrade notebooklm-mcp-cli`).

## Regra de ingestão quando não há fontes

- Coletar e importar **10 fontes** antes da query principal.
- `--mode fast` tende a retornar ~10 fontes de forma rápida; usar `deep` quando o tema exigir maior amplitude.

## Critério de qualidade das fontes

- Priorizar autoridade, atualidade, cobertura e diversidade.
- Evitar duplicatas, spam SEO e páginas sem rastreabilidade.

## Entrega mínima

- Síntese pedida
- Lista explícita de fontes usadas
- Indicação de uso de deep research/web search quando aplicável
