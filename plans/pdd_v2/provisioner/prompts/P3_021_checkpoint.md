---
phase: P3
sequence: 21
name: p3_checkpoint
depends_on: P3_020
exit_criteria:
  - "self-test >= 4/5"
  - "15 skills instaladas"
  - "Bundle + Profiles funcionais"
  - "MEMORY.md entries 013-020"
  - "Configuration State = P4_VALIDATION"
verify_command: "hermes skills list | wc -l"
---

Execute o self-test. Resultado esperado: ≥ 4/5.

Drift Audit de P3:
1. Skills instaladas: esperado = 15 (5 P1 + 2 P2 + 7 P3 + design-system)
2. Bundle `exocortex-alpha` lista = skills instaladas
3. Profiles `exec` e `evol` funcionais
4. setup.sh reflete todas as 15 skills
5. MEMORY.md tem entries para prompts 013-020
6. Configuration State → P4_VALIDATION

Corrija qualquer drift antes de avançar.
