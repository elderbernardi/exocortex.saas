# Fase P3: Tools & Governance

> **Status:** ✅ Completa (2026-05-26)  
> **Prompts:** 015–018 (Core) | 011–014 diferidos → Backlog  
> **Checkpoint:** self-test score ≥ 4/5  
> **Depende de:** P2 completo  
> **Estimated Time:** 1-2 horas (Core)

---

## Objetivo

Criar regras de governança de uso de tools, agrupar skills em bundle operacional, e configurar profiles por vetor de atuação. MCPs externos (filesystem, web search, Google Workspace, observability) foram movidos para backlog — nenhum teste de P4/P5 depende deles.

---

## Decisão de Design: MCPs Diferidos

**Análise de dependência (2026-05-26):** Rastreamos cada MCP proposto contra os testes de P4 (Behavior) e P5 (Validation). Resultado:

| MCP | Dependência real em P4/P5 | Decisão |
|---|---|---|
| Filesystem (011) | Nenhuma — acervo já opera via hermes-cli | Diferido |
| Web Search (012) | Nenhuma — zero smoke tests usam busca web | Diferido |
| Google Workspace (013) | Parcial — teste Draft-First verifica *comportamento* (gerar rascunho), não integração Gmail | Diferido |
| hermes-otel (014) | Nenhuma — observability é operacional | Diferido |

**Backlog:** Ver `plans/pdd/BACKLOG_INTEGRATIONS.md`

---

## Prompts — P3 Core

### Prompt 015 — Tool Governance Skill
Skill `exocortex-tool-governance`:
- Regras de quando usar cada tool
- Whitelist/blacklist por microverso
- Logging obrigatório de tool calls
- Classificação de tools: internos (hermes-cli) vs. externos (MCPs futuros)

### Prompt 016 — Bundle `exocortex-alpha`
Criar bundle que agrupa as skills essenciais:
- exocortex-self-test
- exocortex-prompt-log
- acervo-manager
- exocortex-new-microverso
- exocortex-tool-governance
- stop-slop
- taste-skill (gpt-taste, brandkit, brutalist)

Comando: `hermes bundles create exocortex-alpha --skill <name> ...`
Resultado: `/exocortex-alpha` carrega todas de uma vez.

### Prompt 017 — Profiles por Vetor
Criar profiles Hermes para Vetor de Execução vs. Evolução:

| Profile | Comportamento | Skills extras |
|---|---|---|
| `exec` | Foco em fazer: Draft-First, tools pesados | draft-first, tool-governance |
| `evol` | Foco em pensar: Socrático, reflexões | canvas-cognitivo, reflexão |

Comando: `hermes profile create <name>`

### Prompt 018 — P3 Checkpoint
self-test completo. Se OK → `current_phase: P4_BEHAVIOR`

Critérios:
- [ ] Skill `exocortex-tool-governance` instalada
- [ ] Bundle `exocortex-alpha` funcional (`/exocortex-alpha` carrega skills)
- [ ] Profiles `exec` e `evol` criados
- [ ] SOUL.md atualizado com `current_phase: P3_TOOLS`

---

## Próximo

Após P3 → `P4_BEHAVIOR.md`
