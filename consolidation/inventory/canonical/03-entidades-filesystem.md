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
├── _routines/
│   └── {routine_id}/
│       ├── routine.yaml
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


## 3.2 Global e modo Wiki

`global/` deve seguir a mesma gramática estrutural dos microversos quando armazenar conhecimento canônico transversal, mas com escopo global.

Estrutura candidata:

```text
global/
├── context/
├── knowledge/
├── contracts/
├── prompts/
├── skills/
├── workflows/
├── tools/
├── templates/
├── decisions/
├── reflections/
├── persona/
├── wiki/
├── _meta/
└── _archive/
```

`wiki/` é candidato para conhecimento navegável/interligado em modo wiki dentro de `global/` e, seletivamente, dentro de microversos. O modo Wiki deve ser adotado quando houver rede conceitual estável, glossários, mapas de conceitos ou documentação viva; não deve substituir `knowledge/` para documentos canônicos lineares.

## 3.3 Microversos

Microversos permanecem como fontes canônicas de contexto cognitivo. Eles não devem virar depósitos de todo artefato gerado.

Função:

- preservar contexto;
- armazenar contratos, decisões, reflexões e workflows locais;
- oferecer personas locais;
- manter links semânticos para tarefas e artefatos.

Arquivos recomendados em `_meta/`:

- `artifact-links.md`: índice humano de artefatos relacionados ao microverso;
- `task-links.md`: índice humano de tarefas relacionadas ao microverso.

## 3.4 Tarefas

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
- `links.yaml`: relações com microversos, artefatos, decisões, rotinas, automações.
- `events.log`: trilha append-only.

## 3.5 Artefatos

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

## 3.6 Inbox

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

## 3.7 Rotinas

Rotinas representam manutenção/zeladoria. Nem toda rotina precisa ser persistida.

Persistir rotina quando:

- é recorrente;
- é auditável;
- tem estado;
- afeta múltiplas tarefas/artefatos;
- é acionada por automação;
- pode gerar recomendação ou parecer.

### Recomendações HITL e Kanban

Rotinas de Manutenção não devem executar automaticamente ações sensíveis. Quando uma rotina encontrar uma ação que depende de aprovação humana, ela pode criar uma recomendação estruturada.

Destino preferencial para recomendações acionáveis: Kanban nativo do Hermes, quando disponível.

Exemplos:

- “Arquivar tarefa parada há 60 dias” → card aguardando aprovação.
- “Publicar redundância no Drive” → card com contexto e destino sugerido.
- “Consolidar skill duplicada” → card para Zelador de Skills.
- “Resolver decisão pendente” → card para Arquiteto/Crítico/usuário.

A interface do usuário deve mostrar essas recomendações como fila de decisões, não como execução concluída.

## 3.8 Automação

Automação é gatilho, não trabalho. Ela dispara rotinas/personas.

Exemplo:

```yaml
automation_id: auto_weekly_pending_decisions
trigger: "0 18 * * 0"
routine_id: rtn_review_pending_decisions
persona: sindico
scope:
  microversos: [harness-project, hermes-setup]
action: "revisar decisões pendentes e preparar parecer"
requires_user_approval_for_external_action: true
```

## 3.9 Views e symlinks

Views são derivadas, não canônicas.

Uso recomendado:

```text
_artifacts/views/by_microverso/{slug}/{friendly_name} -> ../../items/{artifact_id}
_artifacts/views/by_task/{task_id}/{friendly_name} -> ../../items/{artifact_id}
```

O nome amigável serve principalmente para filenames entregues ao usuário. Symlinks são conveniência local e não precisam ir para Drive.


### Views geradas por script

Views e índices derivados devem ser gerados por scripts persistentes que leem manifests/metadados e materializam symlinks, índices Markdown ou JSON registries. Isso evita gasto recorrente de LLM para operações determinísticas.

Scripts candidatos:

- `generate_artifact_views.py`
- `rebuild_task_links.py`
- `validate_manifest_registry.py`
- `sindico_scan.py`
