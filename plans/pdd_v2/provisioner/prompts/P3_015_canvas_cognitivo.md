---
phase: P3
sequence: 15
name: canvas_cognitivo
depends_on: P3_014
exit_criteria:
  - "skill exocortex-canvas instalada"
  - "Input complexo → Canvas preenchido com 10 campos"
verify_command: "hermes skills list | grep -q canvas"
---

Instale a skill exocortex-canvas.

Comportamento: Extrai implicitamente intent_focus, gaps, persona de inputs complexos.

Smoke test: Input longo e ambíguo → Canvas preenchido com 10 campos.
