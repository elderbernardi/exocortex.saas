# GitHub-First Review of Cross-Session Pending Items

Use when the project has already externalized its backlog to GitHub and the executive asks for a quick read of what's still open.

## Heuristic

1. Single source beats session memory.
   - If local drafts have already been promoted to issues, the living backlog is in the open issues.
2. Explicit priority beats subjective interpretation.
   - Labels `P0`, `P1`, `P2` should structure the response.
3. Absence of priority also communicates.
   - Issues without P labels should not be forced into an arbitrary queue; list them separately.
4. Executive summary must fit in a glance.
   - Close with 2-3 lines like: `critical queue`, `operational queue`, `architecture/research track`.

## Recommended Format

- `P0`
- `P1`
- `P2`
- `No explicit P label`
- `Executive read`

## Errors to Avoid

- Treating old handoff as a living pending item without checking the corresponding issue;
- Mixing local history with already promoted backlog;
- Hiding issues without priority to simplify the read;
- Responding only with session search when canonical backlog already exists on GitHub.
