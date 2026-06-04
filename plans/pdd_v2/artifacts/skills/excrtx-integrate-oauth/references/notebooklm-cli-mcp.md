# NotebookLM via Hermes (CLI-first, MCP fallback)

## Class

CLI-backed MCP provider (local binary + local auth state), not remote hosted OAuth URL.

## Durable operator pattern

1. Check CLI presence:
   - `command -v nlm`
   - `command -v notebooklm-mcp`

2. Validate NotebookLM auth:
   - `nlm login --check`

3. Add MCP server to Hermes:
   - `hermes mcp add notebooklm --command notebooklm-mcp`

4. If running non-interactively (setup scripts), force confirmation:
   - `printf 'y\n' | hermes mcp add notebooklm --command notebooklm-mcp`

5. Verify persisted result:
   - `hermes mcp list`
   - check `mcp_servers.notebooklm` in config

## Why this matters

`hermes mcp add` can connect and discover tools, then stop on the "Enable all tools?" prompt.
Without explicit confirmation in automation, the setup log may claim success while the server is not saved.

## Version note

For `nlm` v0.6.x, use `nlm login --check` for auth validation. Do not hardcode `nlm auth status` in setup logic.