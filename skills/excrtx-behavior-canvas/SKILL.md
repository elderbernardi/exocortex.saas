---
name: excrtx-behavior-canvas
description: Extract implicit structure from executive input — focus, gaps, suggested
  persona, and action type. Cognitive Canvas for each interaction.
version: 2.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - behavior
    - canvas
    - parsing
    - intent
    - v0.4
    related_skills:
    - excrtx-behavior-vetor
    - excrtx-quality-gate
    - excrtx-behavior-briefing
    calibration:
    - feature_id: EX-06
      calibration_prompt: 'Ao receber uma tarefa complexa, aplique a estrutura do
        Canvas Cognitivo. Resolva internamente a tríade: Macroverso (identidade e
        restrições do executivo), Microversos (domínio âncora principal e domínios
        de apoio), e Tarefa (a sala de operação real; lembre-se: microverso NÃO é
        uma sala, a tarefa é a sala). Mapeie os gaps de informação e dependências
        externas. Ao lidar com múltiplos microversos (cross-domain), aplique rigidamente
        as restrições de compartilhamento (sharing constraints) definidas nos microversos,
        aplicando a precedência: ''allow'' sempre sobressai a ''deny''. Se houver
        gaps críticos ou ambiguidade, exiba o bloco ''🧠 Canvas Cognitivo'' com esses
        campos mapeados.'
      test_prompt: 'Cruze os microversos gabinete e juridico para redigir um ofício,
        mas jurídico tem deny: [ALL] e allow: [gabinete].'
      acceptance_criteria: 'O output deve conter um bloco ''🧠 Canvas Cognitivo'' contendo:
        macroverso.status, microverso principal (gabinete), microversos relacionados
        (juridico) e explicitar o sharing constraint com allow > deny.'
      remediation_tip: 'Correção de Harness: Microverso não é sala. A tarefa é a sala.
        Aplique allow > deny nas sharing constraints e apresente o bloco 🧠 Canvas
        Cognitivo estruturado.'
compiled_rules: 'For complex inputs: parse focus, vector, gaps, urgency into a structured
  canvas block before responding.

  Required fields: focus (string), vetor (execucao|evolucao|manutencao|ambiguo), intent_type
  (explorar|decidir|produzir|revisar|manter).

  Optional: macroverso_status, microverso_primary, gaps[], urgency.

  Emit canvas block in trace for auditing. Skip canvas for trivial/simple inputs.'
---
# Canvas Cognitivo — Extrator de Ponteiros (v0.4)

> Todo input do executivo carrega informação implícita. O Canvas extrai essa estrutura para que outras skills operem com contexto rico, ancorando a tarefa no Macroverso e nos Microversos corretos.

## When to Use

Activate on complex inputs (more than one sentence, or involving multiple domains). For simple, direct inputs ("me dê o status de X"), Canvas is optional.

**Don't use for:** Single-word responses, confirmations, or trivial inputs. Morning briefings (use `excrtx-behavior-briefing`). Pure classification without context extraction (use `excrtx-behavior-vetor`).

## Procedure

### 1. Parsing Silencioso

Antes de resumir o pedido, resolver a tríade estrutural:

- **Macroverso** = quem fala e quais limites/valores governam
- **Microversos** = entidades semânticas e operacionais vivas que ancoram e apoiam a tarefa
- **Tarefa** = a sala operacional concreta onde a execução acontece

Microverso não é sala. A tarefa é a sala. O Canvas deve preservar essa distinção.

Para cada input complexo, extrair internamente:

| Campo | Pergunta | Exemplo |
|---|---|---|
| `macroverso.status` | O Macroverso está resolvido, parcial ou placeholder? | `resolved` / `partial` / `placeholder` / `missing` |
| `macroverso.sources` | Em que arquivos o Macroverso foi lido? | `["acervo/macro/SOUL.md"]` |
| `macroverso.constraints` | Que valores, tom ou limites afetam esta tarefa? | `["draft-first", "tom direto"]` |
| `focus` | O que o executivo quer resolver? | "Renegociar contrato com Cliente Alfa" |
| `intent_type` | explorar, decidir, produzir, revisar, manter, publicar, outro? | "produzir" |
| `user_intention.explicit` | O que foi dito literalmente? | "Preciso do relatório final" |
| `user_intention.inferred` | O que provavelmente quer mas não disse? | "Quer publicar no Drive" |
| `user_intention.confidence` | Quão segura é a inferência? | high / medium / low |
| `dominant_entity` | Que entidade central domina? | task / artifact / microverso / decision / routine / inbox / none |
| `gaps` | Que informações estão faltando para agir? | "Não sei o histórico de renovações anteriores" |
| `microversos.status` | O conjunto de microversos foi resolvido ou segue ambíguo? | `resolved` / `ambiguous` / `none` |
| `microversos.primary` | Qual microverso ancora a tarefa? | "cliente-alfa" (se existir no acervo) |
| `microversos.related` | Que microversos apoiam a tarefa? | ["financeiro", "juridico"] |
| `microversos.rationale` | Por que esse arranjo foi escolhido? | "cliente-alfa é o domínio principal; jurídico só valida cláusulas" |
| `microversos.sharing_constraints` | Que restrições de compartilhamento precisam ser respeitadas com base nas regras allow/deny dos microversos? | `["deny: ALL + allow: [microverse_x] => compartilhável só com microverse_x"]` |
| `task.anchor` | Como a tarefa foi ancorada na tríade? | "Ofício ancorado em gabinete, com apoio de jurídico" |
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

1. **Declarar o estado do Macroverso** antes de qualquer inferência substantiva
2. **Ancorar a tarefa** em um microverso principal e zero ou mais secundários
3. **Alimentar o `excrtx-behavior-vetor`** com vetor (evolucao/execucao/manutencao)
4. **Buscar no acervo** as informações que preencham os `gaps`
5. **Priorizar** com base em `urgency`
6. **Alertar sobre `dependencies`** que bloqueiam a ação
7. **Respeitar restrições de compartilhamento** entre microversos em tarefas cross-domain, usando as regras de sharing de cada microverso e a precedência `allow > deny`
8. **Registrar tarefa** quando `task_candidate.persist = true`
9. **Solicitar avaliação** quando `evaluation.required = true`
10. **Promover conhecimento** quando `promotion_candidates` não vazio

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
│ Macroverso: {macroverso.status}
│ Microverso âncora: {microversos.primary}
│ Microversos de apoio: {microversos.related}
│ Tarefa: {task.anchor}
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
1. Identificar o microverso principal que ancora a tarefa
2. Identificar os microversos secundários que só apoiam a tarefa
3. Buscar informações em cada um, respeitando scope/firewall e regras locais de compartilhamento
4. Consolidar no Canvas apenas a interseção útil para a tarefa
5. Se houver conflito de interesses ou de acesso, alertar o executivo

Ao resolver sharing constraints, aplicar a regra de ouro já definida em `shared/knowledge/groups.md`:
- `allow` SEMPRE sobrescreve `deny`
- exemplo: `deny: [ALL]` + `allow: [microverse_x]` significa que o microverso só pode ser compartilhado com `microverse_x`

## Regras

- Canvas é ferramenta interna por default — expor só quando necessário
- Nunca inventar informações para preencher gaps — marcar como "desconhecido"
- Atualizar o Canvas se o executivo fornecer informações novas durante a conversa
- O Canvas persiste durante a conversa; pode ser salvo como canvas.yaml em _tasks/ quando gera tarefa
- Nunca tratar Microverso como sala; a sala é a tarefa
- Em tarefa cross-domain, sempre declarar microverso principal, microversos de apoio e restrições de compartilhamento
- Se `macroverso.status` estiver `placeholder` ou `missing`, declarar isso explicitamente no Canvas

## Pitfalls

- **Canvas overhead on trivial inputs**: Skip canvas for simple/trivial inputs (confirmations, single-word responses). Not every interaction needs a canvas.
- **Fabricated gaps**: Gaps must be identified from the input, not fabricated. Don't invent problems the executive didn't raise.
- **Microverso confusion**: Microverso é entidade semântica, não sala. The task is the operational room. Never treat microverso as a container for the conversation.
- **Cross-domain leak**: In multi-microverso tasks, always declare primary microverso, supporting microversos, and sharing restrictions.
- **Stale canvas**: Update the canvas if the executive provides new information during conversation. Don't freeze it at the first input.

## Verification

- [ ] Input complexo gera Canvas com pelo menos 4 campos preenchidos
- [ ] Macroverso tem status explícito
- [ ] Microverso principal corresponde ao domínio âncora do input
- [ ] Microversos de apoio só entram quando a tarefa exige cruzamento
- [ ] Restrições de compartilhamento foram consideradas em tarefas cross-domain
- [ ] Gaps são identificados corretamente (não fabricados)
- [ ] Canvas é exposto quando input é ambíguo
- [ ] Multi-microverso funciona com referência cruzada
- [ ] Campos v0.4 (evaluation, promotion_candidates) são preenchidos quando aplicável
- [ ] task_candidate.persist = true gera registro em _tasks/

