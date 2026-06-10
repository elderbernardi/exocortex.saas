---
name: excrtx-hermes-extensions
description: "Deep-dive: Add slash commands (CLI + Gateway) and call tools directly (bypass LLM) in Hermes Agent."
version: 1.1.0
created_by: agent
platforms: [linux]
metadata:
  intent: class-level
---

# Extending the Hermes Agent

Advanced-level skill for developers who need to modify Hermes behavior or add new capabilities via slash commands and custom tools.

## When to Use

- You need to add a new slash command (`/my_command`) that works in both CLI and Gateway (Telegram).
- You want to call a tool directly without spending tokens on the LLM.
- You are debugging the command execution flow in Hermes.

## Anatomy of a Slash Command

A Hermes slash command has two parts: the **registration** (for the user to see in `/help`) and the **handler** (the executed logic).

### 1. Registration (CLI and Gateway)

Edit `~/.hermes/hermes-agent/hermes_cli/commands.py`:

```python
from dataclasses import dataclass

@dataclass
class CommandDef:
    name: str
    description: str
    category: str
    args_hint: str = ""

# Add to COMMAND_REGISTRY list:
COMMAND_REGISTRY.append(CommandDef("tool", "Call tool directly", "Tools & Skills", "<tool_name> [args...]"))
```

### 2. Active Session Bypass (Gateway only)

To prevent the Gateway from queuing your command while the LLM is busy, add the name to `ACTIVE_SESSION_BYPASS_COMMANDS` (also in `commands.py`):

```python
ACTIVE_SESSION_BYPASS_COMMANDS: frozenset[str] = frozenset({
    "help", "tool", ...
})
```

### 3. CLI Handler

Edit `~/.hermes/hermes-agent/cli.py`:
1. Find `process_command`.
2. Add an `elif canonical == "tool":`.
3. Create the method `_handle_tool_command(self, cmd_original)`.

### 4. Gateway Handler

Edit `~/.hermes/hermes-agent/gateway/run.py` — **TWO mandatory locations**:

**A) Main chain (~line 8136):**
```python
# Inside the if/elif block for canonical commands
if canonical == "tool":
    return await self._handle_tool_command(event)
```

**B) _DEDICATED_HANDLERS (~line 7902) — to work during agent execution:**
```python
if _cmd_def_inner.name == "tool":
    return await self._handle_tool_command(event)
```

**C) In `commands.py`, add to `ACTIVE_SESSION_BYPASS_COMMANDS`:**
```python
ACTIVE_SESSION_BYPASS_COMMANDS: frozenset[str] = frozenset({
    "help", "tool", ...
})
```

Create the handler method:
```python
async def _handle_tool_command(self, event: MessageEvent) -> str:
    # Your logic here
    return "result"
```

**Warning about `MessageEvent`:** Do not use `event.session_id`. Use `event.source` to access platform, chat_id, and user_id.

## Direct Tool Call Pattern (LLM Bypass)

If you want to execute a tool without going through the LLM loop (saving tokens and latency), use `handle_function_call` directly.

Location: `tools/model_tools.py`

```python
from tools.model_tools import handle_function_call
import json

def execute_tool_directly(tool_name: str, params: dict) -> dict:
    result_json = handle_function_call(
        function_name=tool_name,
        function_args=params,
        task_id=None,
        tool_call_id="direct-call",
        session_id=None,  # Or session_id if context is needed
        agent_state=None,
        tool=None
    )
    return json.loads(result_json)
```

## Creating a Custom Tool

1. Create `tools/my_tool.py`.
2. Use `registry.register()` to make it visible to Hermes.
3. Always return a JSON string (Hermes expects valid JSON).

Minimal example:

```python
from tools.registry import registry
import json

def my_tool_handler(param1: str, task_id: str = None) -> str:
    return json.dumps({"result": f"You sent {param1}"})

def check_requirements():
    return True  # No external dependencies

registry.register(
    name="my_tool",
    toolset="custom",
    schema={"name": "my_tool", "parameters": {"type": "object", "properties": {"param1": {"type": "string"}}, "required": ["param1"]}},
    handler=lambda args, **kw: my_tool_handler(param1=args.get("param1"), task_id=kw.get("task_id")),
    check_fn=check_requirements
)
```

## Pitfalls (Learned in Production)

1. **LSP Errors in `gateway/run.py`:** Pyright may complain about imports or attributes that only exist at runtime. Ignore if the test passes.
2. **`event.session_id` doesn't exist:** Always use `event.source` to get context in the Gateway.
3. **`frozenset` immutability:** `ACTIVE_SESSION_BYPASS_COMMANDS` is immutable. To add items, recreate the frozenset or edit the source file.
4. **Restart required:** After changing `commands.py` or `cli.py`, restart CLI/Gateway for changes to take effect.
5. **Handler exists but is never called (main trap):** The gateway has TWO independent dispatch chains. Writing the handler and adding it to `_DEDICATED_HANDLERS` is NOT enough — you MUST add `if canonical == "command_name":` in the **main chain** (the `if canonical == "new":` ... `if canonical == "voice":` block in `run.py` ~line 8136+). Without this, the command falls through as a normal message to the agent. ALWAYS verify both locations:
    - **Main chain** (~line 8136): dispatch for sessions without a running agent
    - **`_DEDICATED_HANDLERS`** (~line 7902): dispatch for sessions WITH a running agent
    If either is missing, the command only works in half the scenarios.

## References

- `references/harness-layers.md` (Hermes layers: Input, Agent, Specialization, Tools)
- `references/direct-tool-call.md` (/tool command implementation)
- `references/slash-command-dispatch-debug.md` (Debugging flow when slash command doesn't work in gateway)
