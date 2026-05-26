# Fase P5: Validation — Smoke Tests & Self-Repair

> **Status:** ⬜ Não Iniciada  
> **Prompts:** 026–028  
> **Checkpoint:** self-test score = 5/5  
> **Depende de:** P4 completo  
> **Estimated Time:** 1-2 horas

---

## Objetivo

Validação end-to-end com cenários realistas. Loop de self-repair até score perfeito.

---

## Prompts

### Prompt 026 — Full Smoke Test

Executar em sequência:

1. **Microverso CRUD:** "Crie um microverso para Cliente Alfa"
   → Verifica criação completa da estrutura

2. **Draft-First:** "No contexto do Cliente Alfa, prepare um email de follow-up da última reunião"
   → Verifica que gera DRAFT, não envia

3. **Vetor de Evolução:** "O que eu deveria considerar antes de renegociar com o Cliente Alfa?"
   → Verifica modo Socrático (perguntas, não respostas)

4. **Morning Briefing:** "Me dê um briefing da manhã"
   → Verifica consolidação cross-microverso

5. **self-test:** Relatório completo
   → Score alvo: 5/5

Reportar resultado de cada teste individualmente.

---

### Prompt 027 — Self-Repair Loop

Para cada falha detectada no Prompt 026:
1. Diagnosticar causa raiz
2. Propor fix (skill edit, config change, etc.)
3. Aplicar fix
4. Re-executar APENAS o teste que falhou
5. Repetir até passar

**Constraint:** Máximo 3 tentativas por teste. Se falhar 3x → escalar para humano com diagnóstico detalhado.

**Não avançar para P6 até score 5/5.**

---

### Prompt 028 — Graduation

Todos os testes passaram. Atualizar Configuration State:
```
current_phase: P6_PRODUCTION
prompts_executed: [001-028]
status: ready
```

Gerar relatório final:
- Skills instaladas (lista completa)
- Tools/MCPs configurados
- Testes passados (5/5)
- Microversos ativos
- Tempo total de configuração

---

## Próximo

Após P5 → `P6_PRODUCTION.md`
