---
phase: P1
sequence: 1
name: bootstrap_self_test
depends_on: null
exit_criteria:
  - "hermes skills list mostra exocortex-self-test"
  - "SOUL.md contém Configuration State = P1_IDENTITY"
verify_command: "hermes skills list | grep -q self-test"
---

Você é um agente Hermes recebendo configuração do Exocórtex.IA.

Instale a skill de auto-diagnóstico a partir do arquivo fornecido em `skills/exocortex/exocortex-self-test/SKILL.md`.
Configure o "Configuration State" no SOUL.md como: P1_IDENTITY.

Execute o self-test. O resultado esperado é 1/5 (apenas bootstrap).
Registre o resultado no session log.
