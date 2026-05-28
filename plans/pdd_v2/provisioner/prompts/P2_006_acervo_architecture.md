---
phase: P2
sequence: 6
name: acervo_architecture
depends_on: P1_005
exit_criteria:
  - "hermes skills list mostra acervo-manager"
  - "4 diretórios de camada existem"
verify_command: "ls -d ~/.hermes/acervo/{macro,global,micro,shared} 2>/dev/null | wc -l"
---

Instale o acervo-manager a partir do artefato fornecido em `skills/exocortex/acervo-manager/SKILL.md`.

O acervo-manager é a skill ÚNICA de gestão de memória. Ele suporta:
- READ: buscar artefato por path ou query
- WRITE: criar/atualizar artefato com frontmatter (Nature, tags, scope)
- SEARCH: buscar por Nature, tags, ou texto livre
- PROMOTE: mover artefato de micro para global (ou shared)
- SCOPE: listar o que existe em uma camada

Crie a estrutura de 4 camadas:
  acervo/macro/
  acervo/global/
  acervo/micro/_template/
  acervo/shared/cross-refs/

Execute smoke test: SCOPE em cada camada (deve retornar vazio ou com seed files).
