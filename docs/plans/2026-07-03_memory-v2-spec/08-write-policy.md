# 08 — Ingestion, Write, Update & Deprecation Policy

## 1. Ingestion pipeline (question D)

```text
captured → normalized → classified → extracted → proposed → committed → indexed
                                                     ↘ discarded (logged)
committed → (later) consolidated → superseded / archived / quarantined → purged
```

The prompt's candidate pipeline is kept but **`reviewed` is folded into two concrete gates** (trust gate at `proposed`, review window post-commit) — a standing "reviewed" state was found to be where items go to die in second-brain practice (collector's fallacy).

**Stage rules:**

- **captured** — anything enters `_inbox/` (Telegram file, email, note, PDF) or arrives as conversation. Original is preserved byte-exact. *Nothing in `_inbox/` or `raw/` is memory* (P2).
- **normalized** — docBrain (heavy docs: PDF/CSV/web → Markdown + checksums) or plain copy. Original moves to the target scope's `raw/` on promotion.
- **classified** — scope (06 §7) + type (05 §3) + trust level of source.
- **extracted** — candidate objects distilled (facts→knowledge, commitments→intentions, decisions→decision drafts, events→episode draft). Extraction always records `sources:` + `extraction:` (HaluMem warning: extraction loses >40% — the raw source surviving is what makes that survivable).
- **proposed → committed** — gates below.
- **indexed** — catalog upsert, index.md regen, Hindsight index-file (best-effort; reconcile catches drift).

### Per-input routing (D.1–D.9)

| Input | Raw kept? | Becomes | Decider |
|---|---|---|---|
| Conversations w/ executive | state.db (always) | episode (if significant) + extracted decisions/intentions/knowledge | consolidation agent; executive flag forces |
| Telegram quick notes | inbox item | knowledge/intention per content; else discard-after-triage | triage routine |
| Emails | raw/ on promotion | entity interaction-log line + intentions (commitments!) + knowledge | triage; **untrusted-source gate applies** |
| Meetings (transcripts/minutes) | raw/ | episode + decisions + intentions | consolidation; exec approves decisions |
| PDFs/docs/sheets/decks | raw/ via docBrain | knowledge (curated claims w/ provenance) + artifact if it's ours | docBrain adapter → proposed |
| Web/research | docBrain wiki (working area) | knowledge only on explicit promotion | **never auto-commits (trust gate)** |
| Agent outputs | _artifacts/ | artifact; knowledge/decision only by promotion | producing agent proposes |
| Public company data | raw/ + source URL | knowledge with `observed_at` + `review_after` | pipeline, auto-commit OK (low risk, dated) |
| Tasks/calendar/CRM | native systems | intentions only for *commitments*; pointers otherwise | briefing/triage |
| Operational logs | logs | nothing (session_search/evidence) | — |

**Discard criteria (anti-junk):** no identifiable scope after triage question; duplicate of active object (enrich instead); transcript-shaped content (evidence, not memory); speculation with no source and no owner; anything whose only virtue is "might be useful someday" (collector's fallacy — the raw stays in `raw/` anyway if it came as a file; *memory* is not created for it). Every discard journals one line — auditability without storage.

## 2. Commit gates

```text
TRUST GATE   content from web/email/third-party docs → status: draft, requires
             executive or verifying-agent approval to become active.
             (SpAIware/AgentPoison class defense — untrusted text must never
             silently become persistent instruction/memory.)

RISK GATE    macro/* , global/contracts/* , global/decisions/*, persona, any
             promotion to perene, any merge/retire of microverso
                → DRAFT-first, executive approves.
             micro volatile knowledge/context/episodes/intentions/entities
                → governed auto-commit (journaled, 7-day review window in
                  maintenance digest, reversible via git + status flip).
```

This is P11 operationalized: risk-tiered approval, not approve-everything (rubber stamp) nor auto-everything (poisoning + drift).

## 3. Update rules by mutability class

| Class | Objects | Rule |
|---|---|---|
| **Rewrite-in-place** | context heads, entity profile sections, index (generated), workflows in draft | present-state models; git holds history |
| **Append-only** | entity interaction logs, journals/log.md, episode addenda | event streams |
| **Immutable + supersede** | decisions, contracts (post-approval), knowledge facts, episodes (post-window), artifacts | change = new object + `supersedes:`; pipeline sets `superseded_by` + `status: superseded` on the old one atomically |

## 4. Conflict protocol (P5; replaces "deprecate-on-insert" as the only verb)

`detect_conflict` (07 §3) classifies each overlap:

1. **same-assertion** → NOOP or enrich existing (add source, raise confidence). No new file.
2. **supersession** (old is `volátil`, new plainly replaces: price, config, status) → auto: new `active`, old `superseded` + links. Journaled `SUPERSEDED`.
3. **dispute** (both claims have standing sources; or old is `perene`/decision) → create `conflict` object; both sides get `disputed_by`; **executive resolves** (maintenance digest carries open disputes). Resolution: winner stays active (confidence↑), loser superseded, conflict object records the resolution rationale → it *is* the decision trail.
4. **coexist** (different scopes/aspects/timeframes) → both active; `relates_to` link; valid-time windows disambiguate.

`excrtx-memory-deprecate` survives for genuine junk/wrongness (`deprecated` = was never true / no longer worth keeping), feeding quarantine as today. **Supersession never routes through deprecation.**

## 5. Promotion / demotion

- volátil → perene: `promoted_at` (existing mechanism), requires reading-layer rules; used sparingly.
- micro → global: only when referenced from 2+ microversos (existing threshold) — via `canonical_from` move, tombstone pointer left behind.
- reflection → contract/workflow: only with executive sign-off (it's a rule change).
- knowledge → USER.md/MEMORY.md: only under ADR-021's "needed before first tool call" test.
- artifact/docBrain page → knowledge: explicit adapter promotion with provenance carried.

## 6. Consolidation & deprecation cadence (existing skills, extended)

- **write-time**: conflict protocol (above) — cheap, incremental (ATOM/LazyGraphRAG lesson: no LLM-heavy batch rebuilds).
- **daily** (`manut`): index reconcile (exists) + episode distillation for yesterday's significant sessions + entity refresh queue + intentions expiry sweep.
- **weekly** (syndic, exists): stale-volatile quarantine (90d), long-deprecated quarantine (180d), purge expired (30d window), dedup audit, orphan/broken-link report, `review_after` expiries, open disputes digest.
- **never**: auto-delete anything `perene`, any decision, any episode, any entity with interaction history (relationship memory ages like wine, not milk).

## 7. Write checklist (the one the agent actually runs)

1. Scope resolved? (hard-fail if write + unresolved)
2. Right object type? Right home dir (= type)?
3. Title passes title-as-API test?
4. Tier-0 complete; Tier-1 if knowledge/context/decision/reflection/entity?
5. Sources present? `observed_at` for world-facts? `valid_*` for dated facts?
6. Trust gate: source untrusted → draft.
7. Risk gate: perene/global/macro/contract → DRAFT for executive.
8. `detect_conflict` ran; verdicts applied.
9. Entities resolved via aliases (no new entity page without alias check).
10. Committed via control plane (`acervoctl`/MCP) → journal → hooks fired.
11. Validator passes (v0.2); links resolve.
