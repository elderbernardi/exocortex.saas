# Harness Operational Truth Contract

Use this checklist when a harness feature promises wrappers, local directories, automated setup, or PASS in dogfood.

## When to Apply
- Documentation says a wrapper or directory "exists."
- `setup.sh` promises to provision artifacts in `~/.hermes` / `$HERMES_HOME`.
- A dogfood probe declares PASS/FAIL based on the presence of local artifacts.
- The issue is about operational credibility: the system claims a capability that may not actually exist.

## Minimum Checklist
1. **Files in repo**
   - Confirm the promised wrappers physically exist in the repository.
   - If they don't exist, fix code before modifying documentation.

2. **Provisioning**
   - Confirm `setup.sh` copies wrappers to the correct destination.
   - Also create the operational directories expected by the feature.
   - Apply executable permissions when the feature's contract depends on it.

3. **Path source of truth**
   - Probes and wrappers must use `$HERMES_HOME` or equivalent central helper.
   - Avoid `Path.home() / ".hermes"` when the feature needs to be testable in temporary/provisioned environments.

4. **Isolated test**
   - Create or expand a test that injects a temporary `HERMES_HOME`.
   - Validate both wrapper presence and probe behavior.

5. **Real provisioned artifact smoke**
   - Execute the wrapper installed at the real `HERMES_HOME` destination, not just the repo script.
   - Confirm generation of expected artifacts (`runs/`, `events/`, `reviews/` or equivalents).

6. **Real-agent dogfood**
   - Run the specific feature in real-agent mode.
   - Only declare fix complete when the PASS result is anchored in concrete evidence.

7. **Documentation**
   - Align `FEATURES.md`, operational skill, and any reference that promises the capability.
   - Documentation must never remain more optimistic than the runtime.

## Recurring Pitfalls
- Fix only the markdown and forget the physical file.
- Create the wrapper in repo but don't provision in `setup.sh`.
- Probe using `Path.home()` and breaking tests with temporary `HERMES_HOME`.
- Consider an adjacent smoke timeout as a blocker for the issue, even when the target feature was already provisioned and validated separately.
- Declare PASS without executing the provisioned wrapper at the real destination.

## Evidence That Counts
- Green automated test covering temporary `HERMES_HOME`
- Smoke of provisioned wrapper with generated artifacts
- Dogfood `PASS` result for the specific feature
- Reading the final artifact (`summary.json`, `review.md`, `result.json` or equivalent)

## Captured Base Case
Issue EX-33 / #46: missing wrappers, probe pointing to `Path.home()`, setup not provisioning learning directory. The fix required aligning four layers: actual files in repo, `setup.sh`, runtime at `~/.hermes`, and real-agent dogfood.