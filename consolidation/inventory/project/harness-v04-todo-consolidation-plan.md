# Harness v0.4 TODO Consolidation Implementation Plan

> **For Hermes:** This is a planning artifact only. Do not edit official Acervo files until the executive approves the proposed decisions below.

**Goal:** Convert the `//TODO` comments added in `exocortex.saas/temp/*.md.md` into a coherent update plan for the official Harness Exocórtex v0.4 documentation in the Acervo.

**Architecture:** The temporary files are annotated copies of official Markdown docs. The official files live under `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/`. Apply accepted changes to the official files, not to `temp/`. Comments that imply new concepts should be resolved across all affected docs to keep the ontology consistent.

**Tech Stack:** Markdown documentation, Acervo v2 microversos, Hermes skills, optional future scripts/cron/kanban.

---

## Source scan

Scanned directory:

`/home/elder/projetos/pessoal/exocortex.saas/temp/`

Files with TODOs:

- `01-principios-e-ontologia.md.md` — 2 TODOs
- `03-entidades-filesystem.md.md` — 4 TODOs
- `04-artefatos-avaliacao-publicacao.md.md` — 4 TODOs + 1 `//Add` decision note
- `05-personas-vetores-automacoes.md.md` — 3 TODOs
- `06-templates.md.md` — 1 TODO

File without TODO:

- `Product_Canvas_Sistema_Inteligente_PreVenda.md.md`

Canonical official target directory:

`/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/`

---

## Executive decisions needed before editing

### Decision A — Rename `Atividade` to `Rotina`?

Source TODOs:

- `01-principios-e-ontologia.md.md:91`
- `01-principios-e-ontologia.md.md:92`

Comment:

> atividade pode confundir com “faça atividade sobre assunto...”. Pensar outro substantivo. Pensei em rotina. Automação: rotina.

Recommendation:

Use **Rotina** as the canonical noun for the maintenance unit previously called Atividade.

Rationale:

- The user is right: “atividade” can mean school/classroom exercise, generic work item, or maintenance action.
- “Rotina” naturally suggests programmable, recurring or operational care.
- It pairs well with Manutenção and Síndico/Zelador.
- It avoids competing with Tarefa, which is user-intention-driven.

Proposed vocabulary:

- **Tarefa** = intention of the user persisted from Canvas.
- **Rotina** = maintenance/zeladoria procedure, recurring or triggerable, sometimes intangible.
- **Automação** = trigger/scheduler/event mechanism that invokes a Rotina or Persona.

Important nuance:

Do not collapse Automação into Rotina. A Rotina is the work/procedure; Automação is the trigger. However, the docs can state that an automação usually points to a rotina.

If approved, rename across official docs:

- `Atividade` → `Rotina` when referring to the maintenance entity.
- `_activities/` → `_routines/`.
- `activity_id` → `routine_id`.
- `activity.yaml` → `routine.yaml`.
- `act_*` examples → `rtn_*` or `routine_*`.

Open question:

Should the filesystem be renamed now from `_activities` to `_routines`, or should docs use “Rotina” conceptually while keeping `_activities` for backwards compatibility? My recommendation: rename now because this is still v0.4 design documentation, not a deployed stable API.

---

### Decision B — Add `Cientista` persona?

Source TODO:

- `04-artefatos-avaliacao-publicacao.md.md:105`

Comment:

> Add 'cientista' para verificação de consistência, de alucinações, fatos não verificados, inconsistências metodológicas e desvios cognitivos. Faz peer review.

Recommendation:

Accept and add **Cientista** as a formal evaluator persona.

Proposed definition:

**Cientista**: faz peer review epistemológico. Verifica fatos, alucinações, consistência metodológica, evidência, causalidade, vieses cognitivos, inferências não sustentadas e saltos argumentativos.

Distinction from Auditor:

- Auditor: checks traceability, receipts, hashes, requirements, format and operational evidence.
- Cientista: checks epistemic validity, evidence quality, methodology and claims.

Distinction from Crítico:

- Crítico: adversarial broad critique, risks and fragile assumptions.
- Cientista: evidence/method/claim verification.

No blocker; this is a clean addition.

---

### Decision C — Add `Skill Janitor` persona or role?

Source TODO:

- `05-personas-vetores-automacoes.md.md:110`

Comment:

> add skill-janitor para ser chamado para consertar skills. Deve ser craque em como fazer e avaliar skills eficazes e eficientes.

Recommendation:

Accept concept, but name it in Portuguese as **Zelador de Skills** rather than `skill-janitor` in the user-facing ontology.

Proposed definition:

**Zelador de Skills**: avalia, corrige, consolida, arquiva e melhora skills. Deve conhecer autoria de skills, frontmatter, gatilhos, pitfalls, verificação, escopo, anti-slop e eficiência de uso de contexto.

Where it belongs:

- As a Persona under Personas.
- Also as a maintenance routine target: `routine_skill_curator`.
- Potentially later as a Hermes skill named `exocortex-skill-janitor` or `skill-janitor`.

Possible issue:

Hermes already has a Curator system for skill lifecycle. The docs should explicitly distinguish:

- Hermes Curator: background lifecycle/archive telemetry.
- Zelador de Skills: Exocórtex persona/protocol for qualitative skill repair and evaluation.

No blocker; wording should prevent duplication/confusion.

---

## Planned official file changes

### Task 1: Update ontology and canonical vocabulary

**Objective:** Replace the ambiguous `Atividade` entity with `Rotina` and preserve Automação as trigger.

**Files:**

- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/README.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/01-principios-e-ontologia.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/03-entidades-filesystem.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/05-personas-vetores-automacoes.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/06-templates.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/07-roadmap-e-pendencias.md`
- Modify: `/home/elder/.hermes/acervo/micro/hermes-setup/workflows/exocortex-harness-v0.4-setup-plan.md`

**Planned content changes:**

1. In README, change the thesis bullets:

```md
- **Rotina** é o cuidado programável do sistema.
- **Automação** é o gatilho que aciona rotinas/personas.
```

2. Update the canonical phrase:

```md
... Rotinas mantêm o sistema saudável; Microversos preservam contexto; Automação aciona Personas e Rotinas para cuidar do que não deve depender da lembrança do usuário.
```

3. Update consolidated decisions:

```md
5. Definir Rotina como ação de manutenção/zeladoria, programável, recorrente, acionável por gatilho ou intangível.
```

4. In `01-principios-e-ontologia.md`, replace the ontology table row:

```md
| Rotina | Procedimento de manutenção/zeladoria, programável ou acionável por gatilho | `acervo/_routines/{routine_id}/` quando recorrente/auditável |
| Automação | Gatilho/scheduler/evento que aciona rotina/persona | `acervo/_automations/{automation_id}.yaml` |
```

5. Add a short clarification section:

```md
### Rotina vs Automação

Rotina é o procedimento de cuidado. Automação é o mecanismo que dispara a rotina. Exemplo: “revisar decisões pendentes” é rotina; “todo domingo às 18h” é automação.
```

6. Rename filesystem examples:

```text
_routines/
└── {routine_id}/
    ├── routine.yaml
    ├── state.json
    └── log.md
```

7. Rename template `activity.yaml` to `routine.yaml`.

8. Update setup plan directory creation from `_activities` to `_routines`.

**Verification:**

Run after edits:

```bash
rg "Atividade|atividade_id|activity_id|_activities|activity.yaml|act_" /home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4 /home/elder/.hermes/acervo/micro/hermes-setup/workflows/exocortex-harness-v0.4-setup-plan.md
```

Expected: either no hits, or only historical notes explicitly explaining the rename.

---

### Task 2: Specify `global/` structure and Wiki mode as architectural candidates

**Objective:** Convert TODOs about `global` and Wiki mode into an explicit section without overcommitting.

**Source TODOs:**

- `03-entidades-filesystem.md.md:94`
- `03-entidades-filesystem.md.md:95`

**Files:**

- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/03-entidades-filesystem.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/07-roadmap-e-pendencias.md`

**Planned content changes:**

Add after the top-level filesystem tree:

```md
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
```

Add to roadmap pending decisions:

```md
- Decidir política de adoção do modo Wiki em `global/wiki/` e `micro/{slug}/wiki/`.
- Validar se `global/` deve espelhar integralmente a gramática de microversos ou ter subconjunto próprio.
```

**Question:**

Should `wiki/` be created now in the canonical filesystem tree, or listed only as a candidate? Recommendation: candidate for now.

---

### Task 3: Define Kanban as HITL exposure layer for maintenance recommendations

**Objective:** Formalize how maintenance routines expose recommendations requiring approval.

**Source TODO:**

- `03-entidades-filesystem.md.md:181`

**Files:**

- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/03-entidades-filesystem.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/05-personas-vetores-automacoes.md`
- Modify: `/home/elder/.hermes/acervo/micro/hermes-setup/workflows/exocortex-harness-v0.4-setup-plan.md`

**Planned content changes:**

Add under Rotinas:

```md
### Recomendações HITL e Kanban

Rotinas de Manutenção não devem executar automaticamente ações sensíveis. Quando uma rotina encontrar uma ação que depende de aprovação humana, ela pode criar uma recomendação estruturada.

Destino preferencial para recomendações acionáveis: Kanban nativo do Hermes, quando disponível.

Exemplos:

- “Arquivar tarefa parada há 60 dias” → card aguardando aprovação.
- “Publicar redundância no Drive” → card com contexto e destino sugerido.
- “Consolidar skill duplicada” → card para Zelador de Skills.
- “Resolver decisão pendente” → card para Arquiteto/Crítico/usuário.

A interface do usuário deve mostrar essas recomendações como fila de decisões, não como execução concluída.
```

Add to setup plan:

```md
- Integrar rotinas de manutenção ao Kanban para recomendações HITL, sem execução automática de ações sensíveis.
```

**No blocker.** This aligns with Hermes native Kanban and Draft-First.

---

### Task 4: Add script-generated views and low-token operations

**Objective:** Document that views/indices should be generated by scripts from metadata, not by LLM reasoning every time.

**Source TODOs:**

- `03-entidades-filesystem.md.md:213`
- `04-artefatos-avaliacao-publicacao.md.md:207`

**Files:**

- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/03-entidades-filesystem.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/04-artefatos-avaliacao-publicacao.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/07-roadmap-e-pendencias.md`
- Modify: `/home/elder/.hermes/acervo/micro/hermes-setup/workflows/exocortex-harness-v0.4-setup-plan.md`

**Planned content changes:**

Add under Views:

```md
### Views geradas por script

Views e índices derivados devem ser gerados por scripts persistentes que leem manifests/metadados e materializam symlinks, índices Markdown ou JSON registries. Isso evita gasto recorrente de LLM para operações determinísticas.

Scripts candidatos:

- `generate_artifact_views.py`
- `rebuild_task_links.py`
- `validate_manifest_registry.py`
- `sindico_scan.py`
```

Add to artifact/quality section:

```md
### Operações determinísticas sem LLM

Sempre que possível, tarefas de consolidação do harness devem ser movidas para scripts de skill ou ferramentas locais:

- validar JSON/YAML/frontmatter;
- calcular hashes e tamanhos;
- gerar views por microverso/tarefa/status;
- detectar artefatos sem receipt;
- detectar tarefas sem próximo passo;
- comparar hash de Canvas/tarefa para evitar retrabalho;
- listar decisões pendentes;
- montar ZIP/export.

O LLM deve ser reservado para interpretação, avaliação, síntese, decisão e redação.
```

Add setup scripts:

- `generate_artifact_views.py`
- `scan_maintenance_recommendations.py`
- `compute_task_state_hash.py`

**No blocker.** This is strongly aligned with cost reduction and reliability.

---

### Task 5: Update Quality Gate to use existing skills today

**Objective:** Replace generic Quality Gate wording with current skill-aware checks.

**Source TODO:**

- `04-artefatos-avaliacao-publicacao.md.md:57`

**Files:**

- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/04-artefatos-avaliacao-publicacao.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/07-roadmap-e-pendencias.md`

**Planned content changes:**

Add under Quality Gate:

```md
Skills existentes a aplicar conforme o tipo de artefato:

- `exocortex-output-quality-gate`: gate geral de completude e aderência.
- `exocortex-draft-first`: bloqueio/aprovação para ação externa.
- `stop-slop`: prosa final sem vícios de escrita artificial.
- `personal-artifact-workspace`: pacote, manifesto, exports, receipts e publicação.
- `exocortex-canvas`: Canvas, vetor, tarefa dominante e avaliação requerida.
- `acervo-manager`: persistência correta no Acervo.
- `google-workspace`: publicação privada Drive/Gmail quando aprovada.
- `taste-skill` / `exocortex-design-system`: artefatos visuais quando aplicável.
- `powerpoint`, `exocortex-slides`, `ocr-and-documents`, etc.: conforme mídia/domínio.
```

Add rule:

```md
O Quality Gate deve carregar/aplicar skills existentes antes de inventar procedimento novo.
```

**No blocker.** Good operationalization.

---

### Task 6: Add email as explicit publication/delivery option

**Objective:** Make email delivery first-class while preserving Draft-First.

**Source TODO:**

- `04-artefatos-avaliacao-publicacao.md.md:215`

**Files:**

- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/04-artefatos-avaliacao-publicacao.md`
- Modify: `/home/elder/.hermes/acervo/micro/hermes-setup/workflows/exocortex-harness-v0.4-setup-plan.md`

**Planned content changes:**

Update publication question:

```md
> Quer que eu publique ou entregue este artefato? Posso publicar no Drive privado, gerar ZIP local, preparar email com links/anexos, manter apenas local ou arquivar.
```

Add rules:

```md
- email é opção de entrega, mas sempre comunicação externa;
- email deve ser apresentado como DRAFT antes de envio;
- padrão preferido: publicar no Drive privado, verificar links e preparar email com links;
- anexos diretos podem ser usados quando suportados pelo backend e aprovados pelo usuário;
- receipt deve registrar Drive file IDs e, quando enviado, Gmail message/thread ID.
```

**No blocker.** Already consistent with personal-artifact-workspace.

---

### Task 7: Expand Evolução to include learning and microverso promotion

**Objective:** Clarify Evolução as knowledge evolution, not only “thinking better”.

**Source TODOs:**

- `05-personas-vetores-automacoes.md.md:32`
- `05-personas-vetores-automacoes.md.md:42`

**Files:**

- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/05-personas-vetores-automacoes.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/02-protocolo-cognitivo-canvas.md`

**Planned content changes:**

Change orienting question:

```md
Pergunta orientadora: “Como pensar melhor, aprender melhor e evoluir conhecimento?”
```

Add behavior:

```md
- identificar conhecimento promovível para microversos;
- separar do Canvas da sessão o que deve virar contexto durável;
- sugerir promoção para `micro/{slug}/knowledge`, `context`, `decisions` ou `reflections`;
- preservar lacunas e hipóteses como material de evolução futura.
```

Add to Canvas fields:

```yaml
promotion_candidates:
  microverso_context: []
  knowledge: []
  decisions: []
  reflections: []
  skills: []
```

**No blocker.** This is conceptually important and should be accepted.

---

### Task 8: Add state-cycle/hash fields to task/canvas templates to avoid maintenance retrabalho

**Objective:** Let Síndico/Rotinas skip unchanged tasks and avoid repeated reviews.

**Source TODO:**

- `06-templates.md.md:128`

**Files:**

- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/06-templates.md`
- Modify: `/home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4/03-entidades-filesystem.md`
- Modify: `/home/elder/.hermes/acervo/micro/hermes-setup/workflows/exocortex-harness-v0.4-setup-plan.md`

**Planned content changes:**

Add to `task.yaml` template:

```yaml
state_cycle:
  lifecycle_state: implicit|candidate|registered|active|blocked|ready|completed|maintained|archived
  maintenance_state: never_reviewed|reviewed|needs_attention|ignored_until_change|archived
  content_hash: null
  last_reviewed_hash: null
  last_reviewed_at: null
  last_user_touch_at: null
  last_user_touch_session_id: null
  skip_maintenance_if_hash_unchanged: true
```

Add rule:

```md
Rotinas de manutenção devem comparar `content_hash` com `last_reviewed_hash`. Se a tarefa está arquivada/revisada e o hash não mudou, a rotina deve ficar silenciosa.
```

Hash input recommendation:

Hash should include stable task state, canvas summary, decisions, artifacts and next_moves, but exclude volatile logs/timestamps.

**Question:**

Use session hash or task-content hash? Recommendation: task-content hash. Session IDs are useful for provenance, but content hash is better for “anything changed?” checks.

---

### Task 9: Update setup plan scripts and acceptance criteria

**Objective:** Make the setup plan reflect all accepted vocabulary and deterministic scripts.

**Files:**

- Modify: `/home/elder/.hermes/acervo/micro/hermes-setup/workflows/exocortex-harness-v0.4-setup-plan.md`

**Planned content changes:**

Update script list:

```text
register_task_from_canvas.py
init_artifact_package.py
validate_artifact_manifest.py
run_persona_evaluation.py
generate_artifact_views.py
compute_task_state_hash.py
scan_maintenance_recommendations.py
sindico_maintenance_report.py
```

Update directories:

```bash
mkdir -p "$ACERVO/_routines" ...
```

Update acceptance criteria:

- Rotinas exist as maintenance procedures.
- Automations trigger routines/personas.
- Deterministic views are script-generated.
- Kanban can receive HITL maintenance recommendations.
- Task hash prevents repeated maintenance reports.

---

## Implementation order after approval

1. Decide `Atividade` vs `Rotina` and `_activities` vs `_routines`.
2. Decide whether `wiki/` is candidate only or should enter the canonical tree now.
3. Patch official docs in this order:
   - `01-principios-e-ontologia.md`
   - `README.md`
   - `03-entidades-filesystem.md`
   - `04-artefatos-avaliacao-publicacao.md`
   - `05-personas-vetores-automacoes.md`
   - `06-templates.md`
   - `07-roadmap-e-pendencias.md`
   - `micro/hermes-setup/workflows/exocortex-harness-v0.4-setup-plan.md`
4. Run consistency search:

```bash
rg "Atividade|atividade|_activities|activity_id|activity.yaml|act_" /home/elder/.hermes/acervo/micro/harness-project/knowledge/exocortex-harness-v0.4 /home/elder/.hermes/acervo/micro/hermes-setup/workflows/exocortex-harness-v0.4-setup-plan.md
```

5. Verify frontmatter still present in all Markdown files.
6. Update log files for `harness-project` and `hermes-setup`.
7. Rebuild ZIP artifact and optionally republish to Drive if user requests.

---

## Summary of doubts to ask the executive

1. Should `Atividade` become **Rotina** everywhere, including filesystem path `_routines/`?
2. Should `wiki/` enter the canonical filesystem now, or remain a candidate/pendência?
3. For task maintenance skipping, approve **task-content hash** as primary mechanism instead of session hash?
4. Should `Zelador de Skills` be a persona only for now, or should we also plan a real Hermes skill named `skill-janitor` / `exocortex-skill-janitor`?

My default recommendations are:

1. Yes, rename to Rotina and `_routines/` now.
2. Keep Wiki as candidate for now, not canonical tree yet.
3. Use task-content hash; record session ID only as provenance.
4. Add persona now; create actual skill later after first real skill-maintenance workflow.
