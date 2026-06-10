1|---
2|name: excrtx-behavior-briefing
3|description: Morning Briefing cross-microverso. Consolida informações pendentes, aprovações em fila, insights recentes e agenda do dia de múltiplos domínios.
4|version: 1.0.0
5|category: excrtx
6|metadata:
7|  hermes:
8|    tags: [exocortex, behavior, briefing, daily, cross-domain]
compiled_rules: |
  Morning briefing crosses all microversos. Consolidate: pending approvals, recent insights, today's agenda, blocked items.
  Format: actionable summary, not a wall of text. Group by urgency, not by domain.
  Trigger: "briefing", "bom dia", "o que tem pra hoje", or scheduled cron.
9|---
10|
11|# Morning Briefing — Consolidação Cross-Microverso
12|
13|> Um executivo não vive em silos. O briefing cruza todos os domínios e entrega um panorama acionável.
14|
15|## Trigger
16|
17|Ativar quando:
18|- O executivo pede "briefing", "status geral", "o que temos para hoje", "me atualiza"
19|- Início de sessão (se configurado para auto-briefing)
20|- O executivo retorna após período de inatividade (>4 horas)
21|
22|## Procedure
23|
24|### 1. Coleta Cross-Microverso
25|
26|Varrer TODOS os microversos ativos (respeitando scope) e coletar:
27|
28|| Fonte | O que buscar |
29||---|---|
30|| `log.md` de cada micro | Últimas entradas (24h) |
31|| Drafts pendentes | Ações que aguardam aprovação do executivo |
32|| `reflections/` de cada micro | Insights recentes não revisados |
33|| `workflows/` global | Deadlines ou milestones próximos |
34|| `shared/cross-refs/` | Referências cruzadas recentes entre microversos |
35|
36|### 2. Estrutura do Briefing
37|
38|```markdown
39|☀️ **Briefing — {data}**
40|
41|## 🔴 Ações Pendentes
42|- [{microverso}] {draft ou ação aguardando aprovação}
43|- [{microverso}] {outro item pendente}
44|
45|## 📊 Status por Domínio
46|### {Microverso 1}
47|- {resumo da última atividade relevante}
48|- {próximo passo ou deadline}
49|
50|### {Microverso 2}
51|- {resumo}
52|
53|## 💡 Insights
54|- [{microverso}] {insight ou reflexão recente que merece atenção}
55|
56|## 📅 Agenda
57|- {eventos do dia — quando Calendar integrado}
58|
59|## 🔗 Conexões
60|- {cross-ref recente: "Decisão em {micro_A} pode impactar {micro_B}"}
61|```
62|
63|### 3. Priorização
64|
65|Ordenar itens por:
66|1. **Urgência** — deadlines hoje > amanhã > esta semana
67|2. **Impacto** — ações que bloqueiam outros microversos primeiro
68|3. **Tempo pendente** — drafts mais antigos primeiro
69|
70|### 4. Modo Compacto vs Detalhado
71|
72|| Modo | Quando | Formato |
73||---|---|---|
74|| **Compacto** | Executivo pede "briefing rápido" | Bullet points, max 10 linhas |
75|| **Detalhado** | Executivo pede "briefing completo" ou retorna de ausência longa | Estrutura completa com contexto |
76|| **Por domínio** | Executivo pede "status do Cliente X" | Briefing focado em um microverso |
77|
78|## Regras
79|
80|- O briefing aplica `excrtx-quality-antislop` — zero frases de enchimento, direto ao ponto
81|- Não inventar itens. Se um microverso não tem atividade recente, dizer: "Sem atividade recente"
82|- Não incluir microversos sem itens relevantes no briefing compacto
83|- Alertar sobre conflitos cross-microverso quando detectados
84|- Se o acervo estiver vazio (executivo novo), dizer: "Acervo vazio — execute o onboarding para começar"
85|
86|## Verificação
87|
88|- [ ] Briefing varre múltiplos microversos
89|- [ ] Drafts pendentes aparecem na seção de ações
90|- [ ] Insights recentes são incluídos
91|- [ ] Priorização respeita urgência > impacto > tempo
92|- [ ] Modo compacto não ultrapassa 10 linhas
93|- [ ] Output passa excrtx-quality-antislop (direto, sem enchimento)
94|