---
phase: P3
sequence: 19
name: tool_governance
depends_on: P3_018
exit_criteria:
  - "skill exocortex-tool-governance instalada"
  - "Classificação de risco funcional"
verify_command: "hermes skills list | grep -q tool-governance"
---

Instale a skill exocortex-tool-governance.

Comportamento: Governança de ferramentas internas (sem MCPs).
Scope: Classificar ferramentas por risco (read-only vs. side-effect).

Smoke test: Classificar "salvar arquivo" vs. "enviar email" → risk levels diferentes.
