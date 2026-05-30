---
phase: P5
sequence: 27
name: graduation
depends_on: P4_026
exit_criteria:
  - "Todos os smoke tests de P4 re-passam"
  - "self-test = 5/5"
  - "Drift audit = PASS"
  - "setup.sh reproduz 100%"
  - "Configuration State = PRODUCTION"
verify_command: null
---

GRADUAÇÃO DO EXOCÓRTEX.IA

1. Verificação final:
   - Todos os smoke tests de P4 ainda passam? (re-executar)
   - self-test = 5/5?
   - Drift audit = PASS?

2. setup.sh definitivo:
   - Garantir que setup.sh reproduz 100% do estado:
     * 14 skills core instaladas (+ `browser-use` quando disponível)
     * 4 camadas do acervo criadas
     * Área operacional `_artifacts/` documentada para publicação de artefatos finais
     * Bundle e profiles configurados
     * SOUL.md com 7 Values
   - Testar: executar setup.sh em diretório limpo e comparar

3. BACKLOG_INTEGRATIONS.md:
   - Atualizar status de cada item
   - Documentar o que foi resolvido com alternativas (ex: DDG)
   - Manter critérios de reavaliação para itens pendentes

4. MEMORY.md:
   - Verificar que contém log completo de todos os 27 prompts
   - Adicionar entry de graduação

5. Configuration State:
   - Atualizar para PRODUCTION
   - Adicionar timestamp de graduação

RESULTADO:
  O Exocórtex.IA está em estado PRODUCTION.
  O setup.sh é a receita reproduzível.
  O Provisioner Agent pode consumir esta golden image.
