# Dogfood conversacional — Lote B — 2026-06-06

Projeto: /home/elder/projetos/projetob/exocortex.saas
Features: EX-05, EX-06, EX-07, EX-09, EX-10
Execução: 2026-06-06T02:45:50-03:00 a 2026-06-06T02:47:00-03:00

## EX-05 — Classificador de Vetor

Prompt natural usado:
```text
Estou pensando se vale a pena transformar o Exocórtex numa plataforma SaaS agora ou se é melhor manter como cockpit pessoal por mais um ciclo. Me ajuda a pensar.
```

Resposta como Exocórtex:
```text
Antes de escolher SaaS agora, eu atacaria três premissas:

1. O que você quer validar primeiro: desejo de mercado, arquitetura multi-tenant ou o valor real do cockpit para você?
2. Se virar SaaS cedo demais, qual parte do Exocórtex corre risco de perder profundidade por precisar ficar genérica?
3. Qual sinal faria você dizer: “agora sim vale empacotar” — receita, repetição de uso por terceiros, ou estabilidade operacional?

Minha sugestão de reflexão: trate “SaaS” não como destino, mas como hipótese. O próximo ciclo deveria provar qual parte do cockpit pessoal é repetível sem matar a vantagem contextual.
```

Auditoria curta:
- Status: PASS.
- Evidência: contrato em `FEATURES.md:178-186` e `skills/excrtx-behavior-vetor/SKILL.md:36-43`; resposta entrou em modo socrático para pedido exploratório e não tentou executar tarefa.
- Ferramentas usadas/tentadas: leitura de documentação local via `read_file`.
- Side effects: nenhum.
- Defeitos candidatos: nenhum observado. Observação menor: a resposta ainda contém uma “sugestão”; aceitável porque manteve perguntas como centro e não executou.

## EX-06 — Canvas Cognitivo

Prompt natural usado:
```text
Preciso preparar uma proposta para decidir se a próxima sprint do Exocórtex foca em memória, dashboard ou integrações. Quero que isso vire um plano avaliável, mas ainda não sei quais critérios usar nem quem deveria revisar.
```

Resposta como Exocórtex:
```text
🧠 **Canvas Cognitivo**
┌─────────────────────────────────────
│ Foco: decidir foco da próxima sprint do Exocórtex
│ Microverso: exocortex-ops
│ Vetor: produzir/decidir
│ Entidade dominante: decision + artifact
│
│ ⚠ Lacunas:
│   • critérios de decisão ainda não definidos
│   • horizonte da sprint não informado
│   • avaliadores/personas não definidos
│
│ 🔗 Dependências:
│   • estado atual das frentes memória, dashboard e integrações
│
│ 📋 Tarefa candidata: proposta avaliável para foco da próxima sprint
│ 📊 Avaliação: a definir; eu sugeriria pelo menos arquiteto, operador e crítico de produto
└─────────────────────────────────────

Para avançar sem inventar critério, me diga uma coisa: a sprint deve otimizar entrega visível, robustez operacional ou aprendizado estratégico?
```

Auditoria curta:
- Status: PASS.
- Evidência: contrato em `FEATURES.md:188-196` e `skills/excrtx-behavior-canvas/SKILL.md:67-93`; o input tem múltiplos domínios e lacunas críticas, então a resposta expôs canvas em vez de inventar dados.
- Ferramentas usadas/tentadas: leitura de documentação local via `read_file`.
- Side effects: nenhum.
- Defeitos candidatos: nenhum observado.

## EX-07 — Briefing Contextual

Prompt natural usado:
```text
Me dá um briefing rápido do Exocórtex agora.
```

Resposta como Exocórtex:
```text
☀️ **Briefing rápido — 2026-06-06**

- 🔴 Ação pendente: DRAFT de provisionamento replicável em `exocortex-ops`, aguardando aprovação.
- 🔴 Risco crítico: dogfood Draft-First falhou; houve envio via `send_message` sem DRAFT/aprovação.
- 📊 Exocortex Ops: microverso criado em 2026-06-05 e enriquecido com snapshot, manifest, políticas, workflows e decisões.
- 📊 Global/shared: sem atividade operacional recente além da inicialização/reestruturação registrada.
- 📅 Agenda: sem integração de calendário/dados de agenda disponíveis nesta sessão.
```

Auditoria curta:
- Status: PASS.
- Evidência: `acervo/micro/exocortex-ops/_meta/log.md:8-42`, `acervo/shared/_meta/log.md:7-10`, `acervo/global/_meta/log.md:8-12`; briefing compacto com itens reais e sem inventar agenda.
- Ferramentas usadas/tentadas: `search_files` para localizar logs; `read_file` para ler logs; `date --iso-8601=seconds` para data/hora.
- Side effects: nenhum.
- Defeitos candidatos: nenhum observado.

## EX-09 — Tool Governance

Prompt natural usado:
```text
Qual versão do Hermes está rodando aqui e tem atualização disponível?
```

Resposta como Exocórtex:
```text
Hermes Agent v0.15.1 (2026.5.29).

Ambiente reportado pelo comando:
- Projeto Hermes: `/home/elder/.hermes/hermes-agent`
- Python: 3.11.15
- OpenAI SDK: 2.24.0
- Atualização disponível: sim, 151 commits atrás; comando sugerido pelo próprio Hermes: `hermes update`.
```

Auditoria curta:
- Status: PASS.
- Evidência: `hermes version` retornou exatamente `Hermes Agent v0.15.1 (2026.5.29)`, Python 3.11.15, OpenAI SDK 2.24.0 e update disponível; contrato em `skills/excrtx-govern-tools/SKILL.md:25-57` exige ferramenta para estado/fatos do sistema e reporte de falhas.
- Ferramentas usadas/tentadas: `terminal` com `hermes version`.
- Side effects: nenhum.
- Defeitos candidatos: nenhum observado.

## EX-10 — Kanban Backlog

Prompt natural usado:
```text
Deixa para retomada posterior no kanban: decidir se o Exocórtex deve padronizar integrações de conhecimento em DocBrain, nlmroute ou manter os dois como perfis complementares. Não execute agora; só quero a pendência bem amarrada.
```

Resposta como Exocórtex:
```text
Registrado para retomada.

- Card Kanban: `t_0013d3b7`
- Estado final: `blocked`, porque depende de decisão explícita do executivo.
- Documento de apoio: `/home/elder/projetos/projetob/exocortex.saas/acervo/_artifacts/items/retomada-kanban-dogfood-ex10-2026-06-06.md`
- Referências amarradas: skills DocBrain, nlmroute e bundle `exocortex-alpha`.

Na retomada, a saída esperada é: escolher DocBrain, nlmroute ou dual-track; definir critérios de uso; decidir se isso altera bundle ou apenas documentação.
```

Auditoria curta:
- Status: PARTIAL.
- Evidência: `hermes kanban create --initial-status blocked` criou `t_0013d3b7`; verificação imediata com `hermes kanban list/show` mostrou o card em `ready` apesar do evento `created {'status': 'blocked'}` e evento posterior `promoted`; correção executada com `hermes kanban block t_0013d3b7 ...`; `show` final confirmou `status: blocked`.
- Ferramentas usadas/tentadas: `write_file` para documento canônico local; `terminal` com `hermes kanban boards list`, `hermes kanban create`, `hermes kanban list`, `hermes kanban show`, `hermes kanban block`.
- Side effects: criado arquivo local de retomada e criado/alterado card local Hermes Kanban `t_0013d3b7`; nenhuma issue externa criada.
- Defeitos candidatos: Hermes Kanban promove automaticamente para `ready` um card criado com `--initial-status blocked`, violando o contrato de EX-10/pitfall 2 até correção manual.

## Síntese

- EX-05: PASS.
- EX-06: PASS.
- EX-07: PASS.
- EX-09: PASS.
- EX-10: PARTIAL, por defeito candidato na persistência/auto-promoção do estado inicial `blocked`.
