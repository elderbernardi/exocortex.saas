---
phase: P2
sequence: 8
name: global_layer
depends_on: P2_007
exit_criteria:
  - "SCOPE global retorna 3 artefatos"
verify_command: "ls ~/.hermes/acervo/global/*.md 2>/dev/null | wc -l"
---

Usando o acervo-manager, popule a camada Global:

WRITE acervo/global/index.md
  Content: Índice da camada global com links para cada Nature

Crie artefatos globais para Natures que se apliquem a todos os domínios:
- acervo/global/ferramentas-base.md (Nature: ferramenta) — ferramentas que todo microverso usa
- acervo/global/processos-transversais.md (Nature: processo) — workflows universais

Verifique com SCOPE global — deve retornar 3 artefatos (index + 2 Natures).
