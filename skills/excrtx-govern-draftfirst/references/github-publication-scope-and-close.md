# GitHub Publication: Scope, Publication, and Closing

## When to Use
When the executive asks for commit, push, issue comment, issue closing, PR opening/editing, or merge.

## Recommended Sequence
1. Inspect current branch, remote, and working tree.
2. Separate files in the requested scope from parallel out-of-scope files.
3. Build DRAFT with:
   - Included files
   - Excluded files
   - Suggested commands
   - Tests executed and results
   - Exact external effect (commit, push, comment, closing)
4. Only execute after explicit post-DRAFT approval.

## Recurring Pitfalls
- `git status` may contain parallel noise; don't assume everything pending goes into the commit.
- Local comment/issue drafts may be useful for publication, but don't need to enter the commit.
- Closing an issue is a distinct external effect from commenting on an issue; both must be covered in the DRAFT.
- User's imperative request to publish does not replace post-DRAFT approval.

## Scope Rule
If the initial request is to resolve a specific issue, the default is to publish only files directly related to that issue. Any scope expansion must be made explicit in the DRAFT.
