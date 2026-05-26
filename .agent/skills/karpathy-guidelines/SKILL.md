---
name: karpathy-guidelines
description: Behavioral guardrails to reduce common LLM coding mistakes. Think before coding, simplicity first, surgical changes, goal-driven execution. Derived from Andrej Karpathy's observations on LLM pitfalls.
when_to_use: "ALWAYS ACTIVE as a behavioral overlay. Enforces assumption surfacing, minimal code, surgical edits, and verifiable goals. Complements clean-code, simplify-code, brainstorming, and verify-changes skills."
allowed-tools: Read, Write, Edit, Grep, Glob
version: 1.0
priority: CRITICAL
source: https://github.com/multica-ai/andrej-karpathy-skills
license: MIT
---

# Karpathy Guidelines — LLM Coding Guardrails

> **CRITICAL BEHAVIORAL SKILL** — Four principles that directly combat the most common LLM coding failures.
>
> Source: [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.

**Tradeoff:** These guidelines bias toward **caution over speed**. For trivial tasks (typo fixes, obvious one-liners), use judgment — not every change needs full rigor.

---

## The Problems These Guidelines Solve

> "The models make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should."

> "They really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do."

> "They still sometimes change/remove comments and code they don't sufficiently understand as side effects, even if orthogonal to the task."

---

## 🧠 Principle 1: Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

| Rule | Action |
|------|--------|
| **State assumptions** | If uncertain about interpretation, ASK — don't guess |
| **Present options** | If multiple interpretations exist, list them — don't pick silently |
| **Push back** | If a simpler approach exists, say so — don't blindly comply |
| **Stop when confused** | Name what's unclear and ask for clarification |

### Self-Check Before Implementing

```
Before writing ANY code, answer:
1. What exactly is the user asking for? (restate in your own words)
2. What am I assuming that wasn't explicitly stated?
3. Are there multiple valid interpretations? If yes → present them.
4. Is there a simpler approach the user might not have considered?
```

> 🔗 **Complements:** `brainstorming` skill (Socratic Gate) — use both for complex requests.

---

## ✂️ Principle 2: Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

| ❌ Don't | ✅ Do |
|----------|------|
| Features beyond what was asked | Exactly what was requested |
| Abstractions for single-use code | Direct implementation |
| "Flexibility" or "configurability" not requested | Simple, focused solution |
| Error handling for impossible scenarios | Handle real failure modes only |
| 200 lines when 50 would do | Rewrite until minimal |

### The Test

> **"Would a senior engineer say this is overcomplicated?"** If yes → simplify.

### When Complexity Is Actually Needed

Add complexity **only when**:
- Performance is measurably insufficient
- Multiple concrete use cases exist right now (not "might need later")
- The user explicitly requested the abstraction
- Framework/library constraints require it

> 🔗 **Complements:** `simplify-code` skill — use for refactoring existing overengineered code.
> 🔗 **Complements:** `clean-code` skill (KISS, YAGNI principles).

---

## 🔬 Principle 3: Surgical Changes

**Touch only what you must. Clean up only your own mess.**

### When Editing Existing Code

| Rule | Rationale |
|------|-----------|
| Don't "improve" adjacent code, comments, or formatting | Noise in diffs, risk of breakage |
| Don't refactor things that aren't broken | Unasked-for changes introduce risk |
| Match existing style, even if you'd do it differently | Consistency > personal preference |
| If you notice unrelated dead code → **mention it**, don't delete it | Respect scope boundaries |

### When Your Changes Create Orphans

| Scenario | Action |
|----------|--------|
| Your changes made an import unused | ✅ Remove it |
| Your changes made a variable unused | ✅ Remove it |
| Pre-existing dead code you noticed | ❌ Don't remove — mention to user |

### The Test

> **Every changed line should trace directly to the user's request.** If you can't justify a change by pointing to the request, revert it.

### Diff Hygiene Checklist

```
Before submitting changes, review your diff:
□ No quote style changes ('' → "" or vice versa)
□ No added type hints unless requested
□ No added/changed docstrings unless requested  
□ No whitespace reformatting
□ No variable renames unrelated to the task
□ No "drive-by" refactoring
```

> 🔗 **Complements:** `clean-code` skill (File Dependency Awareness, Self-Check).

---

## 🎯 Principle 4: Goal-Driven Execution

**Define success criteria. Loop until verified.**

### Transform Imperative → Declarative

| Instead of... | Transform to... |
|---------------|-----------------|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Ensure tests pass before and after" |
| "Add logging" | "Verify log output appears for success and error paths" |

### Multi-Step Plan Format

```
Plan:
1. [Step] → verify: [concrete check]
2. [Step] → verify: [concrete check]
3. [Step] → verify: [concrete check]
```

### Success Criteria Quality

| ❌ Weak (requires clarification) | ✅ Strong (enables independent looping) |
|----------------------------------|----------------------------------------|
| "Make it work" | "Test returns expected JSON for valid/invalid inputs" |
| "Fix authentication" | "Old session invalidated after password change" |
| "Improve performance" | "Response time < 200ms for 95th percentile" |

> 🔗 **Complements:** `verify-changes` skill — use for execution-based verification.
> 🔗 **Complements:** `tdd-workflow` skill — use for test-first development.

---

## Anti-Patterns Summary

| Principle | Anti-Pattern | Fix |
|-----------|-------------|-----|
| **Think Before Coding** | Silently assumes file format, fields, scope | List assumptions explicitly, ask for clarification |
| **Simplicity First** | Strategy pattern for single discount calculation | One function until complexity is actually needed |
| **Surgical Changes** | Reformats quotes, adds type hints while fixing bug | Only change lines that fix the reported issue |
| **Goal-Driven** | "I'll review and improve the code" | "Write test for bug X → make it pass → verify no regressions" |

---

## Key Insight

> "LLMs are exceptionally good at looping until they meet specific goals... Don't tell it what to do, give it success criteria and watch it go." — Andrej Karpathy

**Good code is code that solves today's problem simply, not tomorrow's problem prematurely.**

---

## How to Know These Guidelines Are Working

- **Fewer unnecessary changes in diffs** — Only requested changes appear
- **Fewer rewrites due to overcomplication** — Code is simple the first time
- **Clarifying questions come before implementation** — Not after mistakes
- **Clean, minimal PRs** — No drive-by refactoring or "improvements"

---

## 📚 Reference

See `examples/` folder for detailed before/after code examples demonstrating each principle.
