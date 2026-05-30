# P3: Behavior — Skills de Negócio

> **Prompts:** 013–021
> **Gate:** self-test ≥ 4/5
> **Depende de:** P2 completo
> **Drift Audit:** Obrigatório ao final (Prompt 021)

---

## Propósito

Implementar as regras de negócio do Exocórtex como skills comportamentais.
**Sem MCPs.** Integrações externas ficam no BACKLOG_INTEGRATIONS.md.

### Mudanças em relação ao v1

1. MCPs eliminados do fluxo principal (D6). Foco em skills internas.
2. Output Quality Gate agora **consome** stop-slop/taste-skill (já instalados em P1).
3. Onboarding v1.1 — sem auto-provisionamento (D4).
4. Bundle e Profiles criados ao final como consolidação.

---

## Prompts

### Prompt 013 — Draft-First Protocol
**Skill:** `exocortex-draft-first`
**Comportamento:** Ações irreversíveis geram DRAFT local antes de executar.
**Smoke test:** Instruir "envie email para X" → agente gera DRAFT, não envia.

### Prompt 014 — Vetor Ativo (Classifier)
**Skill:** `exocortex-vetor-ativo`
**Comportamento:** Classifica input como Evolução ou Execução, ajusta postura.
**Smoke test:** 
- Input "explique recursão" → perfil `evol` (socrático)
- Input "escreva relatório" → perfil `exec` (agente especialista)

### Prompt 015 — Canvas Cognitivo (Extrator)
**Skill:** `exocortex-canvas`
**Comportamento:** Extrai implicitamente intent_focus, gaps, persona de inputs complexos.
**Smoke test:** Input longo e ambíguo → Canvas preenchido com 10 campos.

### Prompt 016 — Morning Briefing
**Skill:** `exocortex-briefing`
**Comportamento:** Coleta cross-microverso + gera briefing estruturado.
**Smoke test:** Com ≥ 2 microversos populados, gera briefing com dados de ambos.

### Prompt 017 — Onboarding Skill
**Skill:** `exocortex-onboarding` (v1.1)
**Comportamento:** Entrevista de personalização para instâncias já provisionadas.
**Nota v2:** Sem auto-provisionamento. O Provisioner é externo.
**Smoke test:** Simular entrevista de 3 perguntas → preferências salvas.

### Prompt 018 — Output Quality Gate
**Skill:** `exocortex-output-quality-gate`
**Comportamento:**
- Para PROSA: aplica stop-slop (scoring ≥ 35/50)
- Para VISUAL: aplica taste-skill (pre-flight check)
- Princípio: o executor corrige seu próprio output (não o orquestrador)
**Smoke test:** 
- Gerar parágrafo → scoring → se < 35, reescrever automaticamente
- Gerar prompt visual → pre-flight → flag de issues

### Prompt 019 — Tool Governance
**Skill:** `exocortex-tool-governance`
**Comportamento:** Governança de ferramentas internas (sem MCPs).
**Scope:** Classificar ferramentas por risco (read-only vs. side-effect).
**Smoke test:** Classificar "salvar arquivo" vs. "enviar email" → risk levels diferentes.

### Prompt 020 — Bundle + Profiles
**Artefatos:** `exocortex-alpha` bundle + profiles `exec`/`evol`
**Bundle contém:** 14 skills core (5 de P1 + 2 de P2 + 7 de P3) + `browser-use` como skill externa opcional, totalizando 15 entradas quando disponível
**Profile `exec`:** Carrega bundle + ativa Vetor de Execução
**Profile `evol`:** Carrega bundle + ativa Vetor de Evolução
**Smoke test:** Ativar cada profile → verificar skills carregadas.

### Prompt 021 — P3 Checkpoint + Drift Audit
**Verificações:**
- self-test ≥ 4/5
- Skills instaladas: esperado = 14 core (5 de P1 + 2 de P2 + 7 de P3), ou 15 se `browser-use` estiver disponível no bundle
- Bundle `exocortex-alpha` lista = skills instaladas
- Profiles `exec` e `evol` funcionais
- setup.sh reflete todas as skills core e declara `browser-use` como externa/opcional
- MEMORY.md tem entries para prompts 013-020
- Configuration State → P4_VALIDATION

---

## Skills Instaladas ao Final de P3

| # | Skill | Categoria | Fase |
|---|---|---|---|
| 1 | `exocortex-self-test` | Core | P1 |
| 2 | `exocortex-prompt-log` | Core | P1 |
| 3 | `stop-slop` | Quality | P1 |
| 4 | `taste-skill` | Quality | P1 |
| 5 | `exocortex-design-system` | Quality | P1 |
| 6 | `acervo-manager` | Memory | P2 |
| 7 | `exocortex-new-microverso` | Memory | P2 |
| 8 | `exocortex-draft-first` | Behavior | P3 |
| 9 | `exocortex-vetor-ativo` | Behavior | P3 |
| 10 | `exocortex-canvas` | Behavior | P3 |
| 11 | `exocortex-briefing` | Behavior | P3 |
| 12 | `exocortex-onboarding` | Behavior | P3 |
| 13 | `exocortex-output-quality-gate` | Behavior | P3 |
| 14 | `exocortex-tool-governance` | Behavior | P3 |
| 15 | `browser-use` | External | P3 |

---

## Critérios de Saída

| Critério | Verificação |
|---|---|
| 7 skills comportamentais instaladas | `hermes skills list` retorna 14 core ou 15 com `browser-use` |
| Bundle funcional | `exocortex-alpha` carrega todas |
| Profiles funcionais | `exec` e `evol` ativam corretamente |
| Testes comportamentais | 7 smoke tests passam |
| self-test ≥ 4/5 | self-test skill output |
| Drift audit PASS | Todos os checks ✅ |
| Configuration State | P4_VALIDATION |

---

> **Próxima fase:** P4 (Validation)
