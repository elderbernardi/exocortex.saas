---
phase: P4
sequence: 24
name: smoke_vetor_evolucao
depends_on: P4_023
exit_criteria:
  - "Vetor Ativo classifica como EVOLUÇÃO"
  - "Resposta socrática (perguntas, não respostas prontas)"
  - "Output passa stop-slop >= 35/50"
verify_command: null
---

SMOKE TEST: Vetor de Evolução — Input de aprendizado deve ativar postura socrática.

1. Input: "O que eu deveria considerar ao pensar em arquitetura de microsserviços?"
2. Esperado: Vetor Ativo classifica como EVOLUÇÃO
3. Esperado: Resposta com:
   - Perguntas de volta (socrática)
   - Expansão de perspectiva
   - Conexões que o executivo talvez não tenha visto
   - NÃO uma lista de "boas práticas" copiada da internet
4. Verificar: output passa pelo stop-slop (scoring ≥ 35/50)

Critério: Classificação correta + postura socrática + quality gate.
