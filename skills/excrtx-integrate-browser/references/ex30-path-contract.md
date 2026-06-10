# EX-30 — Browser Wrapper Path Contract

## Durable Lesson

The browser automation skill has a public operational interface: the shell wrapper. When documentation promises one path and the repository delivers another, that's a contract failure, not a mere internal detail.

## Canonical Path

```bash
skills/excrtx-integrate-browser/scripts/browser-use.sh
```

## Classification Rule

1. **Divergent path** between documentation/probe and actual file → `FAIL`
2. **Aligned path, but missing prerequisite** (e.g., `uv`) → `BLOCKED`
3. **Aligned path + prerequisites present** → can proceed to smoke / `PASS`

## Surfaces That Must Stay Synchronized

- `SKILL.md` (`setup:` and usage examples)
- Feature catalog (`FEATURES.md` or equivalent)
- Dogfood probes / smoke tests
- Any additional compatible wrapper created in setup

## Quick Audit Recipe

```bash
# 1. Confirm actual script
 test -x skills/excrtx-integrate-browser/scripts/browser-use.sh

# 2. Confirm docs cite the same path
# (adjust search method to environment)

# 3. Separate contract from dependency
 command -v uv
```

## Interpretation

If the actual script exists and docs still point to another location, fix the documentation/probe first. Only then evaluate `uv`, Chromium, and end-to-end smoke.
