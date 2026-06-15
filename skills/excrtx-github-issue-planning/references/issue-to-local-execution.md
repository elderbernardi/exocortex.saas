# Issue to Local Execution

Use this flow when the executive asks for the next issue, chooses one, and then wants either a plan or immediate repository work.

## Decision split

### 1. Choosing the issue
Inspect:
- issue body
- labels and priority
- dependencies and blockers
- current repository state
- nearby open issues that change sequencing

Output:
- recommended next issue
- short justification
- explicit next options such as:
  - transform into executable plan
  - execute locally now
  - draft remote publication

### 2. Converting issue to local plan
When the executive picks the issue but asks for a plan first:
- inspect the issue body again in detail
- inspect target files in the repo
- verify whether the work is SOLO or touches a contract surface
- write the plan to `.hermes/plans/<timestamp>-<slug>.md`
- encode what belongs to this issue and what must stay deferred to related issues

## Boundary rule

Choosing an existing GitHub issue as the next task does **not** require Draft-First by itself. The remote artifact already exists.

Draft-First applies again only when you:
- push commits
- edit/create/comment on remote issues
- open a PR
- publish any external communication derived from the work

## Good pattern

1. Recommend issue.
2. Turn issue into local executable plan.
3. Execute local file edits.
4. Verify with repo-grounded checks.
5. Commit locally.
6. Present DRAFT before push or any remote update.

## Pitfall

Do not confuse "issue work" with "GitHub publication". Most of the implementation path is internal until the moment you update the remote.
