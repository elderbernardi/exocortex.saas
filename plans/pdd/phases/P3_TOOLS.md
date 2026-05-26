# Fase P3: Tools & MCPs

> **Status:** ⬜ Não Iniciada  
> **Prompts:** 011–018  
> **Checkpoint:** self-test score ≥ 4/5  
> **Depende de:** P2 completo  
> **Estimated Time:** 2-3 horas

---

## Objetivo

Instalar ferramentas (MCP servers) e criar regras de governança de uso de tools.

---

## Prompts

### Prompt 011 — Filesystem MCP
```
hermes mcp add filesystem
```
Configurar para acessar `acervo/`. Verificar: agente lê/escreve.

### Prompt 012 — Web Search MCP
```
hermes mcp add web-search
```
Configurar provider. Verificar: agente busca na web.

### Prompt 013 — Google Workspace MCP (Draft-First)
Instalar MCP para Gmail/Calendar/Drive. Todas as operações de escrita devem gerar DRAFT, nunca enviar diretamente. Configurar OAuth2 por tenant.

### Prompt 014 — Observability (hermes-otel)
Instalar `hermes-otel` para logging/tracing. Verificar: logs disponíveis.

### Prompt 015 — Tool Governance Skill
Skill `exocortex-tool-governance`:
- Regras de quando usar cada tool
- Whitelist/blacklist por microverso
- Logging obrigatório de tool calls

### Prompt 016 — Bundle `exocortex-alpha`
Criar bundle que agrupa as skills essenciais:
- exocortex-self-test
- exocortex-prompt-log
- exocortex-search
- exocortex-new-microverso
- exocortex-tool-governance
- 7 nature-* skills

### Prompt 017 — Profiles por Vetor
Criar profiles Hermes para Vetor de Execução vs. Evolução. Cada profile carrega skills e tools diferentes.

### Prompt 018 — P3 Checkpoint
self-test completo. Se OK → `current_phase: P4_BEHAVIOR`

---

## Próximo

Após P3 → `P4_BEHAVIOR.md`
