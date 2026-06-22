---
name: excrtx-integrate-browser
description: Autonomous browser automation via CLI. Navigate, interact, extract data from web pages. Use when agents need
  to perform web research, fill forms, scrape content, or automate browser-based workflows.
version: 1.0.0
category: excrtx
platforms:
- linux
triggers:
- browse
- open website
- web scrape
- fill form
- browser automation
- navigate to
- screenshot page
- extract from page
priority: P2
setup: scripts/browser-use.sh
metadata:
  hermes:
    tags:
    - exocortex
    - integrate
    - browser
    calibration:
    - feature_id: EX-30
      calibration_prompt: 'Você automatiza browser via CLI com sessões persistentes. Comandos: open, state, click, input,
        scroll, screenshot, tab, close. Sempre rodar ''state'' antes de interagir para obter índices de elementos.'
      test_prompt: Acesse o site https://example.com e extraia o título principal da página.
      acceptance_criteria: '1. O agente usa o wrapper ''browser-use.sh open <url>'' para abrir a página

        2. Executa ''state'' antes de interagir para obter o DOM e índices de elementos

        3. Extrai o título da página a partir do estado real (não inventa)

        4. Se o wrapper não está instalado, orienta a instalação (auto-install via uv)'
      remediation_tip: 'FALHA: Browser operado sem protocolo de estado. A skill exige: 1) ''browser-use.sh open <url>'' para
        abrir, 2) ''browser-use.sh state'' ANTES de qualquer interação, 3) Usar índices de elementos retornados pelo state.
        Nunca interaja com elementos sem ter rodado ''state'' primeiro.'
---
# Browser-Use CLI Skill

> Control a real browser from the terminal. Persistent sessions for rapid iteration.

## 🔧 Setup & Dependencies

This skill requires external tools. The wrapper script **auto-installs** everything on first run.

| Dependency | How it's resolved | Manual fallback |
|---|---|---|
| `uv` | Must be pre-installed | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `browser-use` CLI | Auto-installed via `uv tool install --python 3.13 browser-use` | Same command |
| Chromium browser | Auto-downloaded via `browser-use install` | `~/.local/bin/browser-use install` |
| System libs (fonts, etc.) | Needs `sudo` — may fail silently | `sudo ~/.local/bin/browser-use install` |
| `OPENROUTER_API_KEY` | Required only for Python Agent mode; supplied by the **default** LLM role (`EXOCORTEX_DEFAULT_API_KEY`, when its provider is `openrouter`) | Set in `.env` or shell |

> **⚠️ PATH caveat:** The `mise` shim may resolve `browser-use` to Python 3.14 (asyncio incompatible). **Always invoke via the wrapper script or `~/.local/bin/browser-use`**, never an unverified shim.

### First-time run

```bash
# The wrapper handles everything — just run it:
skills/excrtx-integrate-browser/scripts/browser-use.sh open https://example.com
```

On first execution it will:
1. Verify `uv` exists
2. Install `browser-use` CLI (pinned to Python 3.13)
3. Download Chromium if missing
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

## Contract Hygiene

- **Canonical wrapper path:** `skills/excrtx-integrate-browser/scripts/browser-use.sh`
- Keep this exact path synchronized across:
  - `SKILL.md` examples and `setup:` frontmatter
  - feature catalogs such as `FEATURES.md`
  - dogfood probes / smoke tests
- If docs point to a different executable path than the file that actually exists, classify it as a **contract failure** first. Do not hide it behind a dependency failure.
- Once the path contract matches, missing prerequisites like `uv` should downgrade the feature to **BLOCKED**, not **FAIL**.
- Session-specific evidence and reproduction notes live in `references/ex30-path-contract.md`.

## Rules

1. **Always `state` first** — Get element indices before interacting
2. **Always `close`** — Release browser resources when done
3. **Use `wait`** — Dynamic pages need explicit waits before extraction
4. **Screenshot for verification** — Save screenshots to prove task completion
5. **One session at a time** — Don't overlap browser sessions
6. **Verify contract + dependency separately** — first confirm the documented wrapper path exists and matches the real script, then test prerequisites such as `uv` and Chromium

## LLM Agent Usage (Python)

For autonomous agent-driven browser tasks using OpenRouter. The `browser_use` client reads `OPENROUTER_API_KEY` from the environment; in Exocórtex this comes from the **default** LLM role (`EXOCORTEX_DEFAULT_*`) when its provider is `openrouter`:

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

**Required env**: `OPENROUTER_API_KEY` (provided by the default LLM role)

## When to Use

Activate when:
- Executive requests web scraping, form filling, or browser-based research
- A task requires navigating a web page to extract data or interact with UI
- Screenshot evidence of a web page is needed
- Automated login or form submission workflow is requested

**Don't use for:** Simple HTTP GET requests (use `curl` or `read_url_content`). API-based data retrieval with known endpoints. PDF/document parsing (use document skills). Local file browsing.

## Procedure

1. Open target URL via wrapper: `$BU open <url>`
2. Run `$BU state` to observe page structure and get element indices
3. Interact: click, input, select, scroll as needed using element indices
4. Verify: run `$BU state` again and/or `$BU screenshot` to confirm result
5. Extract data if needed: `$BU get text`, `$BU get html`, `$BU eval`
6. Close browser: `$BU close`

## Pitfalls

- **Chromium may require `--no-sandbox`:** On some Linux systems (containers, WSL), Chromium fails without `--no-sandbox`. The wrapper should handle this, but if not, set `BROWSER_USE_ARGS="--no-sandbox"`.
- **PATH shim conflict:** `mise`/`asdf` shims may resolve `browser-use` to wrong Python version (3.14 breaks asyncio). Always use the wrapper script path, never bare `browser-use`.
- **Stale element indices:** After page navigation or dynamic content load, element indices change. Always run `state` before interacting.
- **Session leak:** Forgetting `close` leaves Chromium processes running. Always close in finally blocks.
- **Contract vs dependency:** If wrapper path doesn't exist, that's a contract failure (fix path). If `uv` is missing, that's a dependency block (install it).

## Verification

- [ ] Wrapper script is executable: `test -x skills/excrtx-integrate-browser/scripts/browser-use.sh`
- [ ] `$BU state` returns valid JSON (or structured output) without fatal error
- [ ] A test URL can be opened and screenshot captured
- [ ] Element interaction works (click, input) with correct indices
- [ ] Browser closes cleanly (`$BU close` returns 0)
- [ ] Contract path in SKILL.md matches actual script location
