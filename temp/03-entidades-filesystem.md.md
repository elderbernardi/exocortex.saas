---
title: Harness Exocórtex v0.4 — Entidades e Filesystem
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

# 3. Entidades e filesystem

## 3.1 Estrutura alvo

```text
acervo/
├── macro/
├── global/
├── shared/
├── micro/
│   └── {slug}/
│       ├── context/
│       ├── knowledge/
│       ├── contracts/
│       ├── prompts/
│       ├── skills/
│       ├── workflows/
│       ├── tools/
│       ├── templates/
│       ├── decisions/
│       ├── reflections/
│       ├── persona/
│       ├── _meta/
│       │   ├── artifact-links.md
│       │   └── task-links.md
│       ├── raw/
│       └── _archive/
│
├── _inbox/
│   ├── incoming/
│   ├── processing/
│   ├── promoted/
│   └── _archive/
│
├── _tasks/
│   └── {task_id}/
│       ├── task.yaml
│       ├── canvas.yaml
│       ├── notes.md
│       ├── links.yaml
│       └── events.log
│
├── _activities/
│   └── {activity_id}/
│       ├── activity.yaml
│       ├── state.json
│       └── log.md
│
├── _artifacts/
│   ├── items/
│   │   └── {artifact_id}/
│   │       ├── source/
│   │       ├── assets/
│   │       ├── exports/
│   │       ├── evaluations/
│   │       ├── manifest.json
│   │       └── receipts/
│   ├── views/
│   │   ├── by_microverso/
│   │   ├── by_task/
│   │   ├── by_status/
│   │   └── by_type/
│   └── _ops/
│       ├── events.log
│       └── locks.json
│
└── _automations/
    └── {automation_id}.yaml
```
//TODO especificar global. A princípio igual em estrutura ao microverso. Verificar especificidades.
//TODO avaliar adoção do modo Wiki dentro dos microversos/global
## 3.2 Microversos

Microversos permanecem como fontes canônicas de contexto cognitivo. Eles não devem virar depósitos de todo artefato gerado.

Função:

- preservar contexto;
- armazenar contratos, decisões, reflexões e workflows locais;
- oferecer personas locais;
- manter links semânticos para tarefas e artefatos.

Arquivos recomendados em `_meta/`:

- `artifact-links.md`: índice humano de artefatos relacionados ao microverso;
- `task-links.md`: índice humano de tarefas relacionadas ao microverso.

## 3.3 Tarefas

Tarefas são centralizadas porque podem cruzar microversos.

```text
_tasks/{task_id}/
├── task.yaml
├── canvas.yaml
├── notes.md
├── links.yaml
└── events.log
```

- `task.yaml`: estado operacional.
- `canvas.yaml`: snapshot da intenção original/atualizada.
- `notes.md`: notas narrativas e síntese de evolução.
- `links.yaml`: relações com microversos, artefatos, decisões, atividades, automações.
- `events.log`: trilha append-only.

## 3.4 Artefatos

Artefatos finais são centralizados em `_artifacts/items/`.

Modelo 2 é canônico:

```text
_artifacts/items/{artifact_id}/
├── source/
├── assets/
├── exports/
├── evaluations/
├── manifest.json
└── receipts/
```

O pacote deve ser reprodutível: fonte, assets, exports, hashes, avaliação e receipt.

## 3.5 Inbox

Inbox é separado de artefatos porque entrada bruta não é entrega.

```text
_inbox/
├── incoming/
├── processing/
├── promoted/
└── _archive/
```

- `incoming`: material bruto recém-chegado.
- `processing`: material em triagem.
- `promoted`: material já destinado a tarefa/microverso/artefato.
- `_archive`: descartes ou material histórico sem promoção.

Inbox pode ser compartilhado/sincronizado por natureza. O Acervo inteiro não.

## 3.6 Atividades

Atividades representam manutenção/zeladoria. Nem toda atividade precisa ser persistida.

Persistir atividade quando:

- é recorrente;
- é auditável;
- tem estado;
- afeta múltiplas tarefas/artefatos;
- é acionada por automação;
- pode gerar recomendação ou parecer.

//TODO considerar opção de usar o kanban nativo para inserir as ações recomendadas pela manutenção que dependem de aprovação hitl. Pensar em como expor isso em interface pro usuário.

## 3.7 Automação

Automação é gatilho, não trabalho. Ela dispara atividades/personas.

Exemplo:

```yaml
automation_id: auto_weekly_pending_decisions
trigger: "0 18 * * 0"
activity_id: act_review_pending_decisions
persona: sindico
scope:
  microversos: [harness-project, hermes-setup]
action: "revisar decisões pendentes e preparar parecer"
requires_user_approval_for_external_action: true
```

## 3.8 Views e symlinks

Views são derivadas, não canônicas.

Uso recomendado:

```text
_artifacts/views/by_microverso/{slug}/{friendly_name} -> ../../items/{artifact_id}
_artifacts/views/by_task/{task_id}/{friendly_name} -> ../../items/{artifact_id}
```

O nome amigável serve principalmente para filenames entregues ao usuário. Symlinks são conveniência local e não precisam ir para Drive.

//TODO isso pode ser feito por script persisnte que consulta os meta dados e gera viu sem gastar token.