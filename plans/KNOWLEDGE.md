# Exocórtex.IA — Knowledge Base

> **PURPOSE:** Accumulated discoveries, learnings, and technical findings from research and development. Check here before researching a topic — it may already be documented.

---

## How to Use

- **Before researching:** Search this file for keywords
- **After discovering something useful:** Add an entry following the format below
- **Review periodically:** Mark outdated entries as `[STALE]`

### Entry Format

```markdown
### K-{NNN}: {Title}
- **Date:** {YYYY-MM-DD}
- **Source:** {URL, file, or "experimentation"}
- **Relevance:** {which component/phase this applies to}
- **Tags:** {searchable keywords}

{Description of the finding}
```

---

## Hermes Agent Internals

### K-001: Hermes Project Structure
- **Date:** 2025-05-25
- **Source:** GitHub NousResearch/hermes-agent + Context7
- **Relevance:** PDD (todas as fases), Code Branch
- **Tags:** hermes, architecture, directory-layout

```
hermes-agent/
├── run_agent.py          # AIAgent class — core conversation loop (~12k LOC)
├── model_tools.py        # Tool orchestration, discover_builtin_tools()
├── toolsets.py           # Toolset definitions, _HERMES_CORE_TOOLS
├── cli.py                # HermesCLI — interactive CLI (~11k LOC)
├── hermes_state.py       # SessionDB — SQLite session store (FTS5)
├── hermes_constants.py   # get_hermes_home() — profile-aware paths
├── agent/                # Provider adapters, memory, compression
│   ├── conversation_loop.py  # Core loop (240k bytes!)
│   ├── prompt_builder.py     # System prompt assembly
│   ├── memory_manager.py     # Memory read/write
│   ├── skill_utils.py        # Skill discovery/loading
│   └── curator.py            # Memory curation/nudges
├── tools/                # Built-in tools, auto-discovered
│   └── environments/     # Terminal backends (docker, ssh, modal)
├── gateway/              # Multi-platform messaging
│   └── platforms/        # telegram, whatsapp, discord, slack...
├── plugins/              # Plugin system
│   ├── memory/           # honcho, mem0, supermemory
│   ├── kanban/           # Multi-agent board (Noosphere pattern)
│   └── model-providers/  # openrouter, anthropic, gmi
├── skills/               # Bundled skills (always loaded)
├── optional-skills/      # Heavier skills (opt-in)
└── cron/                 # Background scheduler
```

---

### K-002: Hermes Skill Format (SKILL.md)
- **Date:** 2025-05-25
- **Source:** Context7 /nousresearch/hermes-agent
- **Relevance:** PDD P1-P4 (criação de skills)
- **Tags:** hermes, skills, SKILL.md, format

```yaml
---
name: my-skill
description: Brief description
version: 1.0.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [category, keywords]
    requires_toolsets: [terminal]
    fallback_for_toolsets: [web]
    config:
      - key: my.setting
        description: "What this controls"
        default: "value"
        prompt: "Setup prompt"
required_environment_variables:
  - name: MY_API_KEY
    prompt: "Enter your API key"
---

# Skill Title

## When to Use
Trigger conditions.

## Quick Reference
Common commands table.

## Procedure
1. Step one
2. Step two

## Pitfalls
Known failure modes.

## Verification
How to confirm it worked.
```

Skill directory structure:
```
skills/{category}/{skill-name}/
├── SKILL.md          # Required
├── scripts/          # Optional helper scripts
└── references/       # Optional reference docs
```

---

### K-003: Hermes Memory Architecture
- **Date:** 2025-05-25
- **Source:** hermes-agent-sot-for-agents.md
- **Relevance:** PDD P2 (Memory), Code Branch (Semantic Memory MCP)
- **Tags:** hermes, memory, FTS5, sqlite, SOUL.md, MEMORY.md

**Hybrid Memory:** Immediate context (always in prompt) + historical (FTS5 SQLite search on demand).
- `SOUL.md` → Behavioral identity, loaded into system prompt every turn
- `MEMORY.md` → Persistent memory entries, searched via FTS5
- `USER.md` → User-specific preferences and context
- Memory is curated periodically via "nudges" (background review)
- **Constraint:** Avoids flat vector JSONL to prevent structural degradation

---

### K-004: Hermes MCP Configuration
- **Date:** 2025-05-25
- **Source:** Context7 /nousresearch/hermes-agent
- **Relevance:** PDD P3 (Tools), Code Branch (MCP Servers)
- **Tags:** hermes, mcp, config.yaml, tools

MCP servers are configured in `config.yaml` under `mcp_servers:`:

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
```

CLI commands:
- `hermes mcp add` — add MCP server
- `hermes mcp list` — list configured servers
- `hermes tools list` — list all available tools (built-in + MCP)

---

### K-005: Hermes Multi-Agent Pattern (Noosphere)
- **Date:** 2025-05-25
- **Source:** hermes-agent-sot-for-agents.md
- **Relevance:** PDD Meta-Trainer, Code Branch (Multi-tenant)
- **Tags:** hermes, multi-agent, noosphere, swarm

- **No direct peer-to-peer invocation** (prevents infinite loops)
- Uses "Noosphere" pattern: shared FTS5 SQLite as coordination bus
- Agents write state/messages to shared DB
- Secondary agents poll via cron heartbeats (pub-sub pattern)
- Plugin `plugins/kanban/` implements multi-agent board dispatcher

---

### K-006: Hermes 7-Layer Security Model
- **Date:** 2025-05-25
- **Source:** hermes-agent-sot-for-agents.md
- **Relevance:** All phases, especially Draft-First (PDD P4)
- **Tags:** hermes, security, HITL, isolation

1. User Authorization (allowlists + crypto DM pairing)
2. Command Approval (HITL for destructive actions)
3. Container Isolation (Docker/Singularity/Modal)
4. Credential Filtering (env var isolation in subprocesses)
5. Context File Scanning (prompt injection neutralization)
6. Cross-Session Isolation (crypto boundaries for DB)
7. Path Traversal Defense (storage sanitization)

**Key insight for Exocórtex:** Layer 2 (Command Approval) is the native HITL hook where Draft-First plugs in. Layer 3 (Container Isolation) maps directly to our 1-container-per-tenant model.

---

### K-007: Hermes Gateway Platforms
- **Date:** 2025-05-25
- **Source:** GitHub repo structure
- **Relevance:** PDD P0 (Setup), Code Branch (Routing)
- **Tags:** hermes, gateway, whatsapp, telegram

Supported platforms in `gateway/platforms/`:
telegram, discord, slack, whatsapp, homeassistant, signal, matrix,
mattermost, email, sms, dingtalk, wecom, weixin, feishu, qqbot,
bluebubbles, yuanbao, webhook, api_server

- WhatsApp: QR code pairing via `hermes gateway setup`
- Telegram: BotFather token configuration
- Gateway normalizes all protocols into unified internal format

---

### K-008: Hermes Meta-Harness (Outer Loop)
- **Date:** 2025-05-25
- **Source:** hermes-agent-sot-for-agents.md
- **Relevance:** PDD Meta-Trainer design
- **Tags:** hermes, meta-harness, outer-loop, self-evolution

The Hermes architecture already has a conceptual "Outer Loop":
- **Inner Loop:** Standard protocol execution (tool calling, state commits)
- **Outer Loop:** Analyzes execution archives, orchestrates evaluations, injects mutations
- Integrates `lm-evaluation-harness` for self-verification (>60 academic metrics)

**Key insight:** Our Meta-Trainer IS the Outer Loop for tenant provisioning. The architecture already supports this pattern natively.

---

## Development Environment

### K-009: Hermes Installation
- **Date:** 2025-05-25
- **Source:** GitHub README
- **Relevance:** PDD P0
- **Tags:** hermes, installation, setup, python, uv

Key files for setup:
- `setup-hermes.sh` — main installation script
- `pyproject.toml` — Python dependencies (uses `uv` package manager)
- `.env.example` — comprehensive env var template (23KB!)
- `cli-config.yaml.example` — full config reference (57KB!)
- `hermes_bootstrap.py` — first-run bootstrap

Commands:
- `hermes doctor` — diagnostic check
- `hermes model` — configure LLM provider
- `hermes gateway setup` — configure messaging platforms
