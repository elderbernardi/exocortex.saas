# GitHub issue publication from local drafts

Use when local issue drafts exist in the repo/acervo and the executive asks to publish or consolidate them.

## Rule

Creating or commenting on GitHub issues is an external side effect. Treat it under Draft-First.

## Recommended sequence

1. Inventory existing GitHub issues first (`open` and relevant `closed`).
2. Inventory local draft issues.
3. Classify each draft into one of four buckets:
   - `create`: no strong duplicate exists and the problem is still current;
   - `absorb-open`: fold into an existing open issue;
   - `historical-closed`: already represented by a closed issue; do not recreate;
   - `drop-stale`: no longer relevant under current repo/runtime state.
4. Produce a local consolidation note before publishing anything. That note should list:
   - drafts to create;
   - drafts to merge into existing issues;
   - drafts to discard as stale/historical;
   - local files eligible for deletion after publication.
5. Present one explicit publication/cleanup DRAFT to the executive.
6. Only after approval:
   - create the new issues;
   - update/comment existing umbrella issues with absorbed findings;
   - delete the local draft records that were published, merged, or intentionally archived.

## Anti-duplication heuristics

Prefer merging when the draft is really one of these under a broader open issue:
- harness coverage gap;
- contract/documentation drift under an existing umbrella;
- revalidation of an already-known feature family.

Prefer a new issue when the draft represents:
- a new user-visible failure mode;
- a safety violation;
- a reproducible runtime bug with distinct acceptance criteria;
- a still-current blocker not covered concretely by an existing issue.

## Cleanup rule

Do not leave local draft issues behind after approved publication/merge, or they will become retask bait in later sessions.
Delete only after the GitHub state reflects the decision.

## Example buckets from this session shape

- `historical-closed`: local EX-06 draft when the corresponding issue already exists and is closed.
- `absorb-open`: self-test/OAuth-fixture findings folded into an existing harness umbrella.
- `create`: Draft-First safety regression, Google Drive syntax bug, browser/notebook operational blockers.

## Pitfall

Do not create issues directly from every local draft. First compare with current GitHub state; otherwise the backlog fragments and future sessions waste time reconciling duplicates.