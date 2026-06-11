# Skill Judge — Baseline Report

**Skills evaluated:** 40

## Summary

| Skill | D1 | D2 | D3 | D4 | D5 | Verdict |
|---|---|---|---|---|---|---|
| `excrtx-harness-tooldev` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | 🔴 REWRITE |
| `excrtx-integrate-gdrive` | COMPLIANT | AMBIGUOUS | PARTIAL | NEEDS_HARDENING | EFFICIENT | 🔴 REWRITE |
| `excrtx-integrate-nlmroute` | COMPLIANT | AMBIGUOUS | PARTIAL | NEEDS_HARDENING | ACCEPTABLE | 🔴 REWRITE |
| `excrtx-memory-opsmemory` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | 🔴 REWRITE |
| `excrtx-harness-hermesops` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-harness-promptlog` | COMPLIANT | AMBIGUOUS | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-harness-surfaces` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-integrate-nlmops` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | EFFICIENT | ⚠️ IMPROVE |
| `excrtx-memory-manager` | COMPLIANT | CLEAR | ALIGNED | NEEDS_HARDENING | ACCEPTABLE | ⚠️ IMPROVE |
| `excrtx-assess-repofit` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-assess-selftest` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-accuracy` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-briefing` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-canvas` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-behavior-vetor` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-govern-draftfirst` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-govern-tools` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-codexint` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-core` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-imbroke` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-harness-kanban` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-hermes-extensions` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-browser` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-docbrain` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-integrate-oauth` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-intake` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-mvinstall` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-mvsetup` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-newmicro` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-wikiadapt` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-onboard-interview` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-onboard-welcome` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-produce-artifacts` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-produce-oficios` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-produce-slides` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-antislop` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-designsys` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-gate` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-skilljudge` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-quality-taste` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |

**Totals:** PASS=31, IMPROVE=5, REWRITE=4

## Per-Skill Details

### excrtx-harness-tooldev — REWRITE

**Priority fixes:**
- [D2_CLARITY] Replace procedure section with numbered, sequential steps
- [D2_CLARITY] Add complete code examples with all necessary imports
- [D2_CLARITY] Provide exact file paths and directory structure
- [D2_CLARITY] Include step-by-step testing procedures
- [D2_CLARITY] Add error handling and debugging guidance
- [D4_FITNESS] Add specific verification steps like 'Tool appears in registry', 'Direct call via /tool works'
- [D4_FITNESS] Include code compilation and import verification steps
- [D4_FITNESS] Add troubleshooting section for common development issues
- [D4_FITNESS] Verify referenced files exist or create them
- [D5_ECONOMY] Consolidate scattered procedural information into the procedure section
- [D5_ECONOMY] Remove redundant architectural explanations
- [D5_ECONOMY] Use more tables for structured information like command registry entries

**D2_clarity (AMBIGUOUS):** The skill provides concrete code examples and clear architectural overview, but several critical steps lack specificity. The procedure section is incomplete ('Follow the steps and rules defined in thi
**D4_fitness (NEEDS_HARDENING):** While the skill has a verification section, the checklist items are too generic and not testable ('Skill trigger conditions were correctly matched'). The pitfalls section contains some real production
**D5_economy (ACCEPTABLE):** The skill is reasonably well-organized with good use of code blocks and structured sections. However, there's some redundancy between the architecture overview and implementation details, and the proc

### excrtx-integrate-gdrive — REWRITE

**Priority fixes:**
- [D2_CLARITY] Add specific Google Drive API endpoints and parameters
- [D2_CLARITY] Include example commands with expected responses
- [D2_CLARITY] Provide concrete error handling steps
- [D2_CLARITY] Embed key hardening techniques directly in procedure
- [D3_ALIGNMENT] Add explicit Draft-First protocol for uploads and external operations
- [D3_ALIGNMENT] Reference appropriate vector classification for Drive operations
- [D3_ALIGNMENT] Include anti-slop quality gates for search result validation
- [D4_FITNESS] Create the referenced drive-search-hardening.md file
- [D4_FITNESS] Add specific Drive API pitfalls from real usage
- [D4_FITNESS] Include common Drive API error scenarios and recovery procedures

**D2_clarity (AMBIGUOUS):** The skill provides a good high-level structure but lacks concrete implementation details. The procedure mentions using OAuth tokens and API calls but doesn't specify exact commands, tool names, or exp
**D3_alignment (PARTIAL):** The skill shows awareness of Exocortex behavioral patterns by referencing other skills (excrtx-integrate-oauth, excrtx-produce-artifacts) and mentioning microverso logging. However, it lacks explicit 
**D4_fitness (NEEDS_HARDENING):** The verification section provides testable criteria with checkboxes, which is good for production readiness. The pitfalls section exists but is generic and doesn't reflect real production learnings sp

### excrtx-integrate-nlmroute — REWRITE

**Priority fixes:**
- [D2_CLARITY] Add specific scoring rubric or checklist for source evaluation
- [D2_CLARITY] Specify exact MCP command for token refresh
- [D2_CLARITY] Detail the conditions and steps for CLI-to-MCP fallback
- [D2_CLARITY] Include specific tool commands for deep research and web search integration
- [D3_ALIGNMENT] Add Draft-First protocol for NotebookLM operations that create or modify external resources
- [D3_ALIGNMENT] Include vector classification guidance for different types of knowledge requests
- [D3_ALIGNMENT] Reference quality gates for source evaluation and synthesis output
- [D3_ALIGNMENT] Explicitly map knowledge integration to Acervo Cognitivo layers
- [D4_FITNESS] Add specific verification steps for NotebookLM auth, notebook creation, and source ingestion
- [D4_FITNESS] Expand pitfalls with real production issues like auth expiration patterns, source ingestion failures
- [D4_FITNESS] Include testable criteria for successful knowledge synthesis delivery
- [D4_FITNESS] Add comprehensive error handling patterns for common failure modes
- [D5_ECONOMY] Consolidate 'Standard Flow' and 'Procedure' into a single comprehensive section
- [D5_ECONOMY] Replace generic verification with skill-specific checkpoints
- [D5_ECONOMY] Streamline troubleshooting to focus on unique NotebookLM issues

**D2_clarity (AMBIGUOUS):** The skill provides a clear overall flow and specific commands like `nlm --version` and `nlm login --check`, but several steps require the agent to make assumptions. The 'Top 10 Sources' criteria are s
**D3_alignment (PARTIAL):** The skill generally respects Exocortex behavioral patterns with PT-BR content being appropriate for this system context. However, it lacks explicit acknowledgment of key governance protocols. There's 
**D4_fitness (NEEDS_HARDENING):** The skill has a verification section but it's generic and not testable for this specific skill's functionality. The pitfalls section is minimal and doesn't reflect real production learnings about Note
**D5_economy (ACCEPTABLE):** The skill is reasonably well-organized with clear sections and uses structured formatting effectively. The mandatory rules section provides dense, actionable information. However, there's some redunda

### excrtx-memory-opsmemory — REWRITE

**Priority fixes:**
- [D2_CLARITY] Add numbered procedure steps with specific commands and expected outputs
- [D2_CLARITY] Provide concrete evaluation checklists for provider assessment
- [D2_CLARITY] Include exact file paths and configuration templates for each mentioned provider
- [D2_CLARITY] Add specific diagnostic commands for troubleshooting common issues
- [D4_FITNESS] Replace generic verification with memory-provider-specific checkboxes
- [D4_FITNESS] Add testable criteria like 'Provider status shows available in hermes memory status'
- [D4_FITNESS] Include verification steps for successful provider integration and data flow
- [D4_FITNESS] Add specific checks for precedence hierarchy maintenance
- [D5_ECONOMY] Consolidate overlapping conceptual explanations
- [D5_ECONOMY] Convert provider evaluation criteria into a structured comparison table
- [D5_ECONOMY] Streamline the relationship explanations to reduce redundancy

**D2_clarity (AMBIGUOUS):** The skill provides good conceptual guidance but lacks concrete, actionable steps. The 'Procedure' section simply refers back to 'body sections above' without numbered steps. Key procedures like 'Adopt
**D4_fitness (NEEDS_HARDENING):** The skill has a verification section but it's generic and not testable for this specific domain. The pitfalls section contains real operational learnings (like the Hindsight API key requirement even i
**D5_economy (ACCEPTABLE):** The skill is well-organized with clear sections and uses structured information effectively. The precedence hierarchy is presented as a clean numbered list, and the Hindsight configuration uses approp

### excrtx-harness-hermesops — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Provide exact command syntax for the wrapper: python ~/.hermes/scripts/codex_learning/run_codex_with_learning.py [options]
- [D2_CLARITY] Create a template or example for delegation contract format
- [D2_CLARITY] Add decision tree or specific keywords for track routing
- [D2_CLARITY] Include jq commands or specific JSON validation steps
- [D4_FITNESS] Add success criteria beyond evidence existence (e.g., 'files created match expected list')
- [D4_FITNESS] Include the referenced supporting artifacts in references/ directory
- [D4_FITNESS] Define specific exit codes or output patterns that indicate successful execution

**D2_clarity (AMBIGUOUS):** The skill provides concrete commands and paths (hermes auth list, hermes config set, specific file paths like ~/.hermes/scripts/codex_learning/), which is good for agent execution. However, several cr
**D4_fitness (NEEDS_HARDENING):** The skill has a verification section with specific criteria (git_status_porcelain, git_changed_files, etc.) which is testable. The pitfalls section reflects real production learnings about untracked f

### excrtx-harness-promptlog — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Add specific file paths or tool commands for accessing MEMORY.md
- [D2_CLARITY] Define the P1-P6 phase system or reference where it's defined
- [D2_CLARITY] Specify ID generation logic (sequential, timestamp-based, etc.)
- [D2_CLARITY] Include example of complete execution flow
- [D4_FITNESS] Create specific verification steps like 'Log entry appears in MEMORY.md with correct PDD-ID format'
- [D4_FITNESS] Add real pitfalls like 'ID collision with existing entries' or 'MEMORY.md write permission issues'
- [D4_FITNESS] Reference documentation for P1-P6 phase system
- [D4_FITNESS] Add validation criteria for timestamp format and artifact listing

**D2_clarity (AMBIGUOUS):** The procedure steps are concrete but lack critical details for autonomous execution. Step 1 lists what to register but doesn't specify HOW to access or modify MEMORY.md. The format example in step 2 i
**D4_fitness (NEEDS_HARDENING):** The verification section exists but is too generic and not testable for this specific skill. The checklist items ('Skill trigger conditions were correctly matched', 'Output follows format') could appl

### excrtx-harness-surfaces — IMPROVE

**Priority fixes:**
- [D2_CLARITY] Consider adding a quick reference table summarizing the key commands and their use cases
- [D4_FITNESS] Add ## Verification section with specific checkboxes for testing dashboard deployment, gateway configuration, and security posture
- [D4_FITNESS] Add ## Pitfalls section documenting common issues like Windows embedded chat limitations, OAuth token leakage, and dashboard exposure risks
- [D5_ECONOMY] Complete the truncated final section
- [D5_ECONOMY] Consider using tables for command comparisons and decision matrices
- [D5_ECONOMY] Consolidate some of the longer prose sections into structured lists

**D4_fitness (NEEDS_HARDENING):** While the skill contains extensive operational guidance and references supporting materials, it lacks a proper Verification section with testable checkboxes. The Pitfalls section is missing entirely, 
**D5_economy (ACCEPTABLE):** The skill is comprehensive and well-organized with good use of structured sections and clear headings. However, it's quite lengthy and could benefit from more concise presentation in some areas. Some 

### excrtx-integrate-nlmops — IMPROVE

**Priority fixes:**
- [D4_FITNESS] Add specific pitfalls like 'Source ingestion timeout with large documents', 'MCP connection drops during long queries', 'Authentication token expiry mid-workflow'
- [D4_FITNESS] Include recovery procedures for common NotebookLM API failures

**D4_fitness (NEEDS_HARDENING):** The verification section has testable criteria with specific checkboxes that can be verified (auth check, notebook selection, sources cited). However, the pitfalls section is weak - it only contains g

### excrtx-memory-manager — IMPROVE

**Priority fixes:**
- [D4_FITNESS] Add more specific, testable verification steps (e.g., 'Run `ls $ACERVO/micro/{slug}/log.md` to confirm log entry exists')
- [D4_FITNESS] Expand Pitfalls with real scenarios like 'Scope conflicts when multiple microversos have similar content' or 'Performance issues when searching large wiki directories'
- [D4_FITNESS] Specify what documentation should exist in references/ directory (SCHEMA.md, ADR files, etc.)
- [D5_ECONOMY] Consider moving detailed Natures semantics to references/ and keeping only essential mapping in main body
- [D5_ECONOMY] Compress some of the architecture explanation by referencing acervo/README.md more heavily

**D4_fitness (NEEDS_HARDENING):** The skill has verification sections for each operation with specific checkboxes, which is good. However, the verification criteria could be more testable - many are subjective (e.g., 'Domain Filter ex
**D5_economy (ACCEPTABLE):** The skill is well-organized and uses tables effectively for structured information. However, there is some redundancy - the Natures Reference table repeats information that could be found in SCHEMA do

### excrtx-assess-repofit — PASS


### excrtx-assess-selftest — PASS


### excrtx-behavior-accuracy — PASS


### excrtx-behavior-briefing — PASS


### excrtx-behavior-canvas — PASS

**Priority fixes:**
- [D2_CLARITY] Consider adding more examples of actual canvas outputs to further clarify expected formats
- [D4_FITNESS] Consider adding a reference file with canvas.yaml template examples


### excrtx-behavior-vetor — PASS

**Priority fixes:**
- [D2_CLARITY] Consider adding more examples of edge cases in the signal table
- [D2_CLARITY] Could specify exact log format location (which file/system)
- [D4_FITNESS] Could add more verification scenarios for maintenance vector
- [D4_FITNESS] Consider adding performance benchmarks for classification speed


### excrtx-govern-draftfirst — PASS


### excrtx-govern-tools — PASS


### excrtx-harness-codexint — PASS

**Priority fixes:**
- [D2_CLARITY] Consider adding example prompts for both tracks to further reduce ambiguity
- [D4_FITNESS] Consider adding a troubleshooting section for common configuration issues


### excrtx-harness-core — PASS


### excrtx-harness-imbroke — PASS


### excrtx-harness-kanban — PASS


### excrtx-hermes-extensions — PASS


### excrtx-integrate-browser — PASS


### excrtx-integrate-docbrain — PASS

**Priority fixes:**
- [D2_CLARITY] Consider adding more specific error message examples for common failure modes
- [D4_FITNESS] Consider adding timing expectations for parse operations to help with timeout handling


### excrtx-integrate-oauth — PASS


### excrtx-memory-intake — PASS

**Priority fixes:**
- [D2_CLARITY] Consider adding more specific tool commands for extraction steps
- [D2_CLARITY] Could benefit from example file paths in the verification checklist
- [D4_FITNESS] Consider adding specific file size limits or performance benchmarks to verification
- [D4_FITNESS] Could add monitoring/logging requirements to the checklist


### excrtx-memory-mvinstall — PASS


### excrtx-memory-mvsetup — PASS


### excrtx-memory-newmicro — PASS


### excrtx-memory-wikiadapt — PASS


### excrtx-onboard-interview — PASS


### excrtx-onboard-welcome — PASS


### excrtx-produce-artifacts — PASS


### excrtx-produce-oficios — PASS


### excrtx-produce-slides — PASS


### excrtx-quality-antislop — PASS


### excrtx-quality-designsys — PASS


### excrtx-quality-gate — PASS


### excrtx-quality-skilljudge — PASS


### excrtx-quality-taste — PASS

