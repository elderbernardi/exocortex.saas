---
name: exocortex-notebooklm-operational-workflow
description: Workflow executável padrão para aprendizado com NotebookLM no Exocórtex (CLI-first, MCP fallback), com ingestão automática de fontes e critérios de qualidade.
version: 1.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, notebooklm, workflow, nlm, mcp, research]
---

# Exocortex NotebookLM Operational Workflow

## Quando usar

Use quando o pedido exigir aprender, sintetizar, organizar ou expandir conhecimento.

## Protocolo padrão

### Etapa 0 — Gate rápido

1. Verificar runtime:
```bash
command -v nlm
command -v notebooklm-mcp
```
2. Verificar autenticação:
```bash
nlm login --check
```
3. Se auth falhar: executar `nlm login` e conduzir fluxo remoto via chat (URL de autorização + URL final colada).

### Etapa 1 — Resolver notebook alvo

- Reusar notebook temático existente quando apropriado.
- Criar notebook novo quando o tema exigir isolamento.

Comandos úteis:
```bash
nlm notebook list --title
nlm notebook create "<TEMA>"
```

### Etapa 2 — Ingestão de fontes

#### Caso A: usuário forneceu fontes
Adicionar e validar cobertura mínima.

#### Caso B: usuário não forneceu fontes
1. Buscar fontes confiáveis.
2. Selecionar as 10 melhores por autoridade, atualidade, cobertura e diversidade.
3. Adicionar ao notebook antes de consultar.

Meta: notebook com 10 fontes relevantes (ou justificar número menor quando o domínio não comportar).

### Etapa 3 — Pergunta principal

Executar query principal no notebook somente após ingestão mínima.

```bash
nlm notebook query <notebook_id> "<PERGUNTA>"
```

### Etapa 4 — Lacuna documental

Se a resposta depender de informação dinâmica ou não-documental:
1. usar deep research como fonte,
2. fallback em web search,
3. adicionar os resultados ao notebook,
4. refazer a query principal.

### Etapa 5 — Entrega mínima

Toda entrega deve conter:
1. resposta/síntese pedida,
2. lista de fontes usadas,
3. indicação explícita se foi necessário deep research/web search,
4. limitações e confiança da resposta.

## Fallback MCP

Se a rota CLI falhar por ambiente, usar tools MCP `notebooklm-*` com o mesmo protocolo lógico (auth, notebook, fontes, query, lacuna, entrega).

## Qualidade (checklist rápido)

- [ ] `nlm login --check` passou
- [ ] notebook correto selecionado/criado
- [ ] fontes suficientes e rastreáveis
- [ ] query final executada após ingestão
- [ ] deep research/web search acionado quando necessário
- [ ] fontes citadas na saída final
