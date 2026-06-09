1|---
2|name: excrtx-integrate-nlmroute
3|description: Política operacional para aprendizado com NotebookLM (CLI-first), ingestão automática de fontes e fallback por deep research/web search quando não houver fonte documental.
4|version: 1.0.0
5|category: excrtx
6|metadata:
7|  hermes:
8|    tags: [exocortex, notebooklm, nlm, knowledge, research, mcp]
9|---
10|
11|# Exocortex NotebookLM Knowledge Router
12|
13|## Objetivo
14|
15|Padronizar o uso do NotebookLM como motor de aprendizagem de conhecimento para qualquer agente do Exocórtex.
16|
17|## Regras mandatórias
18|
19|1. Sempre que a tarefa exigir **aprender conhecimento** (síntese, estudo, base conceitual, revisão de literatura, FAQ, glossário, plano de aula, briefing técnico), o agente deve sugerir NotebookLM.
20|2. Se o usuário pedir explicitamente NotebookLM, o agente usa NotebookLM como primeira rota.
21|3. Preferência de execução: **CLI (`nlm`) primeiro**; fallback por **MCP (`notebooklm-mcp`)** quando necessário.
22|4. Se não houver fontes fornecidas:
23|   - buscar as **10 melhores fontes**;
24|   - alimentar o notebook com essas fontes antes da query final.
25|5. Se a pergunta não for resolvível por fonte documental estática:
26|   - usar adição de fonte por **deep research**;
27|   - se deep research não estiver disponível/adequado, usar **web search** e adicionar os resultados ao notebook.
28|
29|## Critério de “10 melhores fontes”
30|
31|Ordenar por:
32|- autoridade da fonte,
33|- atualidade,
34|- cobertura do tópico,
35|- diversidade de perspectivas,
36|- rastreabilidade (URL/identificação clara).
37|
38|Evitar:
39|- conteúdo sem autoria,
40|- páginas duplicadas,
41|- SEO spam,
42|- material desatualizado quando houver alternativa superior.
43|
44|## Fluxo padrão (execução)
45|
46|1. Garantir runtime oficial:
47|   - `nlm` e `notebooklm-mcp` instalados por fonte oficial (`notebooklm-mcp-cli`).
48|   - validar também `nlm --version` para detectar cliente muito defasado antes de gastar tempo com auth.
49|2. Validar auth:
50|   - `nlm login --check`
51|   - se falhar com `HTTP 400`, tratar como problema de credencial expirada ou cliente incompatível com o backend atual.
52|   - ordem de recuperação: `refresh_auth`/reload local de tokens → `nlm login` → upgrade oficial do pacote se o cliente estiver defasado.
53|   - após qualquer reparo, repetir `nlm login --check` antes de seguir.
54|3. Resolver notebook alvo:
55|   - usar notebook existente do tema ou criar novo.
56|4. Ingestão de fontes:
57|   - com fontes do usuário: adicionar e seguir.
58|   - sem fontes: coletar top 10, adicionar, validar cobertura.
59|5. Query principal no notebook.
60|6. Se lacuna documental: acionar deep research/web search e reconsultar.
61|7. Entregar saída estruturada + lista de fontes usadas.
62|
63|## Instalação oficial
64|
65|Fonte oficial de instalação local:
66|
67|```bash
68|uv tool install notebooklm-mcp-cli
69|```
70|
71|Verificação:
72|
73|```bash
74|command -v nlm
75|command -v notebooklm-mcp
76|nlm --version
77|nlm login --check
78|```
79|
80|## Troubleshooting rápido
81|
82|- `nlm login --check` com `HTTP 400 Bad Request`:
83|  1. recarregar tokens locais (`refresh_auth` no MCP ou fluxo equivalente);
84|  2. repetir `nlm login --check`;
85|  3. se persistir, executar novo `nlm login`;
86|  4. se o cliente estiver defasado em relação ao release atual, atualizar por `uv tool upgrade notebooklm-mcp-cli` e revalidar.
87|- `hermes mcp test notebooklm` passar, mas operações reais falharem:
88|  - isso valida só transporte/descoberta de tools; não prova auth funcional.
89|  - confirmar auth com `nlm login --check` ou uma operação real (`notebook_list`) antes de declarar o stack saudável.
90|
91|## Resultado mínimo esperado em qualquer entrega
92|
93|- resumo/síntese pedida,
94|- lista das fontes usadas (até 10 quando não fornecidas),
95|- indicação de quando foi necessário deep research/web search.
96|
97|## Referências internas
98|
99|- `references/ensino-alignment.md` — critérios de alinhamento com o padrão já adotado no workspace de ensino (instalação oficial + roteamento de fontes).
100|