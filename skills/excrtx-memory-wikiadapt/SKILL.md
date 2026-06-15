---
name: excrtx-memory-wikiadapt
description: Safe adapter between the native research/llm-wiki skill and Acervo Cognitivo v2.
version: 1.0.0
category: excrtx
platforms:
- linux
author: Exocórtex
metadata:
  hermes:
    tags:
    - exocortex
    - wiki
    - adapter
    - acervo
    - memory
    calibration:
    - feature_id: EX-12
      calibration_prompt: Você é a bridge entre a LLM Wiki nativa do Hermes e o Acervo Cognitivo v2. Traduz categorias LLM
        Wiki (entity, concept, comparison, query, raw) para a Ontologia Multifocal v2 (context, knowledge, contracts, etc).
        Impede escrita direta da LLM Wiki no Acervo — sempre passa pelo memory-manager.
      test_prompt: Aprendi algo importante sobre 'serverless databases' hoje. Salve esse conhecimento no wiki e garanta que
        fica acessível no acervo.
      acceptance_criteria: '1. O agente NÃO grava diretamente no Acervo — usa o fluxo wiki → wikiadapt → memory-manager

        2. Classifica o tipo de conhecimento (concept/entity/knowledge) antes de persistir

        3. Traduz a categoria wiki para a Nature correta do Acervo (ex: concept → knowledge)

        4. Pergunta em qual escopo gravar (global vs micro) se for ambíguo'
      remediation_tip: 'FALHA: Escrita direta no Acervo sem passar pelo adapter. O fluxo correto é: llm-wiki → wikiadapt (traduz
        categoria) → memory-manager → Acervo. A wiki jamais deve escrever diretamente em $ACERVO/. Verifique se a Nature de
        destino corresponde à categoria wiki original.'
---
# Wiki Adapter — llm-wiki ↔ Acervo v2

Safe bridge between the native `research/llm-wiki` skill and the Acervo Cognitivo.

## Problem

`research/llm-wiki` writes to `~/.hermes/wiki/` — outside the Acervo. Without this adapter, wiki writes bypass the Domain Filter and scope isolation of `excrtx-memory-manager`.

## When to Use

Activate when:
- The agent calls `research/llm-wiki` to create or update wiki pages
- Content needs to be synced between `~/.hermes/wiki/` and the Acervo

**Don't use for:** Direct Acervo writes without wiki involvement (use `excrtx-memory-manager`). Microverso installation (use `excrtx-memory-mvinstall`). Knowledge intake from external sources (use `excrtx-memory-intake`).

## Procedure

### 1. Intercept wiki write

When `llm-wiki` writes a page:

1. **Classify content** — which microverso does this belong to?
2. **Apply Domain Filter** from `excrtx-memory-manager` (Operation: WRITE)
3. **Write to Acervo** at the correct path (`micro/{slug}/{nature}/`)
4. **Register in wiki** — keep a pointer in `~/.hermes/wiki/` linking to the Acervo path

### 2. Intercept wiki read

When `llm-wiki` reads a page:

1. **Check Acervo first** — does the content exist in the Acervo?
2. **If yes** → serve from Acervo (authoritative source)
3. **If no** → serve from wiki (fallback) and suggest promotion to Acervo

### 3. Sync direction

```
Authoritative: Acervo → wiki (one-way)
Wiki is a cache/pointer, never the source of truth.
```

## Rules

- Never let `llm-wiki` write directly to microverso paths without Domain Filter
- Never duplicate content — use pointers
- Acervo is always authoritative over wiki
- If scope denies access to a microverso, the wiki adapter must respect it

## Verification

- [ ] Wiki write triggers Domain Filter
- [ ] Content lands in correct Acervo path
- [ ] Wiki pointer references Acervo location
- [ ] Scope restrictions respected

## Pitfalls

- **Over-application**: Only activate when the skill's trigger conditions are met.
- **Missing context**: Ensure required dependencies and related skills are loaded.
