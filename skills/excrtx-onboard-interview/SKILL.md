---
name: excrtx-onboard-interview
description: >-
  Entrevista de onboarding para novos executivos. Captura valores, estilo, domínios
  e integrações em 5 blocos de perguntas para auto-gerar SOUL.md personalizado e
  microversos iniciais. Ativar após o welcome ou quando executivo pede re-onboarding.
version: 2.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, onboard, interview, soul, setup, personalization]
---

# Onboarding Interview — Arquiteto de Sistemas Cognitivos

> Cada executivo é único. O onboarding captura a essência do novo usuário e configura o Exocórtex sob medida.

## Arquitetura de Provisionamento

O Hermes do executivo **não provisiona a si mesmo**. O ciclo é:

1. **Provisioner Agent** cria a instância: container, `HERMES_HOME`, golden image, skills base.
2. **Hermes do executivo** inicializa com o bundle `exocortex-alpha` já instalado.
3. **Welcome** (`excrtx-onboard-welcome`) apresenta o sistema.
4. **Interview** (esta skill) personaliza a instância pré-provisionada.

O executivo nunca interage com o Provisioner. Ele só vê: welcome → entrevista → Exocórtex pronto.

## Trigger

Ativar quando:
- Transição do `excrtx-onboard-welcome` (fluxo normal)
- Executivo pede "configure para mim", "novo setup", "onboarding", "quero refazer a entrevista"
- Re-calibração solicitada (sem destruir dados existentes — merge)
- SOUL.md detectado com seções "Pendente" (Configuration State)

## Procedure

### 1. Apresentação

Dizer: "Vou fazer perguntas em 5 blocos para entender como você pensa e trabalha. Não existe resposta certa. Pode pular qualquer pergunta — uso defaults razoáveis."

### 2. Entrevista (5 blocos)

**Bloco A — Identidade Profissional:** Papel, estilo de liderança, 3 valores-guia.

**Bloco B — Estilo de Comunicação:** Tom de email, palavras que usa/evita, bullet points vs texto corrido.

**Bloco C — Domínios de Atuação:** Domínios gerenciados, o mais crítico agora, onde quer mais controle.

**Bloco D — Preferências Operacionais:** Manhã ideal, respostas diretas vs provocativas, quando interromper.

**Bloco E — Integrações:** Gmail/Google Workspace, calendário, outras ferramentas.

### 3. Geração de Artefatos

Com base nas respostas, auto-gerar:
1. **SOUL.md personalizado** — Values, Communication Style, Behavioral Boundaries
2. **Microversos iniciais** — um para cada domínio do Bloco C (via `excrtx-memory-newmicro`)
3. **tools/ global** — integrações desejadas do Bloco E
4. **estilo.md no macroverso** — estilo de comunicação do Bloco B

### 4. Confirmação

Apresentar resumo: Estilo, Domínios criados, Integrações, Modo padrão. Perguntar se quer ajustar antes de ativar.

### 5. Ativação

Após confirmação: atualizar SOUL.md, criar microversos via `excrtx-memory-newmicro`, registrar no MEMORY.md.

## Regras

- Perguntas aplicam `excrtx-quality-antislop` — diretas, sem floreio
- Executivo pode pular perguntas — usar defaults razoáveis
- Mapear fielmente o estilo do executivo, sem julgamento
- Re-onboarding não destrói dados existentes (merge)
- Esta skill NÃO provisiona infraestrutura — assume que o Provisioner já fez isso
- Referências a skills usam nomes novos (excrtx-* convention, ADR-015)

## Verificação

- [ ] Entrevista cobre os 5 blocos
- [ ] SOUL.md personalizado com respostas do executivo
- [ ] Microversos criados para cada domínio do Bloco C
- [ ] Resumo apresentado para confirmação antes de ativar
- [ ] Configuration State atualizado para OPERATIONAL
