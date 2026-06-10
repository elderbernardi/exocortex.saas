---
name: excrtx-memory-wikiadapt
description: "Safe adapter between the native research/llm-wiki skill and Acervo Cognitivo v2."
version: 1.0.0
author: Exocórtex
metadata:
  hermes:
    tags: [exocortex, wiki, adapter, acervo, memory]
---

# Wiki Adapter — llm-wiki ↔ Acervo v2

Safe bridge between the native `research/llm-wiki` skill and the Acervo Cognitivo.

## Problem

`research/llm-wiki` writes to `~/.hermes/wiki/` — outside the Acervo. Without this adapter, wiki writes bypass the Domain Filter and scope isolation of `excrtx-memory-manager`.

## Trigger

Activate when:
- The agent calls `research/llm-wiki` to create or update wiki pages
- Content needs to be synced between `~/.hermes/wiki/` and the Acervo

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
