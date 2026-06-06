# DRAFT Issue — Self-test declara saúde 5/5 sem sustentação operacional

Status: DRAFT local. Não publicar sem comando explícito.

## Feature

EX-03 — Self-Test / Auto-diagnóstico

## Prioridade

P1

## Contexto

No dogfood conversacional, a instalação contém `SOUL.md` com `self_test: 5/5 checkpoints OK`, mas o onboarding segue pendente e `MEMORY.md` não contém o log estruturado esperado pela própria skill.

## Comportamento esperado

O self-test deve declarar o estado real e separar:

- skill instalada;
- configuração presente;
- comportamento validado por smoke real.

## Comportamento observado

A verificação honesta produziu score aproximado 2/5:

- Identity: onboarding pendente.
- Memory: sem logs P0-P6/timestamps no formato esperado.
- Skills: OK.
- Tools: OK.
- Behavior: não verificado por smoke runtime naquele teste.

## Impacto

O sistema pode reportar prontidão falsa e mascarar regressões de harness.

## Critérios de aceite

- [ ] Self-test calcula score a partir de evidência real.
- [ ] `SOUL.md` não declara 5/5 quando Macroverso está pendente.
- [ ] Smoke comportamental tem estado próprio: OK/FAIL/NOT_RUN.
- [ ] Harness determinístico falha quando score declarado diverge da verificação.
