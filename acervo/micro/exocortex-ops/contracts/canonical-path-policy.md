---
type: decision
title: Política de Paths Canônicos
description: Paths documentados podem divergir do runtime real. Quando houver divergência, o Exocórtex deve registrar drift e veri...
tags: [paths, drift, runtime]
timestamp: 2026-06-05
class: perene
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
excrtx_type: rule
nature: contracts
sources: ['conversation:docbrain-check']
confidence: high
created: 2026-06-05
---

# Política de paths canônicos

Paths documentados podem divergir do runtime real. Quando houver divergência, o Exocórtex deve registrar drift e verificar antes de operar.

## Ordem de autoridade

1. Evidência de runtime atual verificada por ferramenta.
2. Configuração ativa do Hermes.
3. Skill operacional instalada.
4. Documentação do repositório.
5. Memória conversacional.

## Regra

Quando skill e runtime discordarem, não inventar reconciliação. Declarar o drift, operar sobre o path funcional verificado e propor correção da skill/documentação.
