---
name: excrtx-hermes-extensions
description: 'Deep-dive: Add slash commands (CLI + Gateway) and call tools directly
  (bypass LLM) in Hermes Agent.'
version: 1.1.0
category: excrtx
created_by: agent
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - hermes
    - extensions
    related_skills:
    - excrtx-harness-hermesops
    - excrtx-harness-tooldev
    - excrtx-govern-tools
    calibration:
    - feature_id: EX-51
      calibration_prompt: 'Ao estender comandos slash no Hermes Agent, você deve instruir
        ou aplicar alterações em três pontos estratégicos do código do runtime:

        1. Registro em ''hermes_cli/commands.py'' (dentro da lista ''COMMAND_REGISTRY''
        e no frozenset ''ACTIVE_SESSION_BYPASS_COMMANDS'').

        2. Handler do CLI em ''cli.py'' (método ''process_command'').

        3. Handlers do Gateway em ''gateway/run.py'' (em ambas as localizações: na
        cadeia de dispatch principal para novas sessões e na lista ''_DEDICATED_HANDLERS''
        para sessões ativas).

        Se houver falha de execução de um comando no Telegram/Discord, verifique se
        o dispatch não foi omitido em um dos dois locais de ''run.py''.'
      test_prompt: Criei um slash command chamado '/status_servidor' que funciona
        perfeitamente no terminal, mas no Telegram ele é tratado como uma mensagem
        comum enviada ao agente. Qual é o problema e como corrijo?
      acceptance_criteria: O agente deve identificar a falha no dispatch de gateway
        e indicar a alteração em ambas as localizações em 'gateway/run.py' (cadeia
        principal de rotas e no '_DEDICATED_HANDLERS').
      remediation_tip: 'Erro de Harness: Novos comandos slash exigem o dispatch na
        cadeia principal E no _DEDICATED_HANDLERS em gateway/run.py.'
  intent: class-level
---
# Extending the Hermes Agent

Advanced-level skill for developers who need to modify Hermes behavior or add new capabilities via slash commands and custom tools.

## When to Use

- You need to add a new slash command (`/my_command`) that works in both CLI and Gateway (Telegram).
- You want to call a tool directly without spending tokens on the LLM.
- You are debugging the command execution flow in Hermes.

**Don't use for:**
- General tool development (creating MCP tools) → use `excrtx-harness-tooldev`
- Hermes operational workflows (starting/stopping, delegation) → use `excrtx-harness-hermesops`
- Tool governance and classification → use `excrtx-govern-tools`
- Modifying agent behavior at the prompt/persona level → use `excrtx-behavior-canvas`

## Procedure

### 1. Identify Extension Type

Determine what you're building:

| Type | When | Key files |
|---|---|---|
| **Slash command** | New `/my_command` for CLI + Gateway | `commands.py`, `cli.py`, `run.py` |
| **Direct tool call** | Execute tool without LLM tokens | `tools/model_tools.py` |
| **Custom tool** | New tool visible to Hermes | `tools/my_tool.py` + `registry` |

### 2. Register the Command

Edit `~/.hermes/hermes-agent/hermes_cli/commands.py`:

```python
# Add to COMMAND_REGISTRY list:
COMMAND_REGISTRY.append(
    CommandDef("my_command", "Description here", "Category", "<args_hint>")
)

# Add to ACTIVE_SESSION_BYPASS_COMMANDS frozenset (for Gateway compatibility):
ACTIVE_SESSION_BYPASS_COMMANDS: frozenset[str] = frozenset({
    "help", "my_command", ...
})
```

### 3. Add CLI Handler

Edit `~/.hermes/hermes-agent/cli.py`:

1. Find the `process_command` method
2. Add `elif canonical == "my_command":` branch
3. Create `_handle_my_command(self, cmd_original)` method

### 4. Add Gateway Handler (TWO Mandatory Locations)

Edit `~/.hermes/hermes-agent/gateway/run.py` — **both locations are required**:

**A) Main dispatch chain (~line 8136) — for sessions WITHOUT a running agent:**
```python
if canonical == "my_command":
    return await self._handle_my_command(event)
```

**B) `_DEDICATED_HANDLERS` (~line 7902) — for sessions WITH a running agent:**
```python
if _cmd_def_inner.name == "my_command":
    return await self._handle_my_command(event)
```

Create the handler method:
```python
async def _handle_my_command(self, event: MessageEvent) -> str:
    # Use event.source (NOT event.session_id) for platform/chat/user info
    return "result"
```

### 5. For Direct Tool Calls (LLM Bypass)

Import `handle_function_call` from `tools/model_tools.py`:

```python
from tools.model_tools import handle_function_call
import json

result_json = handle_function_call(
    function_name="tool_name",
    function_args={"param": "value"},
    task_id=None,
    tool_call_id="direct-call",
    session_id=None,
    agent_state=None,
    tool=None
)
result = json.loads(result_json)
```

### 6. For Custom Tools

Create `tools/my_tool.py`:

```python
from tools.registry import registry
import json

def my_tool_handler(param1: str, task_id: str = None) -> str:
    return json.dumps({"result": f"You sent {param1}"})

registry.register(
    name="my_tool",
    toolset="custom",
    schema={"name": "my_tool", "parameters": {"type": "object", "properties": {"param1": {"type": "string"}}, "required": ["param1"]}},
    handler=lambda args, **kw: my_tool_handler(param1=args.get("param1"), task_id=kw.get("task_id")),
    check_fn=lambda: True
)
```

### 7. Restart and Test

After any changes to `commands.py`, `cli.py`, or `run.py`:

1. Restart CLI/Gateway for changes to take effect
2. Test in CLI: `hermes> /my_command` — verify expected output
3. Test in Gateway (Telegram): verify command is NOT treated as normal message
4. Test during active agent session: verify command works via `_DEDICATED_HANDLERS`

## Pitfalls

1. **Handler exists but is never called (main trap):** The gateway has TWO independent dispatch chains. Writing the handler and adding it to `_DEDICATED_HANDLERS` is NOT enough — you MUST add `if canonical == "command_name":` in the **main chain** (~line 8136). Without this, the command falls through as a normal message. Always verify BOTH locations:
   - **Main chain** (~line 8136): for sessions without a running agent
   - **`_DEDICATED_HANDLERS`** (~line 7902): for sessions with a running agent
2. **`event.session_id` doesn't exist:** Always use `event.source` to get platform, chat_id, and user_id in the Gateway handler.
3. **`frozenset` immutability:** `ACTIVE_SESSION_BYPASS_COMMANDS` is immutable. To add items, edit the source frozenset definition — do not try to `.add()`.
4. **Restart required:** Changes to `commands.py` or `cli.py` require CLI/Gateway restart.
5. **LSP Errors in `gateway/run.py`:** Pyright may complain about imports or attributes that only exist at runtime. Ignore if the functional test passes.
6. **Tool must return JSON string:** `handle_function_call` expects the handler to return a JSON string, not a dict or plain text.

## Verification

- [ ] Command appears in `/help` output (`COMMAND_REGISTRY` registration confirmed)
- [ ] Run `/my_command` in CLI: returns expected output (not "unknown command")
- [ ] Run `/my_command` in Gateway (Telegram): not treated as normal message to agent
- [ ] Run `/my_command` during active agent session: dispatched via `_DEDICATED_HANDLERS`
- [ ] `ACTIVE_SESSION_BYPASS_COMMANDS` includes the command name
- [ ] `event.source` used instead of `event.session_id` in Gateway handler
- [ ] Tool returns valid JSON string (verified with `json.loads()`)
- [ ] Both dispatch locations in `run.py` verified: main chain AND `_DEDICATED_HANDLERS`

## References

- `references/harness-layers.md` (Hermes layers: Input, Agent, Specialization, Tools)
- `references/direct-tool-call.md` (/tool command implementation)
- `references/slash-command-dispatch-debug.md` (Debugging flow when slash command doesn't work in gateway)
