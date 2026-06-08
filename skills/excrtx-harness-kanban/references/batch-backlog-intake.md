# Batch Backlog Intake — Múltiplos itens brutos → Backlog Estruturado

> Quando o executivo envia um lote de links, comandos, observações e screenshots e espera que virem backlog organizado.

## Trigger

Usar quando o executivo envia múltiplos itens simultaneamente (>3) com instruções como "cria issues", "coloca no backlog", "adiciona como tarefa", "organiza isso".

## Princípio

O lote bruto não pode virar backlog solto. Cada item precisa de:
- contexto adicional (quando ausente, pedir ou inferir razoavelmente)
- classificação: tipo + prioridade + área
- escopo inicial
- critério de aceite

## Fluxo

### 1. Coleta e consolidação

Agrupar itens por afinidade temática antes de classificar:

- Integrações externas (links, MCPs, serviços)
- Setup/infraestrutura (instalações, binários, configs)
- Arquitetura e comportamento (decisões de design)
- Modelos e roteamento (provedores, rankings)
- Docs e pesquisa (Reddit, manuais)
- Bugfixes (drift, nomes, ruído)

Itens ambíguos demais para implementação direta → marcar como `research` ou `chore` com escopo de clarificação.

### 2. Classificação por item

Cada item recebe:

| Campo | Valores |
|---|---|
| **tipo** | `bug`, `feature`, `docs`, `infra`, `research`, `chore` |
| **prioridade** | `P0` (bloqueante), `P1` (próximo ciclo), `P2` (quando der), `P3` (nice-to-have) |
| **área** | `hermes`, `exocortex`, `memory`, `ui`, `integration`, `models`, `docbrain`, `google`, `telegram` (ajustar ao contexto) |

Regra: itens com dependência entre si herdam a prioridade do mais alto. Ex.: se `gcloud` (P1) bloqueia Google Workspace (P1), ambos P1.

### 3. Documentação com contexto + escopo + critério

Cada issue/backlog-item deve ter:

```markdown
### Título
[Ação] [objeto] — até 80 caracteres, orientado a decisão ou próxima ação

### Contexto
Por que isso existe? O que levou a registrar? 2-3 frases.

### Escopo inicial
- O que fazer primeiro
- O que NÃO fazer
- Dependências conhecidas

### Critérios de aceite
- [ ] Condição verificável A
- [ ] Condição verificável B
```

**Pitfall:** Itens sem critério de aceite viram tarefas que nunca terminam. Sempre definir "como saber que isso está pronto".

### 4. Apresentação e aprovação

- Consolidar em arquivo markdown local (`candidate-issues.md` ou similar)
- Apresentar como DRAFT (seguindo o protocolo Draft-First)
- Só criar issues/kanban-cards apó s aprovação explícita

### 5. Priorização relativa

Apresentar ordem sugerida de ataque:

```
P0 — itens que bloqueiam outros
P1 — itens para o ciclo atual
P2 — itens documentados mas não imediatos
P3 — itens que precisam de clarificação primeiro
```

## Gatilho de design

Quando um backlog pedido envolver **decisão arquitetural** (ex.: "A, B ou C?"), não dar resposta pronta — apresentar opções com trade-offs e pedir escolha explícita antes de registrar.

## Exemplo desta sessão

Nesta sessão, 16 itens brutos (links + comandos + screenshot + observações) foram consolidados em `candidate-issues.md` com:
- classificação tipo/prioridade/área
- contexto + escopo + critério por item
- ordem de ataque sugerida (P0→P3)
- 1 issue criada no GitHub após aprovação