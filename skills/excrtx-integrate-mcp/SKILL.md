---
name: excrtx-integrate-mcp
description: Add, configure, and test MCP servers in Hermes for the Exocórtex ecosystem. Covers stdio and HTTP transports, discovery, and CLI pitfalls with workarounds.
version: 1.3.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - mcp
    - configuration
    - tools
    - integration
    related_skills:
    - excrtx-govern-tools
    - excrtx-hermes-extensions
---

# Exocórtex MCP Server Integration

Adds MCP (Model Context Protocol) servers to the Hermes/Exocórtex runtime.
Covers installation, configuration, testing, and activation — with workarounds
for cases where the Hermes CLI fails with complex arguments.

## When to Use

Activate when the task is to:
- add a new MCP server to the Hermes runtime (stdio or HTTP transport)
- troubleshoot `hermes mcp add` failures with argument parsing
- configure MCP servers that need complex args or environment variables
- verify MCP server connectivity and tool discovery
- document MCP integration patterns for future reference

Do **not** use for:
- removing or updating existing MCP servers (use `hermes mcp remove` directly)
- debugging server-side MCP implementation issues (that's upstream)
- adding Hermes-native tools that are not MCP-based

## Procedure

### 1. Inspect the Server

Before installing, verify:
- `README.md`: recommended installation method, entry command, options
- `pyproject.toml` (Python) or `package.json` (Node): package name, entry point
- Supported transports: `stdio` (most common), `http`, `streamable-http`
- Relevant options: language (`--language`, `--country`), port, authentication

**Tool:** `gh api repos/<owner>/<repo>/readme --jq '.download_url'` to fetch
the raw README URL without cloning. Use `gh api repos/<owner>/<repo>/git/trees/main?recursive=1`
to list the file structure.

If `web_extract` is unavailable (e.g., no Firecrawl — see
`$HERMES_HOME/reminders/firecrawl.md` when degraded), fall back to:

**Option A:** `browser_navigate` + `browser_vision` — for pages with dynamic content
or that need rendering. `browser_vision` takes a screenshot + describes.

**Option B:** `git clone --depth 1 <repo>` + `read_file` — for simple repositories.
Warning: cloning consumes session time. Prefer browser for quick reading.

**Option C:** `curl -sL raw.githubusercontent.com/...` — for known raw files
(README.md, pyproject.toml, etc.). Faster than cloning.

### 2. Install

Prefer the method recommended in the README:

```bash
# Python — via pip (if pipx unavailable)
pip install <package-name>

# Python — via pipx (keeps command globally isolated)
pipx install <package-name>

# Node — global
npm install -g <package-name>
```

**Pitfall:** `pipx` is often absent in managed environments (mise, asdf).
`pip install` works as a fallback if the command enters PATH.

After installing, verify:
```bash
which <command>
<command> --help
```

### 3. Configure in Hermes

#### Path A: `hermes mcp add` (preferred)

Works well for servers **without** complex arguments:

```bash
hermes mcp add <name> --command <command>
```

**Pitfall with `--args`:** The Hermes CLI parses arguments via argparse,
and flags like `--country BR` are interpreted as Hermes CLI flags,
not MCP server arguments. This produces:
```
hermes: error: unrecognized arguments: --country BR
```

**Symptom:** the error appears regardless of quoting, `=`, or positioning.

**Workaround:** use `hermes config set` for simple fields and Python for
complex structures (see Path B).

#### Path B: `hermes config set` + Python (fallback)

When the server has complex arguments (flags, lists, dictionaries):

```bash
# Simple string fields — hermes config set works
hermes config set mcp_servers.<name>.command <command>
```

For `args` (list) and `env` (dictionary), `hermes config set` stores them as
string literals, which breaks YAML loading. Fix via Python:

```python
import yaml
from pathlib import Path

config_path = Path.home() / ".hermes" / "config.yaml"
config = yaml.safe_load(config_path.read_text())

# Force YAML list
config["mcp_servers"]["<name>"]["args"] = ["--country", "BR"]
# or dictionary
config["mcp_servers"]["<name>"]["env"] = {"TOKEN": "value"}

config_path.write_text(
    yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
)
```

Real example (Wikipedia MCP with country BR):
```yaml
mcp_servers:
  wikipedia:
    command: wikipedia-mcp
    args:
    - "--country"
    - "BR"
```

### 4. Test

```bash
hermes mcp test <name>
```

Expected output:
```
Testing '<name>'...
  Transport: stdio → <command>
  Auth: none
  ✓ Connected (XXXms)
  ✓ Tools discovered: N
```

If it fails:
- **"Command not found"**: the package is not in Hermes' PATH. Check `which <command>`.
- **Connection timeout**: server takes too long to start. Increase `connect_timeout`.
- **"No tools discovered"**: server started but exposed no tools. Check logs.

For HTTP servers:
```bash
hermes mcp add <name> --url https://<host>/mcp
```

### 5. Activate

MCP tools are discovered **only at agent startup**.
Configuration changes take effect only after restart:

- **Gateway (Telegram/Discord/etc.):** `/restart` in chat or `hermes gateway restart`
- **CLI:** exit and start a new `hermes chat`

After restart, tools appear as:
```
mcp_<server_name>_<tool_name>
```

All hyphens and dots are converted to underscores. Each tool
also gets an alias with a `wikipedia_` prefix (pattern from some MCP servers).

## Pitfalls

- **pipx missing in managed environments:** tools like mise/asdf may not have pipx. Fall back to `pip install`.
- **`hermes mcp add --args` bug:** argparse in the Hermes CLI consumes flags meant for the MCP server. Use `hermes config set` + Python correction (see Path B above).
- **`hermes config set` serializes lists as strings:** when setting `args` or `env` via `hermes config set`, the value is stored as a YAML string literal, not a list/dict. Fix with the Python script shown in Step 3, Path B.
- **Tools not appearing after config:** MCP discovery happens at startup only. Restart the gateway or CLI session.
- **`hermes model` in non-interactive context:** this command requires an interactive terminal — it does NOT work via pipe/subprocess.
- **OAuth login output buffering:** `hermes auth add nous --no-browser` generates an OAuth URL but may not print output when run in background. Run it directly in a terminal.

## Verification

- [ ] `which <command>` returns the installed binary path
- [ ] `<command> --help` prints usage successfully
- [ ] `hermes mcp list` shows the server as configured
- [ ] `hermes mcp test <name>` shows `✓ Connected` and `✓ Tools discovered: N`
- [ ] After gateway/CLI restart, `hermes tools list` shows `mcp_<name>_*` tools
- [ ] A test query using an MCP tool returns valid results

## Known Server Patterns

### Acervo Control Plane (local semantic MCP)
- **Command:** `python3 scripts/acervo_mcp_server.py`
- **Transport:** stdio
- **Design rule:** thin adapter over `acervo_semantic_core.py` and parity with `acervoctl.py`
- **Tool surface:** 10 semantic tools only (`list/search/read/prepare/commit/create/update/validate/export`)
- **Smoke check:** `python3 scripts/acervo_mcp_server.py --self-test --acervo-root "$PWD/acervo"`
- **Reference:** `references/acervo-mcp-server.md`

### Wikipedia (`Rudra-ravi/wikipedia-mcp`)
- **Package:** `wikipedia-mcp` (PyPI)
- **Command:** `wikipedia-mcp`
- **Transport:** stdio (default), http, streamable-http
- **Language:** `--country BR` for Portuguese, `--language pt` also works
- **Cache:** `--enable-cache` (optional)
- **Token:** `--access-token` to avoid rate limiting (optional)
- **Tools:** 11 (22 with aliases): search, article, summary, sections, links, coordinates, related_topics, extract_key_facts, summarize variants, connectivity test
- **Dependencies:** fastmcp, wikipedia-api, requests, python-dotenv
- **Reference session:** `references/wikipedia-integration-2026-06-11.md` — full integration log, error transcripts, Python/YAML workaround
