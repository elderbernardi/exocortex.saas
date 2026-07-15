# Prompt template — Exocórtex Interactive Audit

> Instantiate this template into `{audit-home}/{YYYY-MM-DD}_{slug}/PROMPT.md`. Fill every placeholder. Delete optional sections that do not apply.

---

# {{AUDIT_TITLE}} — {{ARTIFACT}} ({{ENVIRONMENT}}, interactive)

## 1. Objective

Run a real-conditions evaluation of `{{ARTIFACT}}` with two personas:

1. `{{USER_PERSONA_NAME}}` — user driver, first-person, performing real tasks.
2. `{{EXPERT_ROLE}}` — evidence-based observer, scoring explicit dimensions.

Goal: produce `reports/ISSUES.md` and a GO/NO-GO verdict for `{{GOAL}}`.

Audit jobs, in priority order:

1. **Regression** *(successor audits only)* — re-check every open finding from `{{PRIOR_AUDIT_DIR}}/reports/FINAL_REPORT.md`.
2. **New surface** *(successor audits only)* — evaluate shipped changes: `{{NEW_FEATURES_OR_CHANGES}}`.
3. **Fresh discovery** — walk scoped units under realistic data and conditions.

## 2. Owner-in-the-loop protocol

The executive/owner is present. This is a moderated session.

### Blocking kickoff before touching the artifact

Ask and log in `QUESTIONS.jsonl`:

1. Target: `{{URL / dataset / branch / deploy / file / API / skill path}}`.
2. Account/credentials: read from canonical secret location; never write secrets into repo files.
3. Mutation authorization: what may be read, written, sent, published, deployed, or cleaned up.

### Checkpoints

At the end of each scope unit, pause and post:

- what was exercised;
- findings so far;
- open blocking questions;
- proposed next unit.

Proceed only after `continue`, answer, redirect, or explicit checkpoint waiver.

### Finding-time confirmation

Do not finalize uncertain verdicts alone. Ask the owner before classifying:

```text
real bug | data artifact | by design
```

Use `blocking: true` if the answer affects severity, scope, or next action.

## 3. Personas

### {{USER_PERSONA_NAME}} — driver

Profile: `{{WHO THEY ARE, ROLE, GOALS, TEMPERAMENT, REAL WORK SESSION}}`.

Rules:

- perform real tasks, not abstract inspection;
- narrate in first person;
- record friction, delight, confusion, and workaround;
- continue after breakage when safe.

### {{EXPERT_ROLE}} — observer

Profile: senior specialist critiquing against evidence.

Dimensions:

```text
{{DIMENSIONS}}
```

Default UX/product dimensions:

- D1 Navigation / information architecture;
- D2 Visual consistency;
- D3 Content and data quality;
- D4 Feedback and system status;
- D5 Error handling and resilience;
- D6 Accessibility;
- D7 Fit for the user's real job.

For data audits, use correctness, completeness, freshness, consistency, lineage.
For API/CLI audits, use contract conformance, error surfaces, docs accuracy, DX.
For skill audits, use D1–D5 from `excrtx-quality-skilljudge`.

## 4. Method

### Tooling

Reuse project tooling first. Verify the tooling against the target before starting.

Ask for approval before installing dependencies or adding new external services.

### Coordination files

Maintain:

```text
TASKS.md
PROGRESS.jsonl
QUESTIONS.jsonl
artifacts/
reports/
```

`PROGRESS.jsonl` shape:

```json
{"unit":"U1","step":"...","action":"...","evidence":"artifacts/...","reaction":"...","note":"...","ts":"..."}
```

`QUESTIONS.jsonl` shape:

```json
{"id":"Q1","from":"driver|observer|owner","unit":"U1","question":"...","answer":"...","blocking":true,"ts":"..."}
```

## 5. Scope units

List scope units in execution order.

```text
U1 — {{UNIT_NAME}}
Action: {{WHAT TO EXERCISE}}
Finding threshold: {{WHAT COUNTS AS A FINDING}}
Regression hooks: {{PRIOR_FINDINGS_TO_RECHECK_OR_NONE}}

U2 — {{...}}
```

Known pre-existing conditions:

```text
{{KNOWN_BUGS_DATA_GAPS_SEEDED_STATES}}
```

## 6. Mutation policy

Mutation authorization:

```text
{{MUTATION_POLICY}}
```

Rules:

- tag all allowed writes with `[AUDIT:{{SLUG}}]`;
- log every created/changed row, file, issue, or record in `PROGRESS.jsonl`;
- never mutate surfaces owned by another system/team;
- external actions require DRAFT unless explicitly authorized;
- end with cleanup checklist in `reports/ISSUES.md`.

## 7. Outputs

### `reports/ISSUES.md`

Primary backlog. One issue per entry:

```text
ID
Severity: P0/P1/P2/P3
Area
Title
Repro steps
Evidence
Verdict: real bug | data artifact | by design
Owner-confirmed: yes/no
Regression status: new | carried-over | reopened | fixed | partially-fixed
Suggested fix
Effort: S/M/L
Cleanup impact
```

### `reports/{{user-persona}}-experience.md`

First-person session narrative with evidence references and honest user verdict.

### `reports/expert-critique.md`

Dimension scores, improved areas, regressions, risk notes.

### `reports/FINAL_REPORT.md`

Executive summary, GO/NO-GO verdict, remaining blockers, top-5 improvements beyond bug fixing, and promotion candidates for Acervo.
