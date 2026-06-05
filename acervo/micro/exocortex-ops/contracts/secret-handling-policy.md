---
title: Política de manuseio de segredos
created: 2026-06-05
updated: 2026-06-05
nature: contracts
kind: rule
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
tags: [secrets, seguranca, env, acervo]
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
