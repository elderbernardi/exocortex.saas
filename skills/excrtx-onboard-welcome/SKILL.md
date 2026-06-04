---
name: excrtx-onboard-welcome
description: >-
  Apresentação multi-gateway do Exocórtex.IA para novos executivos. Lê WELCOME.md,
  adapta o conteúdo ao gateway ativo (Telegram, Web, Desktop), guia configuração
  do Telegram como primeiro gate, e transiciona para a entrevista de onboarding.
  Ativar na primeira interação de um novo executivo ou quando pedido explicitamente.
version: 2.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, onboard, welcome, presentation, multi-gateway]
---

# Welcome — Apresentação Multi-Gateway

> A primeira sessão do Exocórtex não é um tutorial. É a primeira vez que o framework cognitivo opera.

## Trigger

Ativar quando:
- Hermes recém-provisionado detecta acervo vazio na primeira interação
- Executivo pede "boas-vindas", "welcome", "me apresente o exocórtex"
- Executivo abre gateway pela primeira vez sem Macroverso preenchido
- Re-apresentação solicitada (sem destruir dados existentes)

## Procedure

### 1. Detectar Gateway

Identificar o gateway ativo para adaptar a apresentação:

| Gateway | Detecção | Adaptação |
|---------|----------|-----------|
| **Telegram** | `$HERMES_GATEWAY == telegram` | Mensagens curtas (≤4096 chars), emojis, botões inline. Dividir em cards sequenciais. |
| **Web UI** | `$HERMES_GATEWAY == web` | Rich HTML, acordeões colapsáveis, diagramas mermaid, progress bar. |
| **Hermes Desktop** | default | Markdown longo, seções com headers, terminal-friendly. |

### 2. Apresentar o Exocórtex

Carregar `$ACERVO/global/knowledge/WELCOME.md` e renderizar conforme gateway:

**Telegram flow (cards sequenciais):**
1. Card 1: "O que é" + filosofia (com emoji 🧠)
2. Card 2: "As 3 camadas" (Macroverso → Microverso → Tarefa)
3. Card 3: "O que você pode fazer" (vetores)
4. Card 4: "Integrações" + setup Telegram
5. Card 5: "Próximo passo: onboarding" (com botão inline)

**Desktop/Web flow:** Renderizar WELCOME.md completo com seções navegáveis.

### 3. Verificar Telegram

Se gateway é Telegram:
- ✅ Já está configurado (estamos conversando por aqui)
- Confirmar que o executivo está confortável com o canal

Se gateway não é Telegram:
- Verificar se `$TELEGRAM_BOT_TOKEN` está definido
- Se sim: informar que Telegram está pronto
- Se não: guiar criação via BotFather (passos do WELCOME.md)
- Criar reminder em `$HERMES_HOME/reminders/telegram-setup.md` se não configurado

### 4. Transição para Onboarding

Perguntar: "Quer começar o onboarding agora ou explorar primeiro?"

- Se sim → invocar `excrtx-onboard-interview`
- Se "explorar" → dar sugestões de primeiros usos (pesquisa, conversa livre)
- Se pular → registrar em memória que welcome foi visto, onboarding pendente

## Regras

- O WELCOME.md é a fonte de verdade — não inventar conteúdo fora dele
- Adaptar formato, nunca conteúdo: a filosofia é a mesma em qualquer gateway
- Executivo pode pular direto para o onboarding a qualquer momento
- Não usar slop: a apresentação deve ter o tom do Exocórtex (direto, preciso, humano)
- Se o executivo já tem SOUL.md preenchido, oferecer apenas re-tour (sem onboarding)

## Verificação

- [ ] WELCOME.md carregado e renderizado
- [ ] Gateway detectado e formato adaptado
- [ ] Status do Telegram verificado
- [ ] Transição para onboarding ou exploração oferecida
- [ ] Reminder criado se Telegram não configurado
