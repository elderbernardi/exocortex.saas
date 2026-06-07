---
name: excrtx-harness-imbroke
description: >-
  Ativa o modo de contingência de roteamento OpenRouter free quando o executivo usa
  o comando /xc imbroke ou pede explicitamente o fallback de modelos gratuitos.
version: 1.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, openrouter, fallback, contingency, imbroke]
---

# Imbroke Mode

Use esta skill quando o executivo disser `/xc imbroke` ou pedir para ativar o modo de contingência de modelos gratuitos.

## Intenção

Esse modo existe para cenários de degradação, orçamento travado ou indisponibilidade do modelo principal.
Ele **não** deve ser ativado por default.

## Triggers

- `/xc imbroke`
- "ativa o modo imbroke"
- "cai para OpenRouter free"
- "estou sem budget / sem crédito / sem provider"

## Procedure

1. Confirmar que o pedido é de **execução**, não apenas explicação.
2. No repositório `exocortex.saas`, preferir um destes caminhos:
   - setup/provisionamento: `bash setup.sh --imbroke`
   - aplicação direta: `python scripts/openrouter_free_model_router.py --imbroke --apply --format text`
3. Se `OPENROUTER_API_KEY` estiver ausente, ainda é válido rodar:
   - `python scripts/openrouter_free_model_router.py --imbroke --format text`
   Isso gera o ranking e o relatório sem aplicar `model.provider`/`model.default`.
4. Reportar:
   - modelo selecionado
   - cadeia de fallback
   - se a configuração foi aplicada de fato ou apenas gerada como relatório

## Regras

- Nunca tratar o modo imbroke como default.
- `--apply` só deve ocorrer junto de `--imbroke`.
- Manter benchmark Fox como fonte primária.
- Usar a cobertura secundária do catálogo OpenRouter apenas para ordenar modelos `unscored`.

## Verificação

- [ ] `setup.sh` aceita `--imbroke`
- [ ] `/xc imbroke` está documentado como gatilho operacional
- [ ] `openrouter_free_model_router.py` rejeita `--apply` sem `--imbroke`
- [ ] relatório JSON continua sendo gravado quando aplicável
