# Isolated Validation for Configuration Mutations via CLI

Use this pattern when automation will call commands like `hermes config set`, setup scripts, provisioners, or routers that change provider/model/defaults.

## Purpose
Validate real logic without touching the main runtime or locking the agent conducting the session.

## Recommended Pattern

### 1. Unit test with local fixtures
- Freeze minimal payloads from external sources in local JSON.
- Verify:
  - Eligibility filter
  - Ordering/ranking
  - Fallback chain
  - Exclusion of ineligible items

### 2. Isolated apply with PATH shim
Set up a temporary directory like this:

```bash
$tmp/bin/hermes
$tmp/hermes-home
$tmp/report.json
$tmp/hermes-calls.log
```

Minimal shim:

```bash
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$HERMES_CALLS_LOG"
exit 0
```

Then:
- Export `PATH="$tmp/bin:$PATH"`
- Export `HERMES_HOME="$tmp/hermes-home"`
- Execute the real script with `--apply`
- Verify the contents of `hermes-calls.log`

This proves the intended mutation without altering the real installation.

## Verification Sequence That Worked Well
1. Create an isolated script test.
2. Run in a temporary venv separate from the main environment.
3. Do a smoke test with real data from the public source.
4. If the smoke reveals a bug, freeze it in a test immediately.
5. Only then integrate the call into `setup.sh`.
6. Run `bash -n setup.sh` and a textual/structural test confirming the integration.

## Pitfall Promoted from This Session

### Datetime naive vs aware
When the remote source exposes `expiration_date`, treat timestamps without timezone as explicit UTC before comparing with `datetime.now(timezone.utc)`.

Safe pattern:

```python
expiration_dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
if expiration_dt.tzinfo is None:
    expiration_dt = expiration_dt.replace(tzinfo=timezone.utc)
```

Without this, the real smoke can fail with:
- `can't compare offset-naive and offset-aware datetimes`

## When to Apply This Pattern
- Model/provider routers
- Provisioners that execute `config set`
- Bootstrap/setup scripts
- Wrappers that choose defaults and persist config
- Local Hermes/Exocórtex runtime migrations

## Done Signal
Only declare done when there are three pieces of evidence:
1. Fixture tests passing
2. Isolated apply recording the exact expected calls
3. Real smoke confirming the logic remains valid with current data
