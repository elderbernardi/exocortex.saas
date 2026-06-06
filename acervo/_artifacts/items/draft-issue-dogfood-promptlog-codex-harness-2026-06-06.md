# DRAFT Issue — Harness infra passa em checks determinísticos sem provar comportamento central

## Features

EX-31, EX-32, EX-33, EX-34

## Prioridade

P1

## Achados

### EX-31

Prompt Log funcionou quando executado manualmente, mas não há prova de automação. Antes do dogfood, `MEMORY.md` não continha entradas estruturadas `[PDD-*]`.

### EX-32 / EX-34

Codex CLI funciona em scratch e auth `openai-codex` existe. Delegação via provider não foi provada de ponta a ponta na subinstância.

### EX-33

Falha funcional: wrapper e diretório de evidências declarados não existem:

- `~/.hermes/scripts/codex_learning/run_codex_with_learning.py`
- `~/.hermes/scripts/codex_learning/review_latest_run.py`
- `~/.hermes/codex-learning/`

Mesmo assim, o harness determinístico marcou EX-33 como PASS.

## Impacto

O sistema aprova features de infraestrutura por presença de skill, mas não valida os artefatos que tornam a feature operacional.

## Critérios de aceite

- [ ] EX-31 tem trigger automático validável ou é rebaixada para procedimento manual.
- [ ] EX-33 instala runner/review/evidence dir ou altera contrato da feature.
- [ ] Harness EX-33 falha quando wrapper não existe.
- [ ] EX-32/EX-34 validam delegação provider ou marcam PARTIAL/BLOCKED com evidência.
