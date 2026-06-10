# Branch and PR Publication — Draft-First Review

Use this flow when the executive asks for push, PR, PR/issue comment, or any repository state publication.

## Purpose

Prevent external publication from mixing:
- Real commit/branch scope
- Local working tree noise
- Remote branch or PR duplication

## Minimum Checklist Before DRAFT

1. Confirm current branch and HEAD.
2. Confirm the exact commit to be published.
3. Compare the branch against the base (`origin/main` or equivalent base).
4. Separate:
   - Files in the tracked branch diff
   - Local parallel files out of scope (modified/untracked outside the commit)
5. Check if the remote branch already exists.
6. Check if a PR already exists for the same head branch.
7. Run relevant checks and record actual results.
8. Only then build the DRAFT.

## DRAFT Format

### Push DRAFT
- External impact
- Exact push command
- Confirmation of published commit/branch
- Explicit confirmation of what stays out

### PR DRAFT
- Base branch
- Head branch
- Suggested title
- Suggested body
- Test plan with actually executed checks
- Explicit risks and pending items

## Observed Pitfalls

- "Dirty working tree" doesn't automatically mean the push will publish everything; differentiating local state from committed scope avoids false alarms.
- Push and PR are two distinct external effects; requiring separate approval reduces operational error.
- If smoke/harness gets blocked by the environment, record as real pending item; don't fill the PR as if it had been executed.

## Expected Result

The executive receives a verifiable publication package: what goes in, what stays out, what was already validated, and the command ready for approval.