---
phase: P3
sequence: 14
name: vetor_ativo
depends_on: P3_013
exit_criteria:
  - "skill exocortex-vetor-ativo instalada"
  - "Input exploratório → perfil evol"
  - "Input executivo → perfil exec"
verify_command: "hermes skills list | grep -q vetor-ativo"
---

Instale a skill exocortex-vetor-ativo.

Comportamento: Classifica input como Evolução ou Execução, ajusta postura.

Smoke test:
- Input "explique recursão" → perfil `evol` (socrático)
- Input "escreva relatório" → perfil `exec` (agente especialista)
