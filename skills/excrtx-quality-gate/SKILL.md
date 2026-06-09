1|---
2|name: excrtx-quality-gate
3|description: Gate de qualidade aplicado pelo agente executor ao final de cada tarefa. Prosa passa por excrtx-quality-antislop, visual por excrtx-quality-taste. Correções são feitas pelo executor, nunca pelo orquestrador.
4|version: 1.1.0
5|category: excrtx
6|metadata:
7|  hermes:
8|    tags: [exocortex, behavior, quality, gate, excrtx-quality-antislop, excrtx-quality-taste]
9|    related_skills: [excrtx-quality-antislop, excrtx-quality-taste]
10|---
11|
12|# Output Quality Gate — Responsabilidade do Executor
13|
14|> O agente que produz o output é o agente que garante sua qualidade. O orquestrador **nunca** corrige — ele devolve.
15|
16|## Princípio Central
17|
18|```
19|Agente Executor  →  produz output  →  aplica quality gate  →  entrega
20|                                            ↓ (falha)
21|                                      corrige ele mesmo
22|                                            ↓ (falha 2x)
23|Orquestrador     →  detecta falha  →  devolve ao executor com feedback
24|                                      (NUNCA corrige por conta própria)
25|```
26|
27|A qualidade do output é indissociável do contexto de produção. Um orquestrador que corrige perde o contexto do domínio, do modelo LLM usado, e da intenção original. Isso degrada a qualidade em vez de melhorá-la.
28|
29|## Trigger
30|
31|O agente executor aplica este gate como **último passo** antes de entregar qualquer output substantivo. O gate é parte do fluxo de produção, não uma camada externa.
32|
33|## Escopo — Quando Aplicar e Quando Ignorar
34|
35|### ✅ APLICAR (outputs para o executivo)
36|
37|| Tipo | Gate | Exemplos |
38||---|---|---|
39|| **PROSA** | `excrtx-quality-antislop` | Email, briefing, análise, reflexão, resumo, apresentação textual |
40|| **VISUAL** | `excrtx-quality-taste` | UI, dashboard, gráfico, layout, apresentação visual |
41|| **MISTO** | Ambos | Apresentação executiva com texto e métricas |
42|
43|### ❌ IGNORAR (outputs técnicos)
44|
45|| Tipo | Motivo | Exemplos |
46||---|---|---|
47|| **CÓDIGO** | Estilo de código segue linters e convenções do projeto, não prosa humana | Scripts, configs, YAML, JSON, SQL, qualquer linguagem |
48|| **DOCUMENTAÇÃO TÉCNICA** | Clareza técnica > estilo narrativo. Jargão é necessário. | README, ADRs, SKILL.md, docstrings, comentários de código, specs, schemas |
49|| **DADOS BRUTOS** | Sem narrativa para filtrar | Tabelas numéricas, logs, dumps, CSVs |
50|| **RESPOSTAS CURTAS** | Overhead desproporcional | Confirmações ("Feito."), perguntas diretas, mensagens de sistema |
51|| **CITAÇÕES LITERAIS** | Fidelidade > estilo | Trechos de fontes externas reproduzidos ipsis litteris |
52|
53|> **Regra de ouro:** Se o output é lido por máquinas ou por desenvolvedores em contexto técnico, o gate não se aplica.
54|
55|## Procedure — Executor
56|
57|### 1. Classificar o Output
58|
59|Antes de entregar, o executor classifica:
60|- É prosa para o executivo? → Gate de Prosa
61|- É visual para o executivo? → Gate Visual
62|- É código, doc técnica, ou dados? → **Entregar sem gate**
63|
64|### 2. Gate de Prosa (excrtx-quality-antislop)
65|
66|Quick Checks — executar em cada parágrafo produzido:
67|
68|| Check | Correção |
69||---|---|
70|| Advérbio presente? | Cortar. "Significativamente aumentou" → "aumentou 40%" |
71|| Voz passiva? | Encontrar o ator. "Foi decidido que" → "O board decidiu" |
72|| Coisa inanimada com verbo humano? | "A decisão emerge" → "Elder decidiu" |
73|| Contraste "não X, é Y"? | Dizer Y diretamente |
74|| Frase soa como pull-quote? | Reescrever — se soa tweetável, está genérico |
75|| Declarativo vago? | Nomear. "Implicações significativas" → "Impacto: R$2M em margem" |
76|| Frase de enchimento? | Cortar. "É importante notar que" → (deletar) |
77|
78|**Scoring (mínimo 35/50):**
79|
80|| Dimensão | 10 pts | Pergunta |
81||---|---|---|
82|| Diretividade | Declarações ou anúncios? | O texto diz algo ou se prepara para dizer? |
83|| Ritmo | Variado ou metrônomo? | Há mix de frases curtas e longas? |
84|| Confiança | Respeita o leitor? | Assume que o executivo é inteligente? |
85|| Autenticidade | Soa humano? | Alguém de verdade falaria assim? |
86|| Densidade | Algo cortável? | Cada frase carrega informação? |
87|
88|### 3. Gate Visual (excrtx-quality-taste)
89|
90|Pre-flight — verificar antes de entregar:
91|
92|| Check | Correção |
93||---|---|
94|| Hero ultrapassa 3 linhas? | Alargar container, reduzir fonte |
95|| Grid tem gaps vazios? | Aplicar grid-flow-dense |
96|| Labels genéricos (SECTION 01)? | Substituir por título descritivo |
97|| Layout idêntico ao anterior? | Forçar variação |
98|| Texto de botão invisível? | Corrigir contraste |
99|
100|Sub-skill por contexto:
101|- Dados/métricas → `brutalist`
102|- Identidade/marca → `brandkit`
103|- Landing/produto/UI → `gpt-taste`
104|
105|### 4. Correção pelo Executor
106|
107|Se o gate falhar:
108|
109|1. **O executor corrige ele mesmo** — ele tem o contexto do domínio, do prompt original, e do modelo LLM
110|2. **Re-aplica o gate** na versão corrigida
111|3. **Se falhar 2x** → sinalizar ao orquestrador com o output + diagnóstico de falha
112|
113|### 5. Escalação ao Orquestrador
114|
115|Quando o executor falha 2x no gate:
116|
117|```
118|[QUALITY-GATE-FAIL] agent: {executor} | type: {prosa|visual} | score: {X}/50
119|Diagnóstico: {o que não passou}
120|Output anexado para revisão.
121|```
122|
123|O orquestrador então:
124|1. **Devolve ao executor** com feedback específico ("reescreva o parágrafo 2, tom muito genérico")
125|2. **Ou roteia para outro agente/modelo** mais adequado ao tipo de output
126|3. **NUNCA** tenta corrigir o output por conta própria — isso degrada qualidade
127|
128|## Regras
129|
130|- O gate é **silencioso** — o executivo nunca sabe que existe
131|- O executor é o **único responsável** pela qualidade do seu output
132|- O orquestrador é **fiscal**, não **corretor** — devolve, não reescreve
133|- Quality score mínimo: 35/50 para prosa. Visual: zero falhas no pre-flight
134|- Código, documentação técnica e dados brutos **nunca** passam pelo gate
135|- Em caso de refatoração de skills, o gate continua vinculado ao executor — não migra para camada superior
136|
137|## Verificação
138|
139|- [ ] Briefing gerado pelo executor passa excrtx-quality-antislop (≥ 35/50)
140|- [ ] Draft de email gerado pelo executor passa excrtx-quality-antislop
141|- [ ] Dashboard gerado pelo executor passa excrtx-quality-taste pre-flight
142|- [ ] Código NÃO é filtrado pelo gate
143|- [ ] Documentação técnica (ADR, README, SKILL.md) NÃO é filtrada
144|- [ ] Falha 2x → orquestrador recebe sinalização, não corrige
145|- [ ] Orquestrador devolve ao executor com feedback, não reescreve
146|- [ ] O harness `validate_artifact_manifest.py` audita o pacote de artefatos rejeitando prosa com slop (score < 35) ou visual com meta-labels.
147|