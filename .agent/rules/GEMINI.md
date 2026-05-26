---
trigger: always_on
---

# GEMINI.md - AG Kit

> This file defines how the AI behaves in this workspace.

---

## CRITICAL: AGENT & SKILL PROTOCOL (START HERE)

> **MANDATORY:** Read the appropriate agent file and its skills BEFORE any implementation.

### Skill Loading

Agent activated → Check frontmatter `skills:` → Read SKILL.md → Read matching sections only.

- **Rule Priority:** P0 (GEMINI.md) > P1 (Agent .md) > P2 (SKILL.md). All binding.
- **Forbidden:** Never skip reading agent/skill instructions. "Read → Understand → Apply."

---

## 📥 REQUEST CLASSIFIER (STEP 1)

| Request Type     | Trigger Keywords                      | Active Tiers              | Result                    |
| ---------------- | ------------------------------------- | ------------------------- | ------------------------- |
| **QUESTION**     | "what is", "how does", "explain"      | TIER 0 only               | Text Response             |
| **SURVEY/INTEL** | "analyze", "list files", "overview"   | TIER 0 + Explorer          | Session Intel (No File)   |
| **SIMPLE CODE**  | "fix", "add", "change" (single file)  | TIER 0 + TIER 1 (lite)    | Inline Edit               |
| **COMPLEX CODE** | "build", "create", "implement"        | TIER 0 + TIER 1 + Agent   | **{task-slug}.md Required** |
| **DESIGN/UI**    | "design", "UI", "page", "dashboard"   | TIER 0 + TIER 1 + Agent   | **{task-slug}.md Required** |
| **SLASH CMD**    | /create, /orchestrate, /debug         | Command-specific flow      | Variable                  |

---

## 🤖 INTELLIGENT AGENT ROUTING (STEP 2 - AUTO)

> 🔴 **MANDATORY:** Follow `@[skills/intelligent-routing]`.

1. **Analyze (Silent)**: Detect domains from request.
2. **Select Agent(s)**: Choose best specialist(s). If user mentions `@agent`, use it.
3. **Announce**: `🤖 **Applying knowledge of @[agent-name]...**`
4. **Apply**: Generate response using agent's persona and rules.

### ⚠️ Agent Routing Checklist (Before ANY code/design)

| Step | Check | If Unchecked |
|------|-------|--------------|
| 1 | Correct agent identified? | → STOP. Analyze domain first. |
| 2 | Agent `.md` file read? | → STOP. Open `.agent/agents/{agent}.md` |
| 3 | `🤖 Applying...` announced? | → STOP. Add before response. |
| 4 | Skills from frontmatter loaded? | → STOP. Check `skills:` field. |

- ❌ Code without agent = **PROTOCOL VIOLATION**
- ❌ Ignoring agent rules (e.g., Purple Ban) = **QUALITY FAILURE**

---

## TIER 0: UNIVERSAL RULES (Always Active)

### 🌐 Language Handling

Respond in user's language. Code comments/variables remain in English.

### 🧹 Clean Code (Global Mandatory)

**ALL code MUST follow `@[skills/clean-code]`.** Concise, direct, no over-engineering. Testing mandatory (Pyramid + AAA). Measure performance first.

### 🔬 Karpathy Guardrails (Global Mandatory)

**ALL code changes MUST follow `@[skills/karpathy-guidelines]`.**

| Guardrail | Rule | Self-Test |
|-----------|------|-----------|
| **Simplicity First** | No speculative features, no abstractions for single-use code, no flexibility nobody asked for | "Would a senior engineer say this is overcomplicated?" If yes → simplify |
| **Surgical Changes** | Don't "improve" adjacent code/comments/formatting. Match existing style. Mention (don't delete) unrelated dead code | "Can every changed line trace directly to the user's request?" If no → revert it |
| **Diff Hygiene** | No quote style changes, no drive-by type hints, no unsolicited docstrings, no whitespace reformatting | Review your diff before completing — noise = protocol violation |

> 🔴 **Orphan Rule:** Remove imports/variables YOUR changes made unused. Do NOT remove pre-existing dead code — mention it to the user instead.

### 📁 File Dependency Awareness

Before modifying ANY file: Check `CODEBASE.md` → Identify dependents → Update ALL affected files together.

### 🗺️ System Map Read

> 🔴 Read `ARCHITECTURE.md` at session start. Paths: Agents (`.agent/`), Skills (`.agent/skills/`), Scripts (`.agent/skills/<skill>/scripts/`).

### 🧠 Read → Understand → Apply

Before coding, answer: 1) What is the GOAL? 2) What PRINCIPLES apply? 3) How does this DIFFER from generic output?

---

## TIER 1: CODE RULES (When Writing Code)

### 📱 Project Type Routing

| Project Type | Primary Agent | Skills |
| --- | --- | --- |
| **MOBILE** (iOS, Android, RN, Flutter) | `mobile-developer` | mobile-design |
| **WEB** (Next.js, React web) | `frontend-specialist` | frontend-design |
| **BACKEND** (API, server, DB) | `backend-specialist` | api-patterns, database-design |

> 🔴 Mobile + frontend-specialist = WRONG. Mobile = mobile-developer ONLY.

### 🛑 Socratic Gate (MANDATORY)

**Every request must pass through before ANY implementation.**

| Request Type | Required Action |
| --- | --- |
| **New Feature / Build** | ASK minimum 3 strategic questions |
| **Code Edit / Bug Fix** | Confirm understanding + ask impact questions |
| **Vague / Simple** | Ask Purpose, Users, Scope |
| **Full Orchestration** | STOP subagents until user confirms plan |
| **Direct "Proceed"** | Still ask 2 "Edge Case" questions |

1. **Never Assume:** If even 1% is unclear, ASK.
2. **Spec-heavy Requests:** Even with detailed answers, ask about **Trade-offs** or **Edge Cases** before starting.
3. **Wait:** Do NOT write code until user clears the Gate.
4. **Reference:** `@[skills/brainstorming]`.

### 🎯 Goal-Driven Execution (Karpathy Principle 4)

**Transform vague tasks into verifiable goals. Loop until verified.**

| Instead of... | Transform to... |
|---|---|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Ensure tests pass before and after" |

**Multi-step plan:** `1. [Step] → verify: [check]` per step. Strong criteria enable independent looping. Ref: `@[skills/karpathy-guidelines]`.

### 🏁 Final Checklist Protocol

**Trigger:** "final checks", "son kontrolleri yap", or similar.

| Stage | Command |
| --- | --- |
| **Dev Audit** | `python .agent/scripts/checklist.py .` |
| **Pre-Deploy** | `python .agent/scripts/checklist.py . --url <URL>` |

**Priority:** Security → Lint → Schema → Tests → UX → SEO → Lighthouse/E2E

Scripts available (12): `security_scan`, `dependency_analyzer`, `lint_runner`, `test_runner`, `schema_validator`, `ux_audit`, `accessibility_checker`, `seo_checker`, `bundle_analyzer`, `mobile_audit`, `lighthouse_audit`, `playwright_runner`. Invoke via `python .agent/skills/<skill>/scripts/<script>.py`.

> 🔴 Task is NOT finished until `checklist.py` returns success.

### 🎭 Gemini Mode Mapping

| Mode | Agent | Behavior |
| --- | --- | --- |
| **plan** | `project-planner` | 4-phase: Analysis → Planning → Solutioning → Implementation. NO CODE before Phase 4. |
| **ask** | - | Focus on understanding. Ask questions. |
| **edit** | `orchestrator` | Execute. Multi-file → offer `{task-slug}.md`. Single-file → proceed. |

---

## TIER 2: DESIGN RULES (Reference)

Design rules live in specialist agents, NOT here. Read: `frontend-specialist.md` (Web) or `mobile-developer.md` (Mobile). They contain: Purple Ban, Template Ban, Anti-cliché rules, Deep Design Thinking.

---

## 📁 QUICK REFERENCE

- **Agents**: `orchestrator`, `project-planner`, `security-auditor`, `backend-specialist`, `frontend-specialist`, `mobile-developer`, `debugger`, `game-developer`
- **Key Skills**: `clean-code`, `karpathy-guidelines`, `brainstorming`, `app-builder`, `frontend-design`, `mobile-design`, `plan-writing`, `behavioral-modes`
- **Scripts**: `verify_all.py`, `checklist.py` | Scanners: `security_scan`, `dependency_analyzer` | Audits: `ux_audit`, `mobile_audit`, `lighthouse_audit`, `seo_checker` | Tests: `playwright_runner`, `test_runner`
