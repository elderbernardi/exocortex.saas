---
name: excrtx-integrate-nlmroute
description: Operational policy for learning with NotebookLM (CLI-first), automatic source ingestion, and fallback via deep
  research/web search when documentary sources are unavailable.
version: 1.1.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - notebooklm
    - nlm
    - knowledge
    - research
    - mcp
    related_skills:
    - excrtx-integrate-nlmops
    - excrtx-memory-manager
    calibration:
    - feature_id: EX-28
      calibration_prompt: 'Você define a política operacional para aprendizado com NotebookLM. Rota CLI-first (nlm) com fallback
        MCP (notebooklm-mcp). Quando sem fontes: busca as 10 melhores por autoridade e atualidade.'
      test_prompt: Quero aprender sobre 'regulação de IA na União Europeia'. Use o NotebookLM para sintetizar as melhores
        fontes.
      acceptance_criteria: '1. O agente tenta usar a rota CLI-first (nlm) antes do MCP

        2. Se não há fontes fornecidas, busca as melhores por autoridade e atualidade

        3. O critério de seleção de fontes é transparente (explica por que escolheu cada uma)

        4. Se nlm não está instalado, oferece fallback ou orienta instalação'
      remediation_tip: 'FALHA: Rota incorreta ou fontes não curadas. A política exige: 1) CLI-first: ''nlm'' (verificar com
        ''which nlm''), 2) Se sem fontes: buscar 10 melhores por autoridade+atualidade+cobertura+diversidade, 3) Se lacuna
        documental: deep research → web search → re-query. Versão mínima do nlm: 0.7.0.'
---
# Exocortex NotebookLM Knowledge Router

Standardize the use of NotebookLM as a knowledge learning engine for any Exocórtex agent.

## When to Use

- Task requires **learning knowledge**: synthesis, study, conceptual base, literature review, FAQ, glossary, lesson plan, or technical briefing
- The executive explicitly requests NotebookLM
- Sources need to be curated and ingested into a structured notebook

**Don't use for:** Simple web searches without knowledge synthesis. Local file management (use `excrtx-memory-manager`). NLM operational commands like notebook creation (use `excrtx-integrate-nlmops`). Tasks that don't require persistent knowledge bases.

## Procedure

### Step 1 — Validate Runtime

```bash
nlm --version          # Must be >= 0.7.0
command -v notebooklm-mcp
```

If missing, install: `uv tool install notebooklm-mcp-cli`

### Step 2 — Validate Authentication

```bash
nlm login --check
```

| Outcome | Action |
|---------|--------|
| Success | Proceed to Step 3 |
| `HTTP 400` | Run `nlm login` to re-authenticate |
| Persistent failure | Upgrade client: `uv tool upgrade notebooklm-mcp-cli`, then retry |

> **Warning:** `hermes mcp test notebooklm` only validates transport/discovery — it does NOT prove functional auth. Always confirm with `nlm login --check`.

### Step 3 — Resolve Target Notebook

Use existing thematic notebook or create a new one via `excrtx-integrate-nlmops`.

### Step 4 — Source Ingestion

| Scenario | Action |
|----------|--------|
| User provides sources | Add them directly to the notebook |
| No sources provided | Collect **Top 10 Sources** (see criteria below), add, validate coverage |

**Top 10 Sources Criteria** — rank by:

| Factor | Weight |
|--------|--------|
| Source authority | High |
| Recency | High |
| Topic coverage | Medium |
| Perspective diversity | Medium |
| Traceability (clear URL) | Required |

**Reject:** Content without authorship, duplicate pages, SEO spam, outdated material when a superior alternative exists.

### Step 5 — Query and Synthesis

1. Run main query on the notebook
2. If documentary gap detected: trigger deep research or web search, add results, re-query
3. Classify operation as Vetor `evol` (knowledge evolution)

### Step 6 — Deliver Output

Minimum delivery:
- Requested summary/synthesis
- List of sources used (up to 10 when not user-provided)
- Indication of when deep research/web search was needed

## Pitfalls

- **Auth false positive:** `hermes mcp test notebooklm` passes but real operations fail. Always validate with `nlm login --check` or a real operation (`nlm notebook list`).
- **Client version mismatch:** Versions < 0.7.0 have broken auth protocol. Always check version first.
- **Source ingestion timeout:** Large documents (>50 pages) may timeout during ingestion. Split into chunks or use URL sources instead of uploads.
- **Token refresh race:** If `HTTP 400` on `nlm login --check`, don't retry indefinitely. Try refresh → login → upgrade, in that order.
- **MCP vs CLI confusion:** CLI (`nlm`) is preferred for reliability. MCP (`notebooklm-mcp`) is fallback only.

## Verification

- [ ] `nlm --version` returns >= 0.7.0
- [ ] `nlm login --check` returns success
- [ ] Notebook contains ingested sources (verify with `nlm notebook list`)
- [ ] Output includes source list with URLs/identifiers
- [ ] Deep research/web search indicated when documentary gap occurred
- [ ] Knowledge output stored in appropriate Acervo layer

## References

- `references/ensino-alignment.md` — alignment criteria with the standard already adopted in the teaching workspace.
