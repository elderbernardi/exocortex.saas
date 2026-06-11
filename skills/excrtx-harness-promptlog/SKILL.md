---
name: excrtx-harness-promptlog
description: Log configuration prompts to MEMORY.md for audit and reproducibility.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - logging
    - audit
    - configuration
    calibration:
    - feature_id: EX-31
      calibration_prompt: Você deve garantir que as operações e regras da skill Prompt
        Log (excrtx-harness-promptlog) estão totalmente ativas no seu comportamento
        e integridade.
      test_prompt: Verifique se MEMORY.md existe e contém registros de prompts.
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill Prompt Log.
      remediation_tip: Certifique-se de que a documentação e os limites da skill Prompt
        Log em seu SKILL.md estão sendo estritamente seguidos.
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
