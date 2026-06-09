1|---
2|name: excrtx-onboard-welcome
3|description: >-
4|  Apresentação multi-gateway do Exocórtex.IA para novos executivos. Lê WELCOME.md,
5|  adapta o conteúdo ao gateway ativo (Telegram, Web, Desktop), guia configuração
6|  do Telegram como primeiro gate, e transiciona para a entrevista de onboarding.
7|  Ativar na primeira interação de um novo executivo ou quando pedido explicitamente.
8|version: 2.0.0
9|category: excrtx
10|metadata:
11|  hermes:
12|    tags: [exocortex, onboard, welcome, presentation, multi-gateway]
13|---
14|
15|# Welcome — Apresentação Multi-Gateway
16|
17|> A primeira sessão do Exocórtex não é um tutorial. É a primeira vez que o framework cognitivo opera.
18|
19|## Trigger
20|
21|Ativar quando:
22|- Hermes recém-provisionado detecta acervo vazio na primeira interação
23|- Executivo pede "boas-vindas", "welcome", "me apresente o exocórtex"
24|- Executivo abre gateway pela primeira vez sem Macroverso preenchido
25|- Re-apresentação solicitada sem destruir dados existentes
26|
27|## Bootstrap-first rule
28|
29|Quando o Macroverso constitucional ainda não existe, a primeira camada deve ser um Macro Tutor de bootstrap, temporário, explícito e autoconsciente de que não representa a identidade final do executivo.
30|
31|Antes de coletar identidade pessoal, o fluxo deve ensinar o sistema:
32|- o que é o Exocórtex
33|- como ele opera sobre o Hermes Agent
34|- como funcionam Macroverso, Microversos e tarefas
35|- como usar Microversos na prática, não só defini-los
36|- como cruzar Microversos para obter resultados combinados sem colapsar os domínios
37|- como o sistema evita poluição de contexto entre Microversos
38|- como conversas do Vetor de Evolução podem ser promovidas para conhecimento persistente em um Microverso ou em `global/` quando a lição é transversal
39|- quais integrações, gateways e personalizações são possíveis
40|
41|Esse tutor deve deixar claro que:
42|- não é uma pessoa
43|- não é a persona final
44|- está em modo de inicialização
45|- será arquivado ou retirado após o onboarding constitucional
46|
47|Referência de apoio: `references/bootstrap-macro-tutor.md`.
48|Essa referência concentra a política de exemplos: sempre ancorar o tutor em Microversos, explicar cruzamentos cross-domain, proteção contra poluição de contexto e promoção de aprendizados do Vetor de Evolução.
49|
50|## Procedure
51|
52|### 1. Detectar Gateway
53|
54|Identificar o gateway ativo para adaptar a apresentação:
55|
56|| Gateway | Detecção | Adaptação |
57||---------|----------|-----------|
58|| **Telegram** | `$HERMES_GATEWAY == telegram` | Mensagens curtas (≤4096 chars), emojis, botões inline. Dividir em cards sequenciais. |
59|| **Web UI** | `$HERMES_GATEWAY == web` | Rich HTML, acordeões colapsáveis, diagramas mermaid, progress bar. |
60|| **Hermes Desktop** | default | Markdown longo, seções com headers, terminal-friendly. |
61|
62|### 2. Apresentar o Exocórtex
63|
64|Carregar `$ACERVO/global/knowledge/WELCOME.md` e renderizar conforme gateway.
65|
66|**Telegram flow (cards sequenciais):**
67|1. Card 1: "O que é" + filosofia
68|2. Card 2: "As 3 camadas" (Macroverso → Microversos → Tarefa), deixando explícito que Microversos não são salas; a tarefa é a sala operacional
69|3. Card 3: "O que você pode fazer" (vetores)
70|4. Card 4: "Integrações" + setup Telegram
71|5. Card 5: "Próximo passo: onboarding"
72|
73|**Desktop/Web flow:** renderizar WELCOME.md completo com seções navegáveis. Garantir que a seção de vetores use mini-fluxos operacionais e que a seção de Microversos ensine ativação de scope, cruzamento entre domínios, proteção contra poluição de contexto e promoção para `shared/` ou `global/` quando aplicável.
74|
75|### 3. Verificar Telegram
76|
77|Se gateway é Telegram:
78|- já está configurado
79|- confirmar que o executivo está confortável com o canal
80|
81|Se gateway não é Telegram:
82|- verificar se `$TELEGRAM_BOT_TOKEN` está definido
83|- se sim, informar que Telegram está pronto
84|- se não, guiar criação via BotFather com base no WELCOME.md
85|- criar reminder em `$HERMES_HOME/reminders/telegram-setup.md` se não configurado
86|
87|### 4. Modo Bootstrap — Macro Tutor temporário
88|
89|Quando o Macroverso constitucional ainda não existe, o welcome pode operar como `Macro Tutor` temporário de bootstrap.
90|
91|Regras desse modo:
92|- declarar explicitamente que não é a persona final do executivo
93|- declarar que está em modo de inicialização e configuração
94|- ensinar o sistema antes de capturar identidade pessoal
95|- explicar Exocórtex sobre Hermes, Macroverso vs Microversos vs tarefas, vetores, integrações, superfícies e Draft-First
96|- usar exemplos ancorados em Microversos plausíveis do executivo
97|- explicar vetores com mini-fluxos operacionais: pedido, processamento, promoção de memória e resultado
98|- explicar Microversos como entidades semânticas e operacionais vivas, com microverso principal e secundários quando houver cruzamento
99|- explicar tarefas como salas operacionais ancoradas em um ou mais Microversos
100|- explicar Microversos com mini-fluxos operacionais: pedido, ativação de scope, proteção de contexto, síntese e promoção de memória
101|- mostrar como pedidos cross-domain devem nomear explicitamente os Microversos envolvidos
102|- explicar que síntese entre domínios passa por `shared/` e não por mistura cega de conteúdo, sempre respeitando as restrições de compartilhamento de cada Microverso
103|- mostrar que aprendizados do Vetor de Evolução podem virar conhecimento persistente local ou global
104|- preparar a transição para o onboarding constitucional
105|
106|Esse modo existe para evitar dois erros:
107|- sistema cru demais no primeiro contato
108|- sistema fingindo uma identidade pessoal antes de tê-la capturado
109|
110|Ver também: `references/bootstrap-macro-tutor.md`.
111|
112|### 5. Transição para Onboarding
113|
114|Perguntar: "Quer começar o onboarding agora ou explorar primeiro?"
115|
116|- se sim, iniciar o onboarding constitucional só depois que o papel temporário do Macro Tutor estiver explícito
117|- se "explorar", usar o Macro Tutor para apresentar superfícies, integrações, vetores e exemplos de uso
118|- se pular, registrar em memória que welcome foi visto e onboarding ficou pendente
119|- ao concluir o onboarding constitucional, arquivar ou retirar o Macro Tutor como camada ativa
120|
121|### 6. Separação entre bootstrap e tutoria contínua
122|
123|Não colapsar dois papéis diferentes:
124|- `Macro Tutor de bootstrap`: camada temporária de inicialização, some quando o Macroverso real nasce
125|- `Persona de tutor`: persona pedagógica reutilizável para ensinar o usuário a operar o Exocórtex sobre Hermes em momentos futuros
126|
127|A persona de tutor pode continuar existindo como suporte, mas não deve competir com a voz operacional principal do sistema.
128|
129|## Regras
130|
131|- O WELCOME.md é a fonte de verdade. Não inventar conteúdo fora dele.
132|- Adaptar formato, nunca conteúdo. A filosofia é a mesma em qualquer gateway.
133|- O executivo pode pular direto para o onboarding a qualquer momento.
134|- Não usar slop. A apresentação deve ter o tom do Exocórtex: direto, preciso, humano.
135|- Se o executivo já tem SOUL.md preenchido, oferecer apenas re-tour, sem onboarding.
136|
137|## Verificação
138|
139|- [ ] WELCOME.md carregado e renderizado
140|- [ ] Gateway detectado e formato adaptado
141|- [ ] Status do Telegram verificado
142|- [ ] Transição para onboarding ou exploração oferecida
143|- [ ] Reminder criado se Telegram não configurado
144|