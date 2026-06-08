# Algoritmos de Rating e Warnings — Modo Imbroke

Detalhamento técnico dos algoritmos para classificação determinística de modelos gratuitos.

## 1. Conversão de Intelligence Index para Escala 1-10

### Algoritmo Principal

```python
def compute_rating(intelligence_index, secondary_index):
    """
    Converte intelligence/secondary index para escala 1-10.
    
    Prioridade:
    1. intelligence_index (fox benchmark) — mais preciso
    2. secondary_index (openrouter catalog) — fallback
    3. 1.0 — fallback mínimo
    
    Args:
        intelligence_index: float 0-100 ou None
        secondary_index: float 0-100 ou None
    
    Returns:
        float: Rating 1.0-10.0
    """
    if intelligence_index is not None:
        return round(intelligence_index / 10, 1)
    elif secondary_index is not None:
        return round(secondary_index / 10, 1)
    else:
        return 1.0
```

### Exemplos de Conversão

| Modelo | Intelligence | Secondary | Rating Final |
|--------|-------------|-----------|--------------|
| moonshotai/kimi-k2.6:free | 92.335 | — | **9.2** |
| openai/gpt-oss-120b:free | 84.14 | — | **8.4** |
| nvidia/nemotron-3-super-120b-a12b:free | 78.615 | — | **7.9** |
| qwen/qwen3-coder:free | None | 92.319 | **9.2** |
| poolside/laguna-m.1:free | None | 51.739 | **5.2** |
| meta-llama/llama-3.2-3b-instruct:free | None | 17.722 | **1.8** |

## 2. Sistema de Warnings

### Algoritmo de Classificação

```python
def get_warning(rating):
    """
    Retorna tupla (emoji, status, mensagem) baseada no rating.
    
    Faixas:
    - ≥ 8: 🟢 OK — Modelo bom
    - 5 a 7.9: 🟡 ALERTA — Possível quebra de regras
    - < 5: 🔴 PERIGO — Baixa capacidade
    
    Args:
        rating: float 1.0-10.0
    
    Returns:
        tuple: (emoji, status, mensagem)
    """
    if rating >= 8:
        return (
            '🟢',
            '[OK]',
            'Aproveite, bom modelo gratuito ativo!'
        )
    elif rating >= 5:
        return (
            '🟡',
            '[ALERTA]',
            'Cuidado: este modelo pode ignorar algumas regras e '
            'alucinar eventualmente. Revise outputs críticos.'
        )
    else:
        return (
            '🔴',
            '[PERIGO]',
            'Modelo de baixa capacidade. Recomenda-se revisar tudo '
            'e avaliar resultados com cautela.\n'
            '🔴 [PERIGO] Cuidado com operações que resultem em '
            'alteração no sistema.'
        )
```

### Justificativa das Faixas

**≥ 8 (Bom modelo):**
- Inteligência próxima dos melhores modelos pagos
- Confiável para maioria das tarefas
- Exemplo: `moonshotai/kimi-k2.6:free` (9.2)

**5 a 7.9 (Uso com ressalvas):**
- Capacidade média, pode quebrar instruções complexas
- Alucinações ocasionais possíveis
- Requer revisão humana em outputs críticos
- Exemplo: `nvidia/nemotron-3-super-120b-a12b:free` (7.9)

**< 5 (Baixa capacidade):**
- Modelo básico, não confiável para tarefas complexas
- Alto risco de alucinações
- NÃO usar para alterações no sistema
- Exemplo: `meta-llama/llama-3.2-3b-instruct:free` (1.8)

## 3. Formatação de Resposta

### Template de Saída

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

### Exemplo de Saída (Rating 9.2)

```
Modelo selecionado: moonshotai/kimi-k2.6:free
✅ Gratuito (custo zero)
✅ Classificação: 9.2/10 (baseado em benchmarks globais)
📊 Fonte: fox

🟢 [OK] Aproveite, bom modelo gratuito ativo!
```

### Exemplo de Saída (Rating 7.9)

```
Modelo selecionado: nvidia/nemotron-3-super-120b-a12b:free
✅ Gratuito (custo zero)
✅ Classificação: 7.9/10 (baseado em benchmarks globais)
📊 Fonte: fox

🟡 [ALERTA] Cuidado: este modelo pode ignorar algumas regras e alucinar eventualmente. Revise outputs críticos.
```

### Exemplo de Saída (Rating 1.8)

```
Modelo selecionado: meta-llama/llama-3.2-3b-instruct:free
✅ Gratuito (custo zero)
✅ Classificação: 1.8/10 (baseado em benchmarks globais)
📊 Fonte: openrouter_catalog

🔴 [PERIGO] Modelo de baixa capacidade. Recomenda-se revisar tudo e avaliar resultados com cautela.
🔴 [PERIGO] Cuidado com operações que resultem em alteração no sistema.
```

## 4. Ordem de Execução (Pipeline Determinístico)

```python
def select_and_format_model():
    """
    Pipeline completo: seleção + rating + warning + formatação.
    """
    # 1. Seleção determinística (sem LLM)
    model = select_free_model()  # openrouter_free_model_router.py
    
    # 2. Extrair dados
    model_id = model['id']
    intelligence = model.get('intelligence')
    secondary = model.get('secondary')
    source = 'fox' if intelligence is not None else 'openrouter_catalog'
    
    # 3. Conversão para escala 1-10
    rating = compute_rating(intelligence, secondary)
    
    # 4. Gerar warning
    warning = get_warning(rating)
    
    # 5. Formatar resposta (determinístico)
    response = format_response(model_id, rating, source, warning)
    
    return response
```

## 5. Pitfalls Descobertos nesta Sessão

### ⚠️ NUNCA use LLM para apresentação

**Erro cometido:** Sugeri usar LLM para "formatar resposta com transparência".

**Correção:** O usuário explicitamente disse:
> "Não. O script `openrouter_free_model_router.py` é **determinístico**"
> "Atualize a issue para ser 100% **deterministico** o processo."

**Lição:** Apresentação = formatação de strings, NUNCA chamada a LLM.

### ⚠️ Priorize intelligence sobre secondary

**Contexto:** O script já prioriza `intelligence` (benchmarks reais), mas a documentação não deixava claro.

**Solução:** Adicionado ao SKILL.md a ordem de prioridade explícita.

## 6. Circuit Breaker — Algoritmos

### select_with_failover()

Seleciona o melhor modelo disponível, pulando modelos em estado de falha.

```python
def select_with_failover(ranked, failed_models):
    """
    Percorre ranking ordenado e retorna o primeiro modelo que:
    - NÃO está em failed_models, OU
    - Está em failed_models mas cooldown_until < now
    
    Se TODOS falharam:
    - Retorna o modelo cujo cooldown_until é o mais próximo de expirar
      (mais provável de ter se recuperado)
    """
    for model in ranked:
        if is_model_available(model.id, failed_models):
            return model
    
    # Fallback: cooldown mais próximo de expirar
    return min(ranked, key=lambda m: failed_models[m.id].get("cooldown_until", "9999"))
```

### is_model_available()

```python
def is_model_available(model_id, failed_models):
    """
    True se:
    - model_id não está em failed_models, OU
    - now >= cooldown_until (cooldown expirou)
    """
    if model_id not in failed_models:
        return True
    deadline = parse_iso(failed_models[model_id]["cooldown_until"])
    return now >= deadline
```

### guard_check()

```python
def guard_check():
    """
    1. Lê model.provider via hermes config get
    2. Se provider != "openrouter":
       - Cancela todos os crons (recovery + watchdog)
       - Remove sentinel file
       - Imprime notificação AUTO-OFF
       - Return False (imbroke desligado)
    3. Se provider == "openrouter" ou indeterminado:
       - Return True (imbroke continua ativo)
    
    Chamado por:
    - Watchdog cron (a cada 5 min)
    - Toda operação do circuit breaker (mark-failed, recover)
    """
```

### Transições de Estado

```
INATIVO ──(--activate)──→ ATIVO
  ↑                          │
  │                          ├──(--mark-failed)──→ FAILOVER
  │                          │                        │
  │                          ├──(cron --recover)──────┘
  │                          │
  ├──(--deactivate)──────────┘
  ├──(guard: provider mudou)─┘
```

### Exemplo: Fluxo de Failover Completo

1. **Ativação**: `--imbroke --activate`
   - Sentinel criado com `previous_provider=anthropic`
   - Modelo selecionado: `kimi-k2.6:free` (9.2/10)
   - Watchdog cron iniciado (a cada 5 min)

2. **Falha**: `--mark-failed kimi-k2.6:free --fail-reason rate_limit`
   - `kimi-k2.6:free` adicionado a `failed_models` com `cooldown_until = now + 30min`
   - `select_with_failover()` → `gpt-oss-120b:free` (8.4/10)
   - `hermes config set model.default gpt-oss-120b:free`
   - Recovery cron agendado: `hermes cron create "in 30m"`

3. **Recovery** (30 min depois): `--recover`
   - `kimi-k2.6:free` cooldown expirou → removido de `failed_models`
   - `select_with_failover()` → `kimi-k2.6:free` (9.2/10) — modelo original volta!
   - `hermes config set model.default kimi-k2.6:free`

4. **Guard** (executivo troca provider): `hermes config set model.provider openai`
   - Watchdog detecta: `model.provider = openai ≠ openrouter`
   - Cancela crons, remove sentinel
   - NÃO restaura config (troca foi intencional)

## 7. Relacionado

- **Issue #48:** [Feature][EX-48] Modo imbroke: classificar modelos 1-10 com transparência
- **Script:** `scripts/openrouter_free_model_router.py`
- **Skill original:** `skills/excrtx-harness-imbroke/SKILL.md`
- **Benchmark source:** fox-in-the-box-ai/hermes-best-models
- **Sentinel:** `~/.hermes/model-routing/imbroke-state.json`
