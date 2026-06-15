---
name: assessment-question-authoring
description: Produce and review high-quality multiple-choice questions from local course materials and/or NotebookLM, with focus on plausible distractors, mandatory manual curation, and draft file delivery.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - teaching
    - assessment
    - question-authoring
    - notebooklm
    related_skills:
    - excrtx-integrate-nlmops
    - excrtx-quality-antislop
---

# Assessment Question Authoring

Produces and reviews multiple-choice questions from course materials, lesson plans,
knowledge bases, or transcripts. Focuses on distractor quality — the incorrect
alternatives — as the primary differentiator between mediocre and effective questions.

## When to Use

Activate when the executive asks to:
- generate multiple-choice questions from course material, teaching plans, or transcripts
- improve an existing question bank, especially the incorrect alternatives
- use NotebookLM/NLM as a generation engine for question drafts, followed by manual curation
- deliver a `.md` draft file for human review before publication

Do **not** use for:
- writing essay prompts, open-ended questions, or rubrics (different skill)
- publishing questions directly to an LMS or student-facing platform without review
- generating questions from thin air with no source material to ground them

## Expected Output

A verifiable artifact containing:
- complete questions with exactly 4 alternatives (A–D)
- exactly one correct answer per item
- plausible, technically defensible distractors (not caricatures)
- an answer key
- a `.md` draft file saved at an explicit path

## Quality Principles

### 1. The main problem is rarely the stem; it's almost always the distractors

When reviewing questions, prioritize the incorrect alternatives first.

Signs of a bad distractor:
- an absurd or obviously false alternative
- an option in a different conceptual category than the others
- a gross terminology error that eliminates the option on quick inspection
- length, precision, or vocabulary starkly mismatched with the correct answer
- lazy exaggerations like "always," "never," "eliminates," "fully guarantees" without technical context

### 2. A good distractor fails by nuance

Prefer incorrect alternatives that look defensible on first reading and fail on a real conceptual detail. Examples:
- inverting implication and its converse (`a → b` vs `b → a`)
- confusing a stronger model with a weaker one (linearizability vs sequential consistency)
- attributing to one abstraction guarantees that belong to another layer (RPC vs transport)
- confusing a sufficient condition with a necessary one (`R + W > N`)
- swapping the scope of a theoretical result (CAP vs FLP)
- turning a trade-off into a false equivalence

### 3. NLM first; manual curation second

When using NotebookLM/NLM:
1. generate draft questions with an explicit prompt requesting plausible distractors and avoiding obvious wrong answers
2. treat the NLM output as raw material, not a final artifact
3. manually rewrite alternatives to adjust conceptual precision, readability, and answer-key uniqueness

## Procedure

### Step 1 — Discovery and source validation
- Verify that the path or source indicated by the executive actually exists.
- If the path does not exist, state this explicitly and pivot to the best available existing source (e.g., an already-registered NLM notebook) without blocking delivery.
- If a relevant notebook already exists, use it to accelerate generation.

### Step 2 — Generation prompt for NLM
When querying NLM, explicitly request:
- intermediate to difficult level
- 4 alternatives (A–D)
- exactly 1 correct answer
- plausible, technically defensible distractors
- avoid obviously wrong alternatives
- correct answer + brief justification
- natural PT-BR, no AI mannerisms

### Step 3 — Mandatory manual curation

Review item by item.

Per-question checklist:
1. is there exactly one unequivocally correct answer?
2. can any incorrect alternative be dismissed in under 2 seconds?
3. do the wrong alternatives belong to the same conceptual universe as the correct one?
4. is the error in the incorrect alternative subtle but real?
5. does the stem require reasoning, not just keyword hunting?
6. does the answer-key commentary explain the fine distinction, not just restate the correct answer?

### Step 4 — Draft assembly

Deliver a `.md` file with at minimum:
- title
- status `draft for review`
- source used (local files and/or NLM notebook)
- question block
- consolidated answer key
- short editorial note explaining what was improved

## Improvement Patterns

### Pattern A — Replace a gross error with a scope error
Bad:
- "RPC eliminates TCP"

Better:
- "RPC guarantees complete failure transparency"

### Pattern B — Replace an absurdity with a half-truth
Bad:
- "causal order only exists in synchronous networks"

Better:
- "total order always preserves causality even when imposed by an arbitrary criterion"

### Pattern C — Make the incorrect answer compete with the correct one
If the correct answer depends on a fine nuance, the incorrect ones must fail on neighboring nuances — not on a different topic entirely.

## Operational Transparency Phrase

When there is a mismatch between the requested path and the actual source, use a short formulation like:

> "The requested path was not available in this session; I used the most topic-relevant existing NLM notebook as the base and delivered the draft."

## Pitfalls

- **Blind trust in NLM output:** never treat NLM-generated text as the final version. Manual curation is mandatory.
- **Correct answer stands out:** if the correct alternative is noticeably more precise or elegant than the others, the question is broken. Rewrite to level the field.
- **Unverified source path:** do not use a user-provided path without checking existence when the task depends on it. Pivot transparently if the path is absent.
- **Model promise without runtime support:** do not promise a specific model when the current runtime offers no practical override. State the limitation and proceed with the best available execution.
- **Generation without artifact:** never stop at generation. Always save the draft to a verifiable file.

## Verification

- [ ] A `.md` draft file exists at an explicit, verifiable path
- [ ] Every question has exactly 4 alternatives (A–D)
- [ ] Each question has exactly one correct answer
- [ ] All distractors are plausible and belong to the same conceptual domain
- [ ] No distractor can be dismissed in under 2 seconds by a competent reader
- [ ] The answer key is complete and correct
- [ ] Source material is cited (local path or NLM notebook reference)
- [ ] Editorial note explains what was improved relative to the base material

## Future Expansion

If this skill grows, add `references/` with:
- example banks of good distractors by discipline
- tested NLM generation prompts
- a multiple-choice quality assessment rubric
