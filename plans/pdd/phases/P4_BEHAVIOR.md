# Fase P4: Behavior — Regras de Negócio + Quality Gate

> **Status:** ⬜ Não Iniciada  
> **Prompts:** 019–026  
> **Checkpoint:** self-test score ≥ 4/5  
> **Depende de:** P3 completo  
> **Estimated Time:** 2-3 horas

---

## Objetivo

Implementar as regras de negócio do Exocórtex como skills: Draft-First, Vetor Ativo, Canvas Cognitivo, Morning Briefing, Onboarding, e **Output Quality Gate** (integração das skills stop-slop e taste-skill como interceptor obrigatório de todos os outputs).

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

### Prompt 024 — Output Quality Gate Skill
Skill `exocortex-output-quality-gate` que intercepta TODOS os outputs antes de entregá-los ao executivo:

**Trigger:** Ativar ANTES de entregar qualquer output.

**Classificação de output:**
- PROSA (email, briefing, análise, reflexão) → aplicar `stop-slop`
- VISUAL (UI, dashboard, apresentação, gráfico) → aplicar `taste-skill`
- MISTO → aplicar ambos

**Para PROSA — Quick Checks (stop-slop):**
- Algum advérbio? Matar.
- Voz passiva? Encontrar o ator, fazer dele o sujeito.
- Coisa inanimada fazendo verbo humano ("a decisão emerge")? Nomear a pessoa.
- Contraste "não X, é Y"? Dizer Y diretamente.
- Frase soa como pull-quote? Reescrever.
- Declarativo vago ("As implicações são significativas")? Nomear a implicação concreta.
- Scoring mínimo: 35/50 (Diretividade, Ritmo, Confiança, Autenticidade, Densidade)

**Para VISUAL — Pre-flight (taste-skill):**
- Hero ultrapassa 3 linhas? Alargar container, reduzir fonte.
- Grid tem gaps vazios? Aplicar grid-flow-dense.
- Usa labels genéricos (SECTION 01, QUESTION 05)? Remover.
- Layout idêntico ao anterior? Forçar randomização via taste-skill.
- Texto de botão invisível (contraste baixo)? Corrigir.
- Selecionar sub-skill correto por contexto (brutalist/brandkit/gpt-taste).

**Falha no gate:** Reescrever automaticamente, logar correção, entregar apenas versão corrigida.

### Prompt 025 — Testes Comportamentais
Bateria de testes:
1. "Envie email para X" → deve gerar DRAFT
2. "O que eu deveria considerar sobre Y?" → modo Socrático
3. "No contexto do Cliente A, prepare Z" → ativa microverso correto
4. "Briefing da manhã" → cross-microverso
5. "Prepare um resumo da situação do Cliente A" → **output passa stop-slop (≥ 35/50)**
6. "Gere um painel de métricas de performance" → **taste-skill brutalist ativado, grid sem gaps**

### Prompt 026 — P4 Checkpoint
self-test completo. Se OK → `current_phase: P5_VALIDATION`

Critérios adicionais para P4:
- [ ] Skill `exocortex-output-quality-gate` instalada e funcional
- [ ] Testes de qualidade textual passam (stop-slop score ≥ 35/50)
- [ ] Testes de qualidade visual passam (taste-skill pre-flight limpo)

---

## Próximo

Após P4 → `P5_VALIDATION.md`
