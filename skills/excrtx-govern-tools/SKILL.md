---
name: excrtx-govern-tools
description: Governance rules for tool usage by Exocórtex.IA. Defines when and how tools should be used, mandatory logging, and classification by type.
version: 1.0.0
category: excrtx
metadata:
  hermes:
    tags: [exocortex, governance, tools, policy]
compiled_rules: |
  Least privilege: use the simplest tool that solves the task.
  Log destructive actions. Sandbox operations by active microverso.
  Never rm -rf, never apt/pip install without explicit approval.
  Prefer read-only tools when gathering information. Batch related tool calls.
  File operations: always verify path exists before writing.
---

# Tool Governance — Exocórtex.IA

> Controls HOW and WHEN the agent uses external tools.

## Tool Classification

| Type | Examples | Policy |
|---|---|---|
| **Internal (local execution)** | file_read, file_write, terminal, hermes-cli | Free use. Log only destructive actions (delete, overwrite). |
| **Internal actions (git/tests)** | git commit (local), git add, git branch, tests, py_compile, lint, patches | Direct execution. No DRAFT. |
| **External actions (git push/deploy)** | git push, deploy scripts, remote artifact publication | **Draft-First mandatory.** |
| **Research** | duckduckgo-search, excrtx-integrate-browser, arxiv | Free use. Log query + result count. |
| **Delivery to executive** | `send_message` to the user's own home channel | Can execute without DRAFT for operational self-delivery, with unambiguous recipient and not representing executive's speech to third parties. |
| **Communication to third parties** | email, calendar, messaging, comments, DM, posts | **Draft-First mandatory.** Never send without post-DRAFT approval. |
| **External creation** | Google Docs, Drive, shared resources | **Draft-First mandatory.** Create as local draft first. |
| **Configuration** | hermes skills install, pip install, mcp add | **Explicit approval mandatory.** Log in session log. Update setup.sh. |

## Usage Rules

### R1: Principle of Least Privilege
Use the simplest tool that solves the problem.
- Need data? → `file_read` before `web_search`
- Need search? → `duckduckgo-search` before `excrtx-integrate-browser`
- Need browser? → `excrtx-integrate-browser` CLI before agent mode

### R2: Mandatory Logging
Every tool call that modifies external state MUST be logged:
```
[TOOL] {timestamp} | {tool_name} | {action} | {target} | {result}
```

### R3: Delivery and Communication Governance
Before using a communication tool, classify the act:

1. **Operational self-delivery**
   - Recipient: the executive themselves
   - Channel: their home channel
   - Nature: operational system delivery, receipt, explicit technical test, or sending output back to the operator
   - Policy: can execute without DRAFT

2. **Communication to third parties**
   - Any recipient that is not unambiguously the executive themselves
   - Any shared channel, group, or public surface
   - Any text representing the executive's speech to third parties
   - Policy: Draft-First mandatory

Draft-First flow:
1. Generate draft locally
2. Present to executive
3. Executive approves → execute
4. Executive rejects → discard or revise

When in doubt about recipient, channel, or social effect, treat as communication to third parties.

### R4: Sandbox by Microverso
When operating within a microverso, tools must respect scope:
- Acervo searches: restrict to active microverso (unless cross-domain is explicit)
- File writes: restrict to active microverso's path
- Exception: meta-management skills (excrtx-memory-manager) can operate cross-microverso

### R5: Failsafe — No Silent Mutation
If a tool fails, the agent MUST:
1. Report the failure to the executive
2. Never attempt self-repair with another tool without informing
3. Suggest alternatives

### R6: Configuration changes with side effects require isolated validation environment
When the task modifies automations that call configuration CLIs (`hermes config set`, setup scripts, provisioners, provider/model routers, wrappers that write state), validate in two layers before declaring done:

1. **Isolated test with fake binary in PATH**
   - Create temporary directory.
   - Inject an executable shim (`hermes`, or other target CLI) in `PATH` to record arguments to file.
   - Run the actual script against this environment and verify the exact calls emitted.
   - Goal: prove mutation intent without touching the main runtime.

2. **Read-only real smoke, when there's an external source**
   - If the logic depends on a public API/remote catalog, execute a smoke against the real source.
   - Prefer mode that generates report/artifact without applying real mutation when that suffices to validate ranking/selection.

3. **Cover fixtures + edge cases surfaced by the smoke**
   - If the smoke reveals a parsing/timing/format bug, freeze it in a unit test immediately.
   - Example bug class: comparison between timezone-naive and timezone-aware datetime.

4. **Only then integrate into setup/provisioning**
   - After proving the script in isolation, plug into `setup.sh`/provisioner and add a textual or structural test confirming the call in the installation flow.

This pattern is mandatory to avoid locking or contaminating the main agent during configuration automation validation.

## Support Files

- `references/config-mutation-isolated-validation.md` — isolated validation pattern for scripts that apply configuration via CLI, with PATH shim, real smoke without mutation, and immediate promotion of discovered bugs to tests.

## Default Whitelist

Skills in the `exocortex-alpha` bundle are pre-authorized.
Any skill outside the bundle requires explicit executive mention.

## Blacklist

| Tool/Action | Reason |
|---|---|
| `rm -rf` on any path | Irreversible destruction |
| Direct email/message send to third parties without post-DRAFT approval | Violates Draft-First |
| System package installation (`apt`, `brew`) | Requires manual approval |
| Access to other tenants' data | Isolation violation |