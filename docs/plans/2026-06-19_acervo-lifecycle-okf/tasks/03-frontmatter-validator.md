# Task 03: Build Frontmatter Validator Script

**Status:** pending
**Depends on:** Task 01 (schema spec)
**Produces:** `scripts/validate_frontmatter.py`

## Context

The frontmatter schema (ADR-013, Task 01 spec) needs a deterministic validator. This script is used by:
- Migration script (Task 08) to verify retroactive migration.
- Skills (Tasks 04–06) to verify their output.
- CI/CI-like checks to prevent non-conformant files from entering the Acervo.

This is a D1-equivalent check — fully deterministic, no LLM needed.

## Deliverable

Create `scripts/validate_frontmatter.py` that:

### Functionality

1. **Accepts arguments:**
   - `--file <path>` — validate a single file
   - `--dir <path>` — validate all `.md` files in a directory (recursive)
   - `--report` — output a summary report instead of per-file errors

2. **Checks (per file):**
   - File has YAML frontmatter (starts with `---` and ends with `---`)
   - OKF canonical fields present: `type`, `title`, `description`, `tags`, `timestamp`
   - `type` value is from allowed vocabulary: `decision`, `memory`, `reflection`, `context`, `knowledge`, `artifact`
   - Acervo extension fields present: `class`, `created_at`
   - `class` value is `perene` or `volátil`
   - `timestamp` is valid ISO 8601 date (YYYY-MM-DD)
   - `created_at` is valid ISO 8601 datetime
   - If `deprecated: true` → `deprecated_at` and `deprecated_reason` present
   - If `quarantined_at` present → `quarantine_reason` and `quarantine_expires_at` present
   - If `promoted_at` present → `class` is `perene` (promoted implies perene)

3. **Exits:**
   - `0` if all files valid
   - `1` if any file invalid (with error message per file)
   - `2` if file/directory not found

4. **Report format (with `--report`):**
   ```
   Frontmatter Validation Report
   =============================
   Scanned: 127 files
   Valid: 119
   Invalid: 8
   Errors:
     micro/exocortex-dev/knowledge/old-file.md: missing 'type' field
     micro/exocortex-dev/knowledge/another.md: 'class' must be 'perene' or 'volátil', got 'permanent'
   ```

### Dependencies

- Python 3 (stdlib only — `yaml` via PyYAML if available, otherwise simple parser)
- No external packages beyond what's in the Hermes environment

### Test Files

Create `tests/fixtures/frontmatter/` with:
- `valid-volatile.md` — correct volatile knowledge
- `valid-perene.md` — correct perene decision
- `valid-deprecated.md` — correct deprecated memory
- `valid-promoted.md` — correct promoted artifact
- `invalid-missing-type.md` — missing `type`
- `invalid-bad-class.md` — `class: permanent` (not in vocabulary)
- `invalid-deprecated-no-reason.md` — `deprecated: true` but no `deprecated_reason`

## Verification

```bash
# Single valid file
python3 scripts/validate_frontmatter.py --file tests/fixtures/frontmatter/valid-volatile.md
echo "Exit: $?"  # should be 0

# Single invalid file
python3 scripts/validate_frontmatter.py --file tests/fixtures/frontmatter/invalid-missing-type.md
echo "Exit: $?"  # should be 1

# Directory with report
python3 scripts/validate_frontmatter.py --dir tests/fixtures/frontmatter/ --report
echo "Exit: $?"  # should be 1 (has invalid files)
```

- [ ] Script exists at `scripts/validate_frontmatter.py`
- [ ] Exit code 0 on valid file
- [ ] Exit code 1 on invalid file with clear error message
- [ ] `--dir` mode scans recursively
- [ ] `--report` mode outputs summary
- [ ] 7 test fixture files created
- [ ] No external dependencies beyond stdlib + PyYAML
