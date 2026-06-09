1|---
2|name: excrtx-integrate-nlmops
3|description: Workflow executável padrão para aprendizado com NotebookLM no Exocórtex (CLI-first, MCP fallback), com ingestão automática de fontes e critérios de qualidade.
4|version: 1.0.0
5|category: excrtx
6|metadata:
7|  hermes:
8|    tags: [exocortex, notebooklm, workflow, nlm, mcp, research]
9|---
10|
11|# Exocortex NotebookLM Operational Workflow
12|
13|## Quando usar
14|
15|Use quando o pedido exigir aprender, sintetizar, organizar ou expandir conhecimento.
16|
17|## Protocolo padrão
18|
19|### Etapa 0 — Gate rápido
20|
21|1. Verificar runtime:
22|```bash
23|command -v nlm
24|command -v notebooklm-mcp
25|nlm --version
26|```
27|2. Verificar autenticação:
28|```bash
29|nlm login --check
30|```
31|3. Verificar binding Hermes quando houver uso MCP:
32|```bash
33|hermes mcp list
34|```
35|Confirmar presença de `notebooklm` habilitado.
36|4. Se auth falhar: executar `nlm login` e conduzir fluxo remoto via chat (URL de autorização + URL final colada).
37|5. Se MCP não estiver habilitado, registrar fallback explícito para trilha CLI-only antes de continuar.
38|
39|Regra operacional: primeiro garantir cadeia de aquisição (fonte + acesso + integração), depois iniciar síntese e learning cards.
40|
41|### Etapa 1 — Resolver notebook alvo
42|
43|- Reusar notebook temático existente quando apropriado.
44|- Criar notebook novo quando o tema exigir isolamento.
45|
46|Comandos úteis:
47|```bash
48|nlm notebook list --title
49|nlm notebook create "<TEMA>"
50|```
51|
52|### Etapa 2 — Ingestão de fontes
53|
54|#### Caso A: usuário forneceu fontes
55|Adicionar e validar cobertura mínima.
56|
57|#### Caso B: usuário não forneceu fontes
58|1. Buscar fontes confiáveis.
59|2. Selecionar as 10 melhores por autoridade, atualidade, cobertura e diversidade.
60|3. Adicionar ao notebook antes de consultar.
61|
62|Meta: notebook com 10 fontes relevantes (ou justificar número menor quando o domínio não comportar).
63|
64|### Etapa 3 — Pergunta principal
65|
66|Executar query principal no notebook somente após ingestão mínima.
67|
68|```bash
69|nlm notebook query <notebook_id> "<PERGUNTA>"
70|```
71|
72|### Etapa 4 — Lacuna documental
73|
74|Se a resposta depender de informação dinâmica ou não-documental:
75|1. usar deep research como fonte,
76|2. fallback em web search,
77|3. adicionar os resultados ao notebook,
78|4. refazer a query principal.
79|
80|### Etapa 5 — Entrega mínima
81|
82|Toda entrega deve conter:
83|1. resposta/síntese pedida,
84|2. lista de fontes usadas,
85|3. indicação explícita se foi necessário deep research/web search,
86|4. limitações e confiança da resposta.
87|
88|## Fallback MCP
89|
90|Se a rota CLI falhar por ambiente, usar tools MCP `notebooklm-*` com o mesmo protocolo lógico (auth, notebook, fontes, query, lacuna, entrega).
91|
92|## Qualidade (checklist rápido)
93|
94|- [ ] `nlm login --check` passou
95|- [ ] notebook correto selecionado/criado
96|- [ ] fontes suficientes e rastreáveis
97|- [ ] query final executada após ingestão
98|- [ ] deep research/web search acionado quando necessário
99|- [ ] fontes citadas na saída final
100|