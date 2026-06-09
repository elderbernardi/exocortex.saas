1|---
2|name: excrtx-onboard-interview
3|description: >-
4|  Entrevista de onboarding para novos executivos. Captura valores, estilo, domínios
5|  e integrações em 5 blocos de perguntas para auto-gerar SOUL.md personalizado e
6|  microversos iniciais. Ativar após o welcome ou quando executivo pede re-onboarding.
7|version: 2.0.0
8|category: excrtx
9|metadata:
10|  hermes:
11|    tags: [exocortex, onboard, interview, soul, setup, personalization]
12|---
13|
14|# Onboarding Interview — Arquiteto de Sistemas Cognitivos
15|
16|> Cada executivo é único. O onboarding captura a essência do novo usuário e configura o Exocórtex sob medida.
17|
18|## Arquitetura de Provisionamento
19|
20|O Hermes do executivo **não provisiona a si mesmo**. O ciclo é:
21|
22|1. **Provisioner Agent** cria a instância: container, `HERMES_HOME`, golden image, skills base.
23|2. **Hermes do executivo** inicializa com o bundle `exocortex-alpha` já instalado.
24|3. **Welcome** (`excrtx-onboard-welcome`) apresenta o sistema.
25|4. **Interview** (esta skill) personaliza a instância pré-provisionada.
26|
27|O executivo nunca interage com o Provisioner. Ele só vê: welcome → entrevista → Exocórtex pronto.
28|
29|## Trigger
30|
31|Ativar quando:
32|- Transição do `excrtx-onboard-welcome` (fluxo normal)
33|- Executivo pede "configure para mim", "novo setup", "onboarding", "quero refazer a entrevista"
34|- Re-calibração solicitada (sem destruir dados existentes — merge)
35|- SOUL.md detectado com seções "Pendente" (Configuration State)
36|
37|## Procedure
38|
39|### 1. Apresentação
40|
41|Dizer: "Vou fazer perguntas em 5 blocos para entender como você pensa e trabalha. Não existe resposta certa. Pode pular qualquer pergunta — uso defaults razoáveis."
42|
43|### 2. Entrevista (5 blocos)
44|
45|**Bloco A — Identidade Profissional:** Papel, estilo de liderança, 3 valores-guia.
46|
47|**Bloco B — Estilo de Comunicação:** Tom de email, palavras que usa/evita, bullet points vs texto corrido.
48|
49|**Bloco C — Domínios de Atuação:** Domínios gerenciados, o mais crítico agora, onde quer mais controle.
50|
51|**Bloco D — Preferências Operacionais:** Manhã ideal, respostas diretas vs provocativas, quando interromper.
52|
53|**Bloco E — Integrações:** Gmail/Google Workspace, calendário, outras ferramentas.
54|
55|### 3. Geração de Artefatos
56|
57|Com base nas respostas, auto-gerar:
58|1. **SOUL.md personalizado** — Values, Communication Style, Behavioral Boundaries
59|2. **Microversos iniciais** — um para cada domínio do Bloco C (via `excrtx-memory-newmicro`)
60|3. **tools/ global** — integrações desejadas do Bloco E
61|4. **estilo.md no macroverso** — estilo de comunicação do Bloco B
62|
63|### 4. Confirmação
64|
65|Apresentar resumo: Estilo, Domínios criados, Integrações, Modo padrão. Perguntar se quer ajustar antes de ativar.
66|
67|### 5. Ativação
68|
69|Após confirmação: atualizar SOUL.md, criar microversos via `excrtx-memory-newmicro`, registrar no MEMORY.md.
70|
71|## Regras
72|
73|- Perguntas aplicam `excrtx-quality-antislop` — diretas, sem floreio
74|- Executivo pode pular perguntas — usar defaults razoáveis
75|- Mapear fielmente o estilo do executivo, sem julgamento
76|- Re-onboarding não destrói dados existentes (merge)
77|- Esta skill NÃO provisiona infraestrutura — assume que o Provisioner já fez isso
78|- Referências a skills usam nomes novos (excrtx-* convention, ADR-015)
79|
80|## Verificação
81|
82|- [ ] Entrevista cobre os 5 blocos
83|- [ ] SOUL.md personalizado com respostas do executivo
84|- [ ] Microversos criados para cada domínio do Bloco C
85|- [ ] Resumo apresentado para confirmação antes de ativar
86|- [ ] Configuration State atualizado para OPERATIONAL
87|