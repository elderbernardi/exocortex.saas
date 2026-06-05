---
title: Política de Paths Canônicos
created: 2026-06-05
updated: 2026-06-05
nature: contracts
type: rule
tags: [paths, drift, runtime]
sources: [conversation:docbrain-check]
confidence: high
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
