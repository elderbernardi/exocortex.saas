# MCP baseline hygiene for Exocórtex setup

When maintaining reproducible setup scripts, enforce MCP baseline explicitly instead of relying on manual state.

## Rule

After configuring required MCP servers (e.g., notebooklm), run a baseline guard that removes deprecated/forbidden servers if present.

Example pattern:

```bash
enforce_mcp_baseline() {
  if ! command -v hermes >/dev/null 2>&1; then
    echo "hermes CLI missing; skip MCP baseline"
    return 0
  fi

  if hermes mcp list 2>/dev/null | grep -q "composio"; then
    printf 'y\n' | hermes mcp remove composio >/dev/null 2>&1 || \
      echo "failed to remove composio"
  fi
}
```

## Why this belongs in setup

- Keeps fresh installs aligned with current architecture decisions.
- Prevents drift when old MCP entries survive profile migration or config reuse.
- Makes setup idempotent: reruns converge to the same MCP state.

## Placement

Call the baseline guard immediately after MCP additions/updates, before final verification.