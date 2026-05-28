---
phase: P2
sequence: 12
name: p2_checkpoint
depends_on: P2_011
exit_criteria:
  - "self-test >= 3/5"
  - "7 skills instaladas"
  - "MEMORY.md tem entries para 006-011"
  - "4 camadas populadas"
  - "Configuration State = P3_BEHAVIOR"
verify_command: "hermes skills list | wc -l"
---

Execute o self-test. Resultado esperado: ≥ 3/5.

Drift Audit de P2:
1. Skills instaladas: esperado = 7 (5 de P1 + acervo-manager + new-microverso)
2. setup.sh: reflete as 7 skills + estrutura de 4 camadas?
3. MEMORY.md: entries para prompts 006-011?
4. Acervo: 4 camadas criadas e populadas?

Corrija qualquer drift antes de avançar.
Atualize Configuration State para P3_BEHAVIOR.
