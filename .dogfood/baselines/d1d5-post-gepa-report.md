# Skill Judge — Baseline Report

**Skills evaluated:** 43

## Summary

| Skill | D1 | D2 | D3 | D4 | D5 | Verdict |
|---|---|---|---|---|---|---|
| `excrtx-memory-wikiadapt` | COMPLIANT | VAGUE | ALIGNED | NEEDS_HARDENING | EFFICIENT | 🔴 REWRITE |
| `excrtx-produce-artifacts` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | BLOATED | 🔴 REWRITE |
| `excrtx-quality-taste` | COMPLIANT | VAGUE | ALIGNED | PROTOTYPE | ACCEPTABLE | 🔴 REWRITE |
| `excrtx-assess-selftest` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-behavior-accuracy` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-brandkit-generator` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-harness-codexint` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-harness-imbroke` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-harness-surfaces` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-onboard-interview` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-onboard-welcome` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-quality-designsys` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-assess-repofit` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-briefing` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-canvas` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-vetor` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-govern-draftfirst` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-govern-tools` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-core` | COMPLIANT | — | — | — | — | ✅ PASS |
| `excrtx-harness-delivery` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-hermesops` | COMPLIANT | — | — | — | — | ✅ PASS |
| `excrtx-harness-kanban` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-promptlog` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-tooldev` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-hermes-extensions` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-browser` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-docbrain` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-gdrive` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-nlmops` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-nlmroute` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-oauth` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-intake` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-manager` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-mvinstall` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-mvsetup` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-newmicro` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-opsmemory` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-produce-oficios` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-produce-slides` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-antislop` | COMPLIANT | — | — | — | — | ✅ PASS |
| `excrtx-quality-gate` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-gepa` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-skilljudge` | COMPLIANT | — | — | — | — | ✅ PASS |

**Totals:** PASS=31, IMPROVE=9, REWRITE=3

## Per-Skill Details

### excrtx-memory-wikiadapt — REWRITE

**Priority fixes:**
- [D2_CLARITY] Add a table mapping wiki categories to Acervo natures (e.g., concept → knowledge).
- [D2_CLARITY] Provide explicit tool invocations (e.g., `hermes tool excrtx-memory-manager --filter WRITE --path ...`).
- [D2_CLARITY] Define path construction from wiki metadata (slug, nature).
- [D2_CLARITY] Include an example walkthrough from wiki write to Acervo entry.
- [D4_FITNESS] Add concrete verification commands (e.g., 'Confirm Acervo entry at micro/{slug}/knowledge/ with pointer in wiki').
- [D4_FITNESS] Expand pitfalls based on actual integration tests (e.g., 'Category mismatch when wiki is used with raw vs. concept').
- [D4_FITNESS] Include a references/mapping.md with the full translation table.

**D2_clarity (VAGUE):** Procedure steps are abstract and lack concrete implementation details. For instance, 'Classify content — which microverso does this belong to?' provides no classification method or mapping between wik
**D4_fitness (NEEDS_HARDENING):** Verification items are testable in principle but lack concrete, checkable steps (e.g., 'Wiki write triggers Domain Filter' requires checking logs, not directly observable). Pitfalls are generic ('Over

### excrtx-produce-artifacts — REWRITE

**Priority fixes:**
- [D2_CLARITY] Add a 'Don't use for' section specifying non-final artifacts (e.g., transient notes, exploratory drafts) to further disambiguate.
- [D4_FITNESS] Ensure referenced files are present and up-to-date in the skill package.
- [D5_ECONOMY] Merge the two 'GitHub vs Drive' sections into a single, concise section covering all cases. Eliminate repeated content.

**D2_clarity (CLEAR):** The skill has a detailed numbered procedure with concrete commands, paths, and tool names. Edge cases are addressed in pitfalls, troubleshooting, and destination policies. Tables and code blocks are u
**D4_fitness (PRODUCTION_READY):** The verification checklist is testable with specific, verifiable conditions. Pitfalls reflect real production learnings (e.g., OAuth vs Drive API, syncing Acervo). Skill references supporting document
**D5_economy (BLOATED):** The body contains significant duplication: the 'GitHub vs Drive' section appears twice with overlapping content. This redundancy wastes tokens. Other sections are reasonably dense.

### excrtx-quality-taste — REWRITE

**Priority fixes:**
- [D2_CLARITY] Rewrite Procedure as numbered steps with exact commands or tool calls, e.g., '1. Call gpt-taste with the user prompt. 2. Apply anti-slop checks...'
- [D2_CLARITY] Specify the Hermes mechanism for activating sub-skills (e.g., skill invocation, tool use)
- [D2_CLARITY] Add counter-triggers: 'Don't use for: non-visual tasks, text-only outputs'
- [D2_CLARITY] Document edge cases: what happens when excrtx-quality-designsys is unavailable?
- [D4_FITNESS] Replace verification with concrete, testable checks (e.g., 'Generated HTML has no empty grid cells')
- [D4_FITNESS] Add real production pitfalls (e.g., 'brutalist may produce unreadably narrow columns on mobile')
- [D4_FITNESS] Declare related_skills in frontmatter metadata.hermes.related_skills
- [D4_FITNESS] Include a references/ directory with the actual sub-skill content or at least stub links
- [D5_ECONOMY] Remove the redundant Procedure paragraph or replace it with a simple 'See routing and anti-slop rules above' without rephrasing

**D2_clarity (VAGUE):** The skill lacks a concrete, step-by-step procedure. The 'Procedure' section merely points back to 'the rules defined in this skill's body sections above' without numbered actions, expected inputs, or 
**D4_fitness (PROTOTYPE):** The verification checklist contains only non-specific items like 'Skill trigger conditions were correctly matched' and 'Output follows the skill's defined format', which are untestable. Pitfalls are g
**D5_economy (ACCEPTABLE):** The body is concise and well-structured, with no significant redundancy or debris. The only inefficiency is the 'Procedure' section, which duplicates the implicit structure without adding value—it cou

### excrtx-assess-selftest — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add a concrete sub-procedure for behavior checks, e.g., 'Simulate an email draft request and inspect the response for DRAFT label' or 'Check the prompt log for classification of Socratic inputs'.

**D2_clarity (AMBIGUOUS):** The procedure for verifying behavior (step 5) lacks a concrete, executable method. It states expected behaviors (e.g., 'prepare um email... deve gerar DRAFT') but does not specify how the agent should

### excrtx-behavior-accuracy — IMPROVE

**Priority fixes:**
- [D4_FITNESS] Move the calibration test (create file, verify with test -f) into the Verification section as a concrete acceptance test.
- [D4_FITNESS] Replace generic pitfalls with specific, previously observed failures (e.g., 'Issue #47 was reported closed but remained open due to network timeout').
- [D5_ECONOMY] Merge the Verification checklist into the Procedure section to eliminate redundancy.

**D4_fitness (NEEDS_HARDENING):** The body's Verification section contains a vague usability checklist ('Skill loaded in action reporting situations') rather than testable, automatable criteria. Although the metadata calibration provi
**D5_economy (ACCEPTABLE):** The skill is generally well-structured with tables and concise prose. There is minor redundancy between the 'What to Verify' table in the Procedure and the separate 'Verification Checklist' section, w

### excrtx-brandkit-generator — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Consider adding an example of the draft presentation output to guide the agent in presenting results to the executive.
- [D5_ECONOMY] Merge Limitations into Pitfalls to avoid duplication.
- [D5_ECONOMY] Combine Acceptance Criteria with Verification checklist, or remove the less specific one.

**D5_economy (ACCEPTABLE):** The skill is well-organized, but there is some overlap: the Limitations section duplicates content found in Pitfalls (e.g., gradients, SVGs, large images), and the Acceptance Criteria table partially 

### excrtx-harness-codexint — IMPROVE


### excrtx-harness-imbroke — IMPROVE

**Priority fixes:**
- [D2_CLARITY] For even greater clarity, consider adding numbered steps in the Procedure section (e.g., 1. Run the appropriate command, 2. Copy output verbatim, 3. Remind about /new).
- [D3_ALIGNMENT] Optionally, add a brief note that this skill operates under the Exocortex deterministic principles to reinforce alignment.
- [D4_FITNESS] Add `related_skills: ['excrtx-govern-tools', 'excrtx-integrate-oauth']` to the frontmatter.
- [D4_FITNESS] Consider using a relative path or a configurable workdir variable to improve portability.
- [D5_ECONOMY] Replace pseudo-code with a brief summary and reference `references/algorithms.md` for full details.
- [D5_ECONOMY] Define the workdir as a variable or use relative paths to avoid repetition.

**D4_fitness (PRODUCTION_READY):** The Verification section contains specific, testable criteria (rating computation, guard tripwire, emoji faixas, verbatim output, /new reminder, sentinel creation). Pitfalls reflect real production co
**D5_economy (ACCEPTABLE):** The skill is concise overall, with dense tables and code blocks. However, the Implementation section duplicates content that likely exists in `references/algorithms.md`, and the command blocks repeat 

### excrtx-harness-surfaces — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add a conditional step for first-time build: 'If dashboard assets are missing, run `hermes dashboard --tui` once to trigger build; then kill, and use `--skip-build` for persistent launch.'
- [D2_CLARITY] Provide a concrete systemd service example or reference the dedicated reference file (`references/dashboard-remote-access-hardening.md`) explicitly for the durable service pattern.
- [D5_ECONOMY] Consider consolidating 'When to Use' as a concise summary and let the body and procedure carry the detail.
- [D5_ECONOMY] Remove duplicate recommendations from Procedure if they are already fully explained above.

**D2_clarity (AMBIGUOUS):** The procedure is largely clear and actionable with concrete commands, but Steps 3 and 5 leave room for assumptions. Step 3 assumes the dashboard is already built and does not account for the first-tim
**D5_economy (ACCEPTABLE):** The skill is reasonably compact and avoids major bloat. However, there is minor repetition between the 'When to Use' section and the preceding body text, and the Procedure steps partially rephrase the

### excrtx-onboard-interview — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add a detailed question prompt for each block (in PT-BR) as a reference table or script
- [D2_CLARITY] Provide a SOUL.md template with placeholders and indicate exactly how to fill it
- [D2_CLARITY] Include explicit CLI or tool invocation examples (e.g., `hermes skill invoke excrtx-memory-newmicro --domain '...'`)
- [D2_CLARITY] Use code blocks for file formats and Markdown tables for interview script

**D2_clarity (AMBIGUOUS):** While the trigger section is clear with positive and counter-triggers, and the procedure has numbered steps, the interview questions are not provided explicitly—only block titles. The agent would need

### excrtx-onboard-welcome — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add a 'Don't use for:' section listing when to avoid this skill (e.g., returning user, onboarding already complete)
- [D2_CLARITY] Add a fallback: if WELCOME.md missing, present a short generic welcome message and log the error

**D2_clarity (AMBIGUOUS):** The procedure is mostly concrete and actionable, with clear steps and outputs. However, the Trigger section lacks explicit counter-triggers ('Don't use for:') to prevent misapplication, and there is n

### excrtx-quality-designsys — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add a 'Don't use for:' subsection (e.g., 'When the request involves brand voice, messaging, or non-visual identity only – defer to brandkit or excrtx-quality-taste').
- [D3_ALIGNMENT] Optionally, include a note in WRITE operation reminding the agent to confirm scope with the executive, reinforcing executive authority (though already implicit in 'determine scope').
- [D4_FITNESS] Add a pre-flight check: verify CLI is available, and if not, install via `npm install -g @google/design.md` (or npx auto-install).
- [D4_FITNESS] Include a bootstrap subsection: if global/DESIGN.md is missing, create an empty skeleton using the canonical format with mandatory fields.
- [D4_FITNESS] Document remediation steps for common lint failures (e.g., 'if wcag-contrast error, adjust lightness by X units').
- [D4_FITNESS] Declare obvious prerequisites: node/npm environment, excrtx-memory-manager enabled.

**D2_clarity (CLEAR):** The skill provides concrete, numbered procedures with explicit commands and path references. Each operation (RESOLVE, WRITE, LINT, EXPORT) has clear steps, input/output expectations, and verification 
**D4_fitness (NEEDS_HARDENING):** The skill has strong verification checklists and realistic pitfalls (YAML quoting, section order). However, it assumes the presence of the `@google/design.md` CLI tool without a setup step, and the gl

### excrtx-assess-repofit — PASS


### excrtx-behavior-briefing — PASS


### excrtx-behavior-canvas — PASS


### excrtx-behavior-vetor — PASS


### excrtx-govern-draftfirst — PASS


### excrtx-govern-tools — PASS

**Priority fixes:**
- [D2_CLARITY] Add a note or environment variable reference for the session log location (e.g., $EXOCORTEX_SESSION_LOG) to eliminate any guesswork.
- [D4_FITNESS] Ensure the reference file `references/config-mutation-isolated-validation.md` exists and is maintained as part of the skill bundle.

**D2_clarity (CLEAR):** The procedure provides concrete, actionable steps (R1-R6) with explicit commands, logging formats, and classification tables. The trigger section clearly delineates when to activate and when not to. E

### excrtx-harness-core — PASS


### excrtx-harness-delivery — PASS

**Priority fixes:**
- [D2_CLARITY] Add conditional steps: 'If connector not found, suggest installing relevant MCP server' or 'If artifact publishing fails, check artifact path and gateway status before retrying.'
- [D4_FITNESS] Add more concrete verification steps where applicable, such as shell commands to check token absence or stdout parsing, to increase testability.

**D2_clarity (CLEAR):** The procedure is concrete, with identifiable steps and commands (e.g., 'hermes mcp list | grep connector', 'publish_artifact(path, kind, ...)'). The 'When to Use' section provides positive triggers an
**D4_fitness (PRODUCTION_READY):** The verification checklist contains specific, testable criteria (e.g., 'OAuth connectors use connection_id, never raw tokens' is auditable). Pitfalls reflect realistic production risks (token leakage,

### excrtx-harness-hermesops — PASS


### excrtx-harness-kanban — PASS


### excrtx-harness-promptlog — PASS

**Priority fixes:**
- [D4_FITNESS] Move `related_skills` to the top level of the frontmatter for better discoverability

**D4_fitness (PRODUCTION_READY):** The verification checklist is specific and testable (sequential ID, ISO 8601 timestamp, phase, artifacts, status, summary). Pitfalls reflect real operational concerns (ID collision, path variability, 

### excrtx-harness-tooldev — PASS


### excrtx-hermes-extensions — PASS

**Priority fixes:**
- [D2_CLARITY] Replace line numbers with descriptive search patterns (e.g., 'find the if/elif chain that dispatches commands for new sessions').
- [D4_FITNESS] Ensure the referenced files exist in the references/ directory and are accessible to the agent.

**D2_clarity (CLEAR):** The procedure provides concrete, actionable steps with exact file paths, code snippets, and clear descriptions. The trigger section includes counter-triggers, edge cases (e.g., frozenset immutability,
**D4_fitness (PRODUCTION_READY):** The verification checklist contains specific, testable criteria (e.g., command appears in /help, Gateway not treating as normal message). Pitfalls reflect genuine production traps (dual dispatch chain

### excrtx-integrate-browser — PASS

**Priority fixes:**
- [D4_FITNESS] Add a specific smoke‑test URL and expected result (e.g., title text) to the verification checklist to make acceptance fully deterministic.
- [D5_ECONOMY] If LLM agent usage grows beyond a few lines, consider extracting it to a separate reference document to keep the primary skill focused on CLI operation.

**D4_fitness (PRODUCTION_READY):** The verification checklist contains testable, specific criteria covering script existence, state return, interaction, cleanup, and path contract. Pitfalls reference real production issues (e.g., shim 

### excrtx-integrate-docbrain — PASS

**Priority fixes:**
- [D2_CLARITY] Add an explicit 'Don't use for:' list to the 'When to Use' section for completeness.

**D2_clarity (CLEAR):** The skill provides concrete, actionable commands for health check, parsing, installation, and troubleshooting. The 'When to Use' section specifies positive triggers and includes a warning about not us

### excrtx-integrate-gdrive — PASS


### excrtx-integrate-nlmops — PASS

**Priority fixes:**
- [D2_CLARITY] Optionally add a pre-flight check for nlm installation with instructions to report missing tool.

**D2_clarity (CLEAR):** The procedure is fully structured with numbered steps, concrete commands, trigger/counter-trigger rules, and edge-case handling for auth failure, MCP unavailability, documentary gaps, and source provi

### excrtx-integrate-nlmroute — PASS

**Priority fixes:**
- [D2_CLARITY] Consider adding a generic fallback for unexpected nlm login --check failures (e.g., 'If other errors occur, check network connectivity or consult nlm documentation').

**D2_clarity (CLEAR):** The procedure is concrete and sequential, with explicit commands (nlm --version, nlm login --check), input/output expectations, and decision tables. Trigger and counter-trigger conditions are clearly 

### excrtx-integrate-oauth — PASS


### excrtx-memory-intake — PASS


### excrtx-memory-manager — PASS

**Priority fixes:**
- [D2_CLARITY] Add a note about script availability or a fallback procedure.

**D2_clarity (CLEAR):** The skill provides concrete, actionable steps with explicit commands, paths, and tool names. The procedure sections are numbered, logically sequenced, and include clear inputs, expected outputs, and e

### excrtx-memory-mvinstall — PASS

**Priority fixes:**
- [D4_FITNESS] Either add a verification step for Node packages in the procedure or remove the Node mention from the verification checklist to align with actual implementation.

**D4_fitness (PRODUCTION_READY):** The verification checklist contains testable criteria, and the calibration acceptance criteria in the frontmatter provide additional, detailed verification steps. Pitfalls and Gotchas reflect real ope

### excrtx-memory-mvsetup — PASS


### excrtx-memory-newmicro — PASS


### excrtx-memory-opsmemory — PASS


### excrtx-produce-oficios — PASS

**Priority fixes:**
- [D2_CLARITY] Add explicit command or tool hint for appending the log entry, e.g., 'use file_append tool to append the entry to micro/gabinete/log.md'.
- [D4_FITNESS] Ensure that the references/ directory is bundled with the skill and that template-spec.md exists in the deployment.

**D2_clarity (CLEAR):** The skill provides concrete, actionable steps with explicit commands, file paths, and tool usage. Trigger conditions and counter-triggers are clear. Steps are sequentially ordered and dependencies are
**D4_fitness (PRODUCTION_READY):** The skill has a robust verification checklist with testable criteria (script exit code, file existence, field validation, quality gate checks). Pitfalls are grounded in real production issues (encodin

### excrtx-produce-slides — PASS


### excrtx-quality-antislop — PASS


### excrtx-quality-gate — PASS


### excrtx-quality-gepa — PASS


### excrtx-quality-skilljudge — PASS

