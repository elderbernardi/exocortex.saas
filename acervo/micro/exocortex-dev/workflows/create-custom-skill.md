---
title: SOP-001: Creating and Registering a Custom Skill
created: 2026-06-11
updated: 2026-06-11
nature: workflows
type: workflow
tags: [dev, exocortex, skill, workflow]
confidence: high
---

# SOP-001: Creating and Registering a Custom Skill

This Standard Operating Procedure (SOP) describes how to scaffold, implement, compile, validate, and calibrate a new custom skill within the Exocortex framework.

---

## Step 1: Scaffolding the Directory

1. Create a new folder inside the `skills/` directory using the kebab-case naming scheme with the `excrtx-` prefix:
   ```bash
   mkdir -p skills/excrtx-my-new-feature
   ```
2. Create an empty `SKILL.md` inside that directory:
   ```bash
   touch skills/excrtx-my-new-feature/SKILL.md
   ```

---

## Step 2: Implementation of `SKILL.md`

Open the file and add the required YAML frontmatter and standard sections:

```markdown
---
name: excrtx-my-new-feature
description: Short English explanation of what this skill achieves.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, new, tag]
    related_skills: [excrtx-behavior-canvas]
compiled_rules: |
  - Always check X before executing Y.
  - When Z is true, default to W behavior.
---

# Feature Title

> Short introductory quote outlining why this extension matters to the executive.

## When to Use

Detail specific prompts, inputs, or system states that trigger this skill. 
*Note: Write the description in English, but PT-BR examples are expected in this section if they match user-facing interactions.*

## Procedure

Provide the step-by-step logic the agent must follow when executing this skill.

## Pitfalls

List common model drifts, API rate limits, or context issues. Explain how to recover.

## Verification

Include a verification checklist using markdown checkboxes (`- [ ]`) to prove the skill works:
- [ ] Input trigger matches expected output.
- [ ] Error conditions handle gracefully.
```

---

## Step 3: Compiling into `SOUL_SEED.md`

The Hermes runtime uses `SOUL_SEED.md` to define the agent's core instructions. You must compile your newly written `compiled_rules` into this seed:

```bash
python3 scripts/compile_soul.py
```

Verify the output prints:
`Compiled N behavioral rules... Written to SOUL_SEED.md`

---

## Step 4: Verification and Quality Audits

1. Run the deterministic structural check (D1) locally to ensure YAML and section compliance:
   ```bash
   python3 scripts/skill_judge.py --skill excrtx-my-new-feature --d1-only
   ```
2. If OpenRouter or DeepSeek keys are set, run the full semantic judge sweep to grade Clarity, Alignment, Fitness, and Economy:
   ```bash
   python3 scripts/skill_judge.py --skill excrtx-my-new-feature
   ```
3. Resolve any issues flagged as `IMPROVE` or `REWRITE`. **The overall verdict must be `PASS` to merge.**

---

## Step 5: Behavioral Calibration (Prompt Calibration)

If the skill implements a core safety or behavioral protocol:
1. Open `scripts/calibrate-hermes.py` (or the corresponding calibration module).
2. Append a calibration check mapping the feature code (e.g., `EX-41`) to an interactive validation prompt, outlining the expected output and corrective hints.
3. Execute the calibration script:
   ```bash
   bash scripts/calibrate-hermes.sh
   ```
4. Verify that the test cases pass and print green checkmarks.

---

## Step 6: Master Preflight Run

Finally, run the project-wide checklist to ensure no regressions are introduced to the repository:
```bash
python3 .agent/scripts/checklist.py .
```
 Ensure that the checklist returns success.
