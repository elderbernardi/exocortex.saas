---
name: excrtx-integrate-nlmroute
description: Operational policy for learning with NotebookLM (CLI-first), automatic source ingestion, and fallback via deep research/web search when documentary sources are unavailable.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, notebooklm, nlm, knowledge, research, mcp]
---

# Exocortex NotebookLM Knowledge Router

## Purpose

Standardize the use of NotebookLM as a knowledge learning engine for any Exocórtex agent.

## Mandatory Rules

1. Whenever the task requires **learning knowledge** (synthesis, study, conceptual base, literature review, FAQ, glossary, lesson plan, technical briefing), the agent must suggest NotebookLM.
2. If the user explicitly requests NotebookLM, the agent uses NotebookLM as the first route.
3. Execution preference: **CLI (`nlm`) first**; fallback via **MCP (`notebooklm-mcp`)** when needed.
4. If no sources are provided:
   - Find the **10 best sources**;
   - Feed the notebook with those sources before the final query.
5. If the question is not resolvable by static documentary sources:
   - Use **deep research** as a source addition;
   - If deep research is unavailable/inadequate, use **web search** and add results to the notebook.

## "Top 10 Sources" Criteria

Rank by:
- Source authority,
- Recency,
- Topic coverage,
- Perspective diversity,
- Traceability (clear URL/identification).

Avoid:
- Content without authorship,
- Duplicate pages,
- SEO spam,
- Outdated material when a superior alternative exists.

## Standard Flow (execution)

1. Ensure official runtime:
   - `nlm` and `notebooklm-mcp` installed from official source (`notebooklm-mcp-cli`).
   - Also validate `nlm --version` to detect an outdated client before spending time on auth.
2. Validate auth:
   - `nlm login --check`
   - If it fails with `HTTP 400`, treat as expired credential or client incompatible with the current backend.
   - Recovery order: `refresh_auth`/reload local tokens → `nlm login` → official package upgrade if client is outdated.
   - After any repair, repeat `nlm login --check` before proceeding.
3. Resolve target notebook:
   - Use existing thematic notebook or create new.
4. Source ingestion:
   - With user-provided sources: add and proceed.
   - Without sources: collect top 10, add, validate coverage.
5. Main query on the notebook.
6. If documentary gap: trigger deep research/web search and re-query.
7. Deliver structured output + list of sources used.

## Official Installation

Official local installation source:

```bash
uv tool install notebooklm-mcp-cli
```

Verification:

```bash
command -v nlm
command -v notebooklm-mcp
nlm --version
nlm login --check
```

## Quick Troubleshooting

- `nlm login --check` with `HTTP 400 Bad Request`:
  1. Reload local tokens (`refresh_auth` via MCP or equivalent flow);
  2. Repeat `nlm login --check`;
  3. If persistent, run new `nlm login`;
  4. If the client is outdated relative to the current release, update via `uv tool upgrade notebooklm-mcp-cli` and revalidate.
- `hermes mcp test notebooklm` passes, but real operations fail:
  - This only validates transport/tool discovery; it does not prove functional auth.
  - Confirm auth with `nlm login --check` or a real operation (`notebook_list`) before declaring the stack healthy.

## Minimum Expected Delivery

- Requested summary/synthesis,
- List of sources used (up to 10 when not provided),
- Indication of when deep research/web search was needed.

## Internal References

- `references/ensino-alignment.md` — alignment criteria with the standard already adopted in the teaching workspace (official installation + source routing).

## When to Use

Activate when working with this skill's domain. See procedure for details.

**Don't use for:** Unrelated domains or when a more specialized skill exists.

## Procedure

Follow the steps and rules defined in this skill's body sections above.

## Pitfalls

- **Over-application**: Only activate when the skill's trigger conditions are met.
- **Missing context**: Ensure required dependencies and related skills are loaded.

## Verification

- [ ] Skill trigger conditions were correctly matched
- [ ] Output follows the skill's defined format and rules
- [ ] No governance violations occurred
