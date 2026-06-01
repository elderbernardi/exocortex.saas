
# Acervo Cognitivo — Exocórtex.IA

O Acervo é a memória canônica do Exocórtex. Ele guarda identidade, conhecimento, contratos, workflows, ferramentas e reflexões. Áreas operacionais ficam ao lado, não misturadas.

## Estrutura macro

```text
acervo/
├── macro/        # identidade do Exocórtex
├── global/       # operação universal
├── micro/        # domínios isolados
├── shared/       # referências cruzadas controladas
├── _inbox/       # intake operacional de arquivos e mídias
└── _artifacts/   # saídas finais, exports e receipts
```

## Regra estrutural

- `macro/`, `global/`, `micro/` e `shared/` compõem o Acervo semântico.
- `_inbox/` guarda bruto, extrações e roteamento de entrada.
- `_artifacts/` guarda fontes, assets, exports, manifestos e receipts de saída.
- `_inbox/` e `_artifacts/` não substituem a ontologia do Acervo; apenas evitam que bruto ou binário final poluam páginas semânticas.

## Gramática operacional

```text
input -> _inbox -> acervo semântico -> _artifacts -> publish
```

## Regras fundamentais

1. Upload bruto nunca entra direto em páginas semânticas.
2. Promoção para `knowledge/`, `contracts/`, `context/`, `decisions/` ou outros diretórios funcionais exige triagem.
3. Saídas finais para consumo humano passam por `_artifacts/`.
4. O original sempre é preservado quando houver ingestão ou publicação.
