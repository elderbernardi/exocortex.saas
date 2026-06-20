---
type: decision
title: Política de manuseio de segredos
description: Nunca registrar tokens, API keys, cookies, refresh tokens ou conteúdo de `.env` no Acervo.
tags: [secrets, seguranca, env, acervo]
timestamp: 2026-06-05
class: perene
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
nature: contracts
kind: rule
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
created: 2026-06-05
---

# Política de manuseio de segredos

## Regras

- Nunca registrar tokens, API keys, cookies, refresh tokens ou conteúdo de `.env` no Acervo.
- Pode registrar o nome da variável, nunca o valor.
- Pode registrar path de credencial, se o conteúdo não for exposto.
- Logs com segredo devem ser redigidos antes de entrar no Acervo.
- Se um segredo aparecer em output, tratar como incidente SEV0.

## Variáveis podem ser citadas por nome

Exemplos permitidos:

```text
OPENROUTER_API_KEY
DOCBRAIN_LLM_API_KEY
CONTEXT7_API_KEY
TELEGRAM_BOT_TOKEN
GOOGLE_APPLICATION_CREDENTIALS
```

Valores dessas variáveis não entram no Acervo.
