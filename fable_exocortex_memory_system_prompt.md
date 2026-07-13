# Prompt for Anthropic Fable: Exocortex Memory and Knowledge Organization System

## Mission

You are Anthropic Fable operating as a senior research architect for LLM agent memory systems, human knowledge management, personal ontologies, retrieval infrastructure, and durable cognitive systems.

Your task is to design the specification for the best possible memory and knowledge organization system for Exocortex.IA: a personal/executive cognitive extension that runs on Hermes Agent and must bridge human thought, work artifacts, isolated domains, and efficient retrieval by LLMs.

Do not produce a loose opinion essay. Produce a rigorous investigation with state-of-the-art research, testable hypotheses, trade-offs, architectural decisions, and an implementable specification.

The central question:

> How should a durable, auditable, evolutionary, and efficient memory system for a personal exocortex be designed, so it can organize one subject's cognitive universe across multiple microverses, preserve the human structure of thought, and make that structure usable by LLMs without contaminating context, losing nuance, or manufacturing coherence?

---

## Current System Context

The system is called **Exocortex.IA**.

It is not a generic chatbot. It is a personalized cognitive extension for an executive. Its role is to amplify memory, strategic context, execution, and clarity of thought.

It runs on **Hermes Agent**, which provides tools, profiles, memory, gateway, automation, skills, and integrations with channels such as Telegram.

The current memory architecture is called the **Cognitive Archive** / **Acervo Cognitivo**. It is organized in layers:

```text
acervo/
├── macro/          # identity of the subject, values, style, personal constitution
├── global/         # universal rules, contracts, tools, workflows
├── micro/{slug}/   # isolated microverses / domains
└── shared/         # bridges and cross-references between microverses
```

Current concepts:

- **Macroverse**: the subject's root identity, values, voice, preferences, and personal/professional context. It changes rarely. It governs system behavior.
- **Microverse**: an isolated domain of knowledge, project, client, company, function, initiative, research area, or life/work context.
- **Shared**: a bridge layer between microverses, without copying knowledge across domains.
- **Global**: universal operational rules, tools, contracts, workflows, and reusable capabilities.
- **Natures**: semantic classifications for content inside domains:
  - `context`
  - `knowledge`
  - `contracts`
  - `prompts`
  - `persona`
  - `workflows`
  - `skills`
  - `tools`
  - `templates`
  - `decisions`
  - `reflections`

The current system has rules such as:

- domain filtering before every write;
- isolation between microverses;
- mandatory YAML frontmatter;
- index and log per microverse;
- distinction between `perennial` and `volatile` memory;
- semantic deprecation of contradictory knowledge;
- quarantine for stale memory;
- preference for a semantic control plane through `acervoctl` or MCP;
- raw files as immutable sources;
- auxiliary agent-memory providers, such as Hindsight, for semantic recall, while canonical truth remains in the Cognitive Archive.

The current architecture is strong, but you must redesign it as if this were the only chance to create the best possible system.

---

## Investigation Objective

Produce a specification for a memory system that creates the best bridge between:

1. **How humans organize thought, projects, relationships, decisions, obligations, and artifacts**
2. **How LLMs retrieve, interpret, compose, and use context efficiently**
3. **How an autonomous agent should write, revise, promote, deprecate, summarize, and audit memory over time**
4. **How multiple domains of the same subject can coexist without semantic contamination**
5. **How to preserve nuance, contradictions, history, and versions without paralyzing operational retrieval**
6. **How to transform events, conversations, files, and decisions into useful memory without creating cognitive junk**

---

## Mandatory Research

Investigate the state of the art up to the current date. Do not limit yourself to the names below. Treat them as starting pointers.

### 1. Memory for LLM Agents

Research and compare:

- MemGPT / Letta
- Generative Agents
- Reflexion
- Voyager
- HippoRAG
- GraphRAG
- LightRAG
- A-MEM / Agentic Memory
- MemoryBank
- LongMem
- classic RAG vs agent memory
- episodic memory for LLM agents
- semantic/procedural/episodic memory in agents
- context engineering vs memory
- lifelong learning / continual learning in agents
- memory consolidation in LLM agents
- memory retrieval evaluation
- personal AI memory systems
- multi-agent memory sharing
- memory-native agent architectures

Initial research pointers:

- “Memory in the Age of AI Agents”
- “Memory for Autonomous LLM Agents: Mechanisms, Evaluation and Directions”
- “A Survey on the Memory Mechanism of Large Language Model-based Agents”
- “Position: Episodic Memory is the Missing Piece for Long-Term LLM Agents”
- “A-MEM: Agentic Memory for LLM Agents”
- “Towards large language models with human-like episodic memory”
- recent surveys on vector memory, graph memory, event logs, and agent memory

### 2. Human Knowledge Management

Research and compare:

- Zettelkasten
- Luhmann and Folgezettel
- PARA method
- Tiago Forte's CODE method
- Obsidian / Markdown-first PKM
- Evergreen notes
- MOCs / Maps of Content
- Second Brain
- executive journaling
- decision logs / ADRs
- project knowledge management
- CRM-like relational memory
- personal knowledge graphs
- personal ontologies
- the archive as cognitive extension
- archive vs working memory
- documents as externalized thought

### 3. Information Systems, Ontology, and Retrieval

Research:

- ontology engineering
- knowledge graphs
- event sourcing
- bitemporal data
- provenance tracking
- CRDTs and versioning, where relevant
- semantic versioning of knowledge
- schema evolution
- faceted classification
- DITA / docs-as-code, where relevant
- document lifecycle management
- information architecture
- taxonomies vs folksonomies
- embeddings, reranking, hybrid search, sparse+dense retrieval
- entity resolution
- temporal retrieval
- graph traversal retrieval
- query planning for RAG
- contradiction detection
- epistemic status / confidence modeling

### 4. Human Cognition and Memory

Research enough to inform design:

- working memory
- episodic memory
- semantic memory
- procedural memory
- autobiographical memory
- prospective memory
- memory consolidation
- forgetting curves
- salience, recency, frequency
- spaced repetition, if applicable
- context-dependent memory
- cognitive offloading
- distributed cognition
- extended mind thesis

Do not turn this into a philosophy essay. Use it as architectural input.

---

## Questions the Investigation Must Answer

### A. Conceptual Model

1. What is the ideal atomic unit of memory for an exocortex?
   - note?
   - event?
   - claim?
   - decision?
   - episode?
   - artifact?
   - entity?
   - relation?
   - chunk?
   - composite memory object?

2. Should the system organize knowledge by:
   - human domain first?
   - cognitive type first?
   - entity first?
   - time first?
   - task/action first?
   - emergent graph?
   - hybrid model?

3. Is the `micro/{slug}` layer the right abstraction?
   - What does it solve?
   - Where does it fail?
   - How should it handle overlapping domains?
   - Should a microverse be a security boundary, a cognitive boundary, an operational namespace, or all of these?

4. What should be the relationship between:
   - Macroverse
   - Microverses
   - Projects
   - People
   - Companies
   - Artifacts
   - Decisions
   - Workflows
   - Conversations
   - Tasks
   - Calendar
   - Files

5. How should useful contradictions be preserved?
   - Example: “in March we believed X; in May we discovered Y.”
   - When should the system deprecate?
   - When should it archive?
   - When should it preserve multiple versions?
   - How should it prevent the LLM from mixing past and present?

### B. Storage Architecture

Define a canonical architecture with:

- human-readable storage;
- LLM-optimized retrieval storage;
- derived indexes;
- logs/events;
- provenance;
- schema versioning;
- mandatory metadata;
- relationships between objects;
- synchronization mechanisms;
- repair mechanisms.

Compare alternatives:

1. Markdown-first with YAML frontmatter
2. Relational database
3. Graph database
4. Vector database
5. Append-only event log
6. Hybrid filesystem + SQLite/Postgres + vector + graph
7. Agent-managed knowledge base

State which combination you recommend and why.

Important constraint: the system must be operable by both humans and agents. It cannot become a black box that only embeddings understand.

### C. Memory Model

Specify memory types and lifecycle.

Consider at least:

- **Constitutional memory**: identity, values, tone, boundaries.
- **Semantic memory**: facts, concepts, relationships.
- **Episodic memory**: events, conversations, experiences, work episodes.
- **Procedural memory**: workflows, skills, scripts, routines.
- **Prospective memory**: commitments, pending items, future intentions.
- **Relational memory**: people, organizations, preferences, interaction history.
- **Artifact memory**: documents, presentations, spreadsheets, emails, proposals.
- **Decision memory**: decisions, rejected alternatives, rationale.
- **Reflective memory**: lessons learned, perceived patterns, after-action reviews.
- **Operational memory**: system state, integrations, non-secret credentials metadata, health checks.

For each type, define:

- function;
- granularity;
- format;
- metadata;
- place in the architecture;
- lifecycle;
- write rules;
- read rules;
- when to summarize;
- when to preserve verbatim;
- when to promote;
- when to deprecate;
- when never to delete.

### D. Ingestion

Define how the system should transform raw inputs into memory.

Possible inputs:

- conversations with the executive;
- Telegram messages;
- emails;
- meetings;
- PDFs;
- documents;
- spreadsheets;
- presentations;
- web pages;
- research;
- agent outputs;
- decisions made in conversation;
- loose files in inbox;
- quick notes;
- tasks;
- calendar;
- CRM;
- commercial artifacts;
- public company data;
- operational logs.

For each input, determine:

1. What remains an immutable raw source.
2. What becomes canonical memory.
3. What becomes an index.
4. What becomes a task.
5. What becomes a decision.
6. What becomes a reflection.
7. What should be discarded.
8. Which agent/process decides.
9. Which checks prevent cognitive junk.

Create an ingestion pipeline with states.

Possible example states:

```text
captured → normalized → classified → extracted → proposed → approved/auto-approved → committed → indexed → reviewed → consolidated → deprecated/archived/quarantined
```

Evaluate whether this pipeline is sufficient. Improve it if needed.

### E. Retrieval

Specify how the agent should retrieve memory for real tasks.

Use cases:

- answer a factual question;
- prepare an email in the executive's style;
- review a commercial proposal;
- remember client history;
- cross information from two microverses;
- generate a morning briefing;
- continue reasoning from previous sessions;
- detect conflict between new information and old belief;
- decide whether information belongs in macro, global, micro, or shared;
- execute a technical task;
- produce strategy;
- help the executive think without giving ready-made answers.

Compare strategies:

- keyword search;
- full-text search;
- dense vector search;
- hybrid search;
- graph traversal;
- temporal filtering;
- entity-first retrieval;
- task-intent retrieval;
- query decomposition;
- reranking;
- summarization-on-read;
- context packing;
- memory salience scoring;
- retrieval budgets;
- source citation;
- confidence scoring.

Define a retrieval policy by task type.

Include pseudocode for:

- `resolve_scope(query, active_context)`
- `retrieve_context(task, scope, budget)`
- `pack_context(memories, budget)`
- `write_memory(candidate, scope)`
- `detect_conflict(candidate, existing_memory)`
- `promote_memory(memory_object)`
- `deprecate_memory(memory_object)`
- `consolidate_episode(episode)`

### F. Human Organization vs LLM Organization

This is the most important section.

The system must respect how humans think and work, while also staying efficient for LLMs.

Investigate and propose a bridge between both models.

Questions:

1. Humans organize by projects, people, companies, themes, urgencies, and narratives. LLMs retrieve better through chunks, entities, relations, embeddings, and compact instructions. How should the system unify both?
2. Should the structure visible to the human be the same structure used internally by the LLM?
3. When should the system have a “human view” and a “machine view”?
4. How should divergence between the two be prevented?
5. What should be the source of truth?
6. How should Markdown files be designed so they are good for both human reading and agent parsing?
7. How can frontmatter be used without turning every file into bureaucracy?
8. How should microverses be organized so they do not become junk drawers?
9. How should indexes be designed so they help both humans and agents?
10. How should relationships be represented without requiring the human to maintain a graph manually?

Deliver a **dual representation model**, or justify why one should not exist.

### G. Microverses

Specify the idea of microverses in depth.

A microverse may represent:

- client;
- project;
- company;
- function;
- life area;
- research domain;
- product;
- campaign;
- person;
- recurring operation;
- technical system;
- strategic initiative.

Answer:

1. Which types of microverse should exist?
2. How should slugs be named?
3. When should a new microverse be created?
4. When should microverses be merged?
5. When should they be archived?
6. How should temporary microverses be handled?
7. How should clients inside a company be handled?
8. How should projects that cross clients be handled?
9. How should duplication between microverses be avoided?
10. How should `shared` work?
11. How should cross-access be resolved?
12. How should sensitive context leakage be prevented?
13. How should groups of microverses be represented?
14. How should an agent decide the active microverse?

Create a formal microverse model with schema.

### H. Quality, Audit, and Governance

Define mechanisms to:

- prevent wrong writes;
- detect contradictory memory;
- detect stale memory;
- detect duplication;
- detect over-summarization;
- detect source loss;
- detect contamination between microverses;
- validate frontmatter;
- validate broken links;
- validate indexes;
- validate that retrieved memory was used correctly;
- audit agent actions;
- version changes;
- differentiate fact, interpretation, hypothesis, decision, and preference.

Create a practical epistemology policy.

Every memory should carry, where applicable:

- claim;
- source;
- confidence;
- valid_from;
- valid_until;
- observed_at;
- created_at;
- updated_at;
- supersedes;
- superseded_by;
- scope;
- sensitivity;
- owner;
- review_after;
- lifecycle_class;
- provenance;
- extraction_method;
- human_approved.

Evaluate which fields are mandatory, optional, or derived.

### I. Agent Interface

Specify how Exocortex should use memory during execution.

The agent must classify each input as:

- execution;
- evolution;
- maintenance;
- ambiguous.

Show how memory should be loaded for each vector.

#### Execution

The agent needs operational context, artifacts, decisions, contracts, templates, and style.

#### Evolution

The agent needs to preserve reasoning, ask questions, bring analogies, retrieve reflections and hypotheses, and avoid stealing the executive's learning process.

#### Maintenance

The agent needs to audit inbox, pending items, microverse health, stale memory, broken links, and open decisions.

Explain:

- which memory enters the prompt;
- which memory remains available through tools;
- which memory never enters unless requested;
- how to control context budget;
- how to handle conflicts between memory and current input;
- how to cite sources;
- how to request confirmation when memory implies an external action.

### J. Implementable Specification

Deliver an implementable architecture in phases.

Phase 0: current-system diagnosis  
Phase 1: minimum schema  
Phase 2: safe ingestion and writing  
Phase 3: hybrid retrieval  
Phase 4: consolidation and deprecation  
Phase 5: graph/ontology  
Phase 6: evaluation and self-improvement  
Phase 7: advanced human/agent interface

For each phase:

- objective;
- deliverables;
- filesystem changes;
- database/index changes;
- required tools;
- risks;
- tests;
- success criteria;
- estimated effort;
- implementation order.

Include concrete file examples.

Example:

```yaml
---
schema_version: 0.3
object_type: decision
title: "Adopt PostgreSQL for the sales portal"
scope:
  layer: micro
  microverse: sales-portal
status: active
epistemic_status: decided
confidence: high
created_at: 2026-07-03T00:00:00Z
decided_at: 2026-07-03
valid_from: 2026-07-03
review_after: 2026-10-03
tags: [architecture, database, sales-portal]
entities:
  - PostgreSQL
  - sales-portal
sources:
  - type: conversation
    ref: session://...
supersedes: []
superseded_by: null
---
```

Do not accept this schema as correct. Review it and propose the best version.

---

## Final Deliverable Structure

Produce a document with the following structure:

### 1. Executive Summary

A direct synthesis of the recommended architecture and its key decisions.

### 2. Research Map

Map the state of the art, with sources, schools of thought, and relevance to Exocortex.

Separate:

- agent memory;
- human PKM;
- ontologies/graphs;
- retrieval/RAG;
- human cognition;
- governance and lifecycle.

### 3. Design Principles

Define the system's design principles.

Examples of candidate principles, to be critically evaluated:

- memory is not storage;
- raw sources are immutable;
- retrieval must be scoped;
- human-readable canonical truth;
- machine indexes are derivative;
- no cross-microverse duplication;
- every claim has provenance;
- contradiction is a first-class object;
- summarize only after preserving source;
- memory must decay unless promoted;
- context budget is a product constraint;
- the system must distinguish knowing, believing, deciding, intending, and remembering.

Create the final principles.

### 4. Proposed Architecture

Describe the architecture:

- layers;
- stores;
- indexes;
- schemas;
- APIs;
- pipelines;
- agents;
- maintenance jobs;
- scope control;
- security;
- versioning.

Include text diagrams where useful.

### 5. Memory Object Model

Define the fundamental objects:

- source;
- episode;
- claim;
- concept;
- entity;
- relation;
- decision;
- task/intention;
- workflow;
- artifact;
- reflection;
- contract/rule;
- persona;
- preference;
- index;
- summary;
- contradiction;
- deprecation;
- quarantine item.

For each object: schema, lifecycle, examples, and how the LLM should use it.

### 6. Microverse Specification

Formally specify microverses:

- purpose;
- types;
- directory structure;
- metadata;
- lifecycle;
- relationships;
- shared/cross-ref;
- groups;
- access;
- examples.

### 7. Retrieval and Context Packing Policy

Define how to retrieve memory by task.

Include:

- algorithms;
- pseudocode;
- ranking;
- budgets;
- fallback;
- conflict handling;
- citation;
- stale-memory protection.

### 8. Write / Update / Deprecate Policy

Define how memory enters the system and how it changes.

Include:

- promotion criteria;
- discard criteria;
- deprecation criteria;
- consolidation criteria;
- human review criteria;
- auto-approval criteria;
- logs;
- audit.

### 9. Human Interface

How should the executive interact with the system?

Include:

- mental or operational commands;
- inbox;
- briefing;
- decision review;
- pending-item review;
- microverse navigation;
- quick capture;
- “research mode”;
- “decision mode”;
- “archive mode”;
- “maintenance mode”.

### 10. Evaluation Framework

How will we know whether the system is good?

Create benchmarks and tests:

- retrieval accuracy;
- context precision;
- context recall;
- cross-domain contamination;
- stale memory rate;
- contradiction handling;
- human usability;
- latency;
- token efficiency;
- write quality;
- source traceability;
- decision continuity;
- executive trust.

Include synthetic tests and real-world tests.

### 11. Open Hypotheses and Research Questions

List unresolved hypotheses that require experiments.

For each hypothesis:

- description;
- why it matters;
- possible paths;
- recommended experiment;
- decision metric;
- risk of choosing incorrectly.

Include at least hypotheses about:

- Markdown-first vs database-first;
- graph-first vs vector-first;
- claim-level memory vs document-level memory;
- microverse as strong boundary vs flexible tag;
- human approval for all memory vs governed auto-commit;
- eager summarization vs lazy summarization;
- append-only event log vs mutable canonical pages;
- LLM-maintained ontology vs human-maintained ontology;
- human/machine dual representation;
- when a conversation becomes an episode;
- when a decision becomes a contract;
- when a reflection becomes a rule;
- how to measure “useful memory”.

### 12. Recommended Implementation Roadmap

Roadmap with phases, deliverables, dependencies, and cut criteria.

### 13. Concrete Artifacts

Include ready-to-use artifacts:

- recommended directory tree;
- YAML schemas;
- Markdown examples;
- desired commands/APIs;
- tool contracts;
- internal prompts for ingestion, retrieval, maintenance, and audit agents;
- write checklist;
- read checklist;
- maintenance checklist;
- log model;
- index model;
- briefing model;
- microverse model.

### 14. Final Recommendation

Close with a clear recommendation:

- what to preserve from the current architecture;
- what to abandon;
- what to redesign;
- what to implement first;
- what to test before coding;
- which decisions require human judgment.

---

## Quality Rules

1. Do not produce a generic answer about RAG.
2. Do not treat “memory” as a synonym for vector database.
3. Do not treat human PKM as folder aesthetics.
4. Do not ignore lifecycle, deprecation, contradiction, and provenance.
5. Do not propose an architecture that only an engineer can understand and the human cannot audit.
6. Do not propose an architecture that only the human can understand and the LLM cannot retrieve from.
7. Do not hide trade-offs.
8. Do not confuse source, summary, claim, decision, and reflection.
9. Do not accept the current architecture as correct just because it exists.
10. Do not invent academic consensus where dispute exists.
11. Always distinguish:
    - fact;
    - hypothesis;
    - preference;
    - decision;
    - rule;
    - interpretation;
    - episodic memory;
    - future intention.
12. When recommending something, state:
    - why;
    - compared against what;
    - cost;
    - risk;
    - how to test it.

---

## Excellence Criterion

The response is excellent if, by the end, an engineer/agent can implement the first version of the system, and an executive can understand why this architecture preserves their way of thinking without turning into clutter or a black box.

The response must produce a specification that combines:

- rigor from distributed systems;
- sensitivity to personal archives;
- product pragmatism;
- LLM efficiency;
- knowledge governance;
- respect for human complexity.

Treat this task as if the resulting design will govern Exocortex memory for the next ten years.
