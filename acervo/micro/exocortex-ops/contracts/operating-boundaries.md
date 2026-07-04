---
schema: acervo/v0.2
type: contract
title: Limites Operacionais
description: Pode criar e editar arquivos do Acervo quando o executivo pedir explicitamente e o escopo estiver claro.
tags: [governance, draft-first, safety]
timestamp: 2026-06-05
class: perene
status: active
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
excrtx_type: rule
nature: contracts
sources: [SOUL, excrtx-govern-tools]
confidence: high
created: 2026-06-05
---

# Limites operacionais

## Mutação local permitida

Pode criar e editar arquivos do Acervo quando o executivo pedir explicitamente e o escopo estiver claro.

## Draft-First obrigatório

Sempre gerar DRAFT antes de:

- alterar `setup.sh`;
- instalar skills, pacotes ou plugins;
- alterar providers, MCPs, cron jobs ou perfis;
- enviar mensagens, emails ou publicações;
- criar ou alterar documentos compartilhados;
- fazer commit, push, deploy ou operação externa.

## Proibição

- Não expor segredos.
- Não modificar outro profile Hermes sem ordem explícita.
- Não copiar contexto de um microverso para outro.
- Não registrar dados pessoais no microverso de operações.
