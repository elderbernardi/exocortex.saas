# LLM-as-Judge for Agent Skills — Knowledge Base

> Synthesized from NotebookLM research across 4 notebooks, 10+ primary sources.
> NLM Notebook: `8bda1bfa-caff-4d00-904e-d55950bb9e93`

---

## 1. Theoretical Foundations

### The Delegation Paradox (Forja Cognitiva)

The more we delegate cognition to AI agents, the more metacognition we need to evaluate their output. Delegating without metacognition is "outsourcing without audit" — a brilliant employee without supervision works until the day it doesn't.

> "Se você não entende o suficiente para avaliar o que a IA produziu, você não está usando IA — ela está usando você."
> — A Forja Cognitiva, Slide 18

This creates the fundamental requirement for a **Skill Judge**: it's the metacognitive layer that makes delegation safe. The human architects the evaluation strategy; the LLM scales the tactical judgment.

### Three Competency Dimensions (Agent Evaluation Theory)

Based on Google DeepMind's Agents Best Practices and multi-agent system research, agent skills should be evaluated across three behavioral dimensions:

| Dimension | What It Measures | Failure Mode |
|---|---|---|
| **Reasoning & Strategy** | Depth of logical decomposition and problem diagnosis | Shallow analysis, wrong tool selection |
| **Execution & Reliability** | Resilience, risk assessment, self-correction when assumptions contradict observations | Infinite loops, silent failures, unsafe state changes |
| **Interaction & Output** | Ambiguity handling (when to pause for human input), precision in edge cases | Over-autonomy, under-specificity, verbose noise |

### The "Alma" Factor

The evaluation of what constitutes a "good" skill only exists when there's a strong initial intention — the "why am I doing this?" that precedes any "how." Skills must be measured against a **cognitive ground** projected by the human architect (SOUL_SEED, behavioral contract, executive persona), not against abstract quality criteria.

---

## 2. Rubric Design Best Practices

### Source: Zheng et al. (2023) — "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"

The foundational paper established that LLM judges can match human preferences at 80%+ agreement when properly designed. Key limitations to mitigate:

| Bias | Description | Mitigation |
|---|---|---|
| **Position bias** | LLMs favor the first response in pairwise comparisons | Swap response order between runs |
| **Verbosity bias** | LLMs rate longer answers higher | Apply explicit length penalties in rubric |
| **Self-enhancement bias** | LLMs prefer their own outputs | Use a different model for judging than for generating |
| **Limited reasoning** | LLMs struggle with math, logic, and subtle errors | Feed full execution traces, not just final output |

### Categorical vs. Numeric Scoring

| Approach | When to Use | Risk |
|---|---|---|
| **Categorical labels** (`COMPLIANT`/`PARTIAL`/`NON_COMPLIANT`) | Binary compliance checks, structural validation | Less granular |
| **Constrained fractional** (0-1 per dimension) | Optimization loops where gradient signal matters | Mean-reversion if dimensions aren't specific |
| **1-10 numeric scales** | Almost never — LLMs cluster around 7-8 | Mean-reversion, unreliable |

**Recommendation from Hermes Self-Evolution**: Use fractional 0-1 scores tied to **very specific behavioral dimensions** (e.g., "Did the agent follow the skill's procedure?") rather than holistic quality ratings. For structural compliance, use categorical labels.

### The Four-Part Rubric Structure

Every rubric criterion must include:

1. **Criterion Definition** — Clear domain-specific vocabulary
2. **Reasoning Structure** — Mandatory chain-of-thought before scoring
3. **Scoring Rules** — Categorical labels with boundary conditions
4. **Edge Case Clauses** — What to do when the skill is ambiguous

---

## 3. Hermes Canonical SKILL.md Format

### Required Frontmatter (Validator-Enforced)

```yaml
name: string        # kebab-case, ≤64 chars
description: string # ≤1024 chars, single sentence, starts with "Use when..."
```

A non-empty body following the closing `---` is required.

### Peer-Matched Frontmatter (Not enforced but expected)

```yaml
version: semver
author: string
license: MIT
platforms: [linux, macos, windows]  # OS gate
metadata:
  hermes:
    tags: [category, subcategory, keywords]
    related_skills: [other-skill-name]
    config:
      - key: setting.name
        description: "What this controls"
        default: "value"
```

### Required Sections (Authoring Standards)

| Section | Purpose | Notes |
|---|---|---|
| `# Title` + Overview | 2-3 sentences: what it does, what it doesn't | First thing the agent sees |
| `## When to Use` | Positive triggers + counter-triggers | MUST include "Don't use for:" |
| `## Prerequisites` | Env vars, tools, MCP setup | Only if dependencies exist |
| `## Quick Reference` | Flat command/API table | Token-efficient lookup |
| `## Procedure` | Numbered steps with copy-paste commands | The actionable body |
| `## Common Pitfalls` | Known limits, things that look broken but aren't | Production-learned failures |
| `## Verification Checklist` | Single command or step proving correctness | Checkbox format preferred |

### Size Budget

- **Peer range**: 8,000–15,000 characters (official skills sit at 8–14K)
- **Split threshold**: If pushing past 20K, extract into `references/*.md`
- **Hard limit**: 100,000 characters (enforced as `MAX_SKILL_CONTENT_CHARS`)
- **Description**: ≤60 characters for PR-quality, ≤1024 enforced

### Progressive Disclosure (How Skills Load)

1. **Discovery** (`skills_list()`): Compact list of names + descriptions (~3K tokens total)
2. **On-demand** (`skill_view()`): Full SKILL.md loaded only when the agent decides it needs it
3. **Reference files**: `skill_view(name, file_path)` for deep reference material

Skills are never all loaded at once — this is critical for token economy.

### Skill Activation Rules

| Rule | Description |
|---|---|
| **Platform gating** | `platforms: [linux]` hides skill on macOS/Windows |
| **Conditional activation** | `requires_toolsets` / `fallback_for_toolsets` show/hide based on available tools |
| **Bundle precedence** | Bundles override individual skills on slug collision |
| **Local precedence** | `~/.hermes/skills/` wins over external dirs on name collision |

---

## 4. Hermes Self-Evolution Pipeline (GEPA + DSPy)

### Architecture

```
SessionDB → Eval Dataset Builder → DSPy Module Wrapper → GEPA Optimizer
    → Candidate Variants → Constraint Validation → Best Valid Variant
    → Git Branch + PR → Human Review & Merge
```

### Three Optimization Engines

| Engine | Optimizes | License | Integration |
|---|---|---|---|
| **DSPy + GEPA** | Skills, prompts, instructions, tool descriptions | MIT | Primary engine |
| **Darwinian Evolver** | Code files, algorithms, tool implementations | AGPL v3 | External CLI |
| **DSPy MIPROv2** | Few-shot examples, instruction text | MIT | Fallback optimizer |

GEPA is primary because it reads execution traces to understand **why** things fail, not just **that** they fail. Works with as few as 3 examples.

### Fitness Function Design

The fitness function is **composite**, mixing:

1. **LLM-as-Judge rubric scores** (0-1 per dimension): procedure adherence, correctness, conciseness
2. **Length penalty**: variants approaching token limit scored lower regardless of quality
3. **Semantic preservation check**: evolved text compared against original for meaning drift
4. **Benchmark gating** (hard gate): TBLite/YC-Bench scores must not regress by even 2%

> **Key principle**: Benchmarks are GATES, not fitness functions. A variant that improves skill quality by 20% but drops TBLite by 5% is REJECTED.

### Eval Dataset Sources

| Source | How | Volume |
|---|---|---|
| **Synthetic** | Strong model generates (task, correct_output) pairs | 10-20 per skill |
| **SessionDB mining** | Extract real (task, response) pairs from production | Grows organically |
| **User corrections** | "No, use X instead" signals from real usage | High-value negatives |
| **Confusing tasks** | Tasks where two tools/skills could apply | 10-20 for disambiguation |

### Deployment Rules

- **No hot-swapping**: Evolved content NEVER replaces active session content
- **PR-only deployment**: All changes go through git PR with before/after scores
- **Human review**: Every evolved artifact requires manual approval
- **Cost**: GEPA runs cost ~$2-10 per optimization, Darwinian Evolver ~$2-9 per task

---

## 5. DeepEval Evaluation Framework Patterns

### Two-Level Evaluation

| Level | What | When |
|---|---|---|
| **End-to-end** | Overall system input/output quality | Final validation |
| **Component-level** | Individual inner workings (via tracing) | Debugging, optimization |

### Evaluation Workflow

```
Generate dataset → Define metrics → Run LLM app → Produce outputs
    → Report failing cases + metric scores → Improve prompts/tools/logic
    → Re-run (iterate)
```

### Tracing for Nested Components

By setting up tracing (~10 lines of code), you can:
- Run different metrics on different components
- Evaluate multiple components simultaneously
- Avoid rewriting codebase to bubble up return variables

---

## 6. Multi-Agent Quality Patterns (Dr. MAS)

### Stability Through Procedural Memory

Agent procedural memory = model weights + agent code + prompt. The most practical self-improvement method is **prompt self-refinement** (meta-prompting):

1. Feed the agent its current instructions + recent conversations + user feedback
2. Agent refines its own instructions based on this input
3. Save refined instructions back to memory store

This is especially useful when instructions are hard to specify upfront — the agent learns from interaction corrections.

### Fitness for Multi-Agent Evolution

Based on cooperative multi-agent research (MARL):

- **Trajectory-based reward**: Score the full interaction trajectory `τ = {(s₁,a₁,k₁), ...}`, not individual steps
- **Binary rule-based rewards**: Simple 1/0 (success/failure) with penalty coefficients for invalid actions
- **Multi-agent architecture**: Solver + Verifier loops for self-correction
- **Group-based rollouts**: Generate N candidate solutions, score all, keep best

---

## 7. Sources

| # | Source | ID | Topic |
|---|---|---|---|
| 1 | Zheng et al. "Judging LLM-as-a-Judge" (arXiv:2306.05685) | `fce6b38a` | Foundational LLM judge framework, bias analysis |
| 2 | Hermes Creating Skills Guide | `2b41fdd1` | Full SKILL.md authoring guide |
| 3 | Hermes CONTRIBUTING.md | `f0d095c1` | PR standards, skill guidelines |
| 4 | Hermes Self-Evolution PLAN.md | `738a69a7` | DSPy+GEPA optimization, fitness functions |
| 5 | hermes-agent-skill-authoring SKILL.md | `15d23837` | Meta-skill for writing skills |
| 6 | DSPy Framework Docs | `49cbd91e` | Module wrapping, signature design |
| 7 | Hermes Work with Skills Guide | `8e5695c9` | Practical skill usage tips |
| 8 | Hermes Configuration Docs | `4b05dd8e` | SOUL.md priority, context limits |
| 9 | Hermes Skills Feature Docs | `053d3c78` | Bundles, categories, activation |
| 10 | DeepEval Evaluation Framework | `1a841b28` | End-to-end + component-level eval |

### NLM Cross-References

| Notebook | ID | Query Topic |
|---|---|---|
| A Forja Cognitiva | `6b55acc7` | Meta-intelligence principles for agent evaluation |
| Dr. MAS | `477a43a0` | Multi-agent stability and fitness patterns |
| LLM-as-Judge (dedicated) | `8bda1bfa` | Rubric design, skill authoring, self-evolution |
