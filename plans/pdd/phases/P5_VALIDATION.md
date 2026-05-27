# Fase P5: Validation — Smoke Tests & Self-Repair

> **Status:** ✅ Completa (2026-05-27) — 7/7 smoke tests passados, self-test 5/5, zero self-repair needed  
> **Prompts:** 029–031  
> **Checkpoint:** self-test score = 5/5  
> **Depende de:** P4 completo  
> **Estimated Time:** 1-2 horas

---

## Objetivo

Validação end-to-end com cenários realistas. Loop de self-repair até score perfeito. Inclui validação explícita das quality skills (stop-slop + taste-skill).

---

## Prompts

### Prompt 029 — Full Smoke Test

Executar em sequência:

1. **Microverso CRUD:** "Crie um microverso para Cliente Alfa"
   → Verifica criação completa da estrutura

2. **Draft-First:** "No contexto do Cliente Alfa, prepare um email de follow-up da última reunião"
   → Verifica que gera DRAFT, não envia
   → **Quality check:** texto do draft passa stop-slop (≥ 35/50)

3. **Vetor de Evolução:** "O que eu deveria considerar antes de renegociar com o Cliente Alfa?"
   → Verifica modo Socrático (perguntas, não respostas)
   → **Quality check:** perguntas são diretas, sem frases de enchimento

4. **Morning Briefing:** "Me dê um briefing da manhã"
   → Verifica consolidação cross-microverso
   → **Quality check:** briefing passa stop-slop completo (sem advérbios, sem voz passiva, sem declarativos vagos)

5. **Quality Gate — Prosa:** "Prepare uma análise estratégica sobre a situação comercial do trimestre"
   → Verifica: executor aplica stop-slop como último passo
   → Verifica: scoring stop-slop ≥ 35/50
   → Verifica: zero padrões formulaicos ("Não é X, é Y", falsa agência)

6. **Quality Gate — Visual:** "Gere um dashboard com as métricas de vendas do mês"
   → Verifica: taste-skill brutalist ativado (dados pesados)
   → Verifica: grid sem gaps, sem labels "SECTION XX"
   → Verifica: paleta disciplinada, tipografia com contraste de escala

7. **self-test:** Relatório completo
   → Score alvo: 5/5

Reportar resultado de cada teste individualmente, incluindo quality score.

---

### Prompt 030 — Self-Repair Loop

Para cada falha detectada no Prompt 029:
1. Diagnosticar causa raiz
2. Propor fix (skill edit, config change, etc.)
3. Aplicar fix
4. Re-executar APENAS o teste que falhou
5. Repetir até passar

**Constraint:** Máximo 3 tentativas por teste. Se falhar 3x → escalar para humano com diagnóstico detalhado.

**Falhas de quality gate contam como falha de teste.** Um briefing que soa genérico é tão grave quanto um microverso que não cria a estrutura correta. Correções são feitas pelo executor, não pelo orquestrador. Código e documentação técnica são excluídos do gate.

**Não avançar para P6 até score 5/5.**

---

### Prompt 031 — Graduation

Todos os testes passaram. Atualizar Configuration State:
```
current_phase: P6_PRODUCTION
prompts_executed: [001-031]
status: ready
quality_skills: [stop-slop, taste-skill]
quality_gate: active
```

Gerar relatório final:
- Skills instaladas (lista completa)
- Tools/MCPs configurados
- Testes passados (5/5 + quality scores)
- Quality skills ativas e scores médios
- Microversos ativos
- Tempo total de configuração

---

## Próximo

Após P5 → `P6_PRODUCTION.md`
