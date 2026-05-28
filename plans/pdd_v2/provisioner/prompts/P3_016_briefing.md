---
phase: P3
sequence: 16
name: morning_briefing
depends_on: P3_015
exit_criteria:
  - "skill exocortex-briefing instalada"
  - "Briefing gerado com dados de >= 2 microversos"
verify_command: "hermes skills list | grep -q briefing"
---

Instale a skill exocortex-briefing.

Comportamento: Coleta cross-microverso + gera briefing estruturado.

Smoke test: Com ≥ 2 microversos populados, gera briefing com dados de ambos.
