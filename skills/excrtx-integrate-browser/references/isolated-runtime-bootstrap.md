# Isolated Runtime Bootstrap for Browser Automation

## When to Apply
- When the skill needs to work in environments without global `uv`
- When setup needs to be portable and self-contained in the skill's own directory
- When the browser (Playwright/Chromium) must not depend on system-wide global caches

## Adopted Pattern
Provision a local runtime in `skills/excrtx-integrate-browser/.runtime/` with explicit subpaths:

- `uv/` — local `uv` installation
- `bin/` — executables exposed by tool install (`browser-use`)
- `python/` — managed Python runtime
- `tools/` — `uv` tool artifacts
- `cache/uv/` — isolated `uv` cache
- `ms-playwright/` — browsers downloaded by Playwright

## Operational Rules
1. The wrapper must prefer the skill's local runtime before depending on global PATH.
2. The installer must auto-bootstrap when `uv` is absent.
3. The wrapper must temporarily inject into PATH both the tool's binary directory and the local `uv` directory.
4. Isolation variables must point to `.runtime/`, especially:
   - `UV_PYTHON_INSTALL_DIR`
   - `UV_TOOL_DIR`
   - `UV_CACHE_DIR`
   - `PLAYWRIGHT_BROWSERS_PATH`
5. Preventive setup (`setup.sh`) and on-demand repair (first wrapper use) must converge to the same runtime layout.

## Confirmed Pitfall
If only `bin/` enters PATH and the `uv` binary directory doesn't, subsequent commands depending on `uvx`/`uv tool` can fail even with the local installation present.

## Stable Workaround
To provision Chromium, prefer:

```bash
uv tool run --from playwright playwright install chromium
```

Instead of relying on indirect `browser-use install` flows, which may try `sudo`, assume global PATH, or fail in more restricted shells.

## Minimum Verification
Validate the presence of:
- `.runtime/uv/uv`
- `.runtime/bin/browser-use`
- `.runtime/ms-playwright/`

And run a real smoke:

```bash
skills/excrtx-integrate-browser/scripts/browser-use.sh --help
```

Acceptance criteria: complete bootstrap + CLI help with exit 0.
