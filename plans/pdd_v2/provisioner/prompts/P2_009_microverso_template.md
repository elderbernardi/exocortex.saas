---
phase: P2
sequence: 9
name: microverso_template
depends_on: P2_008
exit_criteria:
  - "skill exocortex-new-microverso instalada"
  - "acervo/micro/_template/ existe com index.md e SCHEMA.md"
verify_command: "ls ~/.hermes/acervo/micro/_template/ 2>/dev/null"
---

Crie a skill exocortex-new-microverso que:

1. Recebe: nome do microverso (slug), descrição, domínio
2. Cria diretório: acervo/micro/{slug}/
3. Gera: index.md (com metadata), SCHEMA.md (frontmatter YAML spec)
4. Registra: o novo microverso no MEMORY.md
5. Retorna: confirmação com path e conteúdo do index.md

O template base vive em acervo/micro/_template/.

Execute smoke test: criar microverso "test-sandbox", verificar arquivos, deletar.
