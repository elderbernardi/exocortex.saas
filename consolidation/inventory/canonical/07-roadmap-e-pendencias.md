---
title: Harness Exocórtex v0.4 — Roadmap e Pendências
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

# 7. Roadmap, pendências e critérios de aceite

## 7.1 Objetivo da implementação

Consolidar no Hermes um harness Exocórtex que:

- classifique inputs por vetor;
- abstraia intenções em Canvas;
- persista tarefas quando necessário;
- centralize artefatos finais;
- aplique Quality Gate;
- aplique Avaliação por Personas;
- pergunte publicação quando artefato estiver pronto/aprovado;
- permita manutenção por rotinas e automações;
- preserve Acervo v2 como fonte canônica.

## 7.2 Fases

### Fase 1 — Documentação e contratos

- Registrar arquitetura v0.4 no microverso `harness-project`.
- Registrar plano de setup em `hermes-setup`.
- Atualizar índices e logs.
- Criar templates iniciais.

### Fase 2 — Estruturas operacionais

- Criar `_tasks/`, `_routines/`, `_automations/`, `_inbox/` e `_artifacts/items/` se ausentes.
- Definir permissões e políticas de escrita.
- Criar views derivadas sem tratá-las como canônicas.

### Fase 3 — Ferramentas mínimas

- Criar ferramenta/script para registrar tarefa a partir de Canvas.
- Criar ferramenta/script para inicializar artifact package.
- Criar ferramenta/script para validar manifest.
- Criar ferramenta/script para gerar pareceres de avaliação.

### Fase 4 — Integração com Hermes

- Ajustar skills comportamentais: Canvas, Vetor, Draft-First, Quality Gate.
- Criar skill/protocolo `exocortex-harness-v0.4`.
- Definir prompts de personas.
- Integrar cron para rotinas de manutenção e Kanban para recomendações HITL.

### Fase 5 — Publicação e receipts

- Manter publicação expressa no Drive.
- Criar gatilho opcional para redundância Drive após aprovação.
- Não sincronizar `_artifacts` inteiro.
- Permitir `_inbox` compartilhado.

## 7.3 Pendências arquiteturais

1. Como resolver ownership operacional de artefatos multi-microverso.
2. Quando promover avaliação de personas para etapa obrigatória global.
3. Como materializar personas locais de microverso.
4. Política de adoção do modo Wiki em `global/wiki/` e `micro/{slug}/wiki/`.
5. Se `global/` deve espelhar integralmente a gramática de microversos ou ter subconjunto próprio.
6. Quando criar uma skill real `exocortex-skill-janitor` a partir da persona Zelador de Skills.
7. Como criar views derivadas sem quebrar em ambientes sem symlink.
8. Como registrar eventos sem inflar contexto normal.
9. Quando e como habilitar sync mais profundo com Drive, se algum dia.

## 7.4 Critérios de aceite

- Um input complexo gera Canvas explícito ou implícito coerente.
- Uma intenção persistível vira tarefa com `task.yaml` e `canvas.yaml`.
- Um artefato final tem package em `_artifacts/items/{artifact_id}`.
- Manifesto liga artefato a tarefa e microversos por metadados.
- Friendly filenames aparecem nos exports para o usuário.
- Quality Gate ocorre antes de ready.
- Avaliação por personas ocorre quando Canvas exigir.
- Artefato ready/approved dispara pergunta de publicação.
- Publicação externa exige Draft-First.
- Drive permanece publicação expressa, não sync total.
- Inbox é separado e pode ser compartilhado.

## 7.5 Métricas de saúde

- Tarefas ativas sem próximo passo.
- Decisões pendentes por microverso.
- Artefatos sem receipt.
- Artefatos ready não publicados nem arquivados.
- Inbox não triado por mais de N dias.
- Skills criadas/atualizadas a partir de tarefas complexas.
- Pareceres incorporados vs ignorados.

## 7.6 Próxima ação recomendada

Implementar v0.4 como skill/protocolo e scripts mínimos:

1. `register_task_from_canvas.py`
2. `init_artifact_package.py`
3. `validate_artifact_manifest.py`
4. `run_persona_evaluation.py`
5. `generate_artifact_views.py`
6. `compute_task_state_hash.py`
7. `scan_maintenance_recommendations.py`
8. `sindico_maintenance_report.py`

Sem automatizar demais antes de observar uso real.


## Scripts candidatos para reduzir custo com LLM

- `generate_artifact_views.py`
- `rebuild_task_links.py`
- `validate_manifest_registry.py`
- `scan_maintenance_recommendations.py`
- `compute_task_state_hash.py`
- `sindico_maintenance_report.py`

Esses scripts devem cuidar de operações determinísticas: validação, hashes, índices, views, detecção de pendências e geração de recomendações estruturadas.
