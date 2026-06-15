---
name: excrtx-integrate-nlmops
description: Standard executable workflow for learning with NotebookLM in Exocórtex
  (CLI-first, MCP fallback), with automatic source ingestion and quality criteria.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - notebooklm
    - workflow
    - nlm
    - mcp
    - research
    calibration:
    - feature_id: EX-29
      calibration_prompt: Você deve garantir que as operações e regras da skill NotebookLM
        Ops (excrtx-integrate-nlmops) estão totalmente ativas no seu comportamento
        e integridade.
      test_prompt: Verifique se a skill define as 6 etapas do workflow NLM.
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill NotebookLM Ops.
      remediation_tip: Certifique-se de que a documentação e os limites da skill NotebookLM
        Ops em seu SKILL.md estão sendo estritamente seguidos.
---
# Exocortex NotebookLM Operational Workflow

## When to Use

Use when the request requires learning, synthesizing, organizing, or expanding knowledge via NotebookLM.

**Don't use for:** Simple facts already known to the agent (answer directly). Creative writing or brainstorming (no sources needed). Tasks not requiring synthesis or multi-source analysis. Web search only (use Hermes web search tool directly).

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
1. Find reliable sources using Hermes web search tool (`search_web`) or `excrtx-integrate-browser` for deep research. If both unavailable, ask the executive for URLs or documents.
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

- **Source ingestion timeout:** Large documents (>50 pages) may timeout during ingestion. Split into chunks or prefer URL sources over file uploads.
- **MCP connection drops:** Long-running MCP sessions to `notebooklm-mcp` can silently disconnect. Verify connection with a lightweight operation before heavy queries.
- **Auth token expiry mid-workflow:** NLM tokens can expire during multi-step workflows. Re-check `nlm login --check` before each major operation if the workflow exceeds ~30 minutes.
- **False auth positive:** `hermes mcp test notebooklm` validates transport only. Always confirm functional auth with `nlm login --check` or a real operation like `nlm notebook list`.
- **Source quality variance:** NotebookLM answers degrade with low-quality sources. Apply the Top 10 criteria strictly — one authoritative source is worth more than ten mediocre ones.
- **CLI vs MCP confusion:** Use CLI (`nlm`) as primary. MCP is fallback only for environment issues. Don't mix both in the same session.
