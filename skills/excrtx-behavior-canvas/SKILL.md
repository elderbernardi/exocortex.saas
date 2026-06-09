1|---
2|name: excrtx-behavior-canvas
3|description: Extrai estrutura implícita do input do executivo — foco, lacunas, persona sugerida e tipo de ação. Canvas Cognitivo para cada interação. Harness v0.4.
4|version: 2.0.0
5|category: excrtx
6|metadata:
7|  hermes:
8|    tags: [exocortex, behavior, canvas, parsing, intent, v0.4]
9|---
10|
11|# Canvas Cognitivo — Extrator de Ponteiros (v0.4)
12|
13|> Todo input do executivo carrega informação implícita. O Canvas extrai essa estrutura para que outras skills operem com contexto rico, ancorando a tarefa no Macroverso e nos Microversos corretos.
14|
15|## Trigger
16|
17|Ativar em inputs complexos (mais de uma frase, ou que envolvam múltiplos domínios). Para inputs simples e diretos ("me dê o status de X"), o Canvas é opcional.
18|
19|## Procedure
20|
21|### 1. Parsing Silencioso
22|
23|Antes de resumir o pedido, resolver a tríade estrutural:
24|
25|- **Macroverso** = quem fala e quais limites/valores governam
26|- **Microversos** = entidades semânticas e operacionais vivas que ancoram e apoiam a tarefa
27|- **Tarefa** = a sala operacional concreta onde a execução acontece
28|
29|Microverso não é sala. A tarefa é a sala. O Canvas deve preservar essa distinção.
30|
31|Para cada input complexo, extrair internamente:
32|
33|| Campo | Pergunta | Exemplo |
34||---|---|---|
35|| `macroverso.status` | O Macroverso está resolvido, parcial ou placeholder? | `resolved` / `partial` / `placeholder` / `missing` |
36|| `macroverso.sources` | Em que arquivos o Macroverso foi lido? | `["acervo/macro/soul.md"]` |
37|| `macroverso.constraints` | Que valores, tom ou limites afetam esta tarefa? | `["draft-first", "tom direto"]` |
38|| `focus` | O que o executivo quer resolver? | "Renegociar contrato com Cliente Alfa" |
39|| `intent_type` | explorar, decidir, produzir, revisar, manter, publicar, outro? | "produzir" |
40|| `user_intention.explicit` | O que foi dito literalmente? | "Preciso do relatório final" |
41|| `user_intention.inferred` | O que provavelmente quer mas não disse? | "Quer publicar no Drive" |
42|| `user_intention.confidence` | Quão segura é a inferência? | high / medium / low |
43|| `dominant_entity` | Que entidade central domina? | task / artifact / microverso / decision / routine / inbox / none |
44|| `gaps` | Que informações estão faltando para agir? | "Não sei o histórico de renovações anteriores" |
45|| `microversos.status` | O conjunto de microversos foi resolvido ou segue ambíguo? | `resolved` / `ambiguous` / `none` |
46|| `microversos.primary` | Qual microverso ancora a tarefa? | "cliente-alfa" (se existir no acervo) |
47|| `microversos.related` | Que microversos apoiam a tarefa? | ["financeiro", "juridico"] |
48|| `microversos.rationale` | Por que esse arranjo foi escolhido? | "cliente-alfa é o domínio principal; jurídico só valida cláusulas" |
49|| `microversos.sharing_constraints` | Que restrições de compartilhamento precisam ser respeitadas com base nas regras allow/deny dos microversos? | `["deny: ALL + allow: [microverse_x] => compartilhável só com microverse_x"]` |
50|| `task.anchor` | Como a tarefa foi ancorada na tríade? | "Ofício ancorado em gabinete, com apoio de jurídico" |
51|| `urgency` | Há pressão de tempo? | "reunião amanhã" → alta |
52|| `dependencies` | O output depende de algo externo? | "Preciso dos dados financeiros antes" |
53|| `risks` | Riscos identificados? | "Deadline pode ser irrealista" |
54|
55|### 2. Campos v0.4 Avançados
56|
57|Campos adicionais para interação com o harness:
58|
59|| Campo | Quando Preencher | Exemplo |
60||---|---|---|
61|| `task_candidate.title` | Quando o input parece gerar tarefa persistível | "Relatório Q2 para diretoria" |
62|| `task_candidate.persist` | Se o Exocórtex recomenda criar tarefa em _tasks/ | true / false |
63|| `artifacts.expected` | Quando artefatos serão produzidos | ["relatorio-q2.pdf"] |
64|| `evaluation.required` | Se o artefato precisa de avaliação por persona | true / false |
65|| `evaluation.evaluator_personas` | Quais personas devem avaliar | ["critico", "professor"] |
66|| `evaluation.apply_mode` | Como aplicar sugestões | suggest / auto-incorporate / ask-user |
67|| `promotion_candidates` | Conhecimento que deve ser promovido ao Acervo | ["decisão X para micro/harness-project/decisions"] |
68|
69|### 3. Uso do Canvas
70|
71|O Canvas NÃO é apresentado ao executivo (a menos que ele peça). Ele serve para:
72|
73|1. **Declarar o estado do Macroverso** antes de qualquer inferência substantiva
74|2. **Ancorar a tarefa** em um microverso principal e zero ou mais secundários
75|3. **Alimentar o `excrtx-behavior-vetor`** com vetor (evolucao/execucao/manutencao)
76|4. **Buscar no acervo** as informações que preencham os `gaps`
77|5. **Priorizar** com base em `urgency`
78|6. **Alertar sobre `dependencies`** que bloqueiam a ação
79|7. **Respeitar restrições de compartilhamento** entre microversos em tarefas cross-domain, usando as regras de sharing de cada microverso e a precedência `allow > deny`
80|8. **Registrar tarefa** quando `task_candidate.persist = true`
81|9. **Solicitar avaliação** quando `evaluation.required = true`
82|10. **Promover conhecimento** quando `promotion_candidates` não vazio
83|
84|### 4. Quando Expor o Canvas
85|
86|Expor o Canvas ao executivo quando:
87|- O input é tão ambíguo que o agente não consegue agir sem confirmação
88|- Há gaps críticos que só o executivo pode preencher
89|- O Canvas revela conflito entre microversos (ex: o que é bom para Cliente Alfa prejudica Projeto Beta)
90|
91|Formato de exposição:
92|```markdown
93|🧠 **Canvas Cognitivo**
94|┌─────────────────────────────────────
95|│ Foco: {focus}
96|│ Macroverso: {macroverso.status}
97|│ Microverso âncora: {microversos.primary}
98|│ Microversos de apoio: {microversos.related}
99|│ Tarefa: {task.anchor}
100|│ Vetor: {intent_type}
101|│ Entidade dominante: {dominant_entity}
102|│ 
103|│ ⚠ Lacunas:
104|│   • {gap_1}
105|│   • {gap_2}
106|│ 
107|│ 🔗 Dependências:
108|│   • {dep_1}
109|│
110|│ 📋 Tarefa candidata: {task_candidate.title}
111|│ 📊 Avaliação: {evaluation.evaluator_personas}
112|└─────────────────────────────────────
113|```
114|
115|### 5. Persistência (canvas.yaml)
116|
117|Quando `task_candidate.persist = true`, salvar o Canvas como `canvas.yaml` em `_tasks/{task_id}/`:
118|
119|```bash
120|python $ACERVO/global/tools/harness/register_task_from_canvas.py \
121|  --canvas canvas.yaml \
122|  --title "..." \
123|  --primary-microverso slug
124|```
125|
126|O template canônico está em `$ACERVO/global/templates/harness-v0.4/canvas.yaml`.
127|
128|### 6. Multi-microverso
129|
130|Quando o input envolve múltiplos domínios:
131|1. Identificar o microverso principal que ancora a tarefa
132|2. Identificar os microversos secundários que só apoiam a tarefa
133|3. Buscar informações em cada um, respeitando scope/firewall e regras locais de compartilhamento
134|4. Consolidar no Canvas apenas a interseção útil para a tarefa
135|5. Se houver conflito de interesses ou de acesso, alertar o executivo
136|
137|Ao resolver sharing constraints, aplicar a regra de ouro já definida em `shared/knowledge/groups.md`:
138|- `allow` SEMPRE sobrescreve `deny`
139|- exemplo: `deny: [ALL]` + `allow: [microverse_x]` significa que o microverso só pode ser compartilhado com `microverse_x`
140|
141|## Regras
142|
143|- Canvas é ferramenta interna por default — expor só quando necessário
144|- Nunca inventar informações para preencher gaps — marcar como "desconhecido"
145|- Atualizar o Canvas se o executivo fornecer informações novas durante a conversa
146|- O Canvas persiste durante a conversa; pode ser salvo como canvas.yaml em _tasks/ quando gera tarefa
147|- Nunca tratar Microverso como sala; a sala é a tarefa
148|- Em tarefa cross-domain, sempre declarar microverso principal, microversos de apoio e restrições de compartilhamento
149|- Se `macroverso.status` estiver `placeholder` ou `missing`, declarar isso explicitamente no Canvas
150|
151|## Verificação
152|
153|- [ ] Input complexo gera Canvas com pelo menos 4 campos preenchidos
154|- [ ] Macroverso tem status explícito
155|- [ ] Microverso principal corresponde ao domínio âncora do input
156|- [ ] Microversos de apoio só entram quando a tarefa exige cruzamento
157|- [ ] Restrições de compartilhamento foram consideradas em tarefas cross-domain
158|- [ ] Gaps são identificados corretamente (não fabricados)
159|- [ ] Canvas é exposto quando input é ambíguo
160|- [ ] Multi-microverso funciona com referência cruzada
161|- [ ] Campos v0.4 (evaluation, promotion_candidates) são preenchidos quando aplicável
162|- [ ] task_candidate.persist = true gera registro em _tasks/
163|
164|