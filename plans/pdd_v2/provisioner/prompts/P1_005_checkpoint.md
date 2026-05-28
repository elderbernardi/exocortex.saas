---
phase: P1
sequence: 5
name: p1_checkpoint
depends_on: P1_004
exit_criteria:
  - "self-test >= 2/5"
  - "5 skills instaladas"
  - "MEMORY.md tem entries para 001-004"
  - "SOUL.md tem 5 seções + 7 Values"
  - "Configuration State = P2_MEMORY"
verify_command: "hermes skills list | wc -l"
---

Execute o self-test do Exocórtex. O resultado esperado é ≥ 2/5.

Depois, execute o Drift Audit de P1:
1. Quantas skills estão instaladas? (esperado: 5)
2. O setup.sh reflete as 5 skills instaladas?
3. O MEMORY.md tem entries para os prompts 001-004?
4. O SOUL.md tem 5 seções + 7 Values?

Se algum check falhar, corrija antes de avançar.
Se tudo passar, atualize Configuration State para P2_MEMORY.
