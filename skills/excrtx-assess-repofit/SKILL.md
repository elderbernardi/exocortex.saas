1|---
2|name: excrtx-assess-repofit
3|description: Avaliar se um repositório existente é adequado para servir como base de um produto, engine ou serviço maior; validar claims contra código, runtime e contrato operacional.
4|version: 1.0.0
5|category: excrtx
6|metadata:
7|  hermes:
8|    tags: [assessment, architecture, due-diligence, repo, fit-gap, runtime-validation]
9|---
10|
11|# Technical Repo Fit Assessment
12|
13|Use esta skill quando o executivo pedir para estudar um sistema existente e decidir se ele atende a um propósito maior: virar engine, backend, parser, serviço, intake pipeline, viewer, ou base de produto.
14|
15|O objetivo não é resumir o README. O objetivo é medir o delta entre o que o projeto diz ser e o que ele realmente entrega.
16|
17|## Trigger
18|
19|Ative quando o pedido tiver esta forma:
20|
21|- “estude este sistema”
22|- “veja se os requisitos são suficientes para nosso propósito”
23|- “avalie se este projeto serve como base para X”
24|- “escreva um relatório com melhorias necessárias”
25|- auditoria arquitetural de um repo já existente
26|
27|## Entrega esperada
28|
29|A saída padrão deve conter:
30|
31|1. veredito curto
32|2. pontos fortes reais
33|3. lacunas que impedem o uso para o propósito-alvo
34|4. riscos se acoplado como está
35|5. mudanças recomendadas, idealmente em P0/P1/P2
36|6. recomendação final de adoção, adaptação ou descarte
37|
38|Se útil, grave um relatório em arquivo dentro do repo em `plans/`.
39|
40|## Procedimento
41|
42|### 1. Ler o contrato declarado
43|
44|Inspecione primeiro os arquivos que prometem o comportamento do sistema:
45|
46|- README
47|- purpose/design/schema/architecture docs
48|- package manifests e config principal
49|- planos e findings prévios
50|
51|Pergunta central: “o que o projeto afirma ser?”
52|
53|### 2. Ler o contrato executável
54|
55|Depois, valide onde o comportamento realmente vive:
56|
57|- entrypoints CLI/API
58|- pipeline principal
59|- adapters
60|- tipos de saída
61|- config loader
62|- persistência
63|- watcher/worker/server
64|- testes
65|
66|Pergunta central: “o que o código realmente faz?”
67|
68|### 3. Validar a trilha crítica em runtime
69|
70|Não confie só na leitura estática. Sempre que possível:
71|
72|- rode testes
73|- rode lint/build
74|- execute scripts de comparação ou smoke tests do caminho principal
75|- valide dependências opcionais que o fluxo crítico assume
76|
77|Atenção: ambiente incompleto não vira regra durável. Registre apenas o efeito sobre o caminho avaliado.
78|
79|### 4. Procurar quatro classes de mismatch
80|
81|#### a) Claim vs implementation
82|
83|Exemplo: documentação diz que um schema governa a geração, mas o código nunca o carrega.
84|
85|#### b) Fallback prometido vs fallback real
86|
87|Exemplo: o pipeline anuncia Vision fallback, mas o script intermediário não existe.
88|
89|#### c) Contrato de produto vs contrato interno
90|
91|Exemplo: o sistema foi desenhado como CLI/wiki local, mas o novo propósito exige engine de serviço com API, jobs e idempotência.
92|
93|#### d) Arquitetura suficiente vs arquitetura endurecida
94|
95|Exemplo: a ideia está certa, mas faltam telemetria, versionamento, retries, artifacts, qualidade e isolamento de responsabilidades.
96|
97|### 5. Testar “adequação ao propósito”, não “qualidade absoluta”
98|
99|A pergunta correta não é “o sistema é bom?”.
100|A pergunta correta é “ele é suficiente para o propósito-alvo sem impor risco estrutural?”
101|
102|Um projeto pode ser bom como ferramenta local e insuficiente como engine de produção.
103|
104|### 6. Estruturar a análise como delta
105|
106|Use esta moldura:
107|
108|- o que já serve
109|- o que quase serve, mas precisa endurecimento
110|- o que hoje impede adoção
111|- o que precisa virar contrato explícito
112|
113|## Checklist de auditoria
114|
115|### Produto e contrato
116|
117|- Há um input/output canônico para o caso de uso alvo?
118|- O resultado principal é estruturado ou só textual?
119|- O sistema é centrado em CLI, arquivos locais ou serviço?
120|- Existe distinção entre core engine e projeções downstream?
121|
122|### Pipeline
123|
124|- O caminho crítico processa o documento inteiro ou só amostras/chunks parciais?
125|- Há agregação real entre chunks?
126|- Os fallbacks existem de fato?
127|- A escolha entre parsers é explícita e observável?
128|
129|### Operação
130|
131|- Há idempotência por hash ou política de reprocessamento?
132|- Há jobs, status, retries e timeouts?
133|- Há artifacts intermediários para debug?
134|- Há logs suficientes por etapa?
135|
136|### Provenance e auditoria
137|
138|- A origem externa é preservada?
139|- O artefato bruto local é distinguido da origem?
140|- A linhagem do processamento fica registrada?
141|- Dá para saber qual parser, qual fallback e qual LLM foram usados?
142|
143|### Qualidade
144|
145|- Há quality gates por tipo documental?
146|- Há testes nos pontos de maior risco?
147|- Há benchmark com corpus real do domínio?
148|
149|## Heurísticas úteis
150|
151|- Se o tipo principal de saída é wiki page, markdown final ou arquivo local, suspeite de acoplamento excessivo para uso como engine.
152|- Se a documentação promete governança declarativa, procure a leitura efetiva desses arquivos no runtime.
153|- Se o código tem chunking, confirme se ele agrega múltiplos chunks. Muitos sistemas “têm chunking” e processam só o primeiro chunk.
154|- Se o sistema promete escada de fallbacks, valide cada degrau até o fim. Um degrau ausente invalida a promessa operacional.
155|- Se há provenance, verifique se ela preserva origem real e não apenas caminhos locais derivados.
156|
157|## Formato de veredito
158|
159|Use linguagem direta:
160|
161|- “suficiente como base exploratória, insuficiente como engine de produção”
162|- “boa fundação, contrato operacional fraco”
163|- “arquitetura conceitualmente correta, integração crítica quebrada”
164|
165|Evite elogio genérico. Nomeie o que presta e o que falta.
166|
167|## Quando a avaliação vira implementação
168|
169|Se o executivo pedir para seguir do relatório para a correção, mantenha o refactor no menor corte que transforma o contrato operacional sem destruir o produto original:
170|
171|1. preservar o modo existente como projeção downstream — exemplo: wiki continua funcionando
172|2. criar um modo engine/process-only que devolve contrato estruturado sem side effects desnecessários
173|3. introduzir idempotência por hash antes de expor API/worker
174|4. persistir jobs e revisões fora da projeção antiga — exemplo: `.docbrain/parse-jobs/`, não `wiki/`
175|5. tornar a política de reprocessamento explícita (`skip`, `reprocess`, `new_revision` ou equivalente)
176|6. validar com TDD no contrato novo e regressão no contrato antigo
177|7. só depois desenhar API/worker externo
178|
179|Essa sequência evita o erro comum de “ligar a CLI no servidor” antes de existir contrato estável de engine.
180|
181|## Artefatos de apoio
182|
183|- `references/docbrain-parser-engine-case.md` — caso concreto de auditoria e hardening de um parser/document engine, incluindo processo-only, idempotência por hash e store de jobs.
184|
185|## Pitfalls
186|
187|- Não confundir “compila e passa testes” com “serve para o propósito-alvo”.
188|- Não tomar README como verdade operacional.
189|- Não desqualificar o sistema inteiro quando o correto é separar core promissor de contrato incompleto.
190|- Não registrar falhas transitórias de ambiente como se fossem limitações permanentes da arquitetura.
191|
192|## Regra final
193|
194|A boa análise não responde só “serve ou não serve”. Ela mostra qual refactor transforma o sistema em algo adotável.
195|