---
name: excrtx-behavior-briefing
description: Morning Briefing cross-microverso. Consolidates pending information, queued approvals, recent insights, and the
  day's agenda across multiple domains.
version: 2.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - behavior
    - briefing
    - daily
    - cross-domain
    related_skills:
    - excrtx-behavior-vetor
    - excrtx-govern-draftfirst
    - excrtx-memory-manager
    calibration:
    - feature_id: EX-07
      calibration_prompt: 'Você gera briefings de contexto para sessões e tarefas. Sintetiza o estado atual do microverso
        ativo: pendências, decisões recentes, prioridades e arquivos relevantes. Ativado quando uma tarefa inicia em contexto
        de microverso ou quando o executivo pede status/resumo.'
      test_prompt: Me dê um briefing da situação atual do projeto. O que temos pendente? O que foi decidido recentemente?
      acceptance_criteria: '1. O agente consulta fontes reais de estado (MEMORY.md, kanban, logs, acervo) antes de responder

        2. O briefing é estruturado com seções claras (Status Atual, Pendências, Decisões Recentes, Prioridades)

        3. Cada item cita a fonte de onde veio a informação

        4. NÃO inventa pendências ou decisões — se não há dados, diz explicitamente'
      remediation_tip: 'FALHA: Briefing fabricado. A skill exige consulta a fontes reais antes de sintetizar. Leia: ''$ACERVO/macro/MEMORY.md''
        para decisões, ''kanban list'' para pendências, e logs recentes para status. Se não encontrar dados, diga ''Não há
        registros de pendências no acervo atual'' em vez de inventar.'
compiled_rules: 'Briefing v2 cruza todos os microversos via `acervoctl briefing`. Coleta: intenções vencidas/próximas,
  disputas, drafts, episódios das últimas 24h, context heads e agenda quando integrada.

  Formato: acionável, citado, direto ao ponto, ≤4k tokens. Ordenar por urgência, não por domínio. Modo compacto ≤10 linhas.

  Trigger: "briefing", "bom dia", "o que tem pra hoje", ou início de sessão.'
---
# Morning Briefing — Consolidação Cross-Microverso

> Um executivo não vive em silos. O briefing cruza todos os domínios e entrega um panorama acionável.

## When to Use

Ativar quando:
- O executivo pede "briefing", "status geral", "o que temos para hoje", "me atualiza"
- Início de sessão (se configurado para auto-briefing)
- O executivo retorna após período de inatividade (>4 horas)

**Don't use for:** Single-microverso status queries (use the microverso's own log). System diagnostics (use excrtx-assess-selftest).

## Procedure

### 1. Coleta Cross-Microverso

Use primeiro a superfície determinística:

```bash
python3 "$CTL/acervoctl.py" briefing --acervo-root "$ACERVO" --mode detailed
```

Para "briefing rápido", use `--mode compact`. Para um domínio, adicione
`--scope {slug}`. Se existir uma exportação JSON de agenda, passe
`--calendar-file {path}`; se não existir, preserve `calendar_status:not_configured`
e não invente eventos.

Varrer TODOS os microversos ativos (respeitando scope) e coletar:

| Fonte | O que buscar |
|---|---|
| `intentions/` | Vencidas primeiro; depois próximas por `due` |
| Objetos `conflict` | Disputas abertas que exigem decisão |
| Drafts pendentes | Ações que aguardam aprovação do executivo |
| `episodes/` | Episódios significativos das últimas 24h |
| `context/current-state.md` | Cabeça dos domínios ativos |
| Agenda JSON opcional | Eventos reais do dia; ausência fica explícita |

### 2. Estrutura do Briefing

```markdown
☀️ **Briefing — {data}**

## 🔴 Ações Pendentes
- [{microverso}] {draft ou ação aguardando aprovação}
- [{microverso}] {outro item pendente}

## 📊 Status por Domínio
### {Microverso 1}
- {resumo da última atividade relevante}
- {próximo passo ou deadline}

### {Microverso 2}
- {resumo}

## 🕘 Últimas 24h
- [{microverso}] {episódio significativo com path}

## 📅 Agenda
- {eventos do dia — quando Calendar integrado}

## 🔗 Conexões
- {cross-ref recente: "Decisão em {micro_A} pode impactar {micro_B}"}
```

### 3. Priorização

Ordenar itens por:
1. **Urgência** — deadlines hoje > amanhã > esta semana
2. **Impacto** — ações que bloqueiam outros microversos primeiro
3. **Tempo pendente** — drafts mais antigos primeiro

### 4. Modo Compacto vs Detalhado

| Modo | Quando | Formato |
|---|---|---|
| **Compacto** | Executivo pede "briefing rápido" | Bullet points, max 10 linhas |
| **Detalhado** | Executivo pede "briefing completo" ou retorna de ausência longa | Estrutura completa com contexto |
| **Por domínio** | Executivo pede "status do Cliente X" | Briefing focado em um microverso |

## Pitfalls

- **Empty acervo panic**: Se o acervo estiver vazio (executivo novo), dizer: "Acervo vazio — execute o onboarding para começar". Don't fabricate content.
- **Fabricated items**: Não inventar itens. Cada item do briefing deve vir do payload e manter seu path canônico.
- **Calendar fiction**: `calendar_status:not_configured|missing` significa agenda indisponível, nunca agenda vazia confirmada.
- **Slop in briefings**: O briefing aplica `excrtx-quality-antislop` — zero frases de enchimento, direto ao ponto.
- **Compact mode overflow**: Não incluir microversos sem itens relevantes no briefing compacto. Stay within 10 lines.
- **Cross-microverso blind spots**: Alertar sobre conflitos cross-microverso quando detectados. Don't ignore interactions between domains.

## Verification

- [ ] Briefing varre múltiplos microversos
- [ ] Drafts pendentes aparecem na seção de ações
- [ ] Insights recentes são incluídos
- [ ] Priorização respeita urgência > impacto > tempo
- [ ] Modo compacto não ultrapassa 10 linhas
- [ ] Output passa excrtx-quality-antislop (direto, sem enchimento)
