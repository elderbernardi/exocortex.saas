---
name: excrtx-harness-imbroke
description: >
  Gerencia o modo imbroke do Exocórtex: seleção determinística de modelos gratuitos,
  conversão de intelligence index para escala 1-10, sistema de warnings e
  formatação de resposta transparente. 100% determinístico, sem uso de LLM.
triggers:
  - "imbroke"
  - "modo imbroke"
  - "classificar modelo 1-10"
  - "rating de modelo gratuito"
  - "/xc imbroke"
tags: [exocortex, openrouter, imbroke, deterministic, rating, warnings]
---

# excrtx-harness-imbroke

Use esta skill quando o executivo ativar o modo imbroke ou solicitar classificação
de modelos gratuitos do OpenRouter em escala 1-10.

## Visão Geral

O modo imbroke seleciona modelos gratuitos do OpenRouter de forma **100% determinística**,
sem uso de LLM para apresentação ou seleção.

### Princípios
- ✅ **Determinístico:** Sem chamadas a LLM para apresentação
- ✅ **Transparente:** Usuário vê modelo, rating, fonte
- ✅ **Seguro:** Warnings baseados em faixas de capacidade

## Arquitetura

```
Seleção (sem LLM) → Script Python determinístico (openrouter_free_model_router.py)
                     ↓
Modelo selecionado (ex: moonshotai/kimi-k2.6:free)
                     ↓
Classificação (sem LLM) → Conversão matemática (intelligence/10)
                     ↓
Apresentação (sem LLM) → Formatação determinística + Warnings
```

## Implementação

### 1. Conversão para Escala 1-10

```python
def compute_rating(intelligence_index, secondary_index):
    """
    Converte intelligence/secondary index para escala 1-10.
    
    Args:
        intelligence_index: 0-100 (fox benchmark) ou None
        secondary_index: 0-100 (openrouter catalog) ou None
    
    Returns:
        float: Rating 1.0-10.0
    """
    if intelligence_index is not None:
        return round(intelligence_index / 10, 1)
    elif secondary_index is not None:
        return round(secondary_index / 10, 1)
    else:
        return 1.0  # fallback mínimo
```

**Exemplos:**
- `intelligence=92.335` → `rating=9.2`
- `intelligence=84.14` → `rating=8.4`
- `intelligence=78.615` → `rating=7.9`
- `secondary=92.319` → `rating=9.2`

### 2. Sistema de Warnings

```python
def get_warning(rating):
    """
    Retorna tupla (emoji, status, mensagem) baseada no rating.
    
    Args:
        rating: float 1.0-10.0
    
    Returns:
        tuple: (emoji, status, mensagem)
    """
    if rating >= 8:
        return ('🟢', '[OK]', 'Aproveite, bom modelo gratuito ativo!')
    elif rating >= 5:
        return ('🟡', '[ALERTA]', 
                'Cuidado: este modelo pode ignorar algumas regras e '
                'alucinar eventualmente. Revise outputs críticos.')
    else:
        return ('🔴', '[PERIGO]', 
                'Modelo de baixa capacidade. Recomenda-se revisar tudo '
                'e avaliar resultados com cautela.\n'
                '🔴 [PERIGO] Cuidado com operações que resultem em '
                'alteração no sistema.')
```

**Faixas:**
- **≥ 8:** 🟢 OK — Bom modelo, use livremente
- **5 a 7.9:** 🟡 ALERTA — Pode quebrar regras, revisar outputs
- **< 5:** 🔴 PERIGO — Baixa capacidade, revisar tudo

### 3. Formato de Resposta

```python
def format_response(model_id, rating, source, warning):
    """
    Formata resposta determinística para o usuário.
    
    Args:
        model_id: str (ex: 'moonshotai/kimi-k2.6:free')
        rating: float 1.0-10.0
        source: str ('fox' ou 'openrouter_catalog')
        warning: tuple (emoji, status, mensagem)
    
    Returns:
        str: Resposta formatada
    """
    return f"""Modelo selecionado: {model_id}
✅ Gratuito (custo zero)
✅ Classificação: {rating}/10 (baseado em benchmarks globais)
📊 Fonte: {source}

{warning[0]} {warning[1]} {warning[2]}"""
```

**Exemplo de saída:**
```
Modelo selecionado: moonshotai/kimi-k2.6:free
✅ Gratuito (custo zero)
✅ Classificação: 9.2/10 (baseado em benchmarks globais)
📊 Fonte: fox

🟢 [OK] Aproveite, bom modelo gratuito ativo!
```

## Pitfalls

### ⚠️ NUNCA use LLM para apresentação
O processo deve ser 100% determinístico. Não chame LLM para "formatar resposta"
ou "adicionar transparência". Tudo deve ser feito via código Python determinístico.

**Por que?**
- Performance: Sem latência de LLM
- Custo: Sem tokens desperdiçados
- Confiabilidade: Sem falhas de API
- Auditabilidade: Lógica transparente

### ⚠️ Priorize intelligence sobre secondary
O `intelligence` index vem de benchmarks reais (fox-in-the-box-ai/hermes-best-models).
O `secondary` vem do catálogo OpenRouter (menos preciso).

**Algoritmo de prioridade:**
1. Usa `intelligence` se disponível
2. Senão, usa `secondary`
3. Senão, fallback rating=1.0

### ⚠️ Warnings devem ser contextualizados
Para rating < 5, SEMPRE avise sobre:
- Revisão obrigatória de outputs
- Cuidado com alterações no sistema
- Possível baixa capacidade

## Arquivos Relacionados

- `scripts/openrouter_free_model_router.py` — Script principal de seleção
- `skills/excrtx-harness-imbroke/SKILL.md` — Skill original do modo imbroke
- `~/.hermes/model-routing/openrouter-free-models.json` — Cache de modelos

## Checklist de Implementação

- [ ] `compute_rating()` implementado em `openrouter_free_model_router.py`
- [ ] `get_warning()` implementado
- [ ] `format_response()` implementado
- [ ] Script retorna rating 1-10 na saída `--format text`
- [ ] Warnings exibidos conforme faixas
- [ ] Documentado em `skills/excrtx-harness-imbroke/SKILL.md`
- [ ] Testado com modelos em diferentes faixas

## References

- `references/algorithms.md` — Algoritmos detalhados de rating e warnings, com exemplos e pitfalls da sessão
- Issue #48: [Feature][EX-48] Modo imbroke: classificar modelos 1-10 com transparência
- Benchmark source: fox-in-the-box-ai/hermes-best-models
- OpenRouter catalog: https://openrouter.ai/api/v1/models
