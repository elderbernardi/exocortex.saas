---
title: Harness Exocórtex v0.4 — Templates Canônicos
created: 2026-06-02
updated: 2026-06-02
nature: conhecimento
kind: template
scope_mode: micro
scope_slug: harness-project
applies_to: [hermes-setup, acervo-cognitivo, exocortex-saas]
authority: canonical
operational_mode: template
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

# 6. Templates canônicos v0.4

Este arquivo reúne templates iniciais. Eles devem virar arquivos separados em `global/templates/` ou `micro/harness-project/templates/` quando forem promovidos para uso operacional.

## 6.1 `task.yaml`

```yaml
task_id: task_YYYYMMDD_slug
title: "Título da intenção do usuário"
status: implicit|candidate|registered|active|blocked|ready|completed|maintained|archived
vector: evolucao|execucao|manutencao

primary_microverso: null
related_microversos: []

canvas_path: canvas.yaml

personas:
  owner: arquiteto
  reviewers: []
  evaluators: []

artifacts: []
routines: []
automations: []

decisions:
  pending: []
  resolved: []

inbox_items: []

approval:
  required: false
  reason: null

evaluation:
  required: false
  reason: null
  status: not_applicable|pending|completed|skipped


state_cycle:
  lifecycle_state: implicit|candidate|registered|active|blocked|ready|completed|maintained|archived
  maintenance_state: never_reviewed|reviewed|needs_attention|ignored_until_change|archived
  content_hash: null
  last_reviewed_hash: null
  last_reviewed_at: null
  last_user_touch_at: null
  last_user_touch_session_id: null
  skip_maintenance_if_hash_unchanged: true

created_at: ISO-8601
updated_at: ISO-8601
```

## 6.2 `canvas.yaml`

```yaml
canvas_id: canvas_YYYYMMDD_HHMMSS_slug
focus: ""
original_input_summary: ""
vector: evolucao|execucao|manutencao
intent_type: explorar|decidir|produzir|revisar|manter|publicar|ingestao|outro

user_intention:
  explicit: ""
  inferred: ""
  confidence: high|medium|low

dominant_entity:
  type: task|artifact|microverso|decision|routine|inbox|none
  id: null
  inferred: true

task_candidate:
  title: ""
  persist: false
  reason: ""

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

## 6.3 `routine.yaml`

```yaml
routine_id: rtn_slug
name: "Nome da rotina"
vector: manutencao
status: active|paused|archived
persona: sindico

scope:
  microversos: []
  tasks: []
  artifacts: []

objective: ""
triggers: []
outputs: []

permissions:
  can_modify_acervo: false
  can_create_reports: true
  can_publish: false
  requires_user_approval_for_external_action: true

state_path: state.json
log_path: log.md
created_at: ISO-8601
updated_at: ISO-8601
```

## 6.4 `automation.yaml`

```yaml
automation_id: auto_slug
name: "Nome da automação"
status: active|paused|archived
schedule: "0 18 * * 0"
routine_id: rtn_slug
persona: sindico
prompt: "Prompt autocontido para execução futura"
deliver: origin
requires_approval_for_external_action: true
created_at: ISO-8601
updated_at: ISO-8601
```


## 6.5 Regra de hash para manutenção

Rotinas de manutenção devem comparar `state_cycle.content_hash` com `state_cycle.last_reviewed_hash`. Se a tarefa está revisada/arquivada e o hash não mudou, a rotina deve ficar silenciosa.

O hash deve considerar estado estável da tarefa, resumo do Canvas, decisões, artefatos e próximos movimentos. Deve excluir logs e timestamps voláteis. O ID da sessão deve ser preservado como provenance, não como mecanismo principal de detecção de mudança.

## 6.6 `manifest.json`

```json
{
  "artifact_id": "art_YYYYMMDD_HHMMSS_slug",
  "canonical_slug": "slug",
  "friendly_name": "Nome humano",
  "publication_names": {},
  "title": "Título",
  "status": "draft",
  "artifact_type": "document",
  "source_type": "markdown",
  "task_id": null,
  "primary_microverso": null,
  "related_microversos": [],
  "scope": "micro",
  "owner": {"type": "task", "id": null},
  "personas_involved": [],
  "semantic_links": [],
  "source_path": "source/source.md",
  "exports": [],
  "evaluation": {
    "status": "pending",
    "personas": [],
    "reports": [],
    "incorporated_suggestions": [],
    "pending_suggestions": []
  },
  "publication": {
    "drive": {
      "status": "not_published",
      "receipt_path": null
    }
  },
  "provenance": {
    "created_by": "exocortex",
    "created_at": "ISO-8601",
    "origin": "conversation"
  }
}
```

## 6.7 Parecer de persona

```md
# Parecer — {Persona}

## Síntese

## Pontos fortes

## Fragilidades

## Recomendações prioritárias

## Sugestões opcionais

## Veredito
- aprovar
- aprovar com ajustes
- revisar antes de aprovar
```
