# DRAFT Issue — Design System tem mismatch entre contrato, path real e operações

## Feature

EX-20 — Design System

## Prioridade

P2

## Comportamento observado

O lint real passou com 0 erros, mas o dogfood encontrou divergências:

- Skill/FEATURES esperam `acervo/global/DESIGN.md`.
- Arquivo real está em `acervo/global/_meta/DESIGN.md`.
- FEATURES cita operações CREATE/UPDATE.
- Skill usa operação WRITE.
- Lint emitiu warning: `colors.danger` definido sem referência por componente.

## Impacto

Agentes podem editar ou procurar o Design System no path errado. Operações descritas na documentação não batem com a skill.

## Critérios de aceite

- [ ] Unificar path canônico do Design System.
- [ ] Normalizar nomes de operação: CREATE/UPDATE/WRITE.
- [ ] Resolver ou justificar warning de token não referenciado.
- [ ] Harness valida path + lint real.
