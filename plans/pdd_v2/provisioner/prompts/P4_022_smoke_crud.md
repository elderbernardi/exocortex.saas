---
phase: P4
sequence: 22
name: smoke_microverso_crud
depends_on: P3_021
exit_criteria:
  - "8/8 passos do CRUD passam"
verify_command: null
---

SMOKE TEST: Microverso CRUD — Ciclo completo de vida de um microverso.

1. Criar microverso "validation-test" via exocortex-new-microverso
2. WRITE 3 artefatos (Nature: conhecimento, processo, reflexão)
3. READ cada artefato pelo path
4. SEARCH por Nature "conhecimento" — deve retornar apenas o artefato correto
5. PROMOTE o artefato de reflexão para shared/
6. SCOPE micro/validation-test — deve mostrar 2 artefatos (não 3)
7. SCOPE shared — deve mostrar o artefato promovido
8. Deletar microverso "validation-test"

Critério: 8/8 passos passam.
