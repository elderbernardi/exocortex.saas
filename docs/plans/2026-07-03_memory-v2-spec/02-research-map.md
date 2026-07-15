# 02 — Research Map (state of the art through 2026-07)

> Condensed from two research sweeps (~70 primary sources; agent-memory systems/benchmarks, and PKM/ontology/retrieval). Full citations inline. **Bold** = finding this spec directly builds on. Consensus vs disputed is marked.

## A. Agent memory systems

| System / work | Core idea | Relevance to Exocórtex |
|---|---|---|
| MemGPT → Letta ([2310.08560](https://arxiv.org/abs/2310.08560); [memory blocks](https://www.letta.com/blog/memory-blocks/)) | Self-edited, labeled, **size-capped context blocks**; background **sleep-time compute** ([2504.13171](https://arxiv.org/abs/2504.13171)) rewrites memory off the hot path | Validates ADR-021 budgets and motivates the v2 consolidation loop (04 §4) |
| Mem0 ([2504.19413](https://arxiv.org/abs/2504.19413)) / LangMem / MemoryBank ([2305.10250](https://arxiv.org/abs/2305.10250)) | Extract → reconcile (**ADD/UPDATE/DELETE/NOOP**); namespaces; Ebbinghaus decay | The reconcile verbs become v2's supersede/dispute/coexist (08); decay stays retrieval-side only (P3) |
| Zep/Graphiti ([2501.13956](https://arxiv.org/abs/2501.13956)) | **Bitemporal fact edges (`valid_at`/`invalid_at`); contradiction → invalidate, never delete**; LLM-free query path | Direct blueprint for v2 temporal fields + supersedence (05). Their −17.7% on verbatim recall proves lossy summarization hurts — sources must survive |
| HippoRAG 2 ([2502.14802](https://arxiv.org/abs/2502.14802)), GraphRAG → **LazyGraphRAG** ([MSR](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/)), LightRAG | Graphs win multi-hop/temporal; **LLM-heavy batch indexing is a cost trap**; cheap incremental graphs + query-time synthesis win | v2 graph = wikilinks + entities + derived adjacency in SQLite; no graph DB, no eager community summaries |
| **Anthropic**: memory tool, Claude Code `MEMORY.md` ([docs](https://code.claude.com/docs/en/memory)); **OpenAI**: "Dreaming V3" ([2026-06-04](https://openai.com/index/chatgpt-memory-dreaming/)) | Both labs converged from opposite directions: **plain agent-edited files** (Anthropic) and **scheduled offline consolidation** (OpenAI; criticized for losing the audit trail) | Markdown-first + scheduled consolidation is a validated first-party strategy; v2 keeps consolidation git-auditable — the exact property Dreaming was criticized for lacking |
| Hindsight ([2512.12818](https://arxiv.org/abs/2512.12818)) — the provider Exocórtex already runs | Four networks: world facts / experiences / **entity summaries** / **evolving beliefs** — "separating evidence from inference"; 91.4% LongMemEval | The runtime's own provider agrees: epistemic separation (P4) and entity memory (05 §Entity) are load-bearing |
| A-MEM ([2502.12110](https://arxiv.org/abs/2502.12110)), MIRIX, Memp, MemOS | Zettelkasten notes with agent-generated links + evolution; six-type memory; procedural memory lifecycle; memory governance framing | Supports atomic-note + link-on-write duties (08) and the typed object model (05) |

## B. Benchmarks — what survives the vendor noise

- **LoCoMo is broken** (6.4% wrong answer key; judge accepts 62.8% of wrong answers — [Penfield audit](https://dev.to/penfieldlabs/we-audited-locomo-64-of-the-answer-key-is-wrong-and-the-judge-accepts-up-to-63-of-intentionally-33lg)). All Mem0-vs-Zep-vs-Letta rankings are self-reported and harness-dependent ([Fair Fight](https://blog.continua.ai/p/the-locomo-fair-fight): 65–100% spread from harness alone). *Do not import vendor numbers into design decisions.*
- **Verbatim + agentic search beats extraction on accuracy at personal scale**: Letta's plain filesystem agent 74.0% vs Mem0 68.5% ([Letta bench](https://www.letta.com/blog/benchmarking-ai-agent-memory/)); extraction wins only latency/token-cost. **HaluMem** ([2511.03506](https://arxiv.org/abs/2511.03506)): extraction recall <60%, update correctness <50% inside Mem0/Zep/MemOS pipelines.
- **LongMemEval** ([2410.10813](https://arxiv.org/abs/2410.10813)) ablations: the three winning designs are **session decomposition, fact-augmented key expansion, time-aware indexing** — all three appear in 07-retrieval-policy.md.
- MemoryAgentBench ([2507.05257](https://arxiv.org/abs/2507.05257)): no architecture masters retrieval + test-time learning + long-range understanding + **conflict resolution** simultaneously → hybrid routing by task type, not one mechanism.

## C. Human PKM

- **Zettelkasten worked through stable addresses + dense links, not folders** ([zettelkasten.de](https://zettelkasten.de/posts/luhmann-folgezettel-truth/)); atomicity is a principle, not a rule. → stable paths, link-on-write duty, files as atoms.
- **Evergreen notes / "titles are APIs"** ([Matuschak](https://notes.andymatuschak.org/Evergreen_notes)): a claim-shaped filename is a retrieval key an agent can grep and cite. → naming rules in 08.
- **PARA**'s durable idea is only the **active/archive actionability split** ([fortelabs](https://fortelabs.com/blog/para/); critiques: no relations, collector's-fallacy bait). → microverso `status:` drives retrieval weighting.
- **MOCs die of manual maintenance; query-generated MOCs survive** ([Milo](https://obsidian.rocks/maps-of-content-effortless-organization-for-notes/); Dataview practice). → `_meta/index.md` is generated, hand-curation only at the home level.
- **Second-brain failure modes**: collector's fallacy, orphan notes, over-tagging, abandonment arc. Humans sustain far less structure than they design → **the agent absorbs the maintenance loop; the human only captures and reads** (P11); mandatory tier stays hand-writable (P9).
- **ADR practice** ([AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)): accepted decisions immutable; change = new record + `superseded_by`. "Not editing accepted ADRs is what makes the collection trustworthy." → decision objects are immutable (05).
- **Plain-text personal CRM**: one file per person, frontmatter + dated interaction log ([hal_md](https://github.com/thephm/hal_md)). → entity pages (05).
- **Karpathy-style LLM wiki / Claude-Code-on-Obsidian (2025–26)**: agent-maintained entity/concept files, a constitution file with filing rules, "no vector DB needed for most use cases" ([Imhoff](https://www.stefanimhoff.de/writing/agentic-note-taking-obsidian-claude-code/)). → direct validation of the Acervo design; the memory-manager skill is the constitution.

## D. Ontology, time, provenance

- **Bitemporality** (valid vs transaction time; [XTDB](https://docs.xtdb.com/concepts/key-concepts.html)): full bitemporal Markdown is overkill; **git = transaction time (free, exact); `valid_from`/`observed_at` frontmatter = valid time**. → Tier-2 fields (05).
- **Invalidate, don't delete** (Graphiti) — consensus; silent overwrite is universally condemned; automated conflict *resolution* has no consensus → v2 resolves clean supersession automatically, routes true disputes to the human (08).
- **W3C PROV** distinctions (entity/activity/agent) without RDF: every extracted memory records source + extraction method + responsible agent ([PROV-DM](https://www.w3.org/TR/prov-dm/); [PROV-AGENT](https://arxiv.org/pdf/2508.02866)).
- **Epistemic status as metadata** is established practice ([Gwern](https://gwern.net/about), LessWrong norm): small standardized confidence vocabulary, separate from maturity and importance. → `epistemic` + `confidence` fields.
- **Facets beat hierarchies** (Ranganathan; e-commerce practice): frontmatter = small set of orthogonal facets, not a deep tree. → 05 §1.
- **Entity resolution**: canonical file per entity + `aliases:` list + check-before-create duty + periodic dedup audit — the cheap fix for the most damaging personal-KB failure (five files, one person).

## E. Retrieval

- **Hybrid BM25+dense+rerank is baseline consensus**; embeddings underperform exactly on names/dates/IDs — the dominant content of a personal archive ([Anthropic Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval): +BM25 −49% failures, +rerank −67%).
- **Agentic search (grep/list/read) beat RAG for agent-operated corpora** at Claude Code scale; disputed for large corpora/vague queries ([Milvus counterpoint](https://milvus.io/blog/why-im-against-claude-codes-grep-only-retrieval-it-just-burns-too-many-tokens.md)). At Acervo scale (hundreds–thousands of files): **agentic search primary, semantic index supplement** — which makes naming, aliases, and indexes retrieval infrastructure, not hygiene.
- **Small scoped corpus → skip retrieval**: under ~200K tokens, load the whole scoped set with caching (Anthropic guidance). → "load the microverso view" path in 07.
- **The note is the chunk**: atomic notes with descriptive titles need no chunking pipeline; long docs → heading-based chunks + breadcrumbs; semantic chunking not worth it (NAACL 2025 finding).
- **Metadata filter before semantic match** (Multi-Meta-RAG): `type:decision AND microverso:comercial AND date:Q1` then rank — the concrete payoff of disciplined frontmatter.
- **Lost-in-the-middle persists (2025 models)**: pack best-first, second-best-last; fewer, more relevant notes beat stuffing.
- **Evaluation**: RAGAS-style context precision/recall + a personal **golden question set** re-run after every schema/retrieval change ([RAGAS](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/)). → 10-evaluation.md.

## F. Documented failure modes (governance drivers)

1. **Memory poisoning / persistent injection** — SpAIware ([Rehberger](https://embracethered.com/blog/posts/2024/chatgpt-macos-app-persistent-data-exfiltration/)), AgentPoison (≥80% success at <0.1% poison); ranked top agentic risk by Microsoft's 2026 taxonomy. → trust gate (04 §3), review of memory writes from untrusted content.
2. **Stale-memory contamination** — old facts beat new (LongMemEval knowledge-update category). → validity fields + status filtering.
3. **Over-summarization / confabulated continuity** — ChatGPT summaries "fill gaps with approximations"; Zep's verbatim-recall loss. → P8, sources survive.
4. **Duplicate accumulation** — systems "nail write and read and completely neglect manage" (Yan). → consolidation loop + dedup audits.
5. **Retrieval noise degrades reasoning** ([Shi et al.](https://arxiv.org/abs/2302.00093); [context rot](https://research.trychroma.com/context-rot)). → small k, budgets, opt-in retrieval.
6. **Self-reinforcing inference** ("experience-following", [2505.16067](https://arxiv.org/abs/2505.16067)). → epistemic separation; inferences promote only after confirmation.

## G. Where the field genuinely disagrees (spec must not pretend consensus)

- Graph structure below corpus scale: worth it? (HippoRAG 2 says yes for multi-hop; Mem0-g mixed) → H4.
- Consolidation that *rewrites* vs *annotates* (Dreaming vs Zep/Anthropic) → v2 chooses annotate+git, tested by H6.
- Grep-only vs hybrid index at personal scale → H2.
- Claim-level vs document-level memory → H3.
- Whether decay should ever hard-delete → v2: only via quarantine window (P3), revisit at H7.
