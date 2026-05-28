---
phase: P3
sequence: 17
name: onboarding
depends_on: P3_016
exit_criteria:
  - "skill exocortex-onboarding instalada"
  - "Entrevista de 3 perguntas → preferências salvas"
verify_command: "hermes skills list | grep -q onboarding"
---

Instale a skill exocortex-onboarding (v1.1).

Comportamento: Entrevista de personalização para instâncias já provisionadas.
Nota v2: Sem auto-provisionamento. O Provisioner é externo.

Smoke test: Simular entrevista de 3 perguntas → preferências salvas.
