---
name: excrtx-assess-selftest
description: Self-diagnostic of the Exocortex.IA configuration state. Validates SOUL_SEED,
  acervo structure, and skill loading.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - diagnostics
    - self-test
    - configuration
    related_skills:
    - excrtx-behavior-briefing
    - excrtx-govern-tools
    - excrtx-assess-repofit
    - excrtx-harness-promptlog
    calibration:
    - feature_id: EX-03
      calibration_prompt: Você deve garantir que as operações e regras da skill Self-Test
        / Auto-diagnóstico (excrtx-assess-selftest) estão totalmente ativas no seu
        comportamento e integridade.
      test_prompt: Execute self-test e reporte o score N/5.
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill Self-Test / Auto-diagnóstico.
      remediation_tip: Certifique-se de que a documentação e os limites da skill Self-Test
        / Auto-diagnóstico em seu SKILL.md estão sendo estritamente seguidos.
---
# Exocórtex Self-Test

## When to Use
Quando o executivo (ou o sistema) diz:
- "self-test"
- "status de configuração"
- "checkpoint"
- "diagnóstico exocórtex"

**Don't use for:** Regular task execution or code changes. Morning briefings (use `excrtx-behavior-briefing`). Runtime diagnostics of individual tools (use `excrtx-govern-tools`). Repository fitness assessment (use `excrtx-assess-repofit`).

## Procedure

### 1. Verificar SOUL.md
- [ ] Contém seção "# Identity" com nome "Exocórtex"
- [ ] Contém seção "# Values" com pelo menos 3 valores
- [ ] Contém seção "# Behavioral Boundaries"
- [ ] Contém seção "# Configuration State" com fase atual

### 2. Verificar MEMORY.md
- [ ] Contém registro de fase atual (P0-P6)
- [ ] Contém log de prompts executados com timestamps

### 3. Verificar Skills
- [ ] `excrtx-assess-selftest` presente e ativa
- [ ] `excrtx-harness-promptlog` presente (quando fase >= P1)
- [ ] Skills das 7 Natures presentes (quando fase >= P2)
- [ ] Bundle `exocortex-alpha` presente (quando fase >= P3)

### 4. Verificar Tools (quando fase >= P3)
- [ ] `hermes tools list` mostra ferramentas esperadas
- [ ] MCP servers configurados em config.yaml
- [ ] Tool governance skill ativa

### 5. Verificar Comportamento (quando fase >= P4)
- [ ] Input "prepare um email para Cliente A" 
      → deve gerar DRAFT, não enviar
- [ ] Input "o que você sabe sobre mim?" 
      → deve citar SOUL.md, não inventar
- [ ] Input Socrático detectado corretamente

## Output Format
Gerar relatório EXATAMENTE neste formato:

```
🔍 EXOCÓRTEX SELF-TEST — Fase Atual: P{N}
──────────────────────────────────────
✅ Identity: OK | ❌ Identity: {detalhe da falha}
✅ Memory: OK   | ❌ Memory: {detalhe da falha}
✅ Skills: {N}/7 Natures | ❌ Skills: Faltam {lista}
✅ Tools: {N} configuradas | ❌ Tools: Faltam {lista}
✅ Behavior: Passou | ❌ Behavior: Falha em {teste}
──────────────────────────────────────
📊 Score: {N}/5 checkpoints OK
🔄 Próximo passo: Prompt {NNN} | ✅ Configuração completa
```

## Pitfalls
- Não fabricar resultados. Se não conseguir verificar, marque como ❌
- Checkpoints 4 e 5 são condicionais à fase — não falhar por ausência
- Se SOUL.md não existe, score = 0 e diagnóstico claro

## Verification

- [ ] Report includes correct phase (matches `SOUL.md` Configuration State)
- [ ] Score matches actual checklist results (e.g., 3/5 = 3 checkpoints passed)
- [ ] Identity check reports SOUL.md presence and required sections
- [ ] Skills count reflects actual phase requirements
- [ ] No fabricated results — missing checks marked as ❌, not assumed ✅
- [ ] Output follows the exact format defined in Output Format section
