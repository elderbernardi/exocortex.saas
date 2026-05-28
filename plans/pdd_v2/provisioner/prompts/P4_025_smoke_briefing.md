---
phase: P4
sequence: 25
name: smoke_briefing_cross
depends_on: P4_024
exit_criteria:
  - "Briefing gerado com dados de >= 2 microversos"
  - "Output passa stop-slop"
verify_command: null
---

SMOKE TEST: Briefing Cross-Microverso — Briefing consolida dados de múltiplos microversos.

Pré-requisito: Pelo menos 2 microversos populados com artefatos.

1. Ativar exocortex-briefing
2. Esperado: Briefing estruturado com:
   - Status de cada microverso ativo
   - Tarefas pendentes (se houver)
   - Insights ou conexões cross-domain
3. Verificar: output passa pelo stop-slop

Critério: Briefing gerado com dados de ≥ 2 microversos + quality gate.
