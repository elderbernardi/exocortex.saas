---
title: Harness Exocórtex v0.4 — Protocolo Cognitivo e Canvas
created: 2026-06-02
updated: 2026-06-02
nature: conhecimento
kind: concept
scope_mode: micro
scope_slug: harness-project
applies_to: [hermes-setup, acervo-cognitivo, exocortex-saas]
authority: canonical
operational_mode: advisory
stability: experimental
sources:
  - conversa executiva 2026-06-02 sobre harness Exocórtex/Hermes
derived_from: []
confidence: high
promotion_policy: candidate-shared
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
tags: ["exocortex", "harness", "architecture", "v0.4"]
---

# 2. Protocolo cognitivo e Canvas

## 2.1 Ideia central

O protocolo cognitivo do Exocórtex é operacionalizado pelo Canvas.

O Canvas pode ser implícito ou explícito:

- **Implícito**: usado internamente para respostas simples ou execução direta.
- **Explícito**: mostrado quando há ambiguidade, risco, múltiplos microversos, criação de tarefa/artefato, decisão arquitetural ou pedido do usuário.

## 2.2 Fluxo mínimo

```text
input do usuário
→ construir Canvas
→ identificar tarefa latente/dominante
→ classificar vetor
→ resolver contexto
→ escolher persona/modo
→ agir, perguntar ou persistir
→ aplicar Quality Gate
→ aplicar Avaliação quando relevante
→ responder ou entregar
```

## 2.3 Campos do Canvas

```yaml
canvas_id: canvas_YYYYMMDD_HHMMSS_slug
focus: "O que está sendo resolvido"
original_input_summary: "Resumo do input que gerou o Canvas"
vector: evolucao|execucao|manutencao
intent_type: explorar|decidir|produzir|revisar|manter|publicar|ingestao|outro

user_intention:
  explicit: "O que o usuário pediu literalmente"
  inferred: "O que o Exocórtex inferiu como intenção operacional"
  confidence: high|medium|low

dominant_entity:
  type: task|artifact|microverso|decision|routine|inbox|none
  id: null
  inferred: true|false

task_candidate:
  title: "Título candidato"
  persist: true|false
  reason: "Por que deve ou não persistir"

microversos:
  primary: null
  related: []

artifacts:
  existing: []
  expected: []

decisions:
  pending: []
  touched: []
  resolved: []

personas:
  suggested: []
  explicit: []
  evaluators: []

gaps: []
dependencies: []
risks: []

promotion_candidates:
  microverso_context: []
  knowledge: []
  decisions: []
  reflections: []
  skills: []

approval:
  required: false
  reason: null

evaluation:
  required: false
  reason: null
  evaluator_personas: []
  apply_mode: suggest|auto-incorporate|ask-user

next_moves: []
```

## 2.4 Quando persistir uma tarefa

Persistir tarefa quando pelo menos um destes critérios for verdadeiro:

- cruza turnos ou sessões;
- envolve artefato;
- envolve múltiplos microversos;
- envolve decisão pendente;
- demanda manutenção futura;
- exige automação ou rotina recorrente;
- tem entrega verificável;
- foi explicitamente pedido pelo usuário;
- o Canvas indica que a intenção precisa ser retomável.

Não persistir tarefa para:

- perguntas simples;
- resposta factual curta;
- microexecução sem memória futura;
- brainstorming descartável;
- correção local de texto sem continuidade.

## 2.5 Estados da tarefa

```text
implicit → candidate → registered → active → blocked → ready → completed → maintained → archived
```

- **implicit**: existe apenas no Canvas da conversa.
- **candidate**: reconhecida, mas ainda não persistida.
- **registered**: criada em `_tasks/`.
- **active**: possui próximos passos.
- **blocked**: depende de decisão, dado, aprovação ou recurso.
- **ready**: entrega pronta para avaliação/aprovação/publicação.
- **completed**: intenção atendida.
- **maintained**: continua sob rotinas de manutenção.
- **archived**: encerrada historicamente.

## 2.6 Canvas e avaliação

O Canvas pode marcar `evaluation.required: true` quando a tarefa tem potencial de impacto, publicação, ensino, decisão arquitetural, entrega institucional ou melhoria deliberada.

Critérios típicos:

- artefato final;
- entrega para terceiros;
- material didático;
- documento estratégico;
- decisão arquitetural;
- tarefa multi-microverso;
- texto público/institucional;
- pedido explícito de melhoria/revisão;
- risco de qualidade ou ambiguidade.

## 2.7 Canvas explícito

Mostrar o Canvas explicitamente quando:

- o usuário pedir;
- há ambiguidade que muda ação;
- será criada tarefa persistente;
- será criado artefato persistente;
- há múltiplos microversos;
- há decisão pendente;
- há ação externa;
- há risco de escopo.

Formato curto para conversa:

```text
Canvas
- Foco:
- Vetor:
- Tarefa dominante:
- Microversos:
- Lacunas:
- Persona sugerida:
- Avaliação:
- Próximo movimento:
```

## 2.8 Safety e aprovação

O Canvas deve indicar aprovação quando a ação envolve:

- comunicação em nome do usuário;
- envio externo;
- compartilhamento público;
- publicação em site/repositório/release;
- alteração irreversível;
- decisão sensível;
- exposição de informação privada.

Regra: ação externa sempre DRAFT antes.


## 2.8 Promoção para microversos

Em Evolução, o Canvas deve identificar material que merece sair da sessão e virar contexto durável. A promoção não deve ser automática quando houver ambiguidade de escopo; o Exocórtex deve sugerir destino.

Candidatos típicos:

- contexto estável para `micro/{slug}/context/`;
- conhecimento consolidado para `micro/{slug}/knowledge/`;
- decisões resolvidas ou pendentes para `micro/{slug}/decisions/`;
- reflexões úteis para `micro/{slug}/reflections/`;
- procedimentos recorrentes para skills ou workflows.
