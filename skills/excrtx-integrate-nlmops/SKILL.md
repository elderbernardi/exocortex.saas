---
name: excrtx-integrate-nlmops
description: Standard executable workflow for learning with NotebookLM in Exocórtex (CLI-first, MCP fallback), with automatic source ingestion and quality criteria.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, notebooklm, workflow, nlm, mcp, research]
---

# Exocortex NotebookLM Operational Workflow

## When to Use

Use when the request requires learning, synthesizing, organizing, or expanding knowledge.

## Procedure

### Step 0 — Quick Gate

1. Verify runtime:
```bash
command -v nlm
command -v notebooklm-mcp
nlm --version
```
2. Verify authentication:
```bash
nlm login --check
```
3. Verify Hermes binding when using MCP:
```bash
hermes mcp list
```
Confirm `notebooklm` is enabled.
4. If auth fails: run `nlm login` and guide remote flow via chat (authorization URL + final URL pasted).
5. If MCP is not enabled, register explicit fallback to CLI-only track before continuing.

Operational rule: first ensure the acquisition chain (source + access + integration), then start synthesis and learning cards.

### Step 1 — Resolve Target Notebook

- Reuse existing thematic notebook when appropriate.
- Create new notebook when the topic requires isolation.

Useful commands:
```bash
nlm notebook list --title
nlm notebook create "<TOPIC>"
```

### Step 2 — Source Ingestion

#### Case A: user provided sources
Add and validate minimum coverage.

#### Case B: user did not provide sources
1. Find reliable sources.
2. Select top 10 by authority, recency, coverage, and diversity.
3. Add to notebook before querying.

Target: notebook with 10 relevant sources (or justify fewer when the domain doesn't support more).

### Step 3 — Main Query

Execute the main query on the notebook only after minimum ingestion.

```bash
nlm notebook query <notebook_id> "<QUESTION>"
```

### Step 4 — Documentary Gap

If the answer depends on dynamic or non-documentary information:
1. Use deep research as a source,
2. Fall back to web search,
3. Add the results to the notebook,
4. Re-execute the main query.

### Step 5 — Minimum Delivery

Every delivery must contain:
1. Requested answer/synthesis,
2. List of sources used,
3. Explicit indication if deep research/web search was needed,
4. Limitations and confidence of the answer.

## MCP Fallback

If the CLI track fails due to environment issues, use MCP tools `notebooklm-*` with the same logical protocol (auth, notebook, sources, query, gap, delivery).

## Verification

- [ ] `nlm login --check` passed
- [ ] Correct notebook selected/created
- [ ] Sufficient and traceable sources
- [ ] Final query executed after ingestion
- [ ] Deep research/web search triggered when needed
- [ ] Sources cited in final output

## Pitfalls

- **Over-application**: Only activate when the skill's trigger conditions are met.
- **Missing context**: Ensure required dependencies and related skills are loaded.
