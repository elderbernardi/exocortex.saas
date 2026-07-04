---
schema: acervo/v0.2
type: skill
title: Roteamento de Manutenção Operacional
description: Usar Macroverso e skills de onboarding.
tags: [maintenance, routing, ops]
timestamp: 2026-06-05
class: volátil
status: active
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
nature: skills
sources: []
confidence: high
created: 2026-06-05
---

# Roteamento de manutenção operacional

## Se o pedido é sobre identidade ou onboarding
Usar Macroverso e skills de onboarding.

## Se o pedido é sobre acervo ou microversos
Usar `excrtx-memory-manager`, `excrtx-memory-newmicro` e este microverso.

## Se o pedido é sobre Hermes Agent
Usar `hermes-agent` e comandos reais.

## Se o pedido é sobre parser/intake documental
Usar DocBrain via CLI API e registrar drift se paths não baterem.

## Se o pedido é sobre memória externa
Verificar `hermes memory status` antes de responder.
