---
phase: P3
sequence: 20
name: bundle_profiles
depends_on: P3_019
exit_criteria:
  - "Bundle exocortex-alpha contém 15 skills"
  - "Profile exec ativa Vetor de Execução"
  - "Profile evol ativa Vetor de Evolução"
verify_command: "hermes profile list 2>/dev/null"
---

Configure os artefatos de consolidação:

1. Bundle exocortex-alpha:
   Contém todas as 15 skills (5 de P1 + 2 de P2 + 7 de P3 + design-system)

2. Profile `exec`:
   Carrega bundle + ativa Vetor de Execução

3. Profile `evol`:
   Carrega bundle + ativa Vetor de Evolução

Smoke test: Ativar cada profile → verificar skills carregadas.
