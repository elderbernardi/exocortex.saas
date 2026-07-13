---
type: artifact
title: Prompt para Fable — Especificação do Sistema de Memória do Exocórtex
description: Prompt de investigação para Fable especificar a memória cognitiva do Exocórtex.IA
tags: [memory, acervo, architecture, fable, specification, research]
timestamp: 2026-07-01
class: volátil
created_at: 2026-07-01T18:00:00Z
nature: prompts
excrtx_type: prompt
confidence: high
---

# Fable Investigation Prompt — Exocórtex Cognitive Memory System

## Mission

You are tasked with designing the definitive memory and knowledge management system for Exocórtex.IA — a personal cognitive extension system. This is not a general-purpose RAG system. It is a single-human exoskeleton for thought, operating across multiple isolated knowledge domains (microversos) within one person's universe.

Your output should be a **technical specification** that describes the architecture, data model, retrieval strategy, indexing approach, and operational protocols for a memory system that bridges human cognitive organization with LLM-optimal retrieval. Include concrete design decisions, rejected alternatives with rationale, and unresolved hypotheses that need empirical validation.

---

## 1. What Exocórtex Is

Exocórtex.IA is a personal cognitive extension operating on the Hermes Agent runtime. It is not a chatbot, not a generic assistant, not a search engine. It is an exoskeleton for one person's mind with these properties:

**Three Operational Vectors:**
- **Execução (DO):** Specialist agent mode. Deliver complete, verified artifacts. Needs dense, precise context retrieval.
- **Evolução (THINK):** Socratic guide mode. Explore ideas, question premises, expand possibility space. Needs lateral, connection-rich retrieval.
- **Manutenção (CLEAN):** Housekeeper mode. Audit, clean, verify system health. Needs comprehensive, systematic access.

**Three Concentric Layers:**
- **Macroverso:** The executive's "constitution" — identity, values, tone, non-negotiables. Flat files, always loaded (~100 lines). Changes rarely.
- **Microversos:** Isolated semantic domains (clients, projects, disciplines, areas of life). Each is a self-contained knowledge universe with its own: context, knowledge, decisions, contracts, workflows, tools, skills, templates, persona, reflections, and raw sources. Currently 14+ active microversos.
- **Shared:** Cross-domain bridge. References, glossary, group aliases, cross-refs. Minimal by design.

**Critical Constraint — Domain Isolation:** What lives in `micro/cliente-acme/` must NEVER leak into `micro/ensino/`. The executive's research on market intelligence for Client A cannot contaminate lesson plans for University B. This is a hard boundary — not a suggestion, not a soft filter. Cross-domain connections go through explicit `shared/cross-refs/` pointers.

---

## 2. Current Memory Architecture — The Acervo Cognitivo

### 2.1 Physical Layer: Filesystem as Source of Truth

The Acervo Cognitivo is a **file-based knowledge repository** structured as a wiki:

```
acervo/
├── macro/                    # Identity (FLAT — always loaded)
│   ├── soul.md               # Who I am, purpose
│   ├── valores.md            # Decision principles
│   └── estilo.md             # Executive tone and voice
│
├── global/                   # Universal operations (WIKI)
│   ├── _meta/                # Schema, index, log, design tokens
│   ├── context/              # Universal situation
│   ├── knowledge/            # Universal facts (compliance, legal)
│   ├── contracts/            # Universal rules
│   ├── decisions/            # Architectural decisions (ADRs)
│   ├── workflows/            # Global workflows
│   ├── tools/                # Context-wide tools
│   ├── reflections/          # Cross-cutting lessons
│   └── raw/                  # Immutable source documents
│
├── micro/{slug}/             # Isolated domains (14 directories each)
│   ├── _meta/                # SCHEMA.md, index.md, log.md
│   ├── context/              # Domain-specific situation
│   ├── knowledge/            # Domain facts, metrics, references
│   ├── decisions/            # Domain ADRs
│   ├── contracts/            # Domain rules
│   ├── workflows/            # Domain SOPs
│   ├── tools/                # Domain integrations (MCPs, APIs)
│   ├── skills/               # Domain-specific capabilities
│   ├── templates/            # Domain templates
│   ├── persona/              # Domain voice/style
│   ├── reflections/          # Domain lessons learned
│   └── raw/                  # Domain source documents
│
├── shared/                   # Cross-domain bridge
│   ├── groups.md             # Scope aliases (ALL, CLIENTS, PROJECTS)
│   ├── glossario.md          # Common vocabulary
│   └── cross-refs/           # Explicit cross-domain pointers
│
└── .quarantine/              # 30-day purge window for stale/deprecated
```

### 2.2 Semantic Layer: OKF v0.1 Superset Frontmatter

Every file carries YAML frontmatter aligned with Open Knowledge Format v0.1:

```yaml
---
# OKF Canonical (mandatory)
type: knowledge              # decision|memory|reflection|context|knowledge|artifact
title: Descriptive Title
description: One-line summary (≤ 120 chars)
tags: [from SCHEMA taxonomy]
timestamp: YYYY-MM-DD

# Acervo Extensions (mandatory)
class: volátil               # perene (permanent) | volátil (transient)
created_at: YYYY-MM-DDTHH:MM:SSZ

# Acervo Extensions (optional)
last_accessed_at: YYYY-MM-DDTHH:MM:SSZ
promoted_at: YYYY-MM-DDTHH:MM:SSZ     # when promoted volátil → perene

# Legacy retained
nature: knowledge             # directory routing key
excrtx_type: fact             # legacy type vocabulary
confidence: high
deprecated: false             # set true when superseded
---
```

### 2.3 Lifecycle: Deprecation → Quarantine → Purge

Files are never deleted directly. The lifecycle is:
1. **Deprecation** (ADR-016): On write, semantic revision hook detects contradictions. Old file marked `deprecated: true`. Perene files immune.
2. **Quarantine** (ADR-015): Stale volátil files (>90 days unaccessed) and deprecated files (>180 days) moved to `.quarantine/`. 30-day safety window.
3. **Purge**: After 30 days in quarantine without restore, permanent deletion.
4. **Syndic** (ADR-018): Autonomous weekly agent that scans and executes this lifecycle.

### 2.4 Operational Memory Model (ADR-019)

Four memory surfaces with distinct roles:

| Layer | Role | Authority |
|---|---|---|
| `SOUL.md` | Constitution + behavioral rules | Supreme |
| `USER.md` | Durable executive preferences | High |
| `MEMORY.md` | Bootstrap + critical invariants | High but constrained |
| Hindsight | Semantic operational memory on-demand | Retrieval + synthesis |
| Acervo | Structured canonical source | Documentary truth |
| `session_search` | Literal transcript history | Textual evidence |

Retrieval protocol: Hindsight locates → Acervo confirms → session_search proves. Memory.md only bootstraps.

### 2.5 Loading Strategy

| Layer | When Loaded | What |
|---|---|---|
| `macro/` | Every session | 3 files, ~100 lines |
| `global/` | Boot | `index.md` only (~30 lines); pages on demand |
| `micro/{slug}/` | When scope activates | `index.md` only; natures on demand |
| `shared/` | Cross-domain tasks | `groups.md` for scope resolution |

### 2.6 Current Access Patterns

- **READ:** Resolve layer → verify scope → detect format (file vs directory) → read → update `last_accessed_at`
- **WRITE:** Domain Filter classification → scope guard → mandatory frontmatter → semantic revision hook (deprecate contradictions) → log in `log.md` → update `index.md`
- **SEARCH:** Priority: micro (active) > global > shared > other micro (if in scope). Filter out deprecated and quarantined files.
- **SCOPE:** Resolve group aliases → apply deny-list → allow always overrides deny

---

## 3. The Hard Problems — What We Need You to Solve

### 3.1 The Human-Machine Organization Gap

Humans organize knowledge by **domain, narrative, and temporality**. We think in projects, clients, disciplines, and chronologies. LLMs retrieve best by **semantic similarity, graph relationships, and dense structured indexes**.

The current Acervo is organized for humans (files, directories, markdown). But the agent needs to retrieve context for LLM consumption. These two organizational schemes are in tension.

**Key question:** What is the optimal data model that serves both human browsing AND LLM retrieval without duplicating truth?

### 3.2 Context Window Economics

Anthropic's models now have massive context windows (200K+ tokens). This changes the retrieval calculus. The old paradigm of "chunk, embed, retrieve top-K, stuff into prompt" may no longer be optimal.

**Key questions:**
- With 200K context, should the strategy shift from "retrieve sparse relevant chunks" to "load entire relevant domains"?
- When is it better to load a whole microverso's index + recent context vs. semantic search for specific facts?
- How should the system decide between breadth (load many domains shallowly) and depth (load one domain completely)?

### 3.3 The Three-Vector Retrieval Problem

Each operational vector needs fundamentally different memory access:

- **Execução** needs: precise factual retrieval, current state, relevant contracts and templates. High precision, low hallucination tolerance.
- **Evolução** needs: lateral connections, unexpected associations, historical decisions and their rationales, abandoned hypotheses. High recall, serendipity valued.
- **Manutenção** needs: comprehensive audit access, staleness detection, cross-domain consistency checks. Systematic, exhaustive.

**Key question:** Should there be three different retrieval strategies, or one unified strategy with parameterized behavior?

### 3.4 Working Memory vs. Long-Term Memory

The agent operates in sessions. Within a session, it has conversation history as working memory. Between sessions, it has the Acervo as long-term memory. But there's a missing middle layer: **session-level semantic state**.

After a complex multi-turn Evolução session exploring a hypothesis, what should persist? The full transcript (session_search)? A summary? Extracted claims and their status? The current approach relies on the agent manually promoting insights to the Acervo.

**Key questions:**
- What is the right granularity for session → Acervo promotion?
- Should there be an automated "session digest" that extracts claims, decisions, and open questions?
- How should working memory decay be modeled?

### 3.5 Cross-Microverso Reasoning

While microversos must remain isolated, the executive's real work crosses domains. A research insight from `micro/pesquisa-cpg/` might inform a commercial proposal in `micro/comercial/`. A lesson from `micro/ensino/` might apply to `micro/gabinete/`.

The current `shared/cross-refs/` mechanism is explicit and manual. This is safe but low-bandwidth. The agent cannot discover cross-domain connections autonomously.

**Key questions:**
- Is there a safe way to enable cross-domain semantic search that respects the isolation contract?
- Should cross-domain connections be vector-based (similarity search across microversos with scope filtering) or graph-based (explicit typed edges)?
- How to prevent "soft leakage" where cross-domain retrieval becomes a backdoor for contamination?

### 3.6 Temporal and Lifecycle Awareness

Knowledge has a lifecycle. Some facts are timeless (the executive's values). Some decay predictably (market data from Q1 becomes less relevant in Q3). Some should trigger alerts (a contract that expires next month).

The current `class: perene | volátil` and `last_accessed_at` are coarse lifecycle signals. The syndic quarantines based on simple time thresholds.

**Key questions:**
- Should the system model explicit temporal decay functions per knowledge type?
- How should the agent weigh information based on its age and lifecycle class?
- Should there be proactive staleness alerts (e.g., "this market data is 6 months old — refresh?")?

### 3.7 The Index Problem

The current system uses `index.md` files as manual catalogs. But manual indexes drift from reality. The agent updates `index.md` on writes, but reads may miss unindexed files.

**Key questions:**
- Should the index be generated (filesystem scan + frontmatter parsing) rather than manually maintained?
- What is the right indexing granularity? File-level? Section-level? Claim-level?
- Should there be multiple indexes for different access patterns (chronological, semantic, by entity, by tag)?

### 3.8 The Embedding Question

The current system has NO vector embeddings. All retrieval is filesystem-based (grep, index.md, frontmatter tags). This is transparent and debuggable but limited in semantic recall.

**Key questions:**
- At what point does the lack of embeddings become a binding constraint?
- If embeddings are added, should they be at the file level, section level, or paragraph level?
- Should embeddings be stored alongside markdown files or in a separate vector store?
- How to keep embeddings in sync with file edits without complex ETL pipelines?
- Can the system operate gracefully with embeddings as an optional enhancement rather than a dependency?

### 3.9 Multi-Agent Memory Sharing

The Exocórtex ecosystem includes sub-agents (delegate_task), cron jobs (scheduled autonomous agents), and potentially specialized agents for different microversos. Currently, each agent session is isolated — there's no shared working memory between agents.

**Key questions:**
- Should sub-agents have read access to the parent's Acervo scope?
- How should a cron job's findings be integrated into the Acervo for the main agent to discover?
- Should there be an "agent inbox" pattern where sub-agent outputs are queued for executive review?

### 3.10 The Canonical vs. Operational Divide

ADR-019 established a clear hierarchy: SOUL > contracts > Acervo > session_search > Hindsight > memory.md. But in practice, the fastest path to an answer often bypasses this hierarchy.

**Key questions:**
- How to make the canonical path also the fastest path?
- Should the system eagerly pre-load likely-needed context based on the active task vector and microverso?
- What is the right caching strategy for Acervo content in the agent's context?

---

## 4. State of the Art — Reference Points

Your design should engage with (and potentially transcend) these approaches:

### 4.1 RAG Evolution
- **Naive RAG:** Chunk → embed → retrieve top-K → stuff prompt. Brittle, loses structure.
- **Agentic RAG:** Multi-step retrieval with tool use, query decomposition, verification loops.
- **GraphRAG (Microsoft):** Entity extraction → community detection → summary generation. Handles global questions better than naive RAG.
- **LightRAG:** Lighter graph-based approach with dual-level retrieval.
- **Graphiti:** Temporal knowledge graphs with edge decay.

### 4.2 Memory Architectures
- **MemGPT / Letta:** OS-inspired memory hierarchy (core memory, archival memory, working context). Explicit memory management via function calls.
- **Mem0:** Memory layer for AI agents with user, session, and agent memory scopes.
- **Cognee:** ECL (Extract, Cognify, Load) pipeline. Builds knowledge graphs from conversations.
- **LangMem (LangChain):** Semantic memory with profile extraction, summarization, and consolidation.

### 4.3 Context Engineering
- **Anthropic Context Engineering Guide:** Strategic prompt structuring, document positioning, metadata enrichment.
- **Long-context models (Gemini 2M, Claude 200K):** Shift from "retrieve then generate" to "load then reason."
- **Context caching:** Pre-load stable content once, reuse across turns.

### 4.4 Knowledge Organization
- **Karpathy's LLM Wiki:** File-based markdown wiki with index-based loading. The original inspiration for the Acervo.
- **Obsidian-style:** Bidirectional links, graph view, backlinks.
- **Zettelkasten:** Atomic notes, dense linking, emergent structure.
- **PARA Method (Forté):** Projects, Areas, Resources, Archives — actionability-based organization.

### 4.5 Protocols and Standards
- **MCP (Model Context Protocol):** Standardized server interface for context provision. The Acervo has an MCP control plane planned (ADR-022).
- **OKF (Open Knowledge Format):** Standardized frontmatter for interoperable knowledge.
- **DTCG (Design Tokens Community Group):** Token-based design system resolution (relevant for visual memory).

---

## 5. Design Constraints

Your specification must respect these constraints:

1. **Single-human system.** This is not multi-tenant. No user authentication, no permission systems beyond the executive's own scoping.
2. **PT-BR primary language.** Content is in Brazilian Portuguese. Any NLP components must handle PT-BR well.
3. **Filesystem is physical truth.** The Acervo is git-tracked markdown. Human-readable, diffable, greppable. This is non-negotiable for audit, portability, and survival.
4. **Incremental adoption.** The system must work with the current Acervo structure as a starting point. Migration path must be clear.
5. **No external service dependency for core function.** Vector search, embeddings, or graph databases are acceptable as enhancements but the system must degrade gracefully without them.
6. **Token budget awareness.** The executive pays for tokens. Retrieval strategies must justify their cost.
7. **Draft-First for external actions.** The agent never sends, publishes, or shares without explicit approval. This applies to memory operations that export or share data.

---

## 6. Deliverable — What We Need From You

Produce a technical specification covering:

### 6.1 Data Model
The optimal structure for storing knowledge that serves both human navigation and LLM retrieval. Include:
- File/directory structure (evolution from current, not replacement)
- Frontmatter schema (extensions to OKF v0.1)
- Entity and relationship model (what are the first-class entities in this system?)
- Chunking and linking strategy

### 6.2 Retrieval Architecture
- Indexing strategy (what indexes exist, how they're built and maintained)
- Retrieval decision tree (given a task vector + microverso + query, how does the system decide WHAT to retrieve and HOW?)
- Vector embedding strategy (if applicable — where, what granularity, what model)
- Caching and pre-loading strategy
- Cross-microverso retrieval protocol

### 6.3 Lifecycle Model
- Temporal decay functions per knowledge type
- Promotion criteria (when does volátil become perene?)
- Automated session digestion (what persists between sessions?)
- Staleness detection and alert thresholds

### 6.4 Operational Protocols
- Write path: from agent decision → Acervo commit (validation, indexing, cross-referencing)
- Read path: from task context → retrieved knowledge (scope resolution, priority ordering, assembly)
- Agent-to-agent memory sharing protocol
- Degraded mode operation (when embeddings or advanced indexes are unavailable)

### 6.5 Migration Path
How to evolve from the current Acervo to the specified architecture without breaking existing microversos or requiring manual re-organization.

### 6.6 Unresolved Hypotheses
Explicitly list what you believe but cannot prove without empirical testing. For each hypothesis:
- What experiment would validate or falsify it?
- What metric would you measure?
- What is the expected outcome and what would disprove it?

---

## 7. Evaluation Criteria

The specification will be evaluated on:

1. **Coherence:** Does it form a unified system where all parts reinforce each other?
2. **Practicality:** Can it be implemented incrementally on the current Acervo?
3. **Token efficiency:** Does it respect the executive's budget?
4. **Human alignment:** Does it preserve the executive's ability to browse, edit, and understand their own knowledge?
5. **Isolation integrity:** Does it maintain hard boundaries between microversos?
6. **Vector adaptability:** Does it account for the three operational vectors needing different retrieval patterns?
7. **Honesty about uncertainty:** Does it distinguish between architectural decisions and empirical hypotheses?

---

Consider this your mandate. The quality of this specification will determine the cognitive capability of the Exocórtex system for its entire operational lifetime. Every design decision you make — or fail to make — will compound across thousands of agent sessions and millions of tokens.

Begin.
