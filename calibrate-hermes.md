# Project Plan: Calibrate Hermes (calibrate-hermes.md)

This project plan details the deprecation of `scripts/calibrate-hermes.sh` and its replacement with a modern, modular, and smart Python-based Prompt-Driven Development (PDD) calibration system. It pairs with all 42 features (EX-01 to EX-35, EX-48 to EX-54), reads raw personalization profiles from `acervo/macro/`, and supports an interactive hybrid calibration flow.

> **STATUS: ✅ ALL PHASES COMPLETE** — Runner built, 42/42 cases valid, dry-run mode + report export operational. Ready for live calibration when Hermes is running.

## Project Type
- **BACKEND / CLI TOOL** (Python-based script and test runner integration)

## Success Criteria
1. **Full Feature Coverage**: Support calibrating and testing all 42 features (EX-01 to EX-35, EX-48 to EX-54). ✅
2. **Modular Design (Option B)**: Load calibration prompt configurations dynamically from each skill's `SKILL.md` frontmatter.
3. **Personalization Integration (Option B)**: Inject the raw executive personality data (`acervo/macro/valores.md`, `acervo/macro/estilo.md`, `acervo/macro/current-state.md`) directly into the Hermes calibration session.
4. **Interactive Hybrid Flow (Option B)**: Runs each test, prints results, and prompts the operator (`s/n`) with the option to automatically retry with remediation prompts.
5. **No Regression**: Ensure execution aligns with `setup/step-15-calibration.sh` and does not break existing setup flows.

## Tech Stack
- **Python 3**: For robust YAML parsing, interactive CLI prompting, and Hermes CLI process orchestration.
- **PyYAML / ruamel.yaml**: For parsing and updating `SKILL.md` frontmatter.
- **Bash**: For wrapping the python execution if necessary to fit the legacy `setup.sh` entry points.

## File Structure
- `scripts/calibrate-hermes.py` [NEW] — The primary Python runner containing the execution loop, YAML parser, and operator interface.
- `scripts/calibrate-hermes.sh` [MODIFY] — Deprecated/replaced wrapper script that delegates execution to the Python script.
- `skills/excrtx-*/SKILL.md` [MODIFY] — Add calibration metadata block in frontmatter for skills that are missing it.

---

## Task Breakdown

### Phase 1: Research and Schema Definition
- **Task ID**: `TASK-01`
- **Agent**: `backend-specialist`
- **Skill**: `clean-code`, `api-patterns`
- **Priority**: P0
- **Dependencies**: None
- **Description**: Define the YAML metadata schema for calibration under each skill's frontmatter, and design how it will map to the 40 features.
- **INPUT**: `skills/excrtx-*/SKILL.md` files
- **OUTPUT**: YAML schema draft for frontmatter (e.g. `metadata.hermes.calibration`)
- **VERIFY**: Ensure the schema can capture: `test_prompt`, `acceptance_criteria`, `remediation_tip`.

### Phase 2: Metadata Extraction & Skill Updates
- **Task ID**: `TASK-02`
- **Agent**: `code-archaeologist`
- **Skill**: `batch-operations`, `clean-code`
- **Priority**: P1
- **Dependencies**: `TASK-01`
- **Description**: Add/update the frontmatter of all 40 skills to include the structured calibration metadata.
- **INPUT**: Calibration prompts, test cases, and criteria currently in `scripts/calibrate-hermes.sh` and `scripts/test-registry.sh`
- **OUTPUT**: Updated `skills/excrtx-*/SKILL.md` files
- **VERIFY**: Read and validate that each of the 40 skills has a valid frontmatter with a `calibration` section.

### Phase 3: Personality Profile Ingestion
- **Task ID**: `TASK-03`
- **Agent**: `backend-specialist`
- **Skill**: `clean-code`
- **Priority**: P1
- **Dependencies**: None
- **Description**: Implement parsing logic to read the raw executive personalization profile from `acervo/macro/valores.md` and `acervo/macro/estilo.md`.
- **INPUT**: Files in `acervo/macro/`
- **OUTPUT**: Ingestion functions that extract values and style guidelines as a structured context block.
- **VERIFY**: Run unit tests demonstrating that the profile parser correctly handles missing files and extracts plain text sections.

### Phase 4: Runner Development (scripts/calibrate-hermes.py)
- **Task ID**: `TASK-04`
- **Agent**: `backend-specialist`
- **Skill**: `clean-code`
- **Priority**: P0
- **Dependencies**: `TASK-02`, `TASK-03`
- **Description**: Develop the Python runner that scans the skills directory, runs tests via the `hermes chat` CLI, formats output, and provides interactive prompts with remediation flow.
- **INPUT**: `skills/excrtx-*/SKILL.md`, `acervo/macro/`
- **OUTPUT**: `scripts/calibrate-hermes.py`
- **VERIFY**: Run the Python script for a single skill and confirm it starts a Hermes chat session, injects the personality profile, runs the test prompt, prints results, and prompts the operator.

### Phase 5: Re-routing the Bash Wrapper
- **Task ID**: `TASK-05`
- **Agent**: `devops-engineer`
- **Skill**: `bash-linux`
- **Priority**: P1
- **Dependencies**: `TASK-04`
- **Description**: Re-write `scripts/calibrate-hermes.sh` to behave as a thin wrapper that checks dependencies (python, pip, yaml) and runs `scripts/calibrate-hermes.py`.
- **INPUT**: `scripts/calibrate-hermes.sh`
- **OUTPUT**: Refactored `scripts/calibrate-hermes.sh`
- **VERIFY**: Execute `bash scripts/calibrate-hermes.sh --help` and verify it delegates options correctly.

---

## Phase X: Verification

### Verification Checklist
- [ ] Verify that all 40 features are successfully loaded from `skills/` and mapped to their corresponding EX codes.
- [ ] Verify that the personalization profile from `acervo/macro/` is correctly parsed and injected as session context.
- [ ] Verify that the interactive loop operates correctly (supports user feedback `s/n`, and sends `remediation_tip` upon failure).
- [ ] Verify that running `setup.sh --calibrate` successfully triggers the updated calibration flow.
- [ ] Run the master validation script: `python .agents/scripts/checklist.py .` and ensure no regressions.
