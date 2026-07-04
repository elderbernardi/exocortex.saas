---
schema: acervo/v0.2
type: contract
title: Política de manuseio de segredos
description: Nunca registrar tokens, API keys, cookies, refresh tokens ou conteúdo de `.env` no Acervo.
tags: [secrets, seguranca, env, acervo]
timestamp: 2026-06-05
class: perene
status: active
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
EXOCORTEX_DEFAULT_API_KEY
EXOCORTEX_VISION_API_KEY
EXOCORTEX_AUX_API_KEY
CONTEXT7_API_KEY
TELEGRAM_BOT_TOKEN
GOOGLE_APPLICATION_CREDENTIALS
```

Valores dessas variáveis não entram no Acervo.

## Segredos de LLM: 3 papéis

Toda configuração de LLM foi consolidada em 3 papéis. Os segredos de LLM
vivem nas vars de API key desses papéis — não há mais chaves de provider
soltas (`OPENROUTER_API_KEY`, `DOCBRAIN_LLM_API_KEY`, `DEEPSEEK_API_KEY` etc.,
migradas uma única vez para os papéis por `scripts/migrate-env-roles.py`):

- `EXOCORTEX_DEFAULT_API_KEY` — papel **default** (sempre usado; obrigatório).
- `EXOCORTEX_VISION_API_KEY` — papel **visão** (herda do default quando ausente).
- `EXOCORTEX_AUX_API_KEY` — papel **auxiliar** para softwares externos
  (DocBrain, Hindsight; herda do default quando ausente).

Esses segredos persistem em `.env.local` (permissão `600`), nunca são
commitados e devem ser mascarados em logs. As regras gerais acima se aplicam
integralmente a eles: cita-se o nome da variável, nunca o valor.
