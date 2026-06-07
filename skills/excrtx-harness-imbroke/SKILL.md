---
name: excrtx-harness-imbroke
description: >-
  Ativa o modo de contingência de roteamento OpenRouter free quando o executivo usa
  o comando /xc imbroke ou pede explicitamente o fallback de modelos gratuitos.
version: 1.1.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, openrouter, fallback, contingency, imbroke]
---

# Imbroke Mode

Use esta skill quando o executivo disser `/xc imbroke` ou pedir para ativar o modo de contingência de modelos gratuitos.

## Intenção

Este modo existe para cenários de degradação, orçamento travado ou indisponibilidade do modelo principal.
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
   - **classificação 1-10 e warning determinístico** (ver abaixo)

## Transparência e Warnings (Implementado na EX-48)

O modo `imbroke` agora reporta a qualidade do modelo selecionado usando uma escala de 1 a 10 e emite warnings determinísticos de segurança.

### Classificação (1-10)

- **Escala:** 1 (pior) a 10 (melhor)
- **Fonte primária:** `intelligence_index` do benchmark *fox-in-the-box-ai/hermes-best-models* (convertido de 0-100 para 1-10)
- **Fonte secundária:** `secondary_index` do catálogo OpenRouter (quando benchmarks ausentes)
- **Conversão:** `rating = round(intelligence_index / 10, 1)`
- **Determinístico:** Sem uso de LLM ou chamadas externas adicionais

### Sistema de Warnings

O sistema emite alertas baseados na classificação:

- **Rating ≥ 8:**
  - 🟢 `[OK] Aproveite, bom modelo gratuito ativo!`

- **Rating entre 7.9 e 5:**
  - 🟡 `[ALERTA] Cuidado: este modelo pode ignorar algumas regras e alucinar eventualmente. Revise outputs críticos.`

- **Rating < 5:**
  - 🔴 `[PERIGO] Modelo de baixa capacidade. Recomenda-se revisar tudo e avaliar resultados com cautela.`
  - 🔴 `[PERIGO] Cuidado com operações que resultem em alteração no sistema.`

### Formato da Resposta

```
Modelo selecionado: <model_id>
✅ Gratuito (custo zero)
✅ Classificação: <rating>/10 (baseado em benchmarks globais)
📊 Fonte: <fox | openrouter_catalog>

<warning_emoji> [<STATUS>] <mensagem_de_alerta>
```

## Regras

- Nunca tratar o modo imbroke como default.
- `--apply` só deve ocorrer junto de `--imbroke`.
- Manter benchmark Fox como fonte primária.
- Usar a cobertura secundária do catálogo OpenRouter apenas para ordenar modelos `unscored`.
- **Novo:** Apresentar classificação 1-10 e warning em todas as execuções.

## Verificação

- [x] `setup.sh` aceita `--imbroke`
- [x] `/xc imbroke` está documentado como gatilho operacional
- [x] `openrouter_free_model_router.py` rejeita `--apply` sem `--imbroke`
- [x] relatório JSON continua sendo gravado quando aplicável
- [x] **Classificação 1-10 implementada (EX-48)**
- [x] **Sistema de warnings implementado (EX-48)**
- [x] **Resposta formatada com transparência (EX-48)**
