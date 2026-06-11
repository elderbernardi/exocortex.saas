---
name: excrtx-harness-promptlog
description: Log configuration prompts to MEMORY.md for audit and reproducibility.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, logging, audit, configuration]
---

# Exocortex Prompt Log

## When to Use

Activate AUTOMATICALLY after any configuration prompt that modifies SOUL.md, MEMORY.md, config.yaml, or installs skills/tools.

**Don't use for:** Normal conversation or task execution. Code changes without configuration impact. Briefings or status checks (use `excrtx-behavior-briefing`). Self-diagnostics (use `excrtx-assess-selftest`).

## Procedure
1. Registrar em MEMORY.md uma entrada com:
   - Prompt ID (ex: 004)
   - Timestamp (ISO 8601)
   - Fase (P1-P6)
   - Artefatos criados ou modificados
   - Status: success | partial | failed
   - Resumo do que mudou

2. Formato de entrada:
   ```
   [PDD-{ID}] {timestamp} | Phase: P{N} | Status: {status}
   Artifacts: {lista}
   Summary: {resumo em 1 linha}
   ```

## Objective
Manter um log auditável que permite REPRODUZIR a configuração em uma nova instância Hermes. Qualquer agente deve poder ler MEMORY.md e entender o histórico completo de configuração.

## Pitfalls

- **Over-application**: Only activate when the skill's trigger conditions are met.
- **Missing context**: Ensure required dependencies and related skills are loaded.

## Verification

- [ ] Skill trigger conditions were correctly matched
- [ ] Output follows the skill's defined format and rules
- [ ] No governance violations occurred
