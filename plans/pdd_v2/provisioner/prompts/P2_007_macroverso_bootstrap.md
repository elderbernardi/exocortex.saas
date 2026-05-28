---
phase: P2
sequence: 7
name: macroverso_bootstrap
depends_on: P2_006
exit_criteria:
  - "SCOPE macro retorna 3 artefatos"
verify_command: "ls ~/.hermes/acervo/macro/*.md 2>/dev/null | wc -l"
---

Usando o acervo-manager, popule o Macroverso:

WRITE acervo/macro/soul.md
  Nature: contexto
  Source: SOUL.md (espelho)

WRITE acervo/macro/valores.md
  Nature: reflexão
  Content: Os 7 Values do SOUL.md, expandidos com contexto

WRITE acervo/macro/estilo.md
  Nature: instrução
  Content: Regras de tom e voz (direto, sem slop, socrático quando evolução)

Verifique com SCOPE macro — deve retornar 3 artefatos.
