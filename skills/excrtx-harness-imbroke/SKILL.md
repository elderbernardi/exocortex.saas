---
name: excrtx-harness-imbroke
description: 'Gerencia o modo imbroke do Exocórtex: seleção determinística de modelos
  gratuitos, conversão de intelligence index para escala 1-10, sistema de warnings
  e formatação de resposta transparente. 100% determinístico, sem uso de LLM.

  '
version: 1.0.0
category: excrtx
platforms:
- linux
triggers:
- imbroke
- modo imbroke
- classificar modelo 1-10
- rating de modelo gratuito
- /xc imbroke
tags:
- exocortex
- openrouter
- imbroke
- deterministic
- rating
- warnings
metadata:
  hermes:
    tags:
    - exocortex
    - harness
    - imbroke
    calibration:
    - feature_id: EX-48
      calibration_prompt: 'Quando o modo ''imbroke'' for ativado pelo executivo (ou
        por erro de pagamento detectado), você deve agir estritamente por meio do
        script determinístico ''scripts/openrouter_free_model_router.py''.

        - NUNCA use o LLM para adivinhar, classificar ou formatar informações do modo
        imbroke.

        - O script faz a seleção com base em benchmarks reais (escala 1-10) e configura
        o Hermes automaticamente.

        - Copie e apresente exatamente o resultado retornado pelo script, preservando
        o warning contextual de segurança correspondente ao rating (🟢 OK, 🟡 ALERTA
        ou 🔴 PERIGO).

        - Lembre o executivo que a mudança exige reiniciar a sessão com ''/new''.'
      test_prompt: Qual o status do modo imbroke e qual o rating de capacidade do
        modelo atual?
      acceptance_criteria: O agente deve executar o script 'python3 scripts/openrouter_free_model_router.py
        --status' e reportar estritamente o output do script, exibindo o rating 1-10
        e warnings de capacidade sem alucinar.
      remediation_tip: 'Erro de Harness: Modo imbroke é 100% determinístico. Você
        deve ler e reportar o output bruto do script de roteamento sem reformular
        com LLM.'
---
# excrtx-harness-imbroke

## ⚡ Instruções para o Agente (OBRIGATÓRIO)

**TODAS as ações são executadas via script Python determinístico.**
**NÃO use `hermes config set` manualmente. NÃO tente formatar saída com LLM.**

O script fica em: `scripts/openrouter_free_model_router.py` (relativo ao workdir do exocortex.saas).

### Quando o executivo pedir para ATIVAR imbroke:

```bash
cd /home/elder/projetos/projetob/exocortex.saas && python3 scripts/openrouter_free_model_router.py --imbroke --activate
```

**O que o script faz automaticamente:**
- Consulta APIs (OpenRouter + fox benchmarks)
- Seleciona o melhor modelo gratuito por rating
- Configura `model.provider`, `model.default` e `fallback_providers` no Hermes
- Inicia watchdog cron para auto-desativação se provider mudar
- Retorna output formatado com rating, warnings, e status

**Copie a saída do script para o executivo. Não reformate.**

### Quando o executivo pedir para DESATIVAR imbroke:

```bash
cd /home/elder/projetos/projetob/exocortex.saas && python3 scripts/openrouter_free_model_router.py --deactivate
```

### Quando o executivo pedir STATUS:

```bash
cd /home/elder/projetos/projetob/exocortex.saas && python3 scripts/openrouter_free_model_router.py --status
```

### Quando o executivo pedir para VER o ranking (sem ativar):

```bash
cd /home/elder/projetos/projetob/exocortex.saas && python3 scripts/openrouter_free_model_router.py --format text
```

### IMPORTANTE: A troca de modelo exige nova sessão

Após ativar ou desativar, avise o executivo:
> "A troca de modelo exige uma nova sessão do Hermes (`/new`). Esta sessão continua com o modelo anterior."

---

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
                     ↓
Fallback chain → fallback_providers configurado no Hermes para failover nativo
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

- `scripts/openrouter_free_model_router.py` — Script principal de seleção e circuit breaker
- `skills/excrtx-harness-imbroke/SKILL.md` — Skill original do modo imbroke
- `~/.hermes/model-routing/openrouter-free-models.json` — Cache de modelos
- `~/.hermes/model-routing/imbroke-state.json` — Sentinel de estado (circuit breaker)

## Circuit Breaker (Auto-Failover)

Quando um modelo gratuito falha em runtime (rate limit, timeout, API error),
o failover acontece em **duas camadas**:

### Camada 1: Fallback nativo do Hermes (intra-sessão)

Ao ativar o imbroke, o script configura `fallback_providers` no `config.yaml`
com TODOS os modelos do ranking (exceto o primário). O Hermes usa essa lista
nativamente via `try_activate_fallback()`:

```
kimi-k2.6:free (primário) → falha
  → gpt-oss-120b:free (fallback 1) → falha
    → nemotron-3-super-120b (fallback 2) → OK ✅
```

**Este é o mecanismo que age dentro da sessão ativa.**
Não requer nenhum script externo — o Hermes faz sozinho.

### Camada 2: Circuit breaker persistente (cross-sessão)

Para persistir estado entre sessões (ex: modelo continua falhando após restart):

1. **Sentinel** — `imbroke-state.json` controla ativação/desativação
2. **Failover** — `--mark-failed` registra falha e ativa próximo elegível
3. **Cron Recovery** — Após cooldown (30 min default), reavalia modelo
4. **Guard Tripwire** — Watchdog detecta se provider mudou externamente

### Guard Tripwire (Auto-desativação)

Se o executivo ou outro agente trocar o provider externamente:
```bash
hermes config set model.provider openai
# → Watchdog detecta em ≤5min e auto-desativa imbroke
```

O guard NÃO restaura a config anterior (a troca foi intencional).
Ele apenas limpa o sentinel e os crons.

### Overhead quando inativo

**Zero.** Sem sentinel = sem crons = sem processos periódicos.

### CLI Completa

| Flag | Ação |
|---|---|
| `--imbroke --activate` | Ativa modo com circuit breaker |
| `--deactivate` | Desativa e restaura config anterior |
| `--status` | Mostra estado atual |
| `--mark-failed <id>` | Registra falha e failover |
| `--fail-reason <r>` | Motivo da falha |
| `--cooldown <seg>` | Override do cooldown (default: 1800) |
| `--recover` | Reavalia (chamado pelo cron) |
| `--guard` | Verifica provider (chamado pelo watchdog) |

## Checklist de Implementação

- [x] `compute_rating()` implementado em `openrouter_free_model_router.py`
- [x] `get_warning()` implementado
- [x] `format_response()` implementado
- [x] Script retorna rating 1-10 na saída `--format text`
- [x] Warnings exibidos conforme faixas
- [x] Circuit breaker: sentinel, failover, recovery, guard
- [x] Testes automatizados (22 testes)
- [x] Documentado em `skills/excrtx-harness-imbroke/SKILL.md`

## References

- `references/algorithms.md` — Algoritmos detalhados de rating, warnings e circuit breaker
- Issue #48: [Feature][EX-48] Modo imbroke: classificar modelos 1-10 com transparência
- Benchmark source: fox-in-the-box-ai/hermes-best-models
- OpenRouter catalog: https://openrouter.ai/api/v1/models

## When to Use

Activate when working with this skill's domain. See procedure for details.

**Don't use for:** Unrelated domains or when a more specialized skill exists.

## Procedure

Follow the steps and rules defined in this skill's body sections above.

## Verification

- [ ] Skill trigger conditions were correctly matched
- [ ] Output follows the skill's defined format and rules
- [ ] No governance violations occurred
