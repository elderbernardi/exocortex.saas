---
name: excrtx-assess-interactive-audit
description: Use when the executive asks to audit, evaluate, review, or decide GO/NO-GO for a real artifact under production-like conditions — UX/UI, data quality, accessibility, API/CLI contract, workflow, or skill quality — using owner-in-the-loop personas, evidence capture, issue backlog, and Exocortex governance.
version: 1.0.0
category: excrtx
platforms:
- linux
author: Exocórtex
license: MIT
metadata:
  hermes:
    tags:
    - exocortex
    - audit
    - evaluation
    - persona
    - ux-review
    - data-quality
    - accessibility
    - api-contract
    - skill-quality
    related_skills:
    - excrtx-quality-skilljudge
    - excrtx-quality-gate
    - excrtx-govern-draftfirst
    - excrtx-govern-tools
    - excrtx-memory-manager
    - excrtx-integrate-browser
---
# Interactive Audit — Exocórtex

## Overview

Use this skill to run a moderated, evidence-based audit of a real artifact. The audit does not invent a new format per request. It instantiates `references/prompt-template.md`, runs two personas, captures evidence, asks the executive blocking questions at finding-time, and produces an issue backlog ready for action.

The source package was `interactive-audit` v2026.07.07. This adaptation makes it canonical for Exocórtex over Hermes: Vetor classification, Draft-First, Acervo boundaries, tool governance, and skill-quality gates are mandatory.

## When to Use

Activate when the executive asks for:

- product, UX/UI, accessibility, data-quality, API/CLI, workflow, or release-readiness audit;
- beta readiness, production readiness, GO/NO-GO, release sign-off;
- persona-driven review under real conditions;
- issue backlog generation from an artifact;
- audit of a skill, prompt, harness behavior, or agent protocol.

**Don't use for:** simple code review, unit-test creation, bugfix execution, refactor, generic brainstorming, or reading a document without producing an audit. Use specialized development or research skills instead.

## Procedure

### 1. Classify vector and scope

Classify the request before acting:

- **Execução:** the executive wants an audit artifact or GO/NO-GO verdict. Produce the audit directory and reports.
- **Evolução:** the executive wants to understand whether an audit design is right. Ask 2–3 framing questions before writing artifacts.
- **Manutenção:** the executive wants to inspect audit backlog, stale findings, or harness health. Review existing audit dirs and report status.

Completion: vector, target artifact class, and audit goal are explicit.

### 2. Resolve audit home and prior art

Use the first existing audit home in the active project:

```text
.harness/evaluation/
docs/audits/
audits/
```

If none exists, create `audits/` at project root. Search prior audits for the same artifact. A successor audit starts from the predecessor's `reports/FINAL_REPORT.md` and separates regression, new surface, and fresh discovery.

Completion: audit directory path selected and prior-art status recorded.

### 3. Instantiate the template

Read `references/prompt-template.md`, fill every placeholder, drop non-applicable optional sections, and save:

```text
{audit-home}/{YYYY-MM-DD}_{slug}/PROMPT.md
```

Create the required coordination set:

```text
TASKS.md
PROGRESS.jsonl
QUESTIONS.jsonl
artifacts/
reports/
```

Completion: all required files/directories exist.

### 4. Run kickoff Q&A before touching the artifact

Ask the executive, blocking:

1. target: URL, dataset, branch, deploy, file, API, skill path, or repository;
2. credentials/accounts: read secrets only from canonical runtime location; never paste secrets into committed files;
3. mutation authorization: what actions may create, edit, send, publish, or write external state.

Do not guess these. Log every question and answer in `QUESTIONS.jsonl`.

Completion: target, credential path/account, and mutation policy are answered or explicitly waived.

### 5. Enforce Draft-First and tool governance

Internal reads, screenshots, local tests, local file edits, and local commits may run directly. External actions require DRAFT first:

- sending messages, emails, posts, comments;
- opening or editing public/shared issues;
- pushing branches;
- deploying;
- modifying shared docs/calendars;
- writing production data unless explicitly authorized for the audit.

Every mutation allowed during the audit must be tagged with `[AUDIT:{slug}]`, logged in `PROGRESS.jsonl`, and included in the cleanup checklist.

Completion: mutation policy is traceable and reversible.

### 6. Run personas and evidence loop

Use two personas:

1. **Driver usuário:** first-person user performing real tasks on the artifact surface.
2. **Observer especialista:** evidence-based critic using explicit dimensions and severity P0–P3.

For every finding:

- capture evidence: screenshot, log line, query output, trace, file path, or command output;
- inspect the captured artifact before logging reaction;
- if verdict is uncertain, ask the executive at finding-time;
- classify only after the answer: `real bug`, `data artifact`, or `by design`.

Completion: every finding has evidence, severity, verdict, and owner-confirmation status.

### 7. Add skill-quality gate when auditing skills

If the artifact is a Hermes/Exocórtex skill, run the `excrtx-quality-skilljudge` rubric:

| Dimension | Required output |
|---|---|
| D1 Structural Compliance | deterministic pre-check: frontmatter, sections, size, artifacts |
| D2 Instructional Clarity | whether an agent can execute without guessing |
| D3 Behavioral Alignment | fit with Exocórtex contract, Draft-First, vector, Acervo |
| D4 Harness Fitness | production readiness, references, verification, pitfalls |
| D5 Token Economy | context efficiency and duplication |

Compute verdict: all best = `PASS`; 1–2 middle = `IMPROVE`; any worst or 3+ middle = `REWRITE`.

Completion: skill audit includes D1–D5 labels, overall verdict, and remediation queue.

### 8. Produce reports

Write four reports under `reports/`:

1. `ISSUES.md` — primary backlog: ID, severity, area, title, repro, evidence, verdict, owner-confirmed, regression status, suggested fix, effort.
2. `{persona}-experience.md` — first-person user narrative with evidence references.
3. `expert-critique.md` — dimension scores, improvements, regressions, risks.
4. `FINAL_REPORT.md` — executive summary, GO/NO-GO verdict, blockers, top-5 improvements.

Apply the Exocórtex quality gate to executive prose. Do not apply prose anti-slop to technical docs, raw logs, schemas, or SKILL.md content.

Completion: reports exist and cite evidence.

### 9. Preserve in Acervo only after triage

Audit outputs are operational artifacts, not memory by default. Preserve raw evidence in the audit directory. Promote only durable learnings through `excrtx-memory-manager`:

- decisions → `decisions/`;
- reusable procedure → skill/workflow;
- significant event → episode;
- pending commitment → intention;
- third-party/untrusted source → draft until approved.

Completion: promotion candidates are listed; no semantic write occurs without the Acervo write protocol.

## Required Files

| File | Role |
|---|---|
| `PROMPT.md` | instantiated audit contract |
| `TASKS.md` | scope units, observer dimensions, synthesis board |
| `PROGRESS.jsonl` | append-only event log, one JSON object per meaningful state |
| `QUESTIONS.jsonl` | blocking/non-blocking questions and answers |
| `artifacts/` | screenshots, traces, logs, extracted files |
| `reports/ISSUES.md` | primary issue backlog |
| `reports/FINAL_REPORT.md` | executive verdict and blockers |

## Common Pitfalls

1. **Inventing a layout.** Use the required file set; comparability matters.
2. **Auditing the API instead of the surface.** The driver persona must use what real consumers use.
3. **Batching blocking questions.** Ask at finding-time; late domain corrections waste the session.
4. **Classifying verdicts solo.** Uncertain verdicts require executive confirmation.
5. **Mutating without cleanup.** Every write needs tag, log, and cleanup checklist.
6. **Publishing findings externally.** Issues, PRs, docs, messages, and deploys require Draft-First unless explicitly authorized.
7. **Promoting raw audit material as memory.** Raw evidence stays operational; only distilled durable knowledge enters Acervo.
8. **Skipping skill judge on skill audits.** Skill artifacts require D1–D5 quality labels and remediation queue.

## Verification Checklist

- [ ] Vector classified before execution.
- [ ] Audit home selected and prior audits checked.
- [ ] Template instantiated with no unresolved placeholders.
- [ ] Required coordination files and folders created.
- [ ] Kickoff Q&A covers target, credentials/account, and mutation authorization.
- [ ] Draft-First applied to every external action.
- [ ] Mutations are tagged, logged, and included in cleanup checklist.
- [ ] Driver persona exercised the real artifact surface.
- [ ] Observer used explicit dimensions and P0–P3 severity.
- [ ] Every finding cites inspected evidence.
- [ ] Uncertain verdicts were confirmed with the executive at finding-time.
- [ ] Skill audits include D1–D5 skill judge verdicts.
- [ ] `ISSUES.md` is the primary deliverable.
- [ ] `FINAL_REPORT.md` states GO/NO-GO and blockers.
- [ ] Acervo promotion candidates are listed separately from raw evidence.
