# Live memory eval — perguntas privadas

Este diretório existe para a trilha **live** da avaliação de memória v2.

## Como usar

1. Copie `questions.template.yaml` para `questions.local.yaml`.
2. Preencha queries, scopes e `expected_paths` reais do seu Acervo.
3. Rode manualmente:

```bash
bash scripts/run-memory-live-eval.sh "$ACERVO" tests/memory-eval/live/questions.local.yaml
```

4. Fora do fixture sintético, o wrapper materializa automaticamente um knowledge canônico em `micro/exocortex-ops/knowledge/` no Acervo alvo.
5. Quando o arquivo `questions.local.yaml` existir, o step 17 do installer passa a criar o cron mensal `memory-eval-live-monthly`.

## Regras

- `questions.local.yaml` é **privado** e fica no `.gitignore`.
- Use apenas paths relativos ao root do Acervo, por exemplo:
  - `micro/comercial/knowledge/preco-tabela-q3.md`
  - `shared/entities/cliente-x.md`
  - `global/decisions/2026-01-15-politica-precos.md`
- A trilha live deve rodar com `--strategies catalog,production`.
  Não use Hindsight aqui sem revisar o banco/escopo de avaliação.

## Saída esperada

O runner grava relatórios em `tests/memory-eval/report/live-YYYY-MM-DD.{md,json}`.
Esses artefatos viram a trilha histórica da avaliação live.
