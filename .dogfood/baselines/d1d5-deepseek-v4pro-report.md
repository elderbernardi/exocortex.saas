# Skill Judge — Baseline Report

**Skills evaluated:** 40

## Summary

| Skill | D1 | D2 | D3 | D4 | D5 | Verdict |
|---|---|---|---|---|---|---|
| `excrtx-hermes-extensions` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | 🔴 REWRITE |
| `excrtx-memory-newmicro` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | 🔴 REWRITE |
| `excrtx-assess-repofit` | COMPLIANT | CLEAR | PARTIAL | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-assess-selftest` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-behavior-vetor` | COMPLIANT | CLEAR | PARTIAL | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-govern-draftfirst` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-govern-tools` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-harness-hermesops` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-harness-imbroke` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-harness-kanban` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-harness-promptlog` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-harness-tooldev` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-integrate-browser` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-integrate-gdrive` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-integrate-nlmops` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-integrate-oauth` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-memory-manager` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-memory-mvsetup` | COMPLIANT | AMBIGUOUS | ALIGNED | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-memory-opsmemory` | COMPLIANT | CLEAR | PARTIAL | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-onboard-interview` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-produce-oficios` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-produce-slides` | COMPLIANT | CLEAR | PARTIAL | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-quality-designsys` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-quality-skilljudge` | COMPLIANT | CLEAR | PARTIAL | PRODUCTION_READY | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-behavior-accuracy` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-briefing` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-canvas` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-codexint` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-core` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-surfaces` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-docbrain` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-nlmroute` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-intake` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-mvinstall` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-wikiadapt` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-onboard-welcome` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-produce-artifacts` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-antislop` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-gate` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-taste` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |

**Totals:** PASS=16, IMPROVE=22, REWRITE=2

## Per-Skill Details

### excrtx-hermes-extensions — REWRITE

**Priority fixes:**
- [D2_CLARITY] Add a explicit 'Don't use for' list to When to Use
- [D2_CLARITY] Consolidate the procedure into a single numbered sequence with all steps
- [D2_CLARITY] Make the Procedure section refer back with specific step numbers
- [D4_FITNESS] Replace verification checkboxes with specific, verifiable conditions related to slash command functionality
- [D4_FITNESS] Include step-by-step test scenarios (e.g., 'Run /new_command in CLI and verify response')
- [D5_ECONOMY] Remove duplicate mention of ACTIVE_SESSION_BYPASS_COMMANDS from Anatomy step 4.C and reference step 2
- [D5_ECONOMY] Consider moving dispatch trap explanation into pitfalls only, leaving a concise reference in the Anatomy section

**D2_clarity (AMBIGUOUS):** The skill provides concrete code examples and addresses edge cases, but the Procedure section is a non-actionable placeholder, and the 'When to Use' lacks counter-triggers, making the overall instruct
**D4_fitness (NEEDS_HARDENING):** Verification checkboxes are generic and non-specific, lacking testable conditions; while pitfalls reflect production learnings, the verification section fails to provide measurable acceptance criteria
**D5_economy (ACCEPTABLE):** The skill is concise overall but contains slight redundancy: Active Session Bypass is mentioned in both step 2 and step 4.C, and the dispatch trap is explained in step 4 and Pitfall 5, adding minor du

### excrtx-memory-newmicro — REWRITE

**Priority fixes:**
- [D2_CLARITY] Add a 'Don't use for' section listing examples (e.g., 'Don't use for one-off notes that don't require persistent domain context').
- [D2_CLARITY] Include a step to verify the template directory exists before copying, or define fallback behavior.
- [D2_CLARITY] Clarify the relationship between context/ and the 7 Nature files, explicitly stating whether they are separate or nested.
- [D4_FITNESS] Verify the actual template structure and update the body to consistently reference 7 or 11 Natures; correct the index description to 7 if that is the real count.
- [D4_FITNESS] Expand pitfalls with concrete failure scenarios and recovery steps (e.g., 'If the Microverso appears empty after creation, re-run step 3 to ensure SCHEMA.md was saved before placeholder replacement').
- [D4_FITNESS] Add a verification item: 'No remaining {MICROVERSO_NAME} or {slug} placeholders in any file (use grep).'
- [D5_ECONOMY] If placeholder replacement in step 5 covers the same files as step 4, merge the instructions; otherwise, clarify that step 4 only handles context/ and step 5 handles other files.
- [D5_ECONOMY] Move cleanup instructions to a 'Testing' or 'Pitfall' subsection, shortening the primary procedure.
- [D5_ECONOMY] Consider trimming the frontmatter calibration to a concise reference rather than a full re-statement.

**D2_clarity (AMBIGUOUS):** The procedure is concrete with numbered steps and code blocks, but lacks counter-triggers ('Don't use for:') to prevent over-application, and does not address edge cases like a missing template direct
**D4_fitness (NEEDS_HARDENING):** The verification checklist is testable, but a critical inconsistency exists: the procedure references '7 Nature files' in multiple steps, yet step 5 initializes 'index.md' with a catalog of 11 Natures
**D5_economy (ACCEPTABLE):** The skill is concise overall, but contains minor redundancy (step 5 repeats placeholder replacement instruction unnecessarily, and the Cleanup section could be folded into pitfalls). The frontmatter i

### excrtx-assess-repofit — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add a 'Don't use for:' subsection with scenarios where the skill is inappropriate
- [D2_CLARITY] Include example commands for common validation steps (e.g., `pytest`, `mypy`)
- [D2_CLARITY] Expand edge case guidance for runtime failures
- [D3_ALIGNMENT] Add a procedural step: 'Antes de gravar o relatório, apresente um DRAFT para aprovação do executivo'
- [D3_ALIGNMENT] Optionally note that this skill typically operates in Execution mode
- [D4_FITNESS] Add specific verification items: e.g., 'Report contains all 6 required sections (verdict, strengths, gaps, risks, recommendations, final recommendation)'
- [D4_FITNESS] Verify coverage of all four mismatch classes (claim vs implementation, etc.)
- [D4_FITNESS] Declare related_skills if dependent on other skills

**D2_clarity (CLEAR):** The skill provides a well-structured, numbered procedure with concrete steps (inspect specific files, validate runtime, classify mismatches). Each step has a clear central question and expected output
**D3_alignment (PARTIAL):** The skill body is in PT-BR and respects the executive's language. It does not duplicate governance logic from other skills. However, it instructs writing a report file without explicitly requiring a D
**D4_fitness (NEEDS_HARDENING):** The skill includes a references directory with supporting material and has realistic pitfalls from production experience. However, the verification section is generic and lacks testable criteria speci

### excrtx-assess-selftest — IMPROVE

**Priority fixes:**
- [D4_FITNESS] Add specific verification criteria (e.g., 'Report includes correct phase', 'Score matches checklist results')
- [D4_FITNESS] Declare related skills in frontmatter metadata

**D4_fitness (NEEDS_HARDENING):** The verification section is generic and not tailored to self-test outcomes (e.g., verifying report format, phase detection). Pitfalls are realistic but the skill references other skills (excrtx-behavi

### excrtx-behavior-vetor — IMPROVE

**Priority fixes:**
- [D3_ALIGNMENT] Add Manutenção signals to the table (e.g., 'revise pendências', 'audite logs', 'faça uma limpeza')
- [D3_ALIGNMENT] Add a row for Manutenção in the routing table with appropriate behavior (e.g., audit, report status, cleanup)
- [D3_ALIGNMENT] Update Ambiguous clarification to include maintain option
- [D3_ALIGNMENT] Expand verification checklist to cover Manutenção inputs
- [D4_FITNESS] Synchronize body and compiled_rules by either removing Maintenance from rules or adding full Maintenance support to the body
- [D4_FITNESS] Add concrete, testable examples to verification (e.g., input 'preciso revisar os logs de erro' → maintenance response pattern)

**D3_alignment (PARTIAL):** The skill partially aligns with the Exocortex contract. It correctly classifies Execution and Evolution vectors, respects Draft-First, and allows executive overrides. However, it entirely omits the Ma
**D4_fitness (NEEDS_HARDENING):** The verification section has checkboxes but they are generic and lack concrete test inputs. The pitfalls are realistic. However, there is a significant synchronization gap: the compiled_rules in the f

### excrtx-govern-draftfirst — IMPROVE

**Priority fixes:**
- [D4_FITNESS] Ensure the reference file exists in the skill's references directory, or inline the relevant content if it is small.

**D4_fitness (NEEDS_HARDENING):** Verification is thorough and testable, pitfalls reflect real production issues, and related skills are declared. However, the skill references an external file 'references/mixed-working-tree-selective

### excrtx-govern-tools — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Clarify the trigger scope to match the classification table (e.g., 'Activate on any tool call that produces side effects or accesses external resources, as defined in the classification table')
- [D2_CLARITY] Specify the exact logging target (e.g., 'Log to the active session log file with the following format')
- [D2_CLARITY] Either list the skills in the exocortex-alpha bundle or instruct the agent to verify membership via a specific command
- [D4_FITNESS] Add concrete verification steps (e.g., 'Execute a tool call classified as destructive and verify that the [TOOL] log entry appears in the session log with correct fields')
- [D4_FITNESS] If possible, base pitfalls on actual incidents or dogfooding experiences

**D2_clarity (AMBIGUOUS):** The 'When to Use' section contains contradictory instructions: it says 'Activate on EVERY tool call' but then lists 'Reading files' as something not to use this skill for, even though the classificati
**D4_fitness (NEEDS_HARDENING):** The verification section consists of high-level checklist items (e.g., 'Least privilege principle followed', 'Draft-First applied for all external communication') that are not easily testable in an au

### excrtx-harness-hermesops — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Merge the two Verification sections into one authoritative checklist.
- [D2_CLARITY] Use code fences for all command-line snippets, wrapper paths, and configuration keys.
- [D2_CLARITY] Add a comparison table for Track A and Track B summarizing purpose, method, and safety flags.
- [D3_ALIGNMENT] Optionally add a brief reminder that after Track A execution, the agent should present a draft to the executive for review before finalizing changes, if the broader governance skills do not already enforce this.
- [D4_FITNESS] Consolidate verification into one definitive, checklist-based section.
- [D4_FITNESS] Expand the verification checklist to cover every pitfall (e.g., untracked file existence, full-auto flag usage).
- [D5_ECONOMY] Remove the redundant Verification section and keep only the checkbox-based one.
- [D5_ECONOMY] Shorten the Procedure section to reference the detailed tracks without restating them.
- [D5_ECONOMY] Introduce a table summarizing Track A vs Track B: purpose, command/wrapper, safety flags, verification requirements.

**D2_clarity (CLEAR):** The skill provides concrete, actionable steps for each track with explicit commands and paths. The routing heuristic includes positive triggers and counter-triggers. Edge cases are addressed in the Pi
**D4_fitness (PRODUCTION_READY):** The verification checklist contains specific, testable criteria (e.g., git_status_porcelain, hermes auth list check). Pitfalls reflect real operational challenges such as untracked files and read-only
**D5_economy (ACCEPTABLE):** The skill is concise overall but contains redundancy: two Verification sections repeat similar content, and the Procedure essentially restates the track descriptions. No tables are used where structur

### excrtx-harness-imbroke — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Enhance the 'When to Use' with concrete examples: Use for: ..., Don't use for: specific scenarios like non-free model selection
- [D2_CLARITY] Add a brief note: If the script returns an error, report it verbatim and suggest manual debugging
- [D4_FITNESS] Replace generic verification items with concrete checks like: [ ] After activation, model rating is computed correctly for known intelligence indices; [ ] Guard tripwire triggers on provider change
- [D4_FITNESS] Add a brief production anecdote to each pitfall, e.g., 'In staging, LLM formatting once injected hallucinated model names'
- [D5_ECONOMY] Consider moving the algorithm details to references/algorithms.md and summarise key points in the body
- [D5_ECONOMY] Condense deterministic warnings by referencing the earlier directive

**D2_clarity (CLEAR):** The skill provides explicit, concrete commands for activating, deactivating, checking status, and viewing rankings. Each user intent maps to a deterministic script execution. The agent is instructed t
**D4_fitness (NEEDS_HARDENING):** The Verification checklist is generic and non-specific—checking trigger conditions, format rules, and governance violations—without any testable criteria for this particular skill (e.g., rating conver
**D5_economy (ACCEPTABLE):** The skill provides dense, well-structured information with tables for structured data (CLI flags, rating examples) and code blocks for commands. Some redundancy exists: the implementation section dupl

### excrtx-harness-kanban — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add counter-triggers: e.g., 'Do not use for: quick reminders that fit in session notes only, decisions already made but not yet implemented.'
- [D2_CLARITY] In Step 1, specify concrete checks: 'If plans/STATUS.md exists, update it; if not, create under docs/.' Link to conventions if needed.
- [D2_CLARITY] In Step 3A, provide a fallback: 'If TODO tool is unavailable, create a simple markdown note in the project root.'
- [D3_ALIGNMENT] Consider adding a brief note in the Procedure: 'Upon activation, the agent should classify the input as Execução or Manutenção to ensure proper logging, following the Exocortex contract.' This reinforces alignment without duplicating global rules.
- [D4_FITNESS] If future skills emerge for ADR management or project status, add 'related_skills: [excrtx-harness-adr, ...]' to frontmatter to make dependency chains explicit.
- [D5_ECONOMY] Optionally move the template into an appendix or reference file to trim body, but current form is already efficient.

**D2_clarity (AMBIGUOUS):** The skill provides a clear, step-by-step procedure with concrete actions and verification. However, two elements introduce ambiguity: (1) the trigger section lacks counter-triggers ('Don't use for:'),
**D5_economy (EFFICIENT):** The skill is tightly organized with no formatting debris, repeated sections, or excessive prose. The description is search-optimized. The 'Template de retomada' section slightly overlaps with the stru

### excrtx-harness-promptlog — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add explicit instruction: 'Append the formatted entry to the end of MEMORY.md' in step 1.
- [D2_CLARITY] Provide a concrete code snippet, e.g., echo '[PDD-...' >> $HERMES_HOME/MEMORY.md, and mention file creation if it does not exist.
- [D4_FITNESS] Add `related_skills: [excrtx-behavior-briefing, excrtx-assess-selftest]` to the frontmatter.

**D2_clarity (AMBIGUOUS):** The procedure says 'Registrar em MEMORY.md uma entrada' but does not explicitly state that the entry should be appended to the file, nor does it provide a concrete command (e.g., echo with >>). The pi
**D4_fitness (PRODUCTION_READY):** The verification section provides a concrete, testable checklist of 6 items covering ID, timestamp, phase, artifacts, status, and summary. Pitfalls are specific and reflect real-world concerns (ID col

### excrtx-harness-tooldev — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Provide a minimal implementation example for the handler method, or reference a template file.
- [D2_CLARITY] Specify the class and method name where the handler should be added, e.g., 'in the HermesAgent class, add a method _handle_tool_command'.
- [D4_FITNESS] Consider adding a 'related_skills' field in frontmatter to explicitly reference excrtx-hermes-extensions and excrtx-integrate-oauth for better discoverability and dependency management.

**D2_clarity (AMBIGUOUS):** The procedure is generally concrete, but Step 3 (handler implementation) only provides a high-level description without code. The agent would need to figure out the exact implementation details, inclu

### excrtx-integrate-browser — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add numbered steps to Procedure summarizing the workflow: 1. Open URL, 2. Observe state, 3. Interact, 4. Verify, 5. Close
- [D2_CLARITY] Elaborate trigger section with concrete use-case examples and clear 'Don't use for' criteria
- [D4_FITNESS] Replace verification with concrete checks: verify that browser-use.sh is executable, that 'state' returns valid JSON, that a test URL can be opened
- [D4_FITNESS] Add real-world pitfalls like 'chromium may require --no-sandbox on some systems'
- [D4_FITNESS] Include the path contract reference inline or move verification details from references into skill body
- [D5_ECONOMY] Consolidate When to Use into frontmatter triggers, remove the placeholder section
- [D5_ECONOMY] Either detail the Procedure with numbered steps or remove it, as the workflow is already in Quick Start

**D2_clarity (CLEAR):** The skill provides concrete commands with exact paths, a command reference table, and usage patterns. The agent can autonomously execute browser tasks from this text. The trigger section and Procedure
**D4_fitness (NEEDS_HARDENING):** The Verification section contains generic, non-testable criteria. Pitfalls are equally generic rather than specific production learnings. The skill references a references file but does not include it
**D5_economy (ACCEPTABLE):** The skill is relatively concise with tables and code blocks. However, the When to Use and Procedure sections are token-inefficient: they contain almost no actionable content and could be eliminated or

### excrtx-integrate-gdrive — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Clarify folder resolution: specify searching by name first, then prompt executive if not found.
- [D2_CLARITY] Add error handling note for upload failures (retry, fallback).
- [D3_ALIGNMENT] Consider adding a brief note about input classification (exec/evol/manut) when the skill is triggered, for completeness.
- [D4_FITNESS] Ensure that a references/ directory is created if supporting scripts or docs are needed beyond the inline code.

**D2_clarity (AMBIGUOUS):** Procedure steps are largely concrete with commands, code examples, and clear sequencing. However, Step 3.3 'Resolve target folder' lacks specificity on how to resolve (e.g., search by name or prompt u

### excrtx-integrate-nlmops — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add counter-triggers (e.g., 'Don't use for: simple facts already known, creative writing, or tasks not requiring synthesis')
- [D2_CLARITY] Specify concrete tool/command for source search (e.g., web search via Hermes tool or explicit MCP fallback) in Step 2 Case B

**D2_clarity (AMBIGUOUS):** The procedure steps are mostly concrete, but 'When to Use' lacks explicit counter-triggers ('Don't use for') and Step 2 Case B ('Find reliable sources') leaves the sourcing method vague, requiring the

### excrtx-integrate-oauth — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Expand 'When to Use' with concrete trigger examples from frontmatter.
- [D4_FITNESS] Ensure these reference files are included and accurately document the examples.

**D2_clarity (CLEAR):** The procedure steps are concrete, numbered, and include edge cases like interactive enablement. The triggers in frontmatter are detailed, and the body includes a 'Don't use for' counter-trigger, thoug
**D4_fitness (NEEDS_HARDENING):** Verification checklist is testable and specific. Pitfalls reflect real integration gotchas. However, the skill references two markdown files (composio-connect.md and notebooklm-cli-mcp.md) that are no

### excrtx-memory-manager — IMPROVE

**Priority fixes:**
- [D5_ECONOMY] Remove the duplicate 'When to Use' section at the end, or merge it with the top section to eliminate redundancy.

**D5_economy (ACCEPTABLE):** The skill is well-structured with tables and code blocks, but it contains a minor redundancy: the 'When This Skill Activates' section at the top is nearly identical to the 'When to Use' section at the

### excrtx-memory-mvsetup — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add a 'Don't use for:' or 'Contraindications' subsection in the Trigger section, e.g., 'Não use para microversos que são experimentais ou temporários, isso é coberto por excrtx-memory-newmicro.'
- [D2_CLARITY] Include a brief note or link to the frontmatter v2 specification if it is not globally known.

**D2_clarity (AMBIGUOUS):** The procedure steps are specific and actionable with code examples and clear sequencing. However, the Trigger section lacks explicit counter-triggers (e.g., 'Don't use for:') to prevent the agent from

### excrtx-memory-opsmemory — IMPROVE

**Priority fixes:**
- [D3_ALIGNMENT] Add a step before 'Deploy' requiring the agent to prepare a draft plan and seek executive approval before making any system changes.

**D3_alignment (PARTIAL):** The skill describes deployment and configuration actions that modify the system. The Exocortex contract mandates Draft-First for external actions, but the skill does not instruct the agent to present 

### excrtx-onboard-interview — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add a 'Don't use for:' subsection to the Trigger, e.g., 'Don't use for: casual chat, debugging another skill, when SOUL.md already fully populated without 'Pendente' sections.'
- [D2_CLARITY] Expand Procedure to cover edge cases: what to do if the executive answers only some blocks, how to generate defaults for skipped blocks, fallback language if the interview is terminated early.
- [D4_FITNESS] Refine verification: e.g., 'SOUL.md contains identifiable values, communication preferences, and boundaries from the interview (not default template)'.
- [D4_FITNESS] Add production pitfalls: 'Long silence during interview may cause session timeout; echo prompts every 2 minutes.'
- [D4_FITNESS] Add `related_skills: [excrtx-onboard-welcome, excrtx-memory-newmicro]` to frontmatter.

**D2_clarity (AMBIGUOUS):** The agent can execute the interview sequence but would need to make assumptions about edge cases (e.g., user skipping blocks, contradictory answers) and the lack of explicit counter-triggers. The trig
**D4_fitness (NEEDS_HARDENING):** The verification checklist items are testable but somewhat vague (e.g., 'Personalized SOUL.md with executive's responses' lacks concrete criteria). Pitfalls are generic and do not reflect production-s

### excrtx-produce-oficios — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Remove the duplicate 'When to Use' section or consolidate into one
- [D2_CLARITY] Add specific counter-triggers, e.g., 'Don't use for: generating memos, reports, or when a dedicated skill exists'
- [D2_CLARITY] Unify the workflow into a single numbered procedure for clarity
- [D4_FITNESS] Add a verification checklist with items like 'Document generated successfully', 'All mandatory fields filled correctly', 'Draft reviewed by user', 'Quality gate check passed'
- [D4_FITNESS] Declare related_skills in frontmatter, e.g., 'related_skills: [excrtx-quality-gate]'
- [D5_ECONOMY] Remove the duplicate 'When to Use' section
- [D5_ECONOMY] Consider using a table for required fields and validation rules to improve conciseness

**D2_clarity (CLEAR):** The skill provides concrete, actionable steps with exact commands, input/output expectations, and edge case handling. The workflow is logically sequenced, and the agent can autonomously execute the pr
**D4_fitness (NEEDS_HARDENING):** The skill has solid, real-world pitfalls but lacks a testable verification section with checkboxes or specific success criteria. The Verification section is process-oriented rather than a checklist. A
**D5_economy (ACCEPTABLE):** The skill is mostly well-organized but contains a redundant duplicate 'When to Use' section, which wastes tokens. Some prose explanations could be tightened, but overall density is acceptable. No line

### excrtx-produce-slides — IMPROVE

**Priority fixes:**
- [D3_ALIGNMENT] Even for explicit upload requests, present a brief DRAFT confirmation of the upload action, or document an exception in the behavioral contract to align with 'always DRAFT first'.

**D3_alignment (PARTIAL):** The skill generally respects the Exocortex behavioral contract: it uses PT-BR, references Draft-First for public deployment, relies on governance skills, and preserves executive authority. However, th

### excrtx-quality-designsys — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Specify exact logging command or call for excrtx-memory-manager (e.g., 'append to log.md with timestamp and scope').
- [D4_FITNESS] Add checklist-based verification steps for WRITE (e.g., YAML valid, canonical order, extends field), LINT (output zero errors), EXPORT (file generated, format correct).
- [D4_FITNESS] Include a references/design-md-spec.md or a permalink to the current Google DESIGN.md specification to prevent drift.

**D2_clarity (CLEAR):** The skill provides concrete and actionable steps (commands, paths, tool names) for each operation. It includes a clear trigger section with positive conditions and covers edge cases (e.g., override do
**D4_fitness (NEEDS_HARDENING):** The RESOLVE operation has a strong verification checklist, but WRITE, LINT, and EXPORT lack explicit verification criteria. Pitfalls are realistic but not exhaustive (e.g., missing import of external 

### excrtx-quality-skilljudge — IMPROVE

**Priority fixes:**
- [D3_ALIGNMENT] Add Portuguese equivalents to the trigger list, e.g., 'julgue minhas skills', 'avalie qualidade das skills', 'auditoria de skills', 'qualidade de skills'.

**D3_alignment (PARTIAL):** The skill generally respects the Exocortex behavioral contract: no external actions without draft, no autonomy violations, references anti-slop skill. However, the 'When to Use' triggers are exclusive

### excrtx-behavior-accuracy — PASS


### excrtx-behavior-briefing — PASS


### excrtx-behavior-canvas — PASS


### excrtx-harness-codexint — PASS


### excrtx-harness-core — PASS


### excrtx-harness-surfaces — PASS


### excrtx-integrate-docbrain — PASS

**Priority fixes:**
- [D2_CLARITY] Add a numbered list under 'Procedure' that explicitly sequences the key actions (e.g., 1. Resolve workspace, 2. Health check, 3. Parse/query as needed).

**D2_clarity (CLEAR):** The skill provides concrete, actionable instructions for each operation (health check, parse, query, installation) with exact commands, expected outputs, and edge case handling (workspace resolution, 

### excrtx-integrate-nlmroute — PASS

**Priority fixes:**
- [D2_CLARITY] Optionally expand Step 3 with a brief example or heuristic for identifying an appropriate existing notebook (e.g., search by name or tag), but current reference to excrtx-integrate-nlmops is sufficient.


### excrtx-memory-intake — PASS

**Priority fixes:**
- [D2_CLARITY] Add specific counter-trigger examples, e.g., 'Don't use for: raw database storage, direct semantic page creation without triage, or non-file intake tasks.'
- [D5_ECONOMY] Consider replacing the placeholder with a concise, one-line summary of the high-level flow to improve immediate scannability.

**D2_clarity (CLEAR):** The skill provides a complete, self-contained procedure. The 'Standard Flow' section contains concrete, numbered steps (Reception, Initial Manifest, Extraction, Cognitive Triage, Promotion) with clear
**D5_economy (EFFICIENT):** The skill communicates maximum information in minimal tokens. The description is dense and search-optimized. The body uses concise structural definitions (directory trees, JSON schemas) and numbered f

### excrtx-memory-mvinstall — PASS

**Priority fixes:**
- [D4_FITNESS] Add a related_skills list in the frontmatter metadata, including excrtx-memory-newmicro, excrtx-memory-mvsetup, and excrtx-memory-wikiadapt.

**D4_fitness (PRODUCTION_READY):** The verification section includes testable checklist items. Pitfalls are concrete and reflect production concerns (hook safety, dependency fallbacks, rollbacks). No compiled_rules to synchronize. Exte

### excrtx-memory-wikiadapt — PASS


### excrtx-onboard-welcome — PASS

**Priority fixes:**
- [D2_CLARITY] Add an explicit 'Don't use for:' subsection under Trigger
- [D2_CLARITY] Include an edge-case step for missing WELCOME.md (e.g., error, default welcome)
- [D2_CLARITY] Ensure the reference file exists and is maintained, or embed critical bootstrap content as a fallback
- [D4_FITNESS] Ensure the reference file is present and maintained with the skill
- [D4_FITNESS] Optionally embed the essential bootstrap tutor content as a fallback in the skill body

**D2_clarity (CLEAR):** The skill provides a detailed, numbered procedure with concrete steps, conditional logic, and gateway-specific adaptations. The agent can execute autonomously based on this text alone, though some edg
**D4_fitness (PRODUCTION_READY):** The Verification checklist is specific and testable. Pitfalls reflect real operational learnings. The skill references a supporting file, which must exist for full bootstrap functionality. No compiled

### excrtx-produce-artifacts — PASS

**Priority fixes:**
- [D2_CLARITY] Add a brief '## When NOT to Use' section to prevent misapplication, listing scenarios where other skills should be invoked instead.

**D2_clarity (CLEAR):** The skill provides a numbered, step-by-step procedure with concrete commands, directories, and tool names. Inputs and outputs are implied but clear from context. Edge cases are addressed via troublesh

### excrtx-quality-antislop — PASS

**Priority fixes:**
- [D2_CLARITY] Consider adding a small taxonomy or examples of common filler phrases to reduce ambiguity for less capable models.


### excrtx-quality-gate — PASS


### excrtx-quality-taste — PASS

