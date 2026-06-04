---
title: Integração NotebookLM no Exocórtex (CLI-first + MCP fallback)
created: 2026-06-01
updated: 2026-06-01
nature: conhecimento
kind: spec
scope_mode: micro
scope_slug: hermes-setup
applies_to: [setup, notebooklm, mcp]
authority: canonical
operational_mode: read_only
stability: active
tags: [notebooklm, nlm, mcp, setup, hermes]
---

# Objetivo

Habilitar uso do NotebookLM no Exocórtex com prioridade para **CLI (`nlm`)** e fallback por **MCP (`notebooklm-mcp`)**, com setup idempotente em `~/.hermes/setup.sh`.

# Requisitos funcionais

1. Detectar presença do `nlm` e do `notebooklm-mcp`.
2. Validar autenticação do `nlm` via `nlm login --check`.
3. Se auth ausente, gerar orientação operacional para login remoto (Telegram) em `~/.hermes/reminders/notebooklm-login.md`.
4. Garantir MCP fallback no Hermes: server `notebooklm` configurado com `hermes mcp add notebooklm --command notebooklm-mcp`.
5. Setup deve ser idempotente: não duplicar config MCP e não quebrar se componentes já estiverem presentes.

# Requisitos não funcionais

- Zero dependência obrigatória de UI local para operar no dia a dia (login pode ser conduzido por troca de URL no Telegram).
- Mensagens de setup claras, com status de cada subetapa.
- Falhas de integração não interrompem setup global (warnings, não hard fail).

# Credenciais Google — decisão

- **Não há reaproveitamento direto** da credencial do `google-workspace` (`~/.hermes/google_token.json`) no `nlm`.
- `nlm` usa sessão/cookies próprios em `~/.notebooklm-mcp-cli/`.
- É possível usar a **mesma conta Google**; mas o login do `nlm` precisa ocorrer no fluxo dele (`nlm login`).

# Fluxo operacional recomendado

1. Setup instala/verifica `nlm` + `notebooklm-mcp`.
2. Setup testa `nlm login --check`.
3. Sem auth:
   - gerar lembrete local,
   - orientar login assistido no chat.
4. Setup garante MCP `notebooklm` no Hermes.

# Comandos de validação

```bash
nlm login --check
hermes mcp list | grep notebooklm
```

# Próximo incremento

Adicionar etapa opcional no setup para instalar `nlm` automaticamente quando ausente (`uv tool install notebooklm-mcp-cli`), controlada por flag de ambiente (`EXOCORTEX_AUTO_INSTALL_NLM=1`).
