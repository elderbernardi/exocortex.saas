# Cross-Session Pending Audit

Use when the executive asks variations of:
- "o que ficou pendente?"
- "o que temos de outras sessões?"
- "o que ainda está aberto?"
- "quais drafts/planos ainda valem?"

## Purpose

Respond with a living backlog, not blind archaeology. The audit must separate:
1. Living operational pending item;
2. Historical artifact already resolved;
3. Local draft ready for triage/publication;
4. Real external blocker.

## Recommended Reading Order

1. Retrieve previous sessions by resumption terms:
   - `pendente`, `backlog`, `TODO`, `kanban`, `handoff`, `retomada`, `próxima sessão`
2. Check local resumption artifacts:
   - `.hermes/plans/*.md`
3. Check local issue drafts:
   - `acervo/_artifacts/items/draft-issue-*.md`
4. Check consolidated summaries that may reclassify the backlog:
   - e.g., `feature-dogfood-summary-*.md`
5. Check current operational state of the repository:
   - `git status --short`

## Classification Heuristic

### 1. Living Pending Item

Keep as pending when there's work not yet executed, for example:
- Implementation plan not yet started;
- Defect without fix;
- External blocker without resolution;
- Local draft awaiting triage or publication.

### 2. Resolved History

Demote to history when a subsequent session already proves closure, for example:
- PR merged into `main`;
- Branch removed;
- Handoff superseded by subsequent execution;
- Artifact created only for context transition.

### 3. Triageable Draft

List separately when there are local drafts that can already become formal backlog.

### 4. No Local Operational Pending

Declare explicitly when the current state is clean:
- No local changes;
- No remaining work branch;
- No open process in the repository.

## Recommended Response Format

- `Current overall state`
- `What still seems truly pending`
- `What I no longer consider a real pending item`
- `Executive summary`

## Pitfalls

### Pitfall 1 — Treating handoff as eternal backlog

Handoff is a transition artifact. If the following session already executed and closed the work, the handoff becomes history.

### Pitfall 2 — Confusing local draft with already published issue

Draft in `acervo/_artifacts/items/` is potential backlog, not completed execution.

### Pitfall 3 — Ignoring current git state

An old session may mention local pending items, but the current repository may already be clean. Always revalidate the present.

### Pitfall 4 — Returning flat list without prioritization

Separate at least:
- Parent plan;
- Critical failures;
- Drafts for triage;
- Already resolved items.
