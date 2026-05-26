# SYSTEM SPECIFICATION: HERMES AGENT ARCHITECTURE & COMMUNICATION

**DOCUMENT PURPOSE:** Agent-readable Source of Truth (SoT) for Hermes Agent capabilities, constraints, and systemic topologies.

**PARADIGM:** Stateful, autonomous, harness-engineered system (replacing stateless/wrapper paradigms).

## 1. CORE ARCHITECTURAL PILLARS

The system operates on five highly decoupled subsystems governing state, memory, and behavior.

* **[MEMORY] Hybrid Memory Architecture:** * *Mechanism:* Bifurcates immediate context (always-loaded prompt buffer) from historical state (on-demand FTS5-indexed SQLite search).
  * *Constraint:* Avoids flat vector JSONL stores to prevent structural degradation. Relies on periodic nudges to curate memory.
* **[SKILLS] Procedural Memory:** * *Mechanism:* Reusable markdown files stored on disk. Novel workflow solutions are synthesized and saved as playbooks.
* **[SOUL] Behavioral Guardrails:** * *Mechanism:* Global context file defining behavioral instructions and voice. Dynamically updates via user feedback.
* **[CRONS] Autonomous Scheduling:** * *Mechanism:* Centralized execution system for heartbeat scheduling, background data gathering, and maintenance, independent of user prompts.
* **[LOOP] The Self-Improving Loop:** * *Mechanism:* Compounding capability enhancement via internal nudges (curating memory), skill refinement, and explicit user correction.

## 2. SYNCHRONOUS ORCHESTRATION ENGINE

The central core loop managing provider selection, prompt construction, tool execution, and state persistence.

### Execution Flows

* **Interactive Flow (CLI/Gateway):** User Input -> Conversation Runner -> Prompt Builder (aggregates soul, memory, tools) -> Provider Resolution -> API Execution -> Dispatch Handler (intercepts tool calls) -> Loop.
* **Background Flow (Cron):** Background Scheduler triggers task -> Spawns *zero-history, isolated* orchestration instance -> Injects relevant procedural skills -> Executes -> Updates state.

### Engine Optimizations & Principles

* **Preflight Context Compression:** Mathematical token evaluation. If thresholds are exceeded, a lossy summarization engine compresses history.
* **Prefix-Caching:** Breakpoints injected into prompt structures to minimize compute latency.
* **Immutability:** System prompts remain immutable mid-conversation to prevent cache-breaking.
* **Interruptible Logic:** All API/Tool executions can be halted mid-flight via OS signals or user input.

## 3. TOOLS RUNTIME & PROVIDER RESOLUTION

### Tool Registry & Dispatch

* **Discovery:** AST (Abstract Syntax Tree) parsing scans internal tools directory for top-level registrations upon initialization. Supports external Model Context Protocol servers.
* **Dynamic Availability Filtering:** Tools execute self-verification (e.g., checking for API keys or binaries) before advertising to the LLM schema. Prevents hallucinated tool calls.
* **Error Handling:** Dual-layered intercept. Crashes return heavily formatted JSON error payloads directly to the LLM for self-correction.

### Provider Runtime Resolution

* **Credential Scoping:** API keys are strictly scoped to specific base URLs to prevent credential leakage across gateways.
* **Automated Fallback:** Non-retryable/exhausted network errors trigger an automatic, in-place provider swap using fallback credentials, resetting cache/retry counts without human intervention.

## 4. GATEWAY TOPOLOGIES & COMMUNICATION LAYERS

Communication is entirely abstracted from the core execution loop.

* **Gateway Adapters:** Normalizes messaging protocols (Telegram, Slack, Discord, Matrix, Teams, WeChat) into a unified internal format. Maintains strict cross-platform session context.
* **Agent Client Protocol (IDE Integration):** * *Transport:* Asynchronous JSON-RPC standard I/O server.
  * *Environment:* Bound strictly to the IDE's Current Working Directory.
  * *Event Bridge:* Converts synchronous agent callbacks (tool progress) into asynchronous stream updates for IDE frontends (VS Code, Zed, JetBrains).
* **API/TUI Gateways:** Masquerades as standard OpenAI-compatible endpoints (HTTP/SSE) or WebSocket TUI streams for dashboards and Open WebUI.

## 5. SEVEN-LAYER SECURITY & ISOLATION MODEL

Mandatory defense-in-depth protocols for autonomous code execution.

1. **User Authorization:** Network access gated by allowlists and cryptographic DM pairing.
2. **Command Approval (Human-in-the-Loop):** Halts for explicit human authorization on destructive actions. Overrides IDE sessions temporarily.
3. **Container Isolation:** Sandboxed execution inside Docker/Singularity/Modal.
4. **Credential Filtering:** Subprocesses subjected to strict environment variable isolation.
5. **Context File Scanning:** Active parsing of ingested files to neutralize prompt injections.
6. **Cross-Session Isolation:** Hardened pathing and cryptographic boundaries for database read/writes.
7. **Path Traversal Defense:** Sanitization against directory traversal for storage and file manipulation.

## 6. MULTI-AGENT SWARM TOPOLOGY (THE NOOSPHERE PATTERN)

* **Constraint:** Direct peer-to-peer invocation is strictly avoided to prevent infinite loops and cascading failures.
* **Architecture:** Implements the "Noosphere" pattern. A shared FTS5 SQLite database acts as the central coordination environment.
* **Mechanism:** Agents write state/messages to the shared database. Secondary agents use internal cron heartbeats to asynchronously poll the database for unread, profile-relevant messages (Publish-Subscribe mechanism).

## 7. META-HARNESS OPTIMIZATION (OUTER LOOP)

System quality optimization via programmatic manipulation of the harness (execution environment), not model weights.

* **Inner Loop (Hermes Instance):** Handles standard protocol execution, tool calling, benchmark integration, and local state commits.
* **Outer Loop (Meta-Harness Supervisor):** Analyzes execution archives, orchestrates evaluations, tracks performance frontiers, and injects deterministic mutations into the Inner Loop's harness code.
* **Benchmarking:** Integrates `lm-evaluation-harness` as a registered skill for self-verification of harness mutations across >60 academic metrics.
