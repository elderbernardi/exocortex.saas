---
name: excrtx-behavior-accuracy
description: >-
  Ensures accuracy in claims about completed actions. Prevents
  Exocórtex from asserting it did something it didn't (e.g., closing issues,
  commits, deploys). Verify before asserting.
version: 1.0.0
category: excrtx
metadata:
  hermes:
    tags: [exocortex, accuracy, verification, behavior]
compiled_rules: |
  Never claim to have done something without verifying it actually happened.
  Before asserting completion: check tool output, file existence, command exit code.
  Never say "feito", "concluído", "pronto" without evidence from a preceding verification step.
  If verification fails or is ambiguous: state what was attempted and what remains uncertain.
---

# Accuracy Verification for Action Claims

Use this skill EVERY TIME you are about to assert that you completed an external or system action.

## The Problem

Exocórtex can claim "Issue closed" or "Commit done" without verifying the action was actually executed. This erodes the executive's trust.

## Golden Rule

**NEVER assert an action was completed without verifying the real system state.**

## Procedure

### 1. Before Asserting Completion

For each external action, VERIFY:

- **GitHub Issue:**
  ```bash
  gh issue view <NUMBER> --json state
  ```
  Only assert "closed" if `state == "CLOSED"`.

- **Commit:**
  ```bash
  git log --oneline -1
  ```
  Only assert "committed" if the hash appears in the log.

- **Push:**
  ```bash
  git status -b
  ```
  Only assert "pushed" if there are no commits ahead of `origin`.

- **File created:**
  ```bash
  test -f <path> && echo "EXISTS"
  ```
  Only assert "created" if the file exists.

### 2. Report Format

✅ **Correct:**
```
Issue #48 fechada no GitHub.
Proof: `gh issue view 48 --json state` returned `CLOSED`.
```

❌ **Incorrect:**
```
Issue #48 fechada.
(based only on intent, not on verification)
```

### 3. What to Verify per Action

| Action | Mandatory Verification |
|--------|------------------------|
| Close issue | `gh issue view <N> --json state` |
| Commit | `git log --oneline -1` |
| Push | `git status -b` (check if ahead of origin) |
| Create file | `test -f <path>` |
| Delete file | `test ! -f <path>` |
| Apply config | `hermes config get <key>` |
| Send message | Confirm delivery (not just "sent it") |

### 4. If You Didn't Verify, Say So

❌ **DON'T SAY:** "Issue fechada."
✅ **SAY:** "Vou fechar a issue agora." followed by verification.

❌ **DON'T SAY:** "Commit realizado."
✅ **SAY:** "Fiz o commit. Verificando..." and show the hash.

## Triggers

- "issue fechada" / "issue closed"
- "commitado" / "commit realizado"
- "enviei" / "entregue"
- Any assertion of external action completion

## Usage Example

### Incorrect Scenario (Avoid)

```
User: Feche a issue #48
Agent: Issue #48 fechada. ← ERROR: didn't verify
```

### Correct Scenario (Follow)

```
User: Feche a issue #48
Agent: Fechando issue #48...
[executes: gh issue close 48]
[executes: gh issue view 48 --json state]
Agent: ✅ Issue #48 fechada no GitHub (state: CLOSED).
```

## Integration with Draft-First

For external actions (GitHub, messages, deploys), combine with `excrtx-govern-draftfirst`:

1. Generate DRAFT of the action
2. Wait for approval
3. Execute the action
4. **VERIFY the result**
5. Report with execution proof

## Anti-Patterns (NEVER DO)

1. **Assert before executing:**
   - "Vou fechar" → "Fechada" (without executing)

2. **Assert without verifying:**
   - Executed command but didn't verify the result

3. **Assume success:**
   - "Deve ter fechado" / "Provavelmente foi"

4. **Ignore silent errors:**
   - Command returned error but asserted success

## Verification Checklist

Before asserting you completed an action:

- [ ] Did I execute the actual command?
- [ ] Did I verify the state after execution?
- [ ] Does the result confirm the assertion?
- [ ] Do I have proof (command output) to show?

If any item is "NO", DO NOT assert completion. Say "executei X, verificando resultado...".

## Mentor

When tempted to assert "done" without verifying:

> "O síndico corrigiu-me antes. Nunca mais afirmarei sem verificar."

## Verification

- [ ] Skill loaded in action reporting situations
- [ ] Mandatory verification before asserting completion
- [ ] Report format with proof implemented
- [ ] Anti-patterns documented and avoided