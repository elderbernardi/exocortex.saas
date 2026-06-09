1|---
2|name: excrtx-harness-kanban
3|description: Registrar pendências, decisões arquiteturais e pontos de retomada do Exocórtex em backlog durável com Hermes Kanban, mantendo vínculo com os artefatos canônicos do projeto e do Acervo.
4|version: 1.0.0
5|category: excrtx
6|metadata:
7|  hermes:
8|    tags: [exocortex, kanban, backlog, governance, architecture, resumption]
9|---
10|
11|# Exocortex Kanban Backlog
12|
13|Usar quando o executivo pedir para deixar uma decisão, pendência ou plano em estado de espera para retomada posterior.
14|
15|## Trigger
16|
17|Ative esta skill quando houver qualquer um destes sinais:
18|- "coloque isso no kanban"
19|- "deixe para retomada posterior"
20|- "registre como pendente"
21|- "documente e atualize o todo"
22|- "anotar como TODO" / "coloca no TODO"
23|- decisão arquitetural ainda sem martelo do executivo
24|- trabalho que não deve virar implementação imediata
25|
26|## Objetivo
27|
28|Transformar uma conversa em backlog durável, auditável e fácil de retomar, sem depender de memória implícita da sessão.
29|
30|## Princípios
31|
32|1. O kanban não substitui os artefatos canônicos. Primeiro documente em arquivo, depois crie o card.
33|2. O card deve apontar para caminhos absolutos ou inequívocos de retomada.
34|3. Decisão pendente do executivo deve ficar em estado bloqueado, não pronta para execução.
35|4. Sempre verifique o estado final do card após criar ou alterar.
36|5. A retomada deve exigir o mínimo de reconstrução mental.
37|
38|## Fluxo padrão
39|
40|### 1. Consolidar a base documental
41|
42|Antes de criar o card, registrar ou atualizar:
43|- plano do projeto
44|- ADR proposta ou decisão relacionada
45|- status board / backlog textual
46|- log do microverso, quando o tema for canônico no Acervo
47|
48|Sem isso, o card vira lembrete solto.
49|
50|### 2. Criar um ponto de retomada explícito
51|
52|O card deve conter:
53|- título orientado a decisão ou próxima ação
54|- contexto curto
55|- lista de referências obrigatórias
56|- lista de decisões pendentes
57|- saída esperada na retomada
58|
59|Estrutura recomendada do corpo:
60|
61|```text
62|Retomada pendente de decisão do executivo.
63|
64|Referências obrigatórias:
65|- /caminho/arquivo-1.md
66|- /caminho/arquivo-2.md
67|
68|Decisões pendentes:
69|1. ...
70|2. ...
71|
72|Saída esperada na retomada:
73|- decisão explícita
74|- recorte aprovado
75|- autorização para próxima fase
76|```
77|
78|### 3. Estado correto do card
79|
80|Se a próxima etapa depende de decisão do executivo, o estado alvo é `blocked`.
81|
82|Não deixar como `ready` por conveniência. Card pronto dispara execução antes da hora e degrada a governança.
83|
84|### 3A. Modo TODO leve
85|
86|Quando o executivo pedir explicitamente apenas para "anotar como TODO" ou "colocar no TODO", não force a criação imediata de card Kanban se a intenção aparente for só registrar uma pendência. Faça, no mínimo:
87|- registrar no TODO da sessão, se a ferramenta de TODO estiver disponível;
88|- atualizar o backlog textual canônico do projeto, normalmente `plans/STATUS.md` na seção `Pending TODOs` quando esse arquivo existir;
89|- preservar a formulação estratégica do executivo, especialmente restrições como "usar soluções prontas/consolidadas";
90|- criar card Kanban apenas se o pedido mencionar kanban, decisão bloqueada, retomada formal, ou se o trabalho exigir rastreio operacional separado.
91|
92|### 4. Verificação obrigatória
93|
94|Depois de criar o card:
95|- listar o board
96|- abrir o card
97|- confirmar status, referências e resumo mais recente
98|
99|Se o card não terminou no estado esperado, corrigir imediatamente.
100|
101|### 5. Fechar o ciclo documental
102|
103|Após criar o card:
104|- atualizar o status board do projeto, quando houver backlog textual canônico
105|- registrar no log do microverso que a retomada foi ancorada em kanban
106|- citar o `task_id` no log quando isso ajudar a localizar a pendência
107|
108|## Pitfalls
109|
110|### Pitfall 1 — Criar o card antes de documentar
111|
112|Isso gera backlog órfão. O card deve apontar para artefatos reais, não substituir o raciocínio documentado.
113|
114|### Pitfall 2 — Deixar decisão pendente em `ready`
115|
116|`ready` comunica executável. Para decisão humana pendente, use `blocked`.
117|
118|### Pitfall 3 — Assumir que o estado pedido na criação ficou persistido
119|
120|Sempre verificar com `kanban list` e `kanban show`. Se necessário, bloquear explicitamente após a criação.
121|
122|### Pitfall 4 — Corpo do card sem saída esperada
123|
124|Sem saída esperada, a retomada abre nova ambiguidade e desperdiça contexto.
125|
126|## Template de retomada
127|
128|Título:
129|- `Decidir arquitetura da v1 de ...`
130|- `Definir política de ...`
131|- `Escolher caminho de implantação de ...`
132|
133|Corpo:
134|- contexto de uma frase
135|- referências obrigatórias
136|- decisões pendentes
137|- saída esperada
138|
139|## Integração com o Exocórtex
140|
141|- Use esta skill junto com ADRs propostas quando ainda faltar decisão do executivo.
142|- Use esta skill junto com `STATUS.md` quando o projeto já mantém backlog textual.
143|- Use esta skill junto com logs do microverso quando o tema pertence ao Acervo canônico.
144|
145|## Referências
146|
147|- `references/hermes-blocked-card-verification.md` — padrão de verificação e correção do estado final de cards de decisão.
148|- `references/mission-control-ui-todo.md` — nota de retomada para o TODO de Mission Control personalizado do Exocórtex com chat + arquivos e preferência por soluções consolidadas.
149|
150|## Verificação
151|
152|- [ ] Há artefato documental canônico antes do card.
153|- [ ] O card aponta para arquivos de retomada.
154|- [ ] Decisão pendente ficou em `blocked`.
155|- [ ] O estado final foi verificado após a criação.
156|- [ ] O log/status do projeto registra a ancoragem no kanban.
157|