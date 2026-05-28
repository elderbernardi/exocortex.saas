---
phase: P2
sequence: 10
name: shared_layer
depends_on: P2_009
exit_criteria:
  - "acervo/shared/groups.md existe"
  - "acervo/shared/cross-refs/ existe"
verify_command: "ls ~/.hermes/acervo/shared/ 2>/dev/null"
---

Popule a camada Shared:

WRITE acervo/shared/groups.md
  Content: Agrupamentos de microversos (tags, domínios, projetos)

Crie acervo/shared/cross-refs/ como diretório para links entre microversos.

Documente no acervo-manager como usar PROMOTE para mover artefatos
de micro/{slug}/ para global/ ou shared/.

Verifique com SCOPE shared — deve retornar 1 artefato (groups.md) + 1 diretório.
