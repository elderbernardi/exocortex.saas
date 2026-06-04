# Backlog: Integrações Externas (MCPs)

> **Criado:** 2026-05-26  
> **Origem:** P3 — MCPs diferidos (prompts 011–014)  
> **Motivo:** Nenhum teste de P4/P5 depende destes MCPs. Requerem API keys/OAuth não disponíveis.  
> **Reavaliar:** Após P6 (tenant operacional) ou quando o executivo solicitar funcionalidade que exija integração externa.

---

## Critérios de Reavaliação

Reavaliar este backlog quando qualquer condição for verdadeira:

1. **Executivo pede funcionalidade que requer MCP** — "busque na web", "acesse meu email", "veja minha agenda"
2. **P6 atingido** — tenant operacional, hora de expandir capacidades
3. **API keys disponíveis** — credenciais obtidas, faz sentido integrar
4. **Novo caso de uso emerge** — feature que seria manual sem o MCP

---

## Itens do Backlog

### BKL-001: Filesystem MCP
- **Prompt original:** 011
- **Propósito:** Acesso controlado ao `acervo/` via MCP (sandboxed)
- **API Key:** Nenhuma (local)
- **Avaliação:** Redundante agora. O hermes-cli já lê/escreve o acervo via `file_read`/`file_write`. Um MCP Filesystem adicionaria sandboxing por path (o agente só vê `~/.hermes/acervo/`), mas não é crítico enquanto o Exocórtex opera em single-tenant local.
- **Reavaliar quando:** Multi-tenant, containers isolados, ou necessidade de restringir acesso do agente a paths específicos.
- **Comando previsto:** `hermes mcp add filesystem --command npx --args @modelcontextprotocol/server-filesystem ~/.hermes/acervo/`
- **Prioridade:** Baixa

### ~~BKL-002: Web Search MCP~~ ✅ RESOLVIDO
- **Prompt original:** 012
- **Resolução (2026-05-26):** Instaladas duas skills complementares:
  - `duckduckgo-search` (Skills Hub oficial) — busca rápida, zero API key, CLI `ddgs`
  - `browser-use` (skill local) — automação de Chromium para pesquisa profunda
- **API Key:** ❌ Nenhuma necessária (DDG é gratuito, browser-use CLI não requer key)
- **Status:** Ambas instaladas, habilitadas, e smoke-testadas

### BKL-003: Google Workspace
- **Prompt original:** 013
- **Propósito:** Gmail (ler/rascunhar emails), Calendar (ler/criar eventos), Drive (ler/criar docs). Para email, o setup Exocórtex usa `google-workspace` como padrão e não instala/usa `himalaya`/`hymalaia`.
- **Pré-requisitos:**
  - Google Cloud Project com APIs habilitadas (Gmail, Calendar, Drive)
  - OAuth2 Client ID/Secret (tipo "Desktop application")
  - Consentimento do executivo para acesso à conta
  - Configuração de scopes mínimos (read-only por default, write via Draft-First)
- **Setup estimado:** ~30 min (criar projeto GCP + OAuth + autorizar)
- **Avaliação:** Maior impacto de todas as integrações. O Draft-First Protocol (P4) foi projetado especificamente para isto — gerar drafts de email/eventos/docs que o executivo revisa antes de enviar. Sem este MCP, o Draft-First vira skill de *intenção* (o agente gera o texto do email, mas o executivo copia e cola no Gmail).
- **Reavaliar quando:** Executivo quiser automação real de comunicação.
- **Dependências cruzadas:**
  - P4 Prompt 019 (Draft-First Skill) — funciona sem MCP como interceptor de intenção
  - P5 Smoke Test 2 (Draft-First) — testa comportamento, não integração real
- **Prioridade:** Alta (primeiro MCP a integrar pós-P6)

### BKL-004: Observability (hermes-otel)
- **Prompt original:** 014
- **Propósito:** Logging/tracing estruturado de tool calls, latência, erros
- **API Key:** Nenhuma (local) — ou endpoint OTLP se enviar para Grafana/Datadog
- **Avaliação:** Operacional. Útil para debug e otimização, mas o Hermes já tem `hermes logs` built-in.
- **Reavaliar quando:** Debugging complexo, multi-tenant, ou SLA de performance.
- **Prioridade:** Baixa

---

## Resumo de Keys Necessárias

| Key | Para quê | Free tier? | Prioridade |
|---|---|---|---|
| ~~`BRAVE_API_KEY` ou `TAVILY_API_KEY`~~ | ~~Web Search~~ | ~~Sim~~ | ~~Média~~ → **Resolvido (DDG + browser-use)** |
| Google OAuth2 (Client ID + Secret) | Gmail/Calendar/Drive | N/A (acesso à conta do executivo) | Alta |
| OTLP endpoint (opcional) | Observability remota | Depende do provider | Baixa |

---

## Histórico

| Data | Ação |
|---|---|
| 2026-05-26 | Criado. MCPs 011-014 diferidos de P3 para backlog. Análise de dependência confirmou zero bloqueios para P4-P5. |
| 2026-05-26 | BKL-002 resolvido. Instaladas skills `duckduckgo-search` + `browser-use`. Zero API keys necessárias. |
