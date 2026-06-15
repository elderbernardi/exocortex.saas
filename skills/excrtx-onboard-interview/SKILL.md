---
name: excrtx-onboard-interview
description: Onboarding interview for new executives. Captures values, style, domains, and integrations in 5 question blocks
  to auto-generate personalized SOUL.md and initial microversos. Activate after welcome or when executive requests re-onboarding.
version: 2.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - onboard
    - interview
    - soul
    - setup
    - personalization
    related_skills:
    - excrtx-onboard-welcome
    - excrtx-memory-newmicro
    - excrtx-quality-antislop
    calibration:
    - feature_id: EX-02
      calibration_prompt: 'Você conduz a entrevista de calibração do Exocórtex em 5 blocos: 1) Identidade Profissional, 2)
        Estilo de Comunicação, 3) Domínios de Atuação, 4) Preferências Operacionais, 5) Integrações. Cada bloco gera uma seção
        do SOUL.md. Suporte a interrupção parcial, defaults para blocos pulados, e re-onboarding com merge não-destrutivo.'
      test_prompt: Quero refazer a parte de 'Estilo de Comunicação' do meu perfil. O resto pode ficar como está.
      acceptance_criteria: '1. O agente identifica que é um re-onboarding parcial (apenas Bloco 2)

        2. Preserva os blocos existentes (1, 3, 4, 5) sem sobrescrever

        3. Faz perguntas sobre estilo de comunicação (tom, formalidade, preferências)

        4. Indica que o merge será não-destrutivo no SOUL.md'
      remediation_tip: 'FALHA: Re-onboarding parcial não reconhecido. A skill suporta re-onboarding por bloco individual com
        merge não-destrutivo. Quando o executivo pede para refazer apenas um bloco, isole a seção correspondente em SOUL.md,
        conduza a entrevista apenas daquele bloco e faça merge preservando o restante.'
---
# Onboarding Interview — Cognitive Systems Architect

> Every executive is unique. The onboarding captures the new user's essence and configures the Exocórtex to fit.

## Provisioning Architecture

The executive's Hermes **does not provision itself**. The cycle is:

1. **Provisioner Agent** creates the instance: container, `HERMES_HOME`, golden image, base skills.
2. **Executive's Hermes** initializes with `exocortex-alpha` bundle already installed.
3. **Welcome** (`excrtx-onboard-welcome`) presents the system.
4. **Interview** (this skill) personalizes the pre-provisioned instance.

The executive never interacts with the Provisioner. They only see: welcome → interview → Exocórtex ready.

## Trigger

Activate when:
- Transition from `excrtx-onboard-welcome` (normal flow)
- Executive says "configure para mim", "novo setup", "onboarding", "quero refazer a entrevista"
- Re-calibration requested (without destroying existing data — merge)
- SOUL.md detected with "Pendente" sections (Configuration State)

**Don't use for:** Casual chat or debugging another skill. When SOUL.md is already fully populated without 'Pendente' sections (unless re-calibration explicitly requested). Infrastructure provisioning (handled by Provisioner Agent).

## Procedure

### 1. Introduction

Say: "Vou fazer perguntas em 5 blocos para entender como você pensa e trabalha. Não existe resposta certa. Pode pular qualquer pergunta — uso defaults razoáveis."

### 2. Interview (5 blocks)

**Block A — Professional Identity:** Role, leadership style, 3 guiding values.

**Block B — Communication Style:** Email tone, words used/avoided, bullet points vs running text.

**Block C — Domains of Action:** Managed domains, the most critical one right now, where they want more control.

**Block D — Operational Preferences:** Ideal morning, direct vs provocative responses, when to interrupt.

**Block E — Integrations:** Gmail/Google Workspace, calendar, other tools.

### 3. Artifact Generation

Based on responses, auto-generate:
1. **Personalized SOUL.md** — Values, Communication Style, Behavioral Boundaries
2. **Initial microversos** — one for each Block C domain (via `excrtx-memory-newmicro`)
3. **Global tools/** — desired integrations from Block E
4. **estilo.md in macroverso** — communication style from Block B

### 4. Confirmation

Present summary: Style, created Domains, Integrations, default Mode. Ask if they want adjustments before activation.

### 5. Activation

After confirmation: update SOUL.md, create microversos via `excrtx-memory-newmicro`, register in MEMORY.md.

## Rules

- Questions apply `excrtx-quality-antislop` — direct, no fluff
- Executive can skip questions — use reasonable defaults
- Faithfully map the executive's style, without judgment
- Re-onboarding does not destroy existing data (merge)
- If executive answers only some blocks: generate defaults for skipped blocks, present for review
- If interview is terminated early: save partial results, mark unanswered blocks in Configuration State as 'Pendente'
- This skill does NOT provision infrastructure — assumes the Provisioner already did it
- Skill references use new names (excrtx-* convention, ADR-015)

## Verification

- [ ] Interview covers all 5 blocks (or skipped blocks have documented defaults)
- [ ] SOUL.md contains identifiable values from interview (not default template text)
- [ ] Communication preferences from Block B reflected in `estilo.md`
- [ ] Microversos created for each Block C domain
- [ ] Summary presented for confirmation before activation
- [ ] Configuration State updated to OPERATIONAL (or PARTIAL if incomplete)
- [ ] MEMORY.md updated with onboarding log entry

## Pitfalls

- **Long silence during interview:** Executive may lose engagement. Echo a prompt every 2 minutes if no response: "Posso continuar com defaults razoáveis se preferir." Session timeout may occur — save partial state.
- **Over-application:** Only activate when trigger conditions are met. Do not re-interview if SOUL.md is already fully populated.
- **Default leakage:** Defaults should be clearly marked in the generated SOUL.md. Executive must know which values were assumed vs stated.
- **Block C domain explosion:** If executive lists 10+ domains, consolidate into 3-5 primary microversos. Additional domains can be created later.
