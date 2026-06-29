---
type: decision
title: 'ADR-006: Custom Skill vs. MCP Server Selection'
description: When extending Exocortex.IA, developers often face the choice of whether to write a new custom Hermes skill (under `s...
tags: []
timestamp: 2026-06-11
class: perene
created_at: 2026-06-11T03:03:32Z
last_accessed_at: 2026-06-11T03:03:32Z
---

# ADR-006: Custom Skill vs. MCP Server Selection

## Context
When extending Exocortex.IA, developers often face the choice of whether to write a new custom Hermes skill (under `skills/excrtx-*`) or develop/register a new Model Context Protocol (MCP) server. Both approaches expose new capabilities to the LLM agent, but they have distinct performance, security, and maintenance characteristics.

---

## Decision Criteria

### 1. Choose a Custom Skill (`skills/excrtx-*`) when:
*   **Behavior & Persona Gov**: The change requires enforcing conversational postures (e.g., Socratic Mode, specific style guidelines, anti-slop controls).
*   **Prompt-Driven Workflows**: The logic is highly prompt-centric, relying on reasoning prompts, templates, or contextual instructions.
*   **Local System Scripting**: You are wrapping local system scripts, commands, or developer automation routines (e.g., compile utilities, local audits).
*   **No Persistent Network Daemons**: The tool does not require running background services or managing complex OAuth network states.

### 2. Choose an MCP Server when:
*   **SaaS & Third-Party APIs**: You are integrating with external platforms requiring direct API authorization (e.g., Google Workspace, databases, Slack).
*   **Structured Schemas & Data Sources**: You need to expose a large, structured dataset or a complex relational interface directly to the model.
*   **Language-Agnostic Tools**: The integration is written in a language other than Python/Shell, and it is cleaner to run it as a standalone stdio/SSE process.
*   **Stateful Services**: The integration manages long-lived database connections, file handles, or network states.

---

## Technical Comparison

| Dimension | Custom Skill (`excrtx-*`) | MCP Server |
| :--- | :--- | :--- |
| **Integration Method** | Native markdown instructions compiled into `SOUL_SEED.md` | JSON-RPC tool/resource discovery schemas |
| **Memory Footprint** | Low (loaded conditionally; compiled rules add to prompt context) | Medium (runs as a separate stdio/SSE daemon process) |
| **Tool Registry** | Manual bash configuration or direct command script execution | Dynamic registration via `hermes mcp add` |
| **Development Loop** | Edit `SKILL.md` → run `compile_soul.py` → run `skill_judge.py` | Write node/python daemon → test schema → register via CLI |
| **Security Gates** | Directly governed by local Socratic / Draft-First prompts | Governed at the Gateway and system-level interface |

---

## Consequences

*   **Custom Skill Complexity**: Adding many skills increases the size of `SOUL_SEED.md`. While the selective loading protocol mitigates this, developers must ensure skill prompts are concise to avoid context bloat.
*   **MCP Setup Overhead**: Adding MCP servers requires proper credential management. Developers must configure OAuth client secrets or environment tokens securely in `~/.hermes/` (as described in EX-26) to prevent leaking secrets.

## Special Case — Acervo as Semantic Control Plane

When the integration is the Exocórtex's own canonical memory, the question is not "skill or MCP instead of files". The correct split is:

- filesystem remains the physical source of truth
- a local semantic core owns mutation rules
- CLI and MCP become two surfaces over the same core

For this case, an MCP is justified only if it exposes **semantic operations** (`prepare`, `commit`, `validate`, `search`, `export`) rather than arbitrary file editing. If the proposed MCP behaves like a generic file editor, the architecture is wrong.
