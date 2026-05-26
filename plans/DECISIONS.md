# Exocórtex.IA — Architectural Decision Records

> **PURPOSE:** Log of every non-trivial technical decision made during development. Prevents re-debating settled issues.

---

## Format

```markdown
### ADR-{NNN}: {Title}
- **Date:** {YYYY-MM-DD}
- **Status:** Proposed | Accepted | Deprecated | Superseded by ADR-{NNN}
- **Context:** Why this decision was needed
- **Decision:** What was decided
- **Consequences:** Trade-offs and implications
```

---

## Accepted Decisions

### ADR-001: Hermes Agent como Core Runtime
- **Date:** 2025-05-25
- **Status:** Accepted
- **Context:** Precisamos de um runtime de agente com memória persistente, gateway multi-plataforma, sistema de skills, e plugin architecture. Construir do zero levaria meses.
- **Decision:** Clonar o NousResearch/hermes-agent (MIT) e estender via skills, plugins e MCP servers. Clone direto no monorepo, sem fork do GitHub.
- **Consequences:**
  - ✅ Runtime production-grade no dia 1
  - ✅ Gateway WhatsApp/Telegram built-in
  - ✅ MIT license permite uso comercial com crédito público
  - ⚠️ Acoplamento com upstream — mitigar com versionamento por tag
  - ⚠️ Codebase grande (~685KB `cli.py`, ~194KB `run_agent.py`) — exige estudo

### ADR-002: Prompt-Driven Development para Alpha
- **Date:** 2025-05-25
- **Status:** Accepted
- **Context:** Com 1 dev, precisamos da forma mais rápida de validar o conceito do Exocórtex. Hermes é programável via conversação.
- **Decision:** Usar prompts sequenciais (Infrastructure as Prompts) para configurar o Hermes como Exocórtex na fase Alpha. Playbook YAML versionado para reprodutibilidade.
- **Consequences:**
  - ✅ Velocidade: dias em vez de semanas
  - ✅ Reprodutível via Meta-Trainer para multi-tenant
  - ⚠️ Limitado às capacidades nativas do Hermes
  - ⚠️ Code Branch necessário para Beta/V1

### ADR-003: 1 Container Docker por Tenant
- **Date:** 2025-05-25
- **Status:** Accepted
- **Context:** Executivos lidam com dados sensíveis. Shared-process multitenancy traz riscos de data leakage.
- **Decision:** Cada tenant roda em seu próprio container Docker com `HERMES_HOME` isolado. Sem compartilhamento de processo.
- **Consequences:**
  - ✅ Isolamento total (processo, filesystem, rede)
  - ✅ Alinhado com Hermes Layer 3 Security (Container Isolation)
  - ⚠️ Custo de RAM/CPU por tenant
  - ⚠️ Orquestração mais complexa (Docker Compose → K8s)

### ADR-004: sqlite-vec + FTS5 para Alpha, Qdrant para Beta
- **Date:** 2025-05-25
- **Status:** Accepted
- **Context:** Vector DB necessário para busca semântica no Acervo Cognitivo.
- **Decision:** sqlite-vec (Hermes-nativo, zero deps) para Alpha. Migrar para Qdrant quando escala exigir (>100K vectors/tenant ou cross-tenant analytics).
- **Consequences:**
  - ✅ Zero dependências externas no Alpha
  - ✅ Cada tenant tem seu próprio .sqlite
  - ⚠️ Migração necessária na Beta

### ADR-005: OpenAI Primary + OpenRouter Fallback
- **Date:** 2025-05-25
- **Status:** Accepted
- **Context:** LLM provider para o runtime.
- **Decision:** OpenAI subscription (Codex) como primary. OpenRouter como fallback (200+ models, cost optimization). Configurado via `hermes model`.
- **Consequences:**
  - ✅ Best-in-class reasoning (GPT-5.x)
  - ✅ Fallback automático nativo do Hermes
  - ⚠️ Custo de API sob controle via rate limiting

### ADR-006: Configuração de Fallback com DeepSeek V3 no OpenRouter
- **Date:** 2026-05-26
- **Status:** Accepted
- **Context:** Necessidade de resiliência caso o Codex OAuth falhe, garantindo continuidade das operações com modelo de baixo custo e alta velocidade.
- **Decision:** Configurar `fallback_model` no arquivo `~/.hermes/config.yaml` com o provider `openrouter` e modelo `deepseek/deepseek-chat`.
- **Consequences:**
  - ✅ Failover automático e transparente em caso de indisponibilidade ou rate-limit do primary provider.
  - ✅ Baixo custo operacional usando a API do OpenRouter com o modelo DeepSeek V3.
  - ⚠️ Dependência da chave `OPENROUTER_API_KEY` configurada localmente no arquivo `.env`.
