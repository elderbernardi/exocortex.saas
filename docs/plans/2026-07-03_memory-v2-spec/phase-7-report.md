# Phase 7 — Execution Report (Advanced Human/Agent Interface)

> **Executed:** 2026-07-13 · **Status:** complete and deployed live

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

## Live deployment receipt

- Backup tag: `pre-phase7-live-deploy` at the pre-rollout live Acervo commit.
- Runtime rollback copies: `/tmp/phase7-live-backup-20260713/` (`SOUL.md` + both skills).
- Live Acervo commit: `771f7e2` (`acervo_interface.py` + updated `acervoctl.py` only).
- Skills deployed:
  - `excrtx-behavior-briefing` v2.0.0;
  - `excrtx-memory-manager` v3.1.0.
- SOUL recompiled from 20 live behavioral-rule sections.
- MCP Acervo root reconfirmed as `/home/ubuntu/exocortex/acervo`.
- Catalog rebuilt: 222 objects, 20 links, zero parse errors; doctor `ok:true`, zero errors.
- User gateway restarted and active.

### Real-agent conversational acceptance

All scenarios ran through `hermes chat -q` against the live runtime:

1. **Briefing:** used the Phase 7 canonical command, reported no pending items,
   explicitly marked calendar `not_configured`, and cited the context head.
2. **Decision posture:** produced options, trade-offs, questions, and an ADR
   skeleton without deciding for the executive; cited contracts/decisions.
3. **Research posture:** surfaced tensions and open questions without premature
   closure; cited canonical global paths.
4. **Temporal query:** used `as_of=2026-06-15`, explained that no retrieved item
   carried a `HISTORICAL` banner, and cited the June memory ADRs/contracts.

### Read-only regression found and fixed

The first research scenario exposed a legacy memory-manager rule that updated
`last_accessed_at` during READ. All test-induced timestamp/newline mutations were
restored byte-for-byte. Installer commit `353dc32` replaces that behavior with
disposable H12 retrieval-journal telemetry. The corrected skill was redeployed,
SOUL recompiled, and the research scenario rerun without canonical mutations.

Pre-existing dirty Acervo work remained untouched. The only deployment-side
derived change is `global/tools/state/catalog.sqlite` from the required reindex.
