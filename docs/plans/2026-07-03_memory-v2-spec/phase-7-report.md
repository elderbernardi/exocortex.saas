# Phase 7 — Execution Report (Advanced Human/Agent Interface)

> **Executed:** 2026-07-13 · **Status:** complete in installer; live deployment pending explicit approval

## Delivered

- `acervoctl briefing`: deterministic briefing v2 assembled from the canonical Acervo and derived catalog.
  - intentions overdue and upcoming, due-sorted;
  - open disputes and drafts awaiting governance;
  - significant episodes from the recent window;
  - `context/current-state.md` heads for active scopes;
  - optional JSON calendar join with explicit `not_configured|missing|joined` state;
  - detailed output under a hard 4k-token budget and compact output capped at 10 lines;
  - canonical path citations and explicit empty-state behavior.
- `acervoctl posture --mode decision|research`:
  - decision posture prioritizes contracts, conflicts, decisions, entities, intentions, and relevant knowledge;
  - research posture prioritizes reflections, conflicts, rejected alternatives, evidence, episodes, and open questions;
  - both enforce the Phase 3 scope/restricted-content guard, pack under budget, cite paths, and abstain explicitly.
- Existing temporal retrieval remains the conversational surface for “what did we believe in March?”, preserving `HISTORICAL` labels.
- `excrtx-behavior-briefing` upgraded to v2.0.0 and routed through the deterministic briefing verb.
- `excrtx-memory-manager` upgraded to v3.1.0 with natural-language routing for briefing, decision, research, and temporal requests.
- One-page PT-BR executive guide: `docs/guides/como-funciona-sua-memoria.md`.

## Verification

- 34 focused Phase 7/retrieval/control-plane tests passed.
- 170-test Memory v2 regression selection passed.
- CI memory-eval gate unchanged:
  - recall 79.5%;
  - precision 34.7%;
  - abstention 33.3%;
  - contamination 0.0%.
- Both changed skills pass deterministic D1 judgment.
- `git diff --check` passed.
- Global `compile_soul --validate-compiled-rules` still reports six pre-existing unrelated crawler/source skill desyncs; neither Phase 7 skill appears in that list.

## Acceptance mapping

| Roadmap requirement | Evidence |
|---|---|
| Briefing v2 | `acervoctl briefing` + fixture/CLI tests |
| Decision posture | typed `posture --mode decision` pack + tests |
| Research posture | typed `posture --mode research` pack + tests |
| Temporal Telegram phrasing | memory-manager routes natural phrase to temporal retrieval; live chat test pending deployment |
| Executive one-page guide | `docs/guides/como-funciona-sua-memoria.md` |

## Deployment boundary

Installer implementation is complete. Live deployment requires copying
`acervo_interface.py` and the updated `acervoctl.py` into the live Acervo,
deploying briefing v2 and memory-manager v3.1, recompiling SOUL rules, restarting
the user gateway, and running the golden conversational scenarios through
`hermes chat -q`. That operation is intentionally excluded from this commit.
