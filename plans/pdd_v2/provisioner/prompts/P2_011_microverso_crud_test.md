---
phase: P2
sequence: 11
name: microverso_crud_test
depends_on: P2_010
exit_criteria:
  - "7/7 passos do CRUD passam"
verify_command: null
---

Execute o teste completo de Microverso CRUD:

1. CREATE: exocortex-new-microverso "smoke-test-micro"
2. WRITE: Criar artefato de cada Nature (7 artefatos) dentro do microverso
3. READ: Ler cada artefato pelo path
4. SEARCH: Buscar por Nature "conhecimento" — deve retornar artefato correto
5. PROMOTE: Mover 1 artefato para global/
6. SCOPE: Verificar que o artefato saiu do micro e está no global
7. DELETE: Remover o microverso de teste

Todos os passos devem funcionar. Registrar resultado no session log.
