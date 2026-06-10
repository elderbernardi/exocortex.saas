# Hermes Kanban Blocked Card Verification

Use this pattern when the pending item depends on a human decision and must not fall into automatic execution.

## Safe Sequence

1. Create the card with a decision-oriented title.
2. Insert mandatory references in the body.
3. Verify the result with `kanban list` and `kanban show`.
4. If the card is not in `blocked`, apply explicit block.
5. Verify again.

## Quality Signal

The final `show` should make clear:
- Status `blocked`
- Most recent summary explaining the dependency on human decision
- Sufficient references for resumption without session reconstruction

## Recommended Block Comment

```text
Awaiting explicit executive decision on architecture, storage, v1 scope, and private staging.
```

Adapt the phrase to the case, but keep the concrete reason.

## When to Use

- Proposed ADR without final decision
- Architecture decision
- v1 scope choice
- Operational policy still undefined
- Any resumption that depends on executive approval or direction
