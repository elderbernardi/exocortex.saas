---
name: excrtx-quality-gate
description: Quality gate applied by the executor agent at the end of each task. Prose goes through excrtx-quality-antislop, visual through excrtx-quality-taste. Corrections are made by the executor, never by the orchestrator.
version: 1.1.0
category: excrtx
metadata:
  hermes:
    tags: [exocortex, behavior, quality, gate, excrtx-quality-antislop, excrtx-quality-taste]
    related_skills: [excrtx-quality-antislop, excrtx-quality-taste]
compiled_rules: |
  Prose for executive: score with anti-slop (min 35/50). Below threshold: rewrite before delivering.
  Visual output: zero pre-flight failures from excrtx-quality-taste.
  Code and technical docs: no quality gate — deliver directly.
  The agent that produces output is the agent that ensures its quality. Orchestrator never corrects — it returns.
---

# Output Quality Gate — Executor Responsibility

> The agent that produces the output is the agent that ensures its quality. The orchestrator **never** corrects — it returns.

## Core Principle

```
Executor Agent  →  produces output  →  applies quality gate  →  delivers
                                            ↓ (fail)
                                      corrects it themselves
                                            ↓ (fail 2x)
Orchestrator    →  detects failure  →  returns to executor with feedback
                                      (NEVER corrects on its own)
```

Output quality is inseparable from production context. An orchestrator that corrects loses the domain context, the LLM model used, and the original intent. This degrades quality instead of improving it.

## Trigger

The executor agent applies this gate as the **last step** before delivering any substantive output. The gate is part of the production flow, not an external layer.

## Scope — When to Apply and When to Skip

### ✅ APPLY (outputs for the executive)

| Type | Gate | Examples |
|---|---|---|
| **PROSE** | `excrtx-quality-antislop` | Email, briefing, analysis, reflection, summary, textual presentation |
| **VISUAL** | `excrtx-quality-taste` | UI, dashboard, chart, layout, visual presentation |
| **MIXED** | Both | Executive presentation with text and metrics |

### ❌ SKIP (technical outputs)

| Type | Reason | Examples |
|---|---|---|
| **CODE** | Code style follows linters and project conventions, not human prose | Scripts, configs, YAML, JSON, SQL, any language |
| **TECHNICAL DOCS** | Technical clarity > narrative style. Jargon is necessary. | README, ADRs, SKILL.md, docstrings, code comments, specs, schemas |
| **RAW DATA** | No narrative to filter | Numeric tables, logs, dumps, CSVs |
| **SHORT RESPONSES** | Disproportionate overhead | Confirmations ("Feito."), direct questions, system messages |
| **LITERAL QUOTES** | Fidelity > style | Verbatim excerpts from external sources |

> **Golden rule:** If the output is read by machines or by developers in technical context, the gate does not apply.

## Procedure — Executor

### 1. Classify the Output

Before delivering, the executor classifies:
- Is it prose for the executive? → Prose Gate
- Is it visual for the executive? → Visual Gate
- Is it code, technical docs, or data? → **Deliver without gate**

### 2. Prose Gate (excrtx-quality-antislop)

Quick Checks — execute on each produced paragraph:

| Check | Fix |
|---|---|
| Adverb present? | Cut. "Significantly increased" → "increased 40%" |
| Passive voice? | Find the actor. "It was decided" → "The board decided" |
| Inanimate subject with human verb? | "The decision emerges" → "Elder decided" |
| "Not X, it's Y" contrast? | State Y directly |
| Sounds like a pull-quote? | Rewrite — if it sounds tweetable, it's generic |
| Vague declarative? | Name it. "Significant implications" → "Impact: R$2M in margin" |
| Filler phrase? | Cut. "It's important to note that" → (delete) |

**Scoring (minimum 35/50):**

| Dimension | 10 pts | Question |
|---|---|---|
| Directness | Statements or announcements? | Does the text say something or prepare to say? |
| Rhythm | Varied or metronome? | Is there a mix of short and long sentences? |
| Trust | Respects the reader? | Assumes the executive is intelligent? |
| Authenticity | Sounds human? | Would a real person speak like this? |
| Density | Anything cuttable? | Does every sentence carry information? |

### 3. Visual Gate (excrtx-quality-taste)

Pre-flight — verify before delivering:

| Check | Fix |
|---|---|
| Hero exceeds 3 lines? | Widen container, reduce font |
| Grid has empty gaps? | Apply grid-flow-dense |
| Generic labels (SECTION 01)? | Replace with descriptive title |
| Layout identical to previous? | Force variation |
| Invisible button text? | Fix contrast |

Sub-skill by context:
- Data/metrics → `brutalist`
- Identity/brand → `brandkit`
- Landing/product/UI → `gpt-taste`

### 4. Correction by Executor

If the gate fails:

1. **The executor corrects it themselves** — they have the domain context, original prompt, and LLM model
2. **Re-applies the gate** on the corrected version
3. **If fails 2x** → signal to orchestrator with output + failure diagnosis

### 5. Escalation to Orchestrator

When the executor fails the gate 2x:

```
[QUALITY-GATE-FAIL] agent: {executor} | type: {prose|visual} | score: {X}/50
Diagnosis: {what didn't pass}
Output attached for review.
```

The orchestrator then:
1. **Returns to executor** with specific feedback ("rewrite paragraph 2, tone too generic")
2. **Or routes to another agent/model** more suited to the output type
3. **NEVER** attempts to correct the output itself — this degrades quality

## Rules

- The gate is **silent** — the executive never knows it exists
- The executor is the **sole responsible** for their output quality
- The orchestrator is **auditor**, not **corrector** — returns, doesn't rewrite
- Minimum quality score: 35/50 for prose. Visual: zero pre-flight failures
- Code, technical documentation, and raw data **never** pass through the gate
- In skill refactoring, the gate remains bound to the executor — does not migrate to upper layers

## Verification

- [ ] Briefing generated by executor passes excrtx-quality-antislop (≥ 35/50)
- [ ] Email draft generated by executor passes excrtx-quality-antislop
- [ ] Dashboard generated by executor passes excrtx-quality-taste pre-flight
- [ ] Code is NOT filtered by the gate
- [ ] Technical documentation (ADR, README, SKILL.md) is NOT filtered
- [ ] Failure 2x → orchestrator receives signal, does not correct
- [ ] Orchestrator returns to executor with feedback, does not rewrite
- [ ] The harness `validate_artifact_manifest.py` audits the artifact package rejecting prose with slop (score < 35) or visual with meta-labels.