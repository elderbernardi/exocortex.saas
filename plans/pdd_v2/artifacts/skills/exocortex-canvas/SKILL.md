---
name: exocortex-canvas
description: Extrai estrutura implícita do input do executivo — foco, lacunas, persona sugerida e tipo de ação. Canvas Cognitivo para cada interação.
version: 1.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, behavior, canvas, parsing, intent]
---

# Canvas Cognitivo — Extrator de Ponteiros

> Todo input do executivo carrega informação implícita. O Canvas extrai essa estrutura para que outras skills operem com contexto rico.

## Trigger

Ativar em inputs complexos (mais de uma frase, ou que envolvam múltiplos domínios). Para inputs simples e diretos ("me dê o status de X"), o Canvas é opcional.

## Procedure

### 1. Parsing Silencioso

Para cada input complexo, extrair internamente:

| Campo | Pergunta | Exemplo |
|---|---|---|
| `intent_focus` | O que o executivo quer resolver? | "Renegociar contrato com Cliente Alfa" |
| `gaps` | Que informações estão faltando para agir? | "Não sei o histórico de renovações anteriores" |
| `suggested_persona` | Qual microverso ativar? | "cliente-alfa" (se existir no acervo) |
| `action_type` | Execução ou Evolução? (via `exocortex-vetor-ativo`) | "evolução" |
| `urgency` | Há pressão de tempo? | "reunião amanhã" → alta |
| `dependencies` | O output depende de algo externo? | "Preciso dos dados financeiros antes" |

### 2. Uso do Canvas

O Canvas NÃO é apresentado ao executivo (a menos que ele peça). Ele serve para:

1. **Alimentar o `exocortex-vetor-ativo`** com `action_type`
2. **Ativar o microverso correto** via `suggested_persona`
3. **Buscar no acervo** as informações que preencham os `gaps`
4. **Priorizar** com base em `urgency`
5. **Alertar sobre `dependencies`** que bloqueiam a ação

### 3. Quando Expor o Canvas

Expor o Canvas ao executivo quando:
- O input é tão ambíguo que o agente não consegue agir sem confirmação
- Há gaps críticos que só o executivo pode preencher
- O Canvas revela conflito entre microversos (ex: o que é bom para Cliente Alfa prejudica Projeto Beta)

Formato de exposição:
```markdown
🧠 **Canvas Cognitivo**
┌─────────────────────────────────────
│ Foco: {intent_focus}
│ Microverso: {suggested_persona}
│ Vetor: {action_type}
│ 
│ ⚠ Lacunas:
│   • {gap_1}
│   • {gap_2}
│ 
│ 🔗 Dependências:
│   • {dep_1}
└─────────────────────────────────────
```

### 4. Multi-microverso

Quando o input envolve múltiplos domínios:
1. Identificar todos os microversos relevantes
2. Buscar informações em cada um (respeitando scope/firewall)
3. Consolidar no Canvas com referência cruzada
4. Se houver conflito de interesses, alertar o executivo

## Regras

- Canvas é ferramenta interna por default — expor só quando necessário
- Nunca inventar informações para preencher gaps — marcar como "desconhecido"
- Atualizar o Canvas se o executivo fornecer informações novas durante a conversa
- O Canvas persiste durante a conversa, não entre sessões (a menos que salvo no acervo)

## Verificação

- [ ] Input complexo gera Canvas com pelo menos 4 campos preenchidos
- [ ] Microverso sugerido corresponde ao domínio do input
- [ ] Gaps são identificados corretamente (não fabricados)
- [ ] Canvas é exposto quando input é ambíguo
- [ ] Multi-microverso funciona com referência cruzada
