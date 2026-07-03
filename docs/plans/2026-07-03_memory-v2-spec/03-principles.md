# 03 — Design Principles

> Normative. Every schema field, pipeline stage, and skill rule in this spec must trace to one of these principles. When two principles conflict in practice, the lower-numbered one wins.

## P1 — Canonical truth is human-readable, and every machine view is derived

The Acervo (Markdown + YAML frontmatter, on a filesystem, under git) is the only source of truth. Catalogs, embeddings, Hindsight entries, graphs, SQLite indexes are **derived artifacts**: rebuildable from the files at any time, never authoritative, allowed to be stale, forbidden to disagree silently (reconciliation must detect drift). A system the executive cannot audit with `less` and `grep` is a black box; a black box cannot hold a person's cognitive universe for ten years.

*Consequence:* no memory operation is complete until the canonical file is written. Index/embedding failures degrade retrieval, never truth.

## P2 — Memory is a governed process, not storage

Storage is cheap; attention is not. Every object enters through an explicit pipeline (captured → … → committed) with a decision at each gate: promote, discard, or hold. Whatever bypasses the pipeline (raw dumps, transcripts, auto-retained observations) is by definition **not memory** — it is source material that memory may later be distilled from.

*Consequence:* Hindsight auto-retain output, session transcripts, and inbox files are sources, not memories. They carry no authority.

## P3 — The past is preserved; only retrieval defaults change

Nothing true is deleted because it stopped being current. The system distinguishes:

- **superseded** — was true, replaced by newer truth (kept, linked, excluded from default retrieval);
- **deprecated** — was wrong or never useful (kept until quarantine/purge);
- **archived** — closed context, no longer operational (kept indefinitely).

"In March we believed X; in May we discovered Y" must be representable and retrievable *on request*, and invisible *by default*. Forgetting is implemented as retrieval scoping, not as data loss — except for genuine junk, which purges via the existing quarantine window.

## P4 — Every claim carries provenance and epistemic status

A memory without a source is an opinion of the system about itself. Every knowledge/decision/context object records where it came from (`sources`), when the world showed it (`observed_at`), and what kind of assertion it is (`epistemic: fact | observation | interpretation | hypothesis | decision | preference | rule | intention`). The LLM must never present a hypothesis with the confidence of a contract. Retrieval attaches these labels to packed context so downstream reasoning inherits them.

## P5 — Contradiction is a first-class state, not an error

When new information conflicts with existing memory there are three honest outcomes: **supersede** (clean replacement of volatile fact), **dispute** (both live; a conflict object records the tension), or **coexist** (different scopes/aspects). Silent overwriting and silent averaging are forbidden — both manufacture coherence the world does not have. Disputed objects are retrieved *with* their dispute attached.

## P6 — Scope before search

No retrieval or write happens without a resolved scope (microverso + layer). Microversos are cognitive namespaces: isolation is the default, bridges (`shared/`) are explicit, and cross-scope reads are logged. Contamination — client A's context leaking into client B's draft — is the memory-system failure the executive will actually fire the system for.

## P7 — Context budget is a product constraint

Tokens in the prompt are the scarcest resource. The fast layer only bootstraps (ADR-021 budgets are law); everything else is fetched on demand, packed to an explicit budget, most-relevant-first, with pointers instead of bodies wherever a pointer suffices (ADR-020 doctrine). More memory in the prompt is not better memory; it is worse routing.

## P8 — Summaries point, sources speak

Summarize only what has an immutable source underneath, link the source, and prefer *lazy* summarization (at read time, for the task at hand) over eager compaction that bakes in one interpretation forever. When nuance matters — contracts, decisions, personal style — quote or load verbatim. Over-summarization is silent data loss.

## P9 — Structure must be lazy and earned

Directories, natures, indexes, and entity pages are created when content demands them, not preemptively. Empty scaffolding is junk-drawer bait and misleads both human navigation and agent routing. The same holds for metadata: the mandatory tier stays small (a file a human writes by hand in 30 seconds); richer tiers activate only for the object types that need them.

## P10 — The human's model and the machine's model are the same model

One structure, readable by both. Humans get prose bodies, meaningful filenames, MOC-style indexes; machines get frontmatter, stable IDs, and derived catalogs — **on the same files**. Divergent "human view vs machine view" stores are forbidden (they always fork). Where the machine needs shapes humans won't maintain (embeddings, adjacency), it derives them (P1) rather than asking the human to maintain a graph.

## P11 — The agent maintains; the human decides

Agents write, revise, consolidate, index, and flag autonomously *within governed bounds*; the executive decides identity (macro), rules (contracts), disputes, and anything Draft-First classifies as external. Every autonomous mutation is journaled and reversible for its review window. The system must never steal the executive's learning: in Evolução mode it retrieves questions, tensions and prior reasoning — not conclusions.

## P12 — Degrade gracefully, verify empirically

Every retrieval path has a filesystem-only fallback (catalog + grep) for when Hindsight/Postgres is down. Every claim of "memory works" is backed by the evaluation battery (10-evaluation.md), run on synthetic fixtures plus live probes — EX-49 applied to the memory system itself.

---

### Explicitly rejected candidate principles

- **"No cross-microverse duplication, ever"** — rejected as absolute. Deliberate, marked duplication (a cached quote of a global contract inside a client deliverable) is sometimes operationally necessary; the rule is *no unmarked duplication*: copies must declare `canonical_from`.
- **"Memory must decay unless promoted"** — rejected as stated. Decay applies to *retrieval salience* and to `volátil` lifecycle, never to canonical truth (P3). A ten-year archive that silently rots is not an exocortex.
- **"Human approval for all writes"** — rejected. It does not scale past week one and produces rubber-stamping. Approval is risk-tiered (08-write-policy.md).
- **"Claim-level atomicity everywhere"** — rejected. Files are the atom; claims get anchors only where contradiction management pays for them (H3 in 11-hypotheses.md).
