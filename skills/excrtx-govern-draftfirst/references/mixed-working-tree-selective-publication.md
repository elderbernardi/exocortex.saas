# Mixed Working Tree: Selective Publication After Approval

## When to Apply
- The executive approves commit/push/deploy/issue closing
- The repository has local changes from more than one topic simultaneously
- Some approved changes share files with other not-yet-approved changes

## Operational Rule
Approval applies to the **draft's scope**, not to the entire working tree.

## Procedure
1. Before publishing, clearly list the draft scope: files, issue, external effect, and risks.
2. If there are unrelated changes, mention this in the draft before approval.
3. After approval, publish only the approved set:
   - Selective staging by file or hunk;
   - Separate commit per logical unit;
   - Push only what was approved.
4. Only then close the corresponding issue.
5. If the executive also asks to publish the rest, treat as a second publication unit: review, validate, commit, and send separately.

## Pitfalls
- Don't interpret "approved" as authorization to package the entire working tree.
- Don't mix issue A changes with leftover issue B work in the same commit just because both are ready.
- If a file contains hunks from two topics, use selective staging; don't force a monolithic commit.

## Quality Signal
- Each commit can be described in a short sentence.
- Each issue closing points to the right commit.
- The main branch remains green after each published unit.
