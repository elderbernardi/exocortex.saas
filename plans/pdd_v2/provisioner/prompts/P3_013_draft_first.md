---
phase: P3
sequence: 13
name: draft_first
depends_on: P2_012
exit_criteria:
  - "skill exocortex-draft-first instalada"
  - "Smoke: instrução irreversível gera DRAFT"
verify_command: "hermes skills list | grep -q draft-first"
---

Instale a skill exocortex-draft-first.

Comportamento: Ações irreversíveis geram DRAFT local antes de executar.

Smoke test: Instrua "envie email para X" → agente gera DRAFT, não envia.
