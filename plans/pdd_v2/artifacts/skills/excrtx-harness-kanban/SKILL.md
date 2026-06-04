---
name: excrtx-harness-kanban
description: Registrar pendências, decisões arquiteturais e pontos de retomada do Exocórtex em backlog durável com Hermes Kanban, mantendo vínculo com os artefatos canônicos do projeto e do Acervo.
version: 1.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, kanban, backlog, governance, architecture, resumption]
---

# Exocortex Kanban Backlog

Usar quando o executivo pedir para deixar uma decisão, pendência ou plano em estado de espera para retomada posterior.

## Trigger

Ative esta skill quando houver qualquer um destes sinais:
- "coloque isso no kanban"
- "deixe para retomada posterior"
- "registre como pendente"
- "documente e atualize o todo"
- "anotar como TODO" / "coloca no TODO"
- decisão arquitetural ainda sem martelo do executivo
- trabalho que não deve virar implementação imediata

## Objetivo

Transformar uma conversa em backlog durável, auditável e fácil de retomar, sem depender de memória implícita da sessão.

## Princípios

1. O kanban não substitui os artefatos canônicos. Primeiro documente em arquivo, depois crie o card.
2. O card deve apontar para caminhos absolutos ou inequívocos de retomada.
3. Decisão pendente do executivo deve ficar em estado bloqueado, não pronta para execução.
4. Sempre verifique o estado final do card após criar ou alterar.
5. A retomada deve exigir o mínimo de reconstrução mental.

## Fluxo padrão

### 1. Consolidar a base documental

Antes de criar o card, registrar ou atualizar:
- plano do projeto
- ADR proposta ou decisão relacionada
- status board / backlog textual
- log do microverso, quando o tema for canônico no Acervo

Sem isso, o card vira lembrete solto.

### 2. Criar um ponto de retomada explícito

O card deve conter:
- título orientado a decisão ou próxima ação
- contexto curto
- lista de referências obrigatórias
- lista de decisões pendentes
- saída esperada na retomada

Estrutura recomendada do corpo:

```text
Retomada pendente de decisão do executivo.

Referências obrigatórias:
- /caminho/arquivo-1.md
- /caminho/arquivo-2.md

Decisões pendentes:
1. ...
2. ...

Saída esperada na retomada:
- decisão explícita
- recorte aprovado
- autorização para próxima fase
```

### 3. Estado correto do card

Se a próxima etapa depende de decisão do executivo, o estado alvo é `blocked`.

Não deixar como `ready` por conveniência. Card pronto dispara execução antes da hora e degrada a governança.

### 3A. Modo TODO leve

Quando o executivo pedir explicitamente apenas para "anotar como TODO" ou "colocar no TODO", não force a criação imediata de card Kanban se a intenção aparente for só registrar uma pendência. Faça, no mínimo:
- registrar no TODO da sessão, se a ferramenta de TODO estiver disponível;
- atualizar o backlog textual canônico do projeto, normalmente `plans/STATUS.md` na seção `Pending TODOs` quando esse arquivo existir;
- preservar a formulação estratégica do executivo, especialmente restrições como "usar soluções prontas/consolidadas";
- criar card Kanban apenas se o pedido mencionar kanban, decisão bloqueada, retomada formal, ou se o trabalho exigir rastreio operacional separado.

### 4. Verificação obrigatória

Depois de criar o card:
- listar o board
- abrir o card
- confirmar status, referências e resumo mais recente

Se o card não terminou no estado esperado, corrigir imediatamente.

### 5. Fechar o ciclo documental

Após criar o card:
- atualizar o status board do projeto, quando houver backlog textual canônico
- registrar no log do microverso que a retomada foi ancorada em kanban
- citar o `task_id` no log quando isso ajudar a localizar a pendência

## Pitfalls

### Pitfall 1 — Criar o card antes de documentar

Isso gera backlog órfão. O card deve apontar para artefatos reais, não substituir o raciocínio documentado.

### Pitfall 2 — Deixar decisão pendente em `ready`

`ready` comunica executável. Para decisão humana pendente, use `blocked`.

### Pitfall 3 — Assumir que o estado pedido na criação ficou persistido

Sempre verificar com `kanban list` e `kanban show`. Se necessário, bloquear explicitamente após a criação.

### Pitfall 4 — Corpo do card sem saída esperada

Sem saída esperada, a retomada abre nova ambiguidade e desperdiça contexto.

## Template de retomada

Título:
- `Decidir arquitetura da v1 de ...`
- `Definir política de ...`
- `Escolher caminho de implantação de ...`

Corpo:
- contexto de uma frase
- referências obrigatórias
- decisões pendentes
- saída esperada

## Integração com o Exocórtex

- Use esta skill junto com ADRs propostas quando ainda faltar decisão do executivo.
- Use esta skill junto com `STATUS.md` quando o projeto já mantém backlog textual.
- Use esta skill junto com logs do microverso quando o tema pertence ao Acervo canônico.

## Referências

- `references/hermes-blocked-card-verification.md` — padrão de verificação e correção do estado final de cards de decisão.
- `references/mission-control-ui-todo.md` — nota de retomada para o TODO de Mission Control personalizado do Exocórtex com chat + arquivos e preferência por soluções consolidadas.

## Verificação

- [ ] Há artefato documental canônico antes do card.
- [ ] O card aponta para arquivos de retomada.
- [ ] Decisão pendente ficou em `blocked`.
- [ ] O estado final foi verificado após a criação.
- [ ] O log/status do projeto registra a ancoragem no kanban.
