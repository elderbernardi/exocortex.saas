1|---
2|name: excrtx-govern-draftfirst
3|description: Interceptor de ações externas. Toda comunicação ou modificação fora do ambiente local é criada como rascunho para aprovação do executivo.
4|version: 1.0.0
5|category: excrtx
6|metadata:
7|  hermes:
8|    tags: [exocortex, behavior, draft, approval, safety]
9|---
10|
11|# Draft-First — Interceptor de Ações Externas
12|
13|> Nenhuma ação que envie dados para fora do sistema é executada sem aprovação explícita.
14|
15|## Trigger
16|
17|Ativar quando o agente for executar qualquer ação classificada como **Comunicação**, **Entrega ao executivo** ou **Criação externa** pela skill `excrtx-govern-tools`:
18|- Enviar email, mensagem, notificação
19|- Criar ou editar documento compartilhado (Google Docs, Drive, Notion)
20|- Criar ou modificar evento de calendário
21|- Publicar ou compartilhar conteúdo externamente
22|- Qualquer tool call que transmita dados para fora do ambiente Hermes local
23|
24|## Taxonomia obrigatória
25|
26|Antes de agir, classificar em uma destas categorias:
27|
28|1. **Self-delivery operacional**
29|   - Destinatário: o próprio executivo
30|   - Canal: home channel do executivo
31|   - Natureza: resposta operacional do sistema, entrega de artefato, teste técnico explícito ou recibo para o próprio operador
32|
33|2. **Comunicação em nome do executivo**
34|   - Destinatário: terceiro específico ou grupo de terceiros
35|   - Natureza: mensagem, email, comentário, post, convite, pedido, posicionamento ou qualquer fala atribuível ao executivo
36|
37|3. **Publicação/compartilhamento externo**
38|   - Natureza: canal compartilhado, rede social, calendário, documento compartilhado, push, deploy ou equivalente
39|
40|## Procedure
41|
42|### 1. Interceptar a Intenção
43|
44|Quando o executivo pedir uma ação externa, classificar antes de executar:
45|
46|1. **Identificar o tipo de ação** — email, calendar, doc, mensagem
47|2. **Identificar a categoria** — self-delivery operacional, comunicação em nome do executivo ou publicação externa
48|3. **Escolher o regime de execução** conforme a categoria
49|
50|### 2. Formato do Draft
51|
52|```markdown
53|📋 **DRAFT — {tipo de ação}**
54|━━━━━━━━━━━━━━━━━━━━━━━
55|**Para:** {destinatário}
56|**Assunto:** {assunto}
57|
58|{conteúdo do rascunho}
59|━━━━━━━━━━━━━━━━━━━━━━━
60|⚡ Ações: [Aprovar e Enviar] | [Editar] | [Descartar]
61|```
62|
63|### 3. Fluxo de Aprovação
64|
65|| Resposta do Executivo | Ação |
66||---|---|
67|| Aprovação ("ok", "envia", "pode mandar") | Executar via tool **somente no escopo exato do draft aprovado** |
68|| Edição ("mude o tom", "adicione X") | Revisar rascunho, apresentar nova versão |
69|| Descarte ("não", "cancela", "deixa") | Descartar, confirmar que nada foi enviado |
70|| Silêncio (sem resposta) | Manter em fila, lembrar no próximo briefing |
71|
72|**Regra de escopo após aprovação**
73|- Aprovação não autoriza publicar toda a working tree por arrasto.
74|- Se houver mudanças locais não relacionadas, o draft deve explicitar isso antes da aprovação.
75|- Depois da aprovação, stage/commit/push devem ser seletivos por unidade lógica; o restante vira uma segunda publicação, com sua própria validação.
76|- Em fechamento de issue, fechar apenas depois que o commit/push correspondente estiver publicado.
77|
78|Referência operacional: `references/mixed-working-tree-selective-publication.md`
79|
80|### 4. Regime por categoria
81|
82|**Self-delivery operacional**
83|- Pode executar sem DRAFT quando o destinatário é inequivocamente o próprio executivo
84|- Só vale no home channel do executivo
85|- Não vale para grupos, canais compartilhados, destinatários ambíguos ou texto que represente fala do executivo para terceiros
86|
87|**Comunicação em nome do executivo**
88|- Draft-First obrigatório
89|- Aprovação explícita obrigatória depois da apresentação do DRAFT
90|
91|**Publicação/compartilhamento externo**
92|- Draft-First obrigatório
93|- Aprovação explícita obrigatória depois da apresentação do DRAFT
94|
95|### 5. Modo Degradado (sem integração de tool)
96|
97|Quando a tool de comunicação necessária não está integrada ou disponível:
98|- Se a categoria exigir Draft-First, gerar o rascunho completo como texto
99|- Se a categoria for self-delivery operacional, reportar a indisponibilidade da tool e oferecer entrega manual ou alternativa local
100|- Logar a intenção no acervo do microverso ativo
101|
102|## Regras
103|
104|- Draft-First é obrigatório para comunicações externas e publicações externas
105|- Self-delivery operacional NÃO cria autorização implícita para falar com terceiros
106|- Mesmo ações "urgentes" passam pelo draft quando forem comunicação externa — o executivo decide o que é urgente
107|- Destinatário ambíguo ou canal compartilhado deve ser tratado como comunicação externa
108|- Drafts pendentes são incluídos no Morning Briefing
109|- Se o executivo configurar auto-aprovação para um tipo específico (futuro), respeitar
110|
111|## Verificação
112|
113|- [ ] Pedido de email para terceiro gera DRAFT, não envia
114|- [ ] Pedido de evento gera DRAFT com todos os campos
115|- [ ] Resposta de aprovação dispara execução quando o caso exigir Draft-First
116|- [ ] Resposta de descarte confirma que nada foi enviado
117|- [ ] Self-delivery operacional pode executar sem DRAFT quando o destinatário é o próprio executivo no home channel
118|- [ ] Modo degradado gera texto copiável quando a categoria exige DRAFT e a tool está ausente
119|