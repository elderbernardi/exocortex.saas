---
name: exocortex-notebooklm-knowledge-router
description: Política operacional para aprendizado com NotebookLM (CLI-first), ingestão automática de fontes e fallback por deep research/web search quando não houver fonte documental.
version: 1.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, notebooklm, nlm, knowledge, research, mcp]
---

# Exocortex NotebookLM Knowledge Router

## Objetivo

Padronizar o uso do NotebookLM como motor de aprendizagem de conhecimento para qualquer agente do Exocórtex.

## Regras mandatórias

1. Sempre que a tarefa exigir **aprender conhecimento** (síntese, estudo, base conceitual, revisão de literatura, FAQ, glossário, plano de aula, briefing técnico), o agente deve sugerir NotebookLM.
2. Se o usuário pedir explicitamente NotebookLM, o agente usa NotebookLM como primeira rota.
3. Preferência de execução: **CLI (`nlm`) primeiro**; fallback por **MCP (`notebooklm-mcp`)** quando necessário.
4. Se não houver fontes fornecidas:
   - buscar as **10 melhores fontes**;
   - alimentar o notebook com essas fontes antes da query final.
5. Se a pergunta não for resolvível por fonte documental estática:
   - usar adição de fonte por **deep research**;
   - se deep research não estiver disponível/adequado, usar **web search** e adicionar os resultados ao notebook.

## Critério de “10 melhores fontes”

Ordenar por:
- autoridade da fonte,
- atualidade,
- cobertura do tópico,
- diversidade de perspectivas,
- rastreabilidade (URL/identificação clara).

Evitar:
- conteúdo sem autoria,
- páginas duplicadas,
- SEO spam,
- material desatualizado quando houver alternativa superior.

## Fluxo padrão (execução)

1. Garantir runtime oficial:
   - `nlm` e `notebooklm-mcp` instalados por fonte oficial (`notebooklm-mcp-cli`).
2. Validar auth:
   - `nlm login --check`
   - se falhar: `nlm login` (com suporte remoto via Telegram se necessário).
3. Resolver notebook alvo:
   - usar notebook existente do tema ou criar novo.
4. Ingestão de fontes:
   - com fontes do usuário: adicionar e seguir.
   - sem fontes: coletar top 10, adicionar, validar cobertura.
5. Query principal no notebook.
6. Se lacuna documental: acionar deep research/web search e reconsultar.
7. Entregar saída estruturada + lista de fontes usadas.

## Instalação oficial

Fonte oficial de instalação local:

```bash
uv tool install notebooklm-mcp-cli
```

Verificação:

```bash
command -v nlm
command -v notebooklm-mcp
nlm login --check
```

## Resultado mínimo esperado em qualquer entrega

- resumo/síntese pedida,
- lista das fontes usadas (até 10 quando não fornecidas),
- indicação de quando foi necessário deep research/web search.

## Referências internas

- `references/ensino-alignment.md` — critérios de alinhamento com o padrão já adotado no workspace de ensino (instalação oficial + roteamento de fontes).
