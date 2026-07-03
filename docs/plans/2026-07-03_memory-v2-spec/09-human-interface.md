# 09 — Human Interface

## 1. The dual-representation question (F) — answered

**There is one representation with two reading disciplines, not two representations.** (P10.)

- The human reads: filenames, titles, prose bodies, generated MOC indexes, the briefing, git diffs.
- The machine reads: the same files' frontmatter, the derived catalog, the semantic index.
- Divergence is prevented structurally: machine views are derived and rebuildable (P1); the validator enforces that the human-visible axis (directory) and the machine axis (`type:`) agree; the reconcile cron measures drift instead of trusting hooks.

Frontmatter without bureaucracy (F.7): Tier 0 is seven fields a human writes by hand in 30 seconds; Tiers 1–2 are agent-filled on ingestion — if the executive drops a bare note into `_inbox/`, triage dresses it. The human is never blocked by schema; the agent is never allowed to skip it.

## 2. Interaction surfaces (all existing: Telegram + CLI; no new UI required)

Everything below is phrasing the executive already uses naturally — mapped to skills/routines, not new commands to memorize. (Formal `acervoctl` verbs exist for the engineer; the executive talks.)

| Executive says (PT-BR) | System does |
|---|---|
| *"anota isso"* / *"guarda isso"* | quick capture → `_inbox/` → triage proposes scope+type; confirms in one line |
| *"lembra que combinei X com Y até sexta"* | intention object (`owed_to: Y`, `due:`) + entity log line |
| *"o que temos sobre X?"* | scoped retrieval with citations (07) |
| *"o que decidimos sobre X? por quê?"* | decision chain incl. rejected alternatives |
| *"o que eu acreditava sobre X em março?"* | temporal query, HISTORICAL-labeled |
| *"quem é X?"* / *"como está a relação com X?"* | entity page + recent episodes |
| *"briefing"* (or 07:30 routine) | pending intentions (due-sorted), calendar joined, open disputes, yesterday's episodes, context heads of active scopes — ≤ 4k tokens, links to everything |
| *"pendências"* | active intentions + kanban + drafts awaiting approval |
| *"modo pesquisa"* | Evolução posture: retrieves reflections/tensions/questions, not conclusions (P11) |
| *"modo decisão sobre X"* | packs decision-relevant memory: prior decisions, contracts, disputes, entity stakes; drafts the ADR skeleton, executive decides |
| *"arquiva o microverso X"* | lifecycle transition (06 §4), Draft-first |
| *"faxina"* / weekly digest | Manutenção: syndic report, disputes to resolve, review_after expiries, drafts pending — as questions, one line each |

## 3. Review rituals (the minimum viable human loop)

Three, all initiated by the system, all skippable without breaking anything:

1. **Morning briefing** (existing routine, upgraded to read intentions/episodes).
2. **Weekly maintenance digest** — the *only* place the human is asked to govern: open disputes (pick A/B/keep both), pending drafts (approve/reject), dormancy confirmations, quarantine notices before purge. Each item is one line + one question. Target: < 5 minutes.
3. **Decision review** (monthly or on `review_after`): decisions whose review date passed — "still true?".

Everything else the agent maintains alone (P11). If the executive ignores the digest for a month, the system degrades gracefully: disputes stay open (both sides retrievable with banners), drafts stay drafts, nothing is silently committed or purged past its window without notice — the purge notice repeats until acknowledged or restored.

## 4. Navigation for the human

- `acervo/` opens cleanly in Obsidian/any editor: shallow dirs, meaningful names, wikilinks work.
- Each container's `_meta/index.md` is a generated MOC: newest first, grouped by type, one line each.
- `global/_meta/index.md` head section is the only hand-curated map (home MOC).
- git history *is* the audit UI: "what changed in my memory this week" = `git log --stat -- acervo/`.
