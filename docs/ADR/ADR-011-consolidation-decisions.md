# ADR-011 — Decisões Consolidadas do Candidate-Release

## Status

Aceita (candidate-release consolidation, 2026-06-03)

## Contexto

A consolidação do candidate-release levantou 7 decisões (D001-D007) derivadas da comparação entre o Harness v0.4 canônico e o PDD v2 do projeto. Este ADR documenta as resoluções.

## Decisões

### D001 — PDD como Checklist (não Blueprint)

PDD v2 mantido como referência histórica e checklist de validação. Não será atualizado para refletir v0.4 integralmente — isso seria trabalho redundante. Em vez disso, o setup-plan v0.4 e o replicable-setup-workflow cobrem a Camada 1.

### D002 — Rotinas e Automações como Entidades Formais

Criar `_routines/` e `_automations/` no filesystem conforme canônico. A estrutura é leve, não conflita com Hermes, e garante rastreabilidade. Templates `routine.yaml` e `automation.yaml` do harness v0.4 módulo 06 são canônicos.

### D003 — Personas (Professor, Cientista, Zelador de Skills)

Abordagem híbrida:
- Personas documentadas como seções no SOUL.md para referência de identidade
- Pareceres de avaliação usam template canônico do módulo 06
- Script `run_persona_evaluation.py` orquestra a geração de pareceres (pós-release)
- Canvas v0.4 campo `evaluation.evaluator_personas` determina quais personas avaliam
- **Não** criar skills separadas por persona

### D004 — Prioridade Setup-Plan vs PDD v2

Resolvida pelo ADR-010 (layered deployment):
- Camada 1 segue setup-plan + replicable-setup (infraestrutura)
- Camada 2 segue PDD v2 P1 simplificado (identidade)
- Não há conflito de prioridade

### D005 — Scripts Determinísticos

Implementar apenas os 3 críticos para o candidate-release:
1. `register_task_from_canvas.py` — registra tarefa a partir de Canvas
2. `init_artifact_package.py` — inicializa pacote de artefato
3. `validate_artifact_manifest.py` — valida manifest.json

Os outros 5 (`run_persona_evaluation.py`, `generate_artifact_views.py`, `compute_task_state_hash.py`, `scan_maintenance_recommendations.py`, `sindico_maintenance_report.py`) ficam para pós-release.

### D006 — Memória Operacional

Resolvida pelo ADR-010:
- PDD para setup inicial (Camadas 1+2)
- Hindsight/memória para evolução contínua (Camada 3)
- Acervo v2 permanece fonte canônica semântica — memória operacional é complementar

### D007 — Backlog

Adiado para pós-release. Foco no candidate-release.

## Referências

- `plans/candidate-release/DRAFT_CANDIDATE_RELEASE.md`
- `micro/harness-project/knowledge/exocortex-harness-v0.4/` (módulos 01-07)
- `docs/ADR/ADR-010-layered-deployment.md`
