---
phase: P4
sequence: 26
name: quality_gates_drift_audit_final
depends_on: P4_025
exit_criteria:
  - "stop-slop scoring >= 35/50"
  - "taste-skill pre-flight sem flags"
  - "Drift audit 7/7 checks"
  - "self-test = 5/5"
  - "Configuration State = P5_PRODUCTION"
verify_command: null
---

SMOKE TEST: Quality Gates + Drift Audit Final.

PARTE 1 — Quality Gate:
1. Gerar parágrafo sobre "inovação em educação"
2. Aplicar stop-slop scoring
3. Critério: ≥ 35/50 (se <35, reescrever e re-testar)
4. Gerar prompt visual para "dashboard de métricas"
5. Aplicar taste-skill pre-flight check
6. Critério: sem flags de defaults

PARTE 2 — Drift Audit FINAL:
1. Skills count: esperado = 15
2. Bundle exocortex-alpha: contém todas as 15?
3. Profiles exec/evol: funcionais?
4. setup.sh: reproduz o estado completo?
5. MEMORY.md: entries para TODOS os prompts (001-025)?
6. Acervo: 4 camadas populadas?
7. Zero skills fantasma (listadas mas não funcionais)?

PARTE 3 — Self-Test Final:
1. Executar self-test
2. Critério: 5/5

Se TUDO passar → Configuration State = P5_PRODUCTION
