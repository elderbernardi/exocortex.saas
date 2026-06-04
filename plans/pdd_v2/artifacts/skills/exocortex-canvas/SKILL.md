---
name: exocortex-canvas
description: Extrai estrutura implícita do input do executivo — foco, lacunas, persona sugerida e tipo de ação. Canvas Cognitivo para cada interação. Harness v0.4.
version: 2.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, behavior, canvas, parsing, intent, v0.4]
---

# Canvas Cognitivo — Extrator de Ponteiros (v0.4)

> Todo input do executivo carrega informação implícita. O Canvas extrai essa estrutura para que outras skills operem com contexto rico.

## Trigger

Ativar em inputs complexos (mais de uma frase, ou que envolvam múltiplos domínios). Para inputs simples e diretos ("me dê o status de X"), o Canvas é opcional.

## Procedure

### 1. Parsing Silencioso

Para cada input complexo, extrair internamente:

| Campo | Pergunta | Exemplo |
|---|---|---|
| `focus` | O que o executivo quer resolver? | "Renegociar contrato com Cliente Alfa" |
| `intent_type` | explorar, decidir, produzir, revisar, manter, publicar, outro? | "produzir" |
| `user_intention.explicit` | O que foi dito literalmente? | "Preciso do relatório final" |
| `user_intention.inferred` | O que provavelmente quer mas não disse? | "Quer publicar no Drive" |
| `user_intention.confidence` | Quão segura é a inferência? | high / medium / low |
| `dominant_entity` | Que entidade central domina? | task / artifact / microverso / decision / routine / inbox / none |
| `gaps` | Que informações estão faltando para agir? | "Não sei o histórico de renovações anteriores" |
| `microversos.primary` | Qual microverso ativar? | "cliente-alfa" (se existir no acervo) |
| `microversos.related` | Outros microversos envolvidos? | ["financeiro", "juridico"] |
| `urgency` | Há pressão de tempo? | "reunião amanhã" → alta |
| `dependencies` | O output depende de algo externo? | "Preciso dos dados financeiros antes" |
| `risks` | Riscos identificados? | "Deadline pode ser irrealista" |

### 2. Campos v0.4 Avançados

Campos adicionais para interação com o harness:

| Campo | Quando Preencher | Exemplo |
|---|---|---|
| `task_candidate.title` | Quando o input parece gerar tarefa persistível | "Relatório Q2 para diretoria" |
| `task_candidate.persist` | Se o Exocórtex recomenda criar tarefa em _tasks/ | true / false |
| `artifacts.expected` | Quando artefatos serão produzidos | ["relatorio-q2.pdf"] |
| `evaluation.required` | Se o artefato precisa de avaliação por persona | true / false |
| `evaluation.evaluator_personas` | Quais personas devem avaliar | ["critico", "professor"] |
| `evaluation.apply_mode` | Como aplicar sugestões | suggest / auto-incorporate / ask-user |
| `promotion_candidates` | Conhecimento que deve ser promovido ao Acervo | ["decisão X para micro/harness-project/decisions"] |

### 3. Uso do Canvas

O Canvas NÃO é apresentado ao executivo (a menos que ele peça). Ele serve para:

1. **Alimentar o `exocortex-vetor-ativo`** com vetor (evolucao/execucao/manutencao)
2. **Ativar o microverso correto** via `microversos.primary`
3. **Buscar no acervo** as informações que preencham os `gaps`
4. **Priorizar** com base em `urgency`
5. **Alertar sobre `dependencies`** que bloqueiam a ação
6. **Registrar tarefa** quando `task_candidate.persist = true`
7. **Solicitar avaliação** quando `evaluation.required = true`
8. **Promover conhecimento** quando `promotion_candidates` não vazio

### 4. Quando Expor o Canvas

Expor o Canvas ao executivo quando:
- O input é tão ambíguo que o agente não consegue agir sem confirmação
- Há gaps críticos que só o executivo pode preencher
- O Canvas revela conflito entre microversos (ex: o que é bom para Cliente Alfa prejudica Projeto Beta)

Formato de exposição:
```markdown
🧠 **Canvas Cognitivo**
┌─────────────────────────────────────
│ Foco: {focus}
│ Microverso: {microversos.primary}
│ Vetor: {intent_type}
│ Entidade dominante: {dominant_entity}
│ 
│ ⚠ Lacunas:
│   • {gap_1}
│   • {gap_2}
│ 
│ 🔗 Dependências:
│   • {dep_1}
│
│ 📋 Tarefa candidata: {task_candidate.title}
│ 📊 Avaliação: {evaluation.evaluator_personas}
└─────────────────────────────────────
```

### 5. Persistência (canvas.yaml)

Quando `task_candidate.persist = true`, salvar o Canvas como `canvas.yaml` em `_tasks/{task_id}/`:

```bash
python $ACERVO/global/tools/harness/register_task_from_canvas.py \
  --canvas canvas.yaml \
  --title "..." \
  --primary-microverso slug
```

O template canônico está em `$ACERVO/global/templates/harness-v0.4/canvas.yaml`.

### 6. Multi-microverso

Quando o input envolve múltiplos domínios:
1. Identificar todos os microversos relevantes
2. Buscar informações em cada um (respeitando scope/firewall)
3. Consolidar no Canvas com referência cruzada
4. Se houver conflito de interesses, alertar o executivo

## Regras

- Canvas é ferramenta interna por default — expor só quando necessário
- Nunca inventar informações para preencher gaps — marcar como "desconhecido"
- Atualizar o Canvas se o executivo fornecer informações novas durante a conversa
- O Canvas persiste durante a conversa; pode ser salvo como canvas.yaml em _tasks/ quando gera tarefa

## Verificação

- [ ] Input complexo gera Canvas com pelo menos 4 campos preenchidos
- [ ] Microverso sugerido corresponde ao domínio do input
- [ ] Gaps são identificados corretamente (não fabricados)
- [ ] Canvas é exposto quando input é ambíguo
- [ ] Multi-microverso funciona com referência cruzada
- [ ] Campos v0.4 (evaluation, promotion_candidates) são preenchidos quando aplicável
- [ ] task_candidate.persist = true gera registro em _tasks/

