# EX-30 — Contrato de path do wrapper de browser

## Lição durável

A skill de browser automation tem uma interface operacional pública: o wrapper shell. Quando a documentação promete um path e o repositório entrega outro, isso é falha de contrato, não mero detalhe interno.

## Path canônico

```bash
skills/excrtx-integrate-browser/scripts/browser-use.sh
```

## Regra de classificação

1. **Path divergente** entre documentação/probe e arquivo real → `FAIL`
2. **Path alinhado, mas pré-requisito ausente** (ex.: `uv`) → `BLOCKED`
3. **Path alinhado + pré-requisitos presentes** → pode seguir para smoke / `PASS`

## Superfícies que precisam permanecer sincronizadas

- `SKILL.md` (`setup:` e exemplos de uso)
- catálogo de features (`FEATURES.md` ou equivalente)
- probes dogfood / smoke tests
- qualquer wrapper compatível adicional criado no setup

## Receita rápida de auditoria

```bash
# 1. Confirmar script real
 test -x skills/excrtx-integrate-browser/scripts/browser-use.sh

# 2. Confirmar que docs citam o mesmo path
# (ajuste o método de busca ao ambiente)

# 3. Separar contrato de dependência
 command -v uv
```

## Interpretação

Se o script real existe e os docs ainda apontam para outro local, conserte a documentação/probe primeiro. Só depois avalie `uv`, Chromium e smoke end-to-end.
