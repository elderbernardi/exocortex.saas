---
adr: "014"
titulo: "Welcome Flow Multi-Gateway"
status: aceito
data: 2026-06-04
decisores: ["executivo", "exocortex-team"]
---

# ADR-014: Welcome Flow Multi-Gateway

## Contexto

O setup.sh instala o Exocórtex com 33 skills, acervo v0.4 e SOUL.md — mas nenhuma experiência de boas-vindas. Um novo usuário abre o Hermes e não sabe:
- O que é o Exocórtex e qual a filosofia
- O que pode fazer (capabilities)
- Como configurar gateways (Telegram, Web, Desktop)
- Como iniciar o onboarding

O executivo pediu um Welcome que funcione em qualquer gateway, com Telegram como primeiro gate recomendado, e que apresente a metodologia do Framework Cognitivo (Macroverso → Microverso → Tarefa, vetores de Evolução e Execução).

## Decisão

### 1. WELCOME.md — Conteúdo Estático

Um arquivo `WELCOME.md` instalado em `acervo/global/knowledge/` contém:
- Apresentação do Exocórtex (filosofia *Memento te hominem*)
- As 3 camadas (Macroverso, Microverso, Tarefa)
- Os 2 vetores (Evolução e Execução)
- Capabilities agrupadas por vetor
- Setup guides por gateway (Telegram, Web, Desktop)
- Transição para onboarding

### 2. Separação Welcome ↔ Interview

A skill `exocortex-onboarding` atual é dividida em duas:

| Skill | Responsabilidade |
|-------|------------------|
| `excrtx-onboard-welcome` | Apresentação + setup de gateway + transição |
| `excrtx-onboard-interview` | Entrevista dos 5 blocos + geração de SOUL.md |

**Motivação:** Re-onboarding não precisa repetir o Welcome. Novos gateways podem ser configurados sem re-fazer a entrevista.

### 3. Telegram como Primeiro Gate

- O bot Telegram **não pode ser criado programaticamente** (limitação da API — requer BotFather manual)
- O token pode ser fornecido via env var `TELEGRAM_BOT_TOKEN` no setup.sh
- Se fornecido, o setup.sh chama `hermes gateway setup` automaticamente
- Se não fornecido, o WELCOME.md guia o usuário pelo processo manual
- Um reminder é criado em `$HERMES_HOME/reminders/telegram-setup.md` se não configurado

### 4. Adaptação por Gateway

O conteúdo é universal. A apresentação adapta-se:

| Gateway | Adaptação |
|---------|-----------|
| Telegram | Mensagens curtas, emojis, botões inline (limite 4096 chars) |
| Web UI | Rich HTML, diagramas, progress bar, acordeões |
| Hermes Desktop | Markdown longo, terminal-friendly |

A skill `excrtx-onboard-welcome` detecta o gateway ativo e adapta o formato.

## Consequências

- Novos usuários recebem contexto filosófico e operacional na primeira interação
- O Telegram como primeiro gate reduz atrito (mais acessível que CLI)
- WELCOME.md pode ser atualizado independentemente das skills
- A separação welcome/interview permite composição flexível
