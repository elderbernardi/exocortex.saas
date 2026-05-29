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
- **Relevance:** PDD Provisioner Agent, Code Branch (Multi-tenant)
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
- **Relevance:** PDD Provisioner Agent design
- **Tags:** hermes, meta-harness, outer-loop, self-evolution

The Hermes architecture already has a conceptual "Outer Loop":
- **Inner Loop:** Standard protocol execution (tool calling, state commits)
- **Outer Loop:** Analyzes execution archives, orchestrates evaluations, injects mutations
- Integrates `lm-evaluation-harness` for self-verification (>60 academic metrics)

**Key insight:** Our Provisioner Agent IS the Outer Loop for tenant provisioning. It is a **dedicated, separate agent** — a tenant's Exocórtex never provisions another instance. The architecture already supports this pattern natively.

---

## Development Environment

### K-009: Hermes Installation & Doctor Status
- **Date:** 2026-05-26
- **Source:** User manual installation & `hermes doctor`
- **Relevance:** PDD P0 (Setup) Complete
- **Tags:** hermes, installation, setup, doctor

Completed Setup Details:
- **Version:** Hermes Agent v0.14.0 (2026.5.16)
- **Runtime:** Python 3.11.14 (running on Linux)
- **Method:** Manual installation using the curl script:
  `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
- **Executable Path:** `~/.local/bin/hermes`
- **Active Workspace:** `~/.hermes/hermes-agent`

Diagnostic Warnings (from `hermes doctor`):
1. **OAuth/API Auth:** Not logged into Nous Portal, OpenAI Codex, Google Gemini OAuth, MiniMax, or xAI OAuth (can be configured via `hermes model` / `hermes auth` if needed).
2. **First Run State:** `MEMORY.md`, `USER.md`, and `state.db` are not yet created in `~/.hermes/memories/` (they will initialize automatically upon first session run).

---

### K-010: Configuração de Provedores e Fallback (Codex + DeepSeek)
- **Date:** 2026-05-26
- **Source:** experimentação & config.yaml
- **Relevance:** PDD P0/P1
- **Tags:** fallback, openrouter, deepseek, codex, oauth

Configuração atual do runtime do Hermes para o experimento:
1. **Primary Provider:** OpenAI Codex (autenticado via OAuth do Codex).
2. **Fallback Provider:** OpenRouter, configurado no `config.yaml` sob `fallback_model`.
3. **Fallback Model:** `deepseek/deepseek-chat` (DeepSeek V3 no OpenRouter).
4. **API Key:** `OPENROUTER_API_KEY` ativa em `~/.hermes/.env`.

---

### K-011: Hermes Dashboard com TUI embutida é superfície operacional viável, mas deve ficar privada
- **Date:** 2026-05-29
- **Source:** documentação local do Hermes + experimentação em runtime
- **Relevance:** setup operacional, UX executiva, hardening
- **Tags:** hermes, dashboard, tui, systemd, tailscale, security

Achados consolidados:
- `hermes dashboard --tui --no-open` habilita a aba `CHAT` no dashboard e serve como cockpit operacional útil para o administrador.
- O frontend pode fazer build automático na primeira subida; depois disso, `--skip-build` reduz custo de restart em serviço persistente.
- Em Linux com `systemd --user`, o dashboard pode ser persistido com segurança via `hermes-dashboard.service` chamando `python -m hermes_cli.main dashboard --tui --no-open --skip-build`.
- O dashboard expõe superfícies sensíveis: sessões, config, logs, skills e chaves. Portanto, não deve ser publicado em porta pública ou via bind amplo por default.
- Para acesso remoto contínuo, o padrão recomendado é manter o serviço em `127.0.0.1:9119` e usar **Tailscale** ou túnel SSH. Tailscale entra como requisito de segurança do setup, não como conveniência opcional.
