# DRAFT Issue — Kanban não preserva `--initial-status blocked`

## Feature

EX-10 — Kanban Backlog

## Prioridade

P1

## Comportamento observado

Durante dogfood, `hermes kanban create --initial-status blocked` criou o card, mas a verificação imediata mostrou promoção automática para `ready`. Foi necessário rodar `hermes kanban block` depois.

Card observado: `t_0013d3b7`.

## Comportamento esperado

Um card criado como `blocked` deve permanecer bloqueado até desbloqueio explícito.

## Impacto

Decisões pendentes podem aparecer como prontas para execução, quebrando o contrato da skill EX-10.

## Critérios de aceite

- [ ] `--initial-status blocked` preserva estado bloqueado.
- [ ] Teste cobre criação + leitura imediata do card.
- [ ] Skill documenta workaround apenas se o bug for do Hermes upstream.
