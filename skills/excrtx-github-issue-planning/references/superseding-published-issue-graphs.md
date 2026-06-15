# Superseding a Published Issue Graph

Use this when an architectural decision invalidates an issue graph that was already published.

## Trigger

A published META/subissue set reflects an older implementation thesis, and continuing to leave it open would confuse future agents or humans.

Examples:
- Docker-first plan is replaced by barebone-per-user architecture.
- A spike proves the planned direction is wrong.
- A dependency/license constraint changes the delivery path.

## Procedure

1. Verify the old issue set and current state.
   - List the affected issue numbers.
   - Confirm they are still open.
   - Confirm the new canonical local plan or replacement issue graph exists.

2. Draft the deprecation action.
   - Name every issue to close.
   - State the reason: deprecated/superseded, not completed.
   - Point to the successor plan or replacement issue graph.

3. Execute only after explicit approval.
   - GitHub issue edits/comments/closures are external actions.
   - If approval is present but the harness blocks the command, stop and report. Do not retry through another API.

4. Close stale issues as `not planned`.
   - Use `gh issue close N --reason not planned --comment "..."`.
   - The comment should say the issue is deprecated and must not be executed.
   - Include the canonical successor reference.

5. Verify all affected issues.
   - Check state is `CLOSED`.
   - Check state reason is `NOT_PLANNED`.

6. Update local durable plan.
   - Mark the old plan as superseded.
   - Record the issue numbers closed as deprecated.
   - Keep historical context; do not delete the old plan.

## Comment Template

```text
Fechada como deprecated para evitar confusão. A hipótese anterior foi superada por [nova decisão]. Referência canônica local: [path]. Não executar esta issue; usar o plano sucessor e as próximas issues derivadas.
```

## Pitfalls

- Do not leave obsolete P0/P1 issues open after the architecture changes; future agents will execute stale work.
- Do not mark deprecated issues as completed. Use `not planned` unless the work was actually delivered.
- Do not delete issue history. Preserve the old graph as design history and point to the successor.
- Do not expand approval scope. Authorization to close deprecated issues does not authorize creating new ones if the harness previously blocked publication.
