# GitHub backlog → dependency graph → start sequence

Use when the project backlog already lives in GitHub issues and the executive asks not only "what is open" but also "what should we build first".

## Trigger phrases
- "liste as issues"
- "crie um caminho"
- "grafo de dependência"
- "por prioridade, como começamos o desenvolvimento?"

## Workflow
1. List open issues from GitHub with number, title, labels, body, URL.
2. Group by explicit priority labels first (`P0`, `P1`, `P2`).
3. Infer practical dependencies from scope, not just numeric priority:
   - safety/guardrails before broader automation
   - source-of-truth fixes before docs/setup depending on them
   - harness reliability before using harness results to prioritize later work
   - auth/runtime unblockers before feature-level polish
4. Build a small textual graph using `A -> B` edges.
5. Distinguish:
   - foundational spine
   - integration tracks
   - product/onboarding tracks
   - research/optional tracks
6. End with a recommended start sequence of 3-10 issues.
7. Save the roadmap/graph under `.hermes/plans/` when the analysis is likely to guide multiple sessions.

## Heuristics observed
- A P0 is not always the first item if another issue defines the measurement layer needed to verify it, but safety bugs usually stay first.
- Prefer fixing "false positive harness" issues before expanding test matrices.
- When old labels like `high` coexist with `P1`, normalize priority first; otherwise the graph becomes noisy.
- If two issues overlap conceptually (example: bootstrap tutor vs tutor persona), call out likely merge/consolidation before sequencing downstream work.

## Deliverable shape
- Snapshot by priority
- Textual dependency graph
- Strongest dependency edges with one-line rationale
- Phased path to start development
- Single recommended opening tranche

## Example opening tranche
1. safety guardrail bug
2. harness false-positive bug
3. broad post-provision validation
4. source-of-truth / namespace cleanup
5. integration unblockers

This sequence tends to maximize confidence while minimizing rework.
