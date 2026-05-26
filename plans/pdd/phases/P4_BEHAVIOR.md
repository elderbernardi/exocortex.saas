# Fase P4: Behavior — Regras de Negócio

> **Status:** ⬜ Não Iniciada  
> **Prompts:** 019–025  
> **Checkpoint:** self-test score ≥ 4/5  
> **Depende de:** P3 completo  
> **Estimated Time:** 2-3 horas

---

## Objetivo

Implementar as regras de negócio do Exocórtex como skills: Draft-First, Vetor Ativo, Canvas Cognitivo, Morning Briefing, e Onboarding.

---

## Prompts

### Prompt 019 — Draft-First Skill
Skill que intercepta qualquer tool call externo e cria draft em vez de enviar. Padrão: gera rascunho → notifica executivo → aguarda aprovação → executa ou descarta.

### Prompt 020 — Vetor Ativo (Classifier)
Skill que classifica cada input como Execução ou Evolução:
- **Execução:** "prepare o email", "agende a reunião" → executar (draft)
- **Evolução:** "o que você acha de...", "como eu deveria..." → Socrático

### Prompt 021 — Canvas Cognitivo (Extrator de Ponteiros)
Skill que extrai estrutura implícita do input do executivo:
- `intent_focus`: o que o executivo quer
- `gaps`: informações faltantes
- `suggested_persona`: qual microverso ativar
- `action_type`: execução ou evolução

### Prompt 022 — Morning Briefing
Skill cross-microverso que consolida informações de múltiplos domínios:
- Atividades pendentes
- Aprovações em fila
- Insights recentes das reflexões
- Agenda do dia (quando Calendar integrado)

### Prompt 023 — Onboarding Skill
Skill de entrevista para novos executivos:
- Modo "Arquiteto de Sistemas Cognitivos"
- Captura: valores, estilo, domínios, integrações
- Auto-gera: SOUL.md, microversos iniciais, ferramentas.md

### Prompt 024 — Testes Comportamentais
Bateria de testes:
1. "Envie email para X" → deve gerar DRAFT
2. "O que eu deveria considerar sobre Y?" → modo Socrático
3. "No contexto do Cliente A, prepare Z" → ativa microverso correto
4. "Briefing da manhã" → cross-microverso

### Prompt 025 — P4 Checkpoint
self-test completo. Se OK → `current_phase: P5_VALIDATION`

---

## Próximo

Após P4 → `P5_VALIDATION.md`
