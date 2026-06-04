---
name: exocortex-onboarding
description: Entrevista de onboarding para novos executivos. Captura valores, estilo, domínios e integrações para auto-gerar SOUL.md e microversos iniciais.
version: 1.1.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, behavior, onboarding, setup, interview]
---

# Onboarding — Arquiteto de Sistemas Cognitivos

> Cada executivo é único. O onboarding captura a essência do novo usuário e configura o Exocórtex sob medida.

## Arquitetura de Provisionamento

O Hermes do executivo **não provisiona a si mesmo**. O ciclo é:

1. **Provisioner Agent** (agente dedicado, separado do Exocórtex do usuário) cria a instância: container, `HERMES_HOME`, golden image, skills base.
2. **Hermes do executivo** inicializa com o bundle `exocortex-alpha` já instalado.
3. **Onboarding** é a **primeira skill comportamental** que roda no Hermes do novo executivo — personaliza a instância pré-provisionada.

O executivo nunca interage com o Provisioner. Ele só vê o resultado: um Hermes pronto que inicia com esta entrevista.

## Trigger

Ativar quando:
- O Hermes recém-provisionado detecta acervo vazio na primeira interação
- O executivo pede "configure para mim", "novo setup", "onboarding"
- Re-calibração solicitada (sem destruir dados existentes)

## Procedure

### 1. Apresentação

Dizer: "Sou o Exocórtex — seu exoesqueleto de pensamento. Antes de operar, preciso entender como você pensa e trabalha. Vou fazer perguntas. Não existe resposta certa."

### 2. Entrevista (5 blocos)

**Bloco A — Identidade Profissional:** Papel, estilo de liderança, 3 valores-guia.

**Bloco B — Estilo de Comunicação:** Tom de email, palavras que usa/evita, bullet points vs texto corrido.

**Bloco C — Domínios de Atuação:** Domínios gerenciados, o mais crítico agora, onde quer mais controle.

**Bloco D — Preferências Operacionais:** Manhã ideal, respostas diretas vs provocativas, quando interromper.

**Bloco E — Integrações:** Gmail/Google Workspace, calendário, outras ferramentas.

### 3. Geração de Artefatos

Com base nas respostas, auto-gerar:
1. **SOUL.md personalizado** — Values, Communication Style, Behavioral Boundaries
2. **Microversos iniciais** — um para cada domínio do Bloco C
3. **ferramentas.md global** — integrações desejadas do Bloco E
4. **estilo.md no macroverso** — estilo de comunicação do Bloco B

### 4. Confirmação

Apresentar resumo: Estilo, Domínios criados, Integrações, Modo padrão. Perguntar se quer ajustar antes de ativar.

### 5. Ativação

Após confirmação: atualizar SOUL.md, criar microversos via `exocortex-new-microverso`, registrar no MEMORY.md.

## Regras

- Perguntas aplicam `stop-slop` — diretas, sem floreio
- Executivo pode pular perguntas — usar defaults razoáveis
- Mapear fielmente o estilo do executivo, sem julgamento
- Re-onboarding não destrói dados existentes (merge)
- Esta skill NÃO provisiona infraestrutura — assume que o Provisioner já fez isso

## Verificação

- [ ] Entrevista cobre os 5 blocos
- [ ] SOUL.md personalizado com respostas
- [ ] Microversos criados para cada domínio
- [ ] Resumo apresentado para confirmação
