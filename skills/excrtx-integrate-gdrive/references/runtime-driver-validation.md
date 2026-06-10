# Runtime Driver Validation for Google Drive Integration

## When to Apply
Use this procedure when a test, dogfood, or harness for Google Drive integration needs to decide between:
- Driver absent
- Driver present but invalid
- OAuth/API failure after driver is already intact

## Path Precedence Rule
Validate the real Hermes runtime first. Recommended order:

1. `$HERMES_HOME/skills/productivity/google-workspace/scripts/google_api.py`
2. `$HERMES_HOME/hermes-agent/skills/productivity/google-workspace/scripts/google_api.py`
3. Local repo copies, only as development artifacts

Rationale: the user's operational contract runs on the Hermes runtime driver. If the probe passes on a local copy and fails at runtime, the PASS is false.

## Minimum Probe Heuristic
1. Resolve `$HERMES_HOME`; fallback: `~/.hermes`.
2. Build the ordered list of candidates.
3. Record all `driver_candidates` as evidence.
4. Select the first existing candidate.
5. Run syntactic validation (`py_compile` or equivalent) on that file.
6. Only then proceed to OAuth and API calls.

## Recommended Classification
- No candidate exists → `driver_found=false` / diagnosis: driver absent.
- Candidate exists and fails `py_compile` → `driver_found=true` / diagnosis: invalid runtime driver.
- `py_compile` passes and OAuth fails → authentication/configuration problem.
- `py_compile` passes, OAuth passes, and API fails → permission, query, or API usage problem.

## Evidence That Must Be Preserved
- `driver_candidates`
- `driver_path`
- `driver_found`
- `py_compile_exit`
- Full stderr from `py_compile`

## Captured Real Case
Fix session for issue #44 in `elderbernardi/exocortex.saas`:
- The corrected probe started locating `~/.hermes/skills/productivity/google-workspace/scripts/google_api.py`
- The correct status was no longer "driver absent"
- The real failure appeared as `SyntaxError` in the runtime driver before any OAuth

## Useful Regression Tests
- Finds main driver via `HERMES_HOME`
- Prioritizes Hermes runtime over local repo copy
- Accepts `hermes-agent/...` fallback
- Serializes paths outside the repo without breaking evidence
