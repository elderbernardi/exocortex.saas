---
name: excrtx-github-issue-planning
description: Transform Exocórtex plans, architectural refactors, and microverso work into GitHub issue graphs with a meta issue, dependent subissues, and subagent-readable acceptance criteria.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - github
    - planning
    - issues
    - project-management
    related_skills:
    - excrtx-harness-kanban
    - excrtx-govern-draftfirst
---
# Exocórtex GitHub Issue Planning

Use this when the executive wants a plan materialized as GitHub issues rather than kept as prose or local TODOs.

## When to Use

Activate when the task is to:
- convert an assessment into executable GitHub issues
- break a roadmap/refactor into sequenced issues
- publish a microverso consolidation plan
- create issues that subagents can execute with low ambiguity

Do **not** use for one isolated bug/feature issue with no planning graph; basic issue creation is enough there.

## Core Principle

Do not publish a flat pile of tickets. Publish a **graph**:
1. one **META** issue that states the thesis, phases, and definition of done
2. a small set of **subissues** with explicit scope boundaries
3. **dependency comments** that declare blocked-by / blocks relationships in plain language

## Draft-First Rule

GitHub issue creation is an external action.
- If the executive asks to publish the issues now, that instruction is approval for that exact publication scope.
- If the executive asks for a plan but not for publication, prepare the issue set as DRAFT first.
- Do not expand the publication scope by analogy; publish only the issue set that was approved/requested.
- If the runtime/harness still blocks `gh issue create`, `gh issue comment`, or another GitHub write after chat approval, treat the block as authoritative: stop, report what did and did not publish, and offer a local publication package instead of retrying or switching APIs. See `references/github-publication-approval-blocks.md`.

## Local Execution After Issue Selection

When the executive is choosing the next issue to work on, separate two phases:
1. **Selection and planning** — inspect the issue body, labels, dependencies, and current repo state.
2. **Local execution** — once the executive picks the issue, convert it into an executable local plan and work the repository directly.

Rules:
- Turning an existing issue into a local execution plan is **internal work**, not publication.
- If the intended issue graph cannot be published because the runtime blocks GitHub writes, continue from the local plan instead of retrying publication: save the plan, spawn or run a local implementation session with a self-contained prompt, and explicitly prohibit GitHub writes in that prompt.
- Save temporary execution plans under `.hermes/plans/` when the plan should not become repo documentation.
- Save durable roadmap/reference plans under `docs/plans/` when issues must anchor to a project artifact and future agents need continuity.
- If the user then says to proceed, local edits and local commits can execute directly.
- Only `git push`, remote issue edits, comments, or any new publication step re-enter Draft-First.

References:
- `references/issue-to-local-execution.md`
- `references/local-plan-anchored-issue-graphs.md`
- `references/superseding-published-issue-graphs.md` — close/deprecate an obsolete published issue graph after an architectural pivot, using `not planned` and successor-plan comments.
- `references/github-blocked-local-continuation.md`

## Procedure

### 1. Inspect the target repository first
Before drafting issues, determine:
- repository owner/name
- existing labels
- whether nearby issues already exist
- naming style already used in the repo

### 2. Decide the plan topology
Prefer this shape:
- **META** issue: thesis, phases, definition of done, dependency graph
- **P0/P1/P2 subissues**: executable units

Good issue cuts are:
- structurally independent
- small enough for one agent to finish
- large enough to produce a coherent artifact

Bad issue cuts are:
- vague buckets ("improve studio")
- mixed concerns (index cleanup + architecture + tooling in one ticket)
- purely narrative issues with no acceptance criteria

### 3. Write issue bodies for subagents, not for executives
Each subissue should include, in this order:
- Context
- Problem
- Objective
- Scope / Non-scope
- Detailed tasks
- Expected deliverables
- Acceptance criteria
- Notes for smaller agents
- Target files/areas
- Related issues

The body must be executable by someone who did **not** read the whole chat.

### 4. Make dependencies explicit in comments
After creation, add comments such as:
- "Blocked by: #X"
- "Blocks: #Y, #Z"
- short reason for the dependency

Do not rely only on numbering or chronology.

### 5. Verify after publishing
After creating issues, verify:
- issue numbers
- labels applied
- bodies rendered correctly
- dependency comments posted
- META issue links/subissue numbers are correct

## Recommended labels
Use the repo's existing label vocabulary when possible.
For Exocórtex planning work, common combinations are:
- `documentation`
- `enhancement`
- `exocortex`
- `P0` / `P1` / `P2`

## Standard decomposition pattern

### META issue
Must contain:
- why this plan exists
- current diagnosis
- phase ordering
- explicit dependency summary
- definition of done for the whole initiative

### P0 issue
Use for:
- truth-restoring work
- broken indexes/manifests/contracts
- missing state/logs
- blockers to reliable downstream execution

### P1 issue
Use for:
- boundary formalization
- corpus densification
- capability expansion
- receipt/case capture

### P2 issue
Use for:
- optional polish
- secondary optimizations
- future expansion that is not blocking current operation

## Published Graph Supersedence

When an architectural pivot invalidates a published issue graph, do not leave obsolete issues open. After explicit approval, close the superseded META/subissues as `not planned`, add a short deprecation comment pointing to the successor plan, verify their closed state/reason, and update the local plan to mark the old graph as historical. Use `references/superseding-published-issue-graphs.md` for the operational recipe.

## Pitfalls

### Structural
- Publishing one giant issue instead of a graph
- Creating subissues without acceptance criteria
- Encoding dependencies only in your head
- Writing for the executive instead of for future subagents
- Letting a body describe desired maturity as if it already existed
- Duplicating an existing issue rather than linking/complementing it

### Bash quoting with `gh issue create --body`
Inline `--body '...'` is fragile. Bash interprets backticks, single quotes,
dollar signs, and parentheses inside the body string. The command may succeed
but produce a corrupted title or body — the issue is created with wrong content
and no error is surfaced.

**Symptoms:**
- Issue title shows wrong text (e.g., "[Download]" instead of "[Prompt]")
- Two distinct issues get identical bodies
- Shell error: `/usr/bin/bash: line N: <word>: No such file or directory`
  (bash tried to execute a backtick-quoted word as a command)

**Fix — always use `--body-file`:**
```bash
# Write body to a temp file, then create
echo "$body" > /tmp/gh_issue_body.md
gh issue create --title "..." --body-file /tmp/gh_issue_body.md
```
This is the only reliable method for bodies containing backticks, code paths,
single quotes, or any shell-special characters. From `execute_code`, use
`write_file()` + `terminal()` with `--body-file`.


## Support files
- See `references/issue-body-outline.md` for the preferred structure of META and subissue bodies.

## Verification
- [ ] META issue exists and names the initiative clearly
- [ ] Each subissue has executable scope and non-scope
- [ ] Acceptance criteria are specific enough for a smaller agent
- [ ] Dependencies are posted as comments, not implied
- [ ] Published issue set matches the exact scope requested by the executive
