---
phase: P3
sequence: 18
name: output_quality_gate
depends_on: P3_017
exit_criteria:
  - "skill exocortex-output-quality-gate instalada"
  - "Prosa >= 35/50 no stop-slop"
  - "Visual passa pre-flight taste-skill"
verify_command: "hermes skills list | grep -q output-quality-gate"
---

Instale a skill exocortex-output-quality-gate.

Comportamento:
- Para PROSA: aplica stop-slop (scoring ≥ 35/50)
- Para VISUAL: aplica taste-skill (pre-flight check)
- Princípio: o executor corrige seu próprio output (não o orquestrador)

Smoke test:
- Gerar parágrafo → scoring → se < 35, reescrever automaticamente
- Gerar prompt visual → pre-flight → flag de issues
