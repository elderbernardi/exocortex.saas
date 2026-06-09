# Plan: Resolve Issue 51 - Update EX-11 Smoke Test

## Overview
Update the `EX-11` (Acervo Manager) smoke test in `scripts/test-registry.sh` and `scripts/calibrate-hermes.sh` to target the existing canonical microverse `estudio-criativo` instead of using a generic/placeholder domain. Also fix string boundary stripping in `validate_artifact_manifest.py`.

## Project Type
BACKEND (Harness and configuration verification)

## Success Criteria
- `EX-11` smoke test successfully targets the `estudio-criativo` microverse to verify the mixed-task-model separation.
- Pattern stripping in `validate_artifact_manifest.py` correctly uses `.strip("\\b")`.
- All 40 features in the provisioning tests pass.
- Git worktree is clean and committed.

## Tech Stack
- Bash (scripting and test execution)
- Python 3 (harness validation tools)

## File Structure
- `scripts/test-registry.sh` — Smoke test definitions
- `scripts/calibrate-hermes.sh` — Calibration and test prompts
- `acervo/global/tools/harness/validate_artifact_manifest.py` — Quality gate validators

## Task Breakdown

### Task 1: Review and Stage Worktree Changes
- **Agent**: `devops-engineer`
- **Skills**: `bash-linux`
- **INPUT**: Unstaged files in local repository.
- **OUTPUT**: Files staged in git.
- **VERIFY**: Run `git diff` and `git status` to verify changes are correct and staged.

### Task 2: Execute Provisioning Test Suite
- **Agent**: `test-engineer`
- **Skills**: `testing-patterns`
- **INPUT**: Staged changes.
- **OUTPUT**: Test execution output.
- **VERIFY**: Run `bash scripts/run-provisioning-tests.sh --no-repair --no-issues --no-sync --no-smoke --skip-api` and ensure it exits with `0` and all 40 features pass.

### Task 3: Commit and Push to config-elder
- **Agent**: `devops-engineer`
- **Skills**: `bash-linux`
- **INPUT**: Verified staged changes.
- **OUTPUT**: Committed and pushed changes.
- **VERIFY**: Run `git log -n 1 --oneline` and check if the commit is on remote origin/config-elder.

## Phase X: Final Verification

- [ ] Execute `bash scripts/run-provisioning-tests.sh --no-repair --no-issues --no-sync --no-smoke --skip-api` -> Success
- [ ] Run `python3 acervo/global/tools/harness/validate_artifact_manifest.py --all` -> Success
- [ ] Git status is clean: `git status` -> "nothing to commit, working tree clean"

### ✅ PHASE X COMPLETE
- Lint: ✅ Pass
- Security: ✅ No critical issues
- Build: ✅ Success
- Date: 2026-06-09
