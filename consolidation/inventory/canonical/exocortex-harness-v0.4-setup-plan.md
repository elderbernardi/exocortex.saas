---
title: Plano de Setup Hermes — Harness Exocórtex v0.4
created: 2026-06-02
updated: 2026-06-02
nature: processos
kind: workflow
scope_mode: micro
scope_slug: hermes-setup
applies_to: [harness-project, acervo-cognitivo, exocortex-saas]
authority: canonical
operational_mode: executable
stability: experimental
sources:
  - micro/harness-project/knowledge/exocortex-harness-v0.4/README.md
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
tags: [exocortex, hermes, setup, harness, canvas, tasks, artifacts, evaluation]
---
# Plano de Setup Hermes — Harness Exocórtex v0.4

> Para Hermes/Exocórtex: este workflow transforma a arquitetura `micro/harness-project/knowledge/exocortex-harness-v0.4/` em trilha de implementação reproduzível.

## Goal

Implantar no Hermes Agent um harness Exocórtex com Canvas persistível, tarefas centralizadas, artefatos centralizados, avaliação por personas, manutenção programável e publicação controlada.

## Arquitetura

O setup preserva o Acervo v2 como fonte canônica semântica e adiciona registros operacionais globais:

```text
acervo/_tasks/
acervo/_routines/
acervo/_automations/
acervo/_inbox/
acervo/_artifacts/items/
acervo/_artifacts/views/
```

Microversos continuam isolados. Relações cruzadas ficam em metadados.

## Pré-requisitos

- Hermes Agent instalado e configurado.
- Perfil Exocórtex ativo.
- Acervo v2 disponível.
- Skills mínimas: `acervo-manager`, `exocortex-canvas`, `exocortex-vetor-ativo`, `personal-artifact-workspace`, `exocortex-output-quality-gate`, `exocortex-draft-first`.

## Etapa 1 — Criar diretórios operacionais

Criar, se ausentes:

```bash
ACERVO="${EXOCORTEX_ACERVO:-${HERMES_HOME:-$HOME/.hermes}/acervo}"
mkdir -p "$ACERVO/_tasks"          "$ACERVO/_routines"          "$ACERVO/_automations"          "$ACERVO/_inbox/incoming"          "$ACERVO/_inbox/processing"          "$ACERVO/_inbox/promoted"          "$ACERVO/_inbox/_archive"          "$ACERVO/_artifacts/items"          "$ACERVO/_artifacts/views/by_microverso"          "$ACERVO/_artifacts/views/by_task"          "$ACERVO/_artifacts/views/by_status"          "$ACERVO/_artifacts/views/by_type"          "$ACERVO/_artifacts/_ops"
```

Verificação:

```bash
test -d "$ACERVO/_tasks" && test -d "$ACERVO/_artifacts/items" && test -d "$ACERVO/_inbox/incoming"
```

## Etapa 2 — Instalar templates

Promover templates de:

- `task.yaml`
- `canvas.yaml`
- `routine.yaml`
- `automation.yaml`
- `manifest.json`
- parecer de persona

Origem inicial:

```text
micro/harness-project/knowledge/exocortex-harness-v0.4/06-templates.md
```

Destino recomendado futuro:

```text
acervo/global/templates/exocortex-harness-v0.4/
```

## Etapa 3 — Atualizar skills comportamentais

Ajustar ou criar skills para refletir v0.4:

1. `exocortex-vetor-ativo`

   - Vetores: Evolução, Execução, Manutenção.
2. `exocortex-canvas`

   - Canvas como abstração da intenção.
   - Tarefa dominante/latente.
   - Campo `evaluation`.
   - Persistência em `canvas.yaml` quando tarefa for registrada.
3. `personal-artifact-workspace`

   - Modelo 2 com `_artifacts/items/`.
   - Inbox separado.
   - Friendly filenames.
   - Avaliação por personas.
   - Pergunta de publicação quando ready/approved.
4. `exocortex-output-quality-gate`

   - Separar Quality Gate de Avaliação.
   - Quality Gate como piso mínimo.
5. Nova skill candidata: `exocortex-harness-v0.4`

   - Procedimento de ponta a ponta.

## Etapa 4 — Criar ferramentas mínimas

Scripts recomendados:

```text
acervo/global/tools/harness/register_task_from_canvas.py
acervo/global/tools/harness/init_artifact_package.py
acervo/global/tools/harness/validate_artifact_manifest.py
acervo/global/tools/harness/run_persona_evaluation.py
acervo/global/tools/harness/generate_artifact_views.py
acervo/global/tools/harness/compute_task_state_hash.py
acervo/global/tools/harness/scan_maintenance_recommendations.py
acervo/global/tools/harness/sindico_maintenance_report.py
```

### `register_task_from_canvas.py`

Entrada:

```bash
python register_task_from_canvas.py --canvas canvas.yaml --title "..." --primary-microverso harness-project
```

Saída:

```text
acervo/_tasks/{task_id}/task.yaml
acervo/_tasks/{task_id}/canvas.yaml
acervo/_tasks/{task_id}/notes.md
acervo/_tasks/{task_id}/links.yaml
acervo/_tasks/{task_id}/events.log
```

### `init_artifact_package.py`

Cria:

```text
_artifacts/items/{artifact_id}/source/
_artifacts/items/{artifact_id}/assets/
_artifacts/items/{artifact_id}/exports/
_artifacts/items/{artifact_id}/evaluations/
_artifacts/items/{artifact_id}/receipts/
_artifacts/items/{artifact_id}/manifest.json
```

### `validate_artifact_manifest.py`

Verifica:

- JSON válido;
- campos obrigatórios;
- source existe;
- exports existem quando status >= ready;
- hashes/tamanhos quando exportado;
- receipt quando status published;
- relação com task/microversos.

### `run_persona_evaluation.py`

Gera pareceres em `evaluations/` usando personas definidas no manifesto ou Canvas.

### `generate_artifact_views.py`

Lê manifests e metadados para gerar views/symlinks/índices derivados sem gastar LLM.

### `compute_task_state_hash.py`

Calcula hash estável da tarefa a partir de `task.yaml`, `canvas.yaml`, decisões, artefatos e próximos movimentos, excluindo logs e timestamps voláteis.

### `scan_maintenance_recommendations.py`

Detecta pendências e gera recomendações estruturadas para Kanban/HITL quando a ação depender de aprovação humana.

### `sindico_maintenance_report.py`

Gera relatório de manutenção:

- tasks sem próximo passo;
- artefatos sem receipt;
- inbox antigo;
- decisões pendentes;
- manifests inválidos;
- links quebrados.

## Etapa 5 — Configurar rotinas e automações

Rotinas iniciais recomendadas:

1. `rtn_weekly_pending_decisions`

   - Persona: Síndico
   - Frequência: semanal
   - Output: relatório de decisões pendentes
2. `rtn_artifact_quality_audit`

   - Persona: Auditor
   - Frequência: semanal
   - Output: artefatos sem receipt/hash/avaliação
3. `rtn_inbox_triage`

   - Persona: Arquivista
   - Frequência: sob demanda ou diária se inbox compartilhado for usadoa
   - Output: sugestões de promoção para tarefa/microverso/artefato
4. `rtn_ready_artifact_publication_prompt`

   - Persona: Operador
   - Gatilho: artefato status `ready|approved`
   - Output: pergunta ao usuário sobre publicação

## Etapa 6 — Política de publicação

Estado v0.4:

- Não sincronizar o Acervo inteiro com Drive.
- Não sincronizar `_artifacts` inteiro.
- `_inbox` pode ser compartilhado/sincronizado.
- Drive é publicação expressa com receipt.
- Futuro: gatilho opcional de redundância Drive quando artefato aprovado/publicado.

## Etapa 7 — Critérios de aceite do setup

- Diretórios operacionais existem.
- Templates estão disponíveis.
- Skills comportamentais reconhecem Canvas/Tarefa/Artefato/Rotina.
- Um Canvas pode gerar uma tarefa persistida.
- Uma tarefa pode gerar artifact package.
- Manifesto valida relações por metadados.
- Avaliação por personas pode gerar pareceres.
- Quality Gate e Avaliação são etapas distintas.
- Artefato ready/approved gera pergunta de publicação.
- Publicação externa segue Draft-First.

## Etapa 8 — Não fazer ainda

- Não automatizar sync completo com Drive.
- Não transformar toda mensagem em tarefa.
- Não exigir avaliação para artefatos descartáveis.
- Não permitir decisão sensível por persona em background.
- Não substituir microversos por tarefas.
- Não mover contexto canônico para `_artifacts`.

## Referência principal

```text
/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/README.md
```

## Critérios adicionais incorporados dos TODOs

- Rotinas existem como procedimentos de manutenção.
- Automações acionam rotinas/personas.
- Views derivadas são geradas por scripts determinísticos.
- Kanban pode receber recomendações HITL de manutenção.
- Hash de conteúdo de tarefa evita relatórios repetidos do Síndico.
- Email é opção de entrega sob Draft-First.
