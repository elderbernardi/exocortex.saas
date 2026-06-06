# DRAFT Issue — Acervo diverge entre contrato de boot, seed e template de microverso

## Features

EX-11, EX-13, EX-14

## Prioridade

P1

## Problemas observados

1. `global/index.md` não existe após setup temporário, embora EX-11/Acervo Manager indique leitura desse índice no boot.
2. Template de microverso usa `_meta/SCHEMA.md`, `_meta/index.md`, `_meta/log.md`.
3. FEATURES/smoke esperam `SCHEMA.md`, `index.md`, `log.md` na raiz do microverso.
4. `exocortex-ops` segue a estrutura `_meta/`, não a estrutura raiz esperada por parte da documentação.

## Impacto

Agentes podem procurar arquivos canônicos no lugar errado e o harness pode aprovar uma estrutura incompatível com o contrato.

## Critérios de aceite

- [ ] Definir canonicamente se `SCHEMA/index/log` ficam na raiz ou em `_meta/`.
- [ ] Atualizar FEATURES.md, templates, setup e skills para o mesmo contrato.
- [ ] Criar `global/index.md` ou corrigir o boot para o índice real.
- [ ] Harness valida os paths canônicos escolhidos.
