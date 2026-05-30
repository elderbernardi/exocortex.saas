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
  - ✅ Reprodutível via Provisioner Agent (agente dedicado, separado) para multi-tenant
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

### ADR-007: Dashboard como superfície de operação; Tailscale como requisito de acesso remoto
- **Date:** 2026-05-29
- **Status:** Accepted
- **Context:** O setup do Exocórtex precisa de uma superfície visual para administração sem aumentar a fricção do executivo nem expor o runtime Hermes na internet pública.
- **Decision:** Adotar `Telegram + Hermes Gateway` como interface principal do executivo e `Hermes Dashboard` com TUI embutida como superfície secundária de operação. Persistir o dashboard via `systemd --user` quando disponível. Para acesso remoto, manter o dashboard privado em `127.0.0.1:9119` e exigir **Tailscale** ou túnel SSH; não expor a porta 9119 publicamente por padrão.
- **Consequences:**
  - ✅ Separa UX do executivo da UX do operador
  - ✅ Preserva o dashboard como cockpit técnico para sessão, logs, config e recuperação
  - ✅ Reduz risco operacional ao evitar bind público de uma superfície sensível
  - ⚠️ Adiciona dependência operacional de Tailscale ou túnel seguro para administração remota
  - ⚠️ O instalador ainda precisa incorporar esse hardening de forma mais automatizada nas próximas iterações

---

## Decisões PDD v2

> ADRs 008-012 derivam da retrospectiva v1 → v2. Ver `pdd_v2/RETROSPECTIVE.md` para análise detalhada de cada drift.

### ADR-008: Redução de fases de 7 (P0-P6) para 6 (P0-P5)
- **Date:** 2026-05-30
- **Status:** Accepted
- **Context:** O PDD v1 tinha 7 fases (P0-P6) com 31 prompts. P6 (Production) era um "estado final" sem ações concretas — redundante com o checkpoint de P5. A renomeação de fases (P3=Tools → P3=Behavior, P4=Behavior → P4=Validation) reflete melhor a separação de concerns real.
- **Decision:** Consolidar em 6 fases (P0-P5) com 27 prompts. P5 (Production) absorve o estado final de P6. Fases renomeadas: P0=Foundation, P1=Identity, P2=Memory, P3=Behavior, P4=Validation, P5=Production.
- **Consequences:**
  - ✅ Eliminação de fase redundante
  - ✅ Nomes de fase refletem o conteúdo real (P3 é comportamento, não ferramentas)
  - ⚠️ Documentação e referências ao v1 precisam de atualização

### ADR-009: MCPs removidos do fluxo principal → BACKLOG
- **Date:** 2026-05-30
- **Status:** Accepted
- **Context:** No v1, MCPs (prompts 011-014) faziam parte do fluxo sequencial em P3 (Tools). Na execução, todos foram diferidos por dependências externas (API keys, OAuth). Nenhum smoke test de P4/P5 dependia deles. (Ref: RETROSPECTIVE D6)
- **Decision:** MCPs são extensões pós-golden-image, não parte do fluxo principal. Ficam em `BACKLOG_INTEGRATIONS.md` com critérios de reavaliação. P3 foca exclusivamente em skills comportamentais internas.
- **Consequences:**
  - ✅ Fluxo PDD avança sem bloqueios por dependências externas
  - ✅ Separação clara entre core (skills) e extensões (MCPs)
  - ⚠️ MCPs precisam de um fluxo de instalação pós-provisioning

### ADR-010: Quality Skills como identidade (P1), não comportamento (P4)
- **Date:** 2026-05-30
- **Status:** Accepted
- **Context:** No v1, stop-slop e taste-skill eram previstas para P4 (Behavior). Na execução real, foram instaladas em P1 como parte da identidade (Values #6 e #7 do SOUL.md). Qualidade de output é constitutiva: prosa gerada durante P2/P3 já precisa do gate. (Ref: RETROSPECTIVE D3)
- **Decision:** Quality skills (stop-slop, taste-skill, exocortex-design-system) são instaladas em P1 (Identity). São parte da identidade do agente, não regras de negócio adicionadas depois.
- **Consequences:**
  - ✅ Toda prosa gerada a partir de P2 já passa pelo gate de qualidade
  - ✅ Consistência: identidade e qualidade são inseparáveis
  - ⚠️ P1 fica mais pesado (5 skills em vez de 2)

### ADR-011: Drift Audit obrigatório em todas as fases
- **Date:** 2026-05-30
- **Status:** Accepted
- **Context:** No v1, não havia auditoria intermediária de integridade. Drift entre setup.sh e estado real só era detectado em P5, gerando retrabalho. (Ref: RETROSPECTIVE D5)
- **Decision:** Cada fase termina com um drift audit automatizado: comparação de skills declaradas vs. instaladas, setup.sh vs. estado real, MEMORY.md vs. prompts executados, e bundle vs. skills. Se o audit falhar, a fase não avança.
- **Consequences:**
  - ✅ Drift é detectado e corrigido incrementalmente
  - ✅ Reprodutibilidade validada a cada fase
  - ⚠️ Overhead de verificação em cada fase (mitigado por automação em `lib/drift_audit.sh`)

### ADR-012: Provisioner Agent como pacote externo
- **Date:** 2026-05-30
- **Status:** Accepted
- **Context:** No v1, o provisionamento era manual via `setup.sh` e prompts colados individualmente. O onboarding original tinha auto-provisionamento implícito, violando separação de concerns. (Ref: RETROSPECTIVE D4)
- **Decision:** Criar `pdd_v2/provisioner/` como pacote de automação auto-contido: RUNBOOK.md (documento executável para agentes), 27 prompts atomizados, scripts de verificação, suporte a Docker. Distribuído como `dist/exocortex-provisioner-v2.0.0.tar.gz`. O Hermes do executivo nunca provisiona a si mesmo.
- **Consequences:**
  - ✅ Provisionamento reproduzível e automatizado
  - ✅ Agente dedicado (qualquer CLI) pode executar o RUNBOOK
  - ✅ Suporte a Docker para teste isolado
  - ⚠️ Pacote precisa ser mantido em sincronia com mudanças nos artifacts
