# Exocórtex UI — Arquitetura da Interface no Telegram

> Documento de arquitetura gerado na sessão de brainstorm de 2026-06-09.
> Meta-issue: [#54](https://github.com/elderbernardi/exocortex.saas/issues/54)

---

## 1. Visão Geral

O Exocórtex no Telegram opera sobre o **Multi-Session DM Mode** do Hermes (`/topic`), onde cada tópico do Telegram é uma sessão isolada mapeada para um Microverso. O DM raiz vira um **lobby de comando** (só aceita `/xc *` e comandos de sistema). A navegação é por tópicos + slash commands com prefixo `/xc`.

```
┌─────────────────────────────────────────────────┐
│              DM Exocórtex (root lobby)           │
│  /xc → hub   /xc macro   /xc mv   /xc status    │
│  /xc vetor   /xc acervo  /xc sobre              │
│  /help        /topic                             │
└──────────┬──────────────────────────────────────┘
           │
   ┌───────┼──────────┬──────────┬──────────┬──────────┐
   ▼       ▼          ▼          ▼          ▼          ▼
🏛️       🏫         ⚙️         💼         🧠         ⚔️
gabinete  ensino    dev        comercial  bunker    war-room
sessão A  sessão B  sessão C   sessão D   sessão E  sessão F
```

---

## 2. Camadas do Sistema

| Camada | Onde vive | Função |
|--------|-----------|--------|
| **Lobby** | Root DM | Comandos `/xc`, sistema, navegação |
| **Microversos** | Tópicos Telegram | Sessões isoladas por domínio |
| **Bunker** | Tópico especial | Sessões de evolução sem poluir microversos |
| **War Room** | Tópico especial | Cruzamento explícito entre microversos |
| **Cron Jobs** | Agendados | Briefings, alertas, feed — entregues em tópicos |
| **Acervo** | Filesystem | Fonte de verdade, sync bidirecional |

---

## 3. Comandos `/xc`

Todos os comandos do Exocórtex usam prefixo `/xc`. Comandos nativos do Hermes (`/help`, `/topic`, `/status`, etc.) mantêm-se sem prefixo.

| Comando | Escopo | Descrição |
|---------|--------|-----------|
| `/xc` | Lobby | Hub de navegação — mapa do território + sugestões |
| `/xc macro` | Lobby | Constituição completa (Macroverso) |
| `/xc mv [nome]` | Lobby | Detalhes de um microverso (skills, status, última atividade) |
| `/xc mv` | Lobby | Lista todos os microversos com status resumido |
| `/xc vetor` | Qualquer | Classifica o input atual (execução/evolução/manutenção) |
| `/xc status` | Lobby | Health check: quality gates, memória, cron jobs, conexões |
| `/xc acervo [termo]` | Lobby | Busca no acervo cognitivo |
| `/xc sobre` | Lobby | Cartão de visita do Exocórtex (o que é, como funciona) |
| `/xc sync` | Tópico | Promove conhecimento da sessão atual para o acervo |
| `/xc bunker` | Lobby | Instruções para abrir sessão no bunker |
| `/xc warroom [microverso]...` | Lobby | Abre war room com microversos específicos |

---

## 4. Mapa de Tópicos

### Tópicos de Microverso (persistentes)

| Tópico | Microverso | Cor sugerida | Ícone |
|--------|------------|-------------|-------|
| `gabinete` | Prioridade máxima — ofícios, chefia, diretoria | 🔴 | 🏛️ |
| `ensino` | Aulas, material didático, pedagógico | 🔵 | 🏫 |
| `exocortex-dev` | Desenvolvimento do framework | 🟢 | ⚙️ |
| `comercial` | Integrações e side projects | 🟡 | 💼 |

### Tópicos Especiais (efêmeros ou reutilizáveis)

| Tópico | Função | Persistência |
|--------|--------|-------------|
| `bunker` | Reflexão, estudo, evolução — sem poluir microversos | Sessão efêmera (`/new` ao sair) |
| `war-room` | Cruzamento explícito entre 2+ microversos | Sessão efêmera |
| `cron` | Entrega de briefings e alertas | Persistente |
| `system` | Status e comandos do sistema (criado automaticamente) | Persistente |

---

## 5. Cron Jobs

| Job | Frequência | Entrega em | Função |
|-----|-----------|------------|--------|
| Morning Briefing | Diário 7h | Tópico `cron` | Pendências, saúde, issues abertas |
| Alertas de Manutenção | A cada 6h | Tópico `cron` | Links quebrados, memória cheia, manifests inconsistentes |
| Feed de Decisões | On-demand (trigger) | Tópico `cron` | Cada decisão arquitetural ou promoção gera entrada |

---

## 6. Fluxos Experimentais

### Bunker

1. Executivo digita `/xc bunker` no lobby
2. Exocórtex responde com instrução: "Vá ao tópico `bunker` e comece sua reflexão"
3. No tópico `bunker`, o Exocórtex opera em modo puramente socrático (Vetor de Evolução forçado)
4. Ao final, `/xc sync` promove insights para o microverso correto ou `shared/`
5. `/new` limpa a sessão para a próxima reflexão

### War Room

1. Executivo digita `/xc warroom gabinete juridico`
2. Exocórtex carrega knowledge base de ambos os microversos
3. Sessão opera com consciência cross-domain explícita
4. Restrições de compartilhamento (`allow`/`deny`) são respeitadas
5. Outputs são salvos em `shared/` ou no microverso âncora

---

## 7. Princípio de Atualização Orgânica

A UI do Exocórtex no Telegram não é um artefato estático. Ela é uma **projeção viva do Acervo Cognitivo**.

Mudanças estruturais devem refletir automaticamente na interface:

| Evento no Acervo | Reflexo na UI |
|------------------|---------------|
| Criação de microverso | Novo tópico no Telegram (ou sugestão) |
| Remoção/arquivamento de microverso | Tópico marcado como inativo ou arquivado |
| Novo cron job | Entrada no tópico `cron` ou tópico dedicado |
| Nova skill | Refletida no `/xc mv <nome>` e no hub |
| Alteração no Macroverso | Notificação no feed de decisões |
| Promoção de artefato | Entrada no feed de decisões |

**Implicações técnicas:**
- **Watcher/hook** que detecta mudanças no acervo (`mtime`, eventos git, ou triggers nas skills de create/delete)
- **Mapper** `slug → thread_id` mantido em arquivo de configuração (atualizado automaticamente)
- **`/xc rescan`** para forçar re-sincronização manual

---

## 8. Entregáveis e Fases

### Fase 0 — Fundação (bloqueante)
- [ ] Ativar `/topic` (Multi-Session DM Mode) e verificar BotFather
- [ ] Criar tópicos base: gabinete, ensino, exocortex-dev, comercial, cron
- [ ] Implementar scoping de memória por tópico/microverso

### Fase 1 — Comandos `/xc`
- [ ] `/xc` — Hub de navegação
- [ ] `/xc macro` — Visualização do Macroverso
- [ ] `/xc mv` — Navegação de microversos
- [ ] `/xc status` — Health check
- [ ] `/xc sobre` — Cartão de visita

### Fase 2 — Tópicos Especiais
- [ ] Bunker — Tópico de evolução/reflexão
- [ ] War Room — Tópico cross-microverso
- [ ] `/xc sync` — Promoção de conhecimento

### Fase 3 — Automação (Cron)
- [ ] Morning Briefing diário
- [ ] Alertas de manutenção
- [ ] Feed de decisões

### Fase 4 — Navegação e Extras
- [ ] `/xc vetor` — Classificador de input
- [ ] `/xc acervo` — Busca no acervo
- [ ] Árvore textual de navegação
- [ ] Diagrama de arquitetura (`/xc mapa`)
- [ ] Onboarding interativo via Telegram

---

## 9. Relatório de Viabilidade

**Plataforma:** Hermes Agent com Telegram gateway
**Mecanismo central:** Multi-Session DM Mode (`/topic`)
**Isolamento:** Cada tópico = sessão independente (histórico, estado do modelo, ferramentas)
**Chave de isolamento:** `agent:main:telegram:dm:{chat_id}:{thread_id}`
**Pré-requisito:** BotFather com Threaded Mode ON e users-can-create-topics ON

### O que é viável nativamente
- Tópicos como sessões isoladas ✅
- Slash commands por tópico e no lobby ✅
- Cron jobs com entrega em tópico específico (`TELEGRAM_CRON_THREAD_ID`) ✅
- Auto-rename de tópicos baseado no conteúdo da sessão ✅
- `/new` para resetar apenas o tópico atual ✅

### Risco principal
A memória do Hermes (`memory` tool) é por usuário, não por sessão. Sem scoping explícito, aprendizados podem vazar entre microversos. A solução proposta usa o Acervo Cognitivo como fonte de verdade com mapeamento `thread_id → microverso_slug`.

### Cron deliveries em modo tópico
Cron jobs entregues no root DM caem no lobby (só comandos). Solução: criar tópico `cron` e configurar `TELEGRAM_CRON_THREAD_ID` para rotear entregas.

---

## 10. Comandos Hermes Relevantes

| Comando | Função |
|---------|--------|
| `/topic` | Ativar/status/desativar multi-session mode |
| `/topic off` | Desativar e limpar bindings |
| `/topic <session-id>` | Restaurar sessão anterior no tópico atual |
| `/new` | Resetar apenas o tópico atual |
| `/sethome` | Definir canal principal para entregas |
| `/status` | Status da sessão atual |

---

## 11. Referência Técnica

- **Hermes Multi-Session DM:** `/topic` command, isolamento por `thread_id`
- **Config:** `gateway.platforms.telegram.extra.dm_topics` (config-driven, alternativo ao `/topic` user-driven)
- **Cron routing:** `TELEGRAM_CRON_THREAD_ID` em `.env`
- **Auto-rename:** `gateway.platforms.telegram.extra.disable_topic_auto_rename` (desabilitar se quiser nomes manuais)
- **Repo:** `elderbernardi/exocortex.saas`
- **Meta-issue:** [#54](https://github.com/elderbernardi/exocortex.saas/issues/54)
