---
name: excrtx-behavior-briefing
description: Morning Briefing cross-microverso. Consolida informações pendentes, aprovações em fila, insights recentes e agenda do dia de múltiplos domínios.
version: 1.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, behavior, briefing, daily, cross-domain]
---

# Morning Briefing — Consolidação Cross-Microverso

> Um executivo não vive em silos. O briefing cruza todos os domínios e entrega um panorama acionável.

## Trigger

Ativar quando:
- O executivo pede "briefing", "status geral", "o que temos para hoje", "me atualiza"
- Início de sessão (se configurado para auto-briefing)
- O executivo retorna após período de inatividade (>4 horas)

## Procedure

### 1. Coleta Cross-Microverso

Varrer TODOS os microversos ativos (respeitando scope) e coletar:

| Fonte | O que buscar |
|---|---|
| `log.md` de cada micro | Últimas entradas (24h) |
| Drafts pendentes | Ações que aguardam aprovação do executivo |
| `reflections/` de cada micro | Insights recentes não revisados |
| `workflows/` global | Deadlines ou milestones próximos |
| `shared/cross-refs/` | Referências cruzadas recentes entre microversos |

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

## 💡 Insights
- [{microverso}] {insight ou reflexão recente que merece atenção}

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

## Regras

- O briefing aplica `excrtx-quality-antislop` — zero frases de enchimento, direto ao ponto
- Não inventar itens. Se um microverso não tem atividade recente, dizer: "Sem atividade recente"
- Não incluir microversos sem itens relevantes no briefing compacto
- Alertar sobre conflitos cross-microverso quando detectados
- Se o acervo estiver vazio (executivo novo), dizer: "Acervo vazio — execute o onboarding para começar"

## Verificação

- [ ] Briefing varre múltiplos microversos
- [ ] Drafts pendentes aparecem na seção de ações
- [ ] Insights recentes são incluídos
- [ ] Priorização respeita urgência > impacto > tempo
- [ ] Modo compacto não ultrapassa 10 linhas
- [ ] Output passa excrtx-quality-antislop (direto, sem enchimento)
