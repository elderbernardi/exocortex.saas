# Exocórtex Memory System v2 — Specification

> **Date:** 2026-07-03 · **Status:** Proposed (adoption: ADR-023) · **Scope:** memory & knowledge organization for Exocórtex.IA on Hermes Agent
> Produced as a full investigation: current-system audit (installer + live runtime), state-of-the-art research (~70 primary sources, agent memory + PKM + ontology + retrieval), and an implementable phased design.

## 1. Executive summary

**The diagnosis:** the June 2026 memory reform got the hard part right — Markdown canonical truth, semantic index as pointers, tools-first recall, hard prompt budgets. Research through mid-2026 independently validates every one of those bets (Anthropic went plain-files; OpenAI went scheduled consolidation; verbatim+agentic search beats extraction pipelines on accuracy at personal scale). What the system lacks is a **model of truth over time and people**: it cannot say *since when* a fact holds, *how sure* it is, *what happened* in a meeting, *who* someone is across domains, or *what was promised* — and its only answer to contradiction is destructive deprecation.

**The design:** keep the four planes (bootstrap → canonical Markdown → derived indexes → immutable evidence) and the authority ladder unchanged. Upgrade the object model (schema v0.2): one `type` axis instead of three, a `status` lifecycle scalar, bitemporal-lite validity (`observed_at`, `valid_from/until` + git as transaction time), an epistemic tier (`epistemic`, `confidence`, `sources`), and structured supersedence. Add the three missing memory types — **episodes, entities, intentions** — and make **contradiction a first-class object** with retrieval banners instead of silent flattening. Add a **catalog.sqlite** (rebuildable) for metadata/lexical retrieval and graceful degradation when Hindsight is down. Add a **daily consolidation loop** (distill episodes, refresh entities, reconcile conflicts) and a **trust gate** so web/email content can never silently become memory (documented attack class). Retrieval becomes a routed, budgeted, cited policy; evaluation becomes a versioned golden-question harness with a zero-contamination requirement.

**The bridge (human ↔ LLM):** one representation, two reading disciplines. Humans get domains, filenames, prose, and a 5-minute weekly digest of only the decisions that are genuinely theirs; agents get frontmatter facets, derived indexes, and enforced scope. No parallel "machine view" — machine views are always derived and rebuildable.

## 2. Documents

| # | File | Deliverable section |
|---|---|---|
| 01 | [01-diagnosis.md](01-diagnosis.md) | Phase 0 — current-system diagnosis (verified) |
| 02 | [02-research-map.md](02-research-map.md) | Research map with sources; consensus vs disputed |
| 03 | [03-principles.md](03-principles.md) | 12 design principles + rejected candidates |
| 04 | [04-architecture.md](04-architecture.md) | Four planes, storage decision, pipelines, security |
| 05 | [05-object-model.md](05-object-model.md) | Atomic unit, schema v0.2, object catalog, relations |
| 06 | [06-microverse-spec.md](06-microverse-spec.md) | Formal microverso model: types, lifecycle, sharing, scope |
| 07 | [07-retrieval-policy.md](07-retrieval-policy.md) | Routing table, pseudocode, budgets, packing, fallback |
| 08 | [08-write-policy.md](08-write-policy.md) | Ingestion pipeline, gates, conflict protocol, promotion |
| 09 | [09-human-interface.md](09-human-interface.md) | Dual-representation answer; executive surfaces & rituals |
| 10 | [10-evaluation.md](10-evaluation.md) | Metrics, fixture, golden questions, regression rule |
| 11 | [11-hypotheses.md](11-hypotheses.md) | 12 open hypotheses with experiments & decision metrics |
| 12 | [12-roadmap.md](12-roadmap.md) | Phases 0–7, effort, risks, tests, cut criteria |
| 13 | [13-artifacts/](13-artifacts/) | SCHEMA-v0.2, file examples, agent prompts, checklists, models |
| 14 | [14-final-recommendation.md](14-final-recommendation.md) | Preserve / abandon / redesign / first / test / human |

## 3. Relationship to existing canon

Builds on and does not contradict: ADR-013…018 (lifecycle/OKF), ADR-019/020/021 (routing), the memory-routing contract, and the acervoctl/MCP control plane. Supersedes on adoption: SCHEMA v1.0.0 (via v0.2), the deprecate-only conflict flow, and the dual `groups.md`. Phase 0 of the roadmap repairs ten verified spec/implementation drift items regardless of whether the rest is adopted.
