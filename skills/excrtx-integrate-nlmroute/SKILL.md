---
name: excrtx-integrate-nlmroute
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
   - validar também `nlm --version` para detectar cliente muito defasado antes de gastar tempo com auth.
2. Validar auth:
   - `nlm login --check`
   - se falhar com `HTTP 400`, tratar como problema de credencial expirada ou cliente incompatível com o backend atual.
   - ordem de recuperação: `refresh_auth`/reload local de tokens → `nlm login` → upgrade oficial do pacote se o cliente estiver defasado.
   - após qualquer reparo, repetir `nlm login --check` antes de seguir.
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
nlm --version
nlm login --check
```

## Troubleshooting rápido

- `nlm login --check` com `HTTP 400 Bad Request`:
  1. recarregar tokens locais (`refresh_auth` no MCP ou fluxo equivalente);
  2. repetir `nlm login --check`;
  3. se persistir, executar novo `nlm login`;
  4. se o cliente estiver defasado em relação ao release atual, atualizar por `uv tool upgrade notebooklm-mcp-cli` e revalidar.
- `hermes mcp test notebooklm` passar, mas operações reais falharem:
  - isso valida só transporte/descoberta de tools; não prova auth funcional.
  - confirmar auth com `nlm login --check` ou uma operação real (`notebook_list`) antes de declarar o stack saudável.

## Resultado mínimo esperado em qualquer entrega

- resumo/síntese pedida,
- lista das fontes usadas (até 10 quando não fornecidas),
- indicação de quando foi necessário deep research/web search.

## Referências internas

- `references/ensino-alignment.md` — critérios de alinhamento com o padrão já adotado no workspace de ensino (instalação oficial + roteamento de fontes).
