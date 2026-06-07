---
name: excrtx-integrate-browser
description: Autonomous browser automation via CLI. Navigate, interact, extract data from web pages. Use when agents need to perform web research, fill forms, scrape content, or automate browser-based workflows.
version: 1.0.0
triggers:
  - "browse"
  - "open website"
  - "web scrape"
  - "fill form"
  - "browser automation"
  - "navigate to"
  - "screenshot page"
  - "extract from page"
priority: P2
setup: scripts/browser-use.sh
---

# Browser-Use CLI Skill

> Control a real browser from the terminal. Persistent sessions for rapid iteration.

## 🔧 Setup & Dependencies

This skill requires external tools. The wrapper script **auto-installs** everything on first run, and `setup.sh` can pre-provision the same runtime in the skill path.

| Dependency | How it's resolved | Manual fallback |
|---|---|---|
| `uv` | Auto-installed into the skill-local runtime when absent | `curl -LsSf https://astral.sh/uv/install.sh \| env UV_INSTALL_DIR="<skill>/.runtime/uv" sh` |
| `browser-use` CLI | Auto-installed via `uv tool install --python 3.13 browser-use` into `<skill>/.runtime/bin/` | Same command with `UV_TOOL_DIR` / `UV_TOOL_BIN_DIR` pointed at the runtime |
| Chromium browser | Auto-downloaded via `browser-use install` into `<skill>/.runtime/ms-playwright/` | `<skill>/.runtime/bin/browser-use install` |
| System libs (fonts, etc.) | Needs `sudo` — may fail silently | `sudo <skill>/.runtime/bin/browser-use install` |
| `OPENROUTER_API_KEY` | Reused automatically from Hermes `.env` by the wrapper; mapped to browser-use's OpenAI-compatible env when needed | Set in Hermes `.env` or shell |

> **⚠️ PATH caveat:** The `mise` shim may resolve `browser-use` to Python 3.14 (asyncio incompatible). **Always invoke via the wrapper script or the skill-local runtime binary**, never an unverified shim.

### First-time run

```bash
# The wrapper handles everything — just run it:
skills/excrtx-integrate-browser/scripts/browser-use.sh open https://example.com
```

On first execution it will:
1. Reuse the skill-local `uv` runtime when present, otherwise install it into `.runtime/uv`
2. Install `browser-use` CLI (pinned to Python 3.13) into `.runtime/bin`
3. Download Chromium into `.runtime/ms-playwright` if missing
4. Forward your command

## Quick Start Workflow

```bash
BU="skills/excrtx-integrate-browser/scripts/browser-use.sh"

# 1. Navigate
$BU open <url>

# 2. Observe — ALWAYS run state first to get element indices
$BU state

# 3. Interact using indices from state
$BU click <index>
$BU input <index> "text"

# 4. Verify
$BU state

# 5. Cleanup
$BU close
```

## Command Reference

### Navigation
| Command | Description |
|---|---|
| `open <url>` | Navigate to URL |
| `back` | Go back in history |
| `scroll down` | Scroll down (`--amount N` for pixels) |
| `scroll up` | Scroll up |
| `tab list` | List all tabs |
| `tab new [url]` | Open new tab |
| `tab switch <index>` | Switch to tab |
| `tab close <index>` | Close tab |

### Page State
| Command | Description |
|---|---|
| `state` | URL, title, clickable elements with indices |
| `screenshot [path.png]` | Screenshot (base64 if no path, `--full` for full page) |

### Interactions
| Command | Description |
|---|---|
| `click <index>` | Click element by index |
| `click <x> <y>` | Click at pixel coordinates |
| `type "text"` | Type into focused element |
| `input <index> "text"` | Click element, clear, then type |
| `input <index> ""` | Clear a field |
| `keys "Enter"` | Send keyboard keys (`"Control+a"`, etc.) |
| `select <index> "option"` | Select dropdown option |
| `upload <index> <path>` | Upload file to file input |
| `hover <index>` | Hover over element |
| `dblclick <index>` | Double-click element |
| `rightclick <index>` | Right-click element |

### Data Extraction
| Command | Description |
|---|---|
| `eval "js code"` | Execute JavaScript, return result |
| `get title` | Page title |
| `get html [--selector "h1"]` | Page HTML (or scoped to selector) |
| `get text <index>` | Element text content |
| `get value <index>` | Input/textarea value |
| `get attributes <index>` | Element attributes |
| `get bbox <index>` | Bounding box (x, y, width, height) |

### Waiting
| Command | Description |
|---|---|
| `wait selector ".results"` | Wait for CSS selector |
| `wait text "Success"` | Wait for text to appear |

## Patterns

### Research Pattern
```bash
BU="skills/excrtx-integrate-browser/scripts/browser-use.sh"
$BU open https://example.com/search
$BU state
$BU input 3 "search query"
$BU click 4   # search button
$BU wait selector ".results"
$BU state
$BU get text 10  # first result
$BU screenshot results.png
$BU close
```

### Form Fill Pattern
```bash
BU="skills/excrtx-integrate-browser/scripts/browser-use.sh"
$BU open https://example.com/form
$BU state
$BU input 1 "John Doe"
$BU input 2 "john@example.com"
$BU select 3 "Option A"
$BU click 5   # submit
$BU wait text "Success"
$BU screenshot confirmation.png
$BU close
```

### Data Extraction Pattern
```bash
BU="skills/excrtx-integrate-browser/scripts/browser-use.sh"
$BU open https://example.com/data
$BU state
$BU get html --selector "table"
$BU eval "JSON.stringify([...document.querySelectorAll('tr')].map(r => [...r.cells].map(c => c.textContent)))"
$BU close
```

## Rules

1. **Always `state` first** — Get element indices before interacting
2. **Always `close`** — Release browser resources when done
3. **Use `wait`** — Dynamic pages need explicit waits before extraction
4. **Screenshot for verification** — Save screenshots to prove task completion
5. **One session at a time** — Don't overlap browser sessions

## LLM Agent Usage (Python)

For autonomous agent-driven browser tasks using OpenRouter:

```python
import asyncio
from browser_use import Agent
from browser_use.llm.openrouter.chat import ChatOpenRouter

async def run():
    llm = ChatOpenRouter(model="google/gemini-2.5-flash")  # or anthropic/claude-sonnet-4
    agent = Agent(task="Go to example.com and find the main heading", llm=llm)
    result = await agent.run()
    print(result)

asyncio.run(run())
```

**Required env**: `OPENROUTER_API_KEY`
