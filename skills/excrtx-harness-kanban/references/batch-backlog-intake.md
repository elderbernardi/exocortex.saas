# Batch Backlog Intake — Multiple Raw Items → Structured Backlog

> When the executive sends a batch of links, commands, observations, and screenshots and expects them to become organized backlog.

## Trigger

Use when the executive sends multiple items simultaneously (>3) with instructions like "cria issues", "coloca no backlog", "adiciona como tarefa", "organiza isso".

## Principle

The raw batch cannot become loose backlog. Each item needs:
- Additional context (when absent, ask or infer reasonably)
- Classification: type + priority + area
- Initial scope
- Acceptance criteria

## Flow

### 1. Collection and Consolidation

Group items by thematic affinity before classifying:

- External integrations (links, MCPs, services)
- Setup/infrastructure (installations, binaries, configs)
- Architecture and behavior (design decisions)
- Models and routing (providers, rankings)
- Docs and research (Reddit, manuals)
- Bugfixes (drift, names, noise)

Items too ambiguous for direct implementation → mark as `research` or `chore` with clarification scope.

### 2. Per-Item Classification

Each item receives:

| Field | Values |
|---|---|
| **type** | `bug`, `feature`, `docs`, `infra`, `research`, `chore` |
| **priority** | `P0` (blocker), `P1` (next cycle), `P2` (when possible), `P3` (nice-to-have) |
| **area** | `hermes`, `exocortex`, `memory`, `ui`, `integration`, `models`, `docbrain`, `google`, `telegram` (adjust to context) |

Rule: items with dependencies between them inherit the priority of the highest. E.g., if `gcloud` (P1) blocks Google Workspace (P1), both P1.

### 3. Documentation with Context + Scope + Criteria

Each issue/backlog-item must have:

```markdown
### Title
[Action] [object] — up to 80 chars, oriented to decision or next action

### Context
Why does this exist? What led to registering it? 2-3 sentences.

### Initial Scope
- What to do first
- What NOT to do
- Known dependencies

### Acceptance Criteria
- [ ] Verifiable condition A
- [ ] Verifiable condition B
```

**Pitfall:** Items without acceptance criteria become tasks that never finish. Always define "how to know this is done."

### 4. Presentation and Approval

- Consolidate in a local markdown file (`candidate-issues.md` or similar)
- Present as DRAFT (following Draft-First protocol)
- Only create issues/kanban-cards after explicit approval

### 5. Relative Prioritization

Present suggested attack order:

```
P0 — items that block others
P1 — items for the current cycle
P2 — documented but not immediate items
P3 — items that need clarification first
```

## Design Trigger

When a requested backlog involves **architectural decision** (e.g., "A, B, or C?"), don't give a ready answer — present options with trade-offs and ask for explicit choice before registering.

## Example from This Session

In this session, 16 raw items (links + commands + screenshot + observations) were consolidated in `candidate-issues.md` with:
- type/priority/area classification
- context + scope + criteria per item
- suggested attack order (P0→P3)
- 1 issue created on GitHub after approval