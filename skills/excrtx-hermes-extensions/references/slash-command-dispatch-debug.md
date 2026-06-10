# Debug: Slash Command Not Working on Gateway (Telegram/Discord)

## Decision Flow

When a slash command is registered but doesn't work on the gateway:

```
/command typed in Telegram
    │
    ├─ 1. Is it in COMMAND_REGISTRY? (commands.py)
    │     └─ NO → Add CommandDef
    │
    ├─ 2. cli_only=True?
    │     └─ YES → Remove or add gateway_config_gate
    │
    ├─ 3. Is it in GATEWAY_KNOWN_COMMANDS?
    │     └─ NO → Check if cli_only blocks it
    │
    ├─ 4. Does handler exist on gateway? (_handle_*_command)
    │     └─ NO → Create async method in Gateway class
    │
    ├─ 5. ⚡ MAIN CHAIN (run.py ~line 8136+)
    │     │   Block: if canonical == "new": ... if canonical == "voice":
    │     └─ NO → Add if canonical == "my_cmd": return await self._handle_...
    │               WITHOUT THIS THE COMMAND FALLS AS NORMAL MESSAGE TO AGENT
    │
    └─ 6. ⚡ ACTIVE_SESSION_BYPASS_COMMANDS (commands.py)
          │   To work WHILE the agent is running
          └─ NO → Add to frozenset + handler in _DEDICATED_HANDLERS block (~7902)
```

## The 3 Dispatch Points on Gateway

### A) Main Chain (~line 8136-8310)
```python
# gateway/run.py — run_agent_message() or similar
if canonical == "new":
    ...
if canonical == "help":
    ...
if canonical == "my_command":          # ← ADD HERE
    return await self._handle_my_command(event)
if canonical == "voice":
    ...
```
**When it fires:** Session without active agent (user typed command before sending a message).

### B) _DEDICATED_HANDLERS (~line 7900-7912)
```python
# Inside the "agent is running" block
if _cmd_def_inner and _cmd_def_inner.name in _DEDICATED_HANDLERS:
    if _cmd_def_inner.name == "my_command":     # ← ADD HERE
        return await self._handle_my_command(event)
```
**When it fires:** Session WITH active agent (LLM is processing).

### C) ACTIVE_SESSION_BYPASS_COMMANDS (commands.py)
```python
ACTIVE_SESSION_BYPASS_COMMANDS: frozenset[str] = frozenset({
    "help", "commands", "tool", "my_command",  # ← ADD HERE
    ...
})
```
**What it controls:** Whether the command is recognized by block B above.

## Real Case: /tool

The `/tool` command was:
- ✅ In COMMAND_REGISTRY
- ✅ In GATEWAY_KNOWN_COMMANDS
- ✅ Handler implemented (`_handle_tool_command`)
- ✅ In _DEDICATED_HANDLERS block
- ❌ **MISSING** from main chain (A)

Result: `/tool` worked when the agent was running, but fell as normal text when it wasn't.

## Quick Checklist

Before concluding that "the command is ready," verify:

- [ ] `COMMAND_REGISTRY` — has `CommandDef`
- [ ] `cli.py:process_command()` — has `elif canonical == "X":`
- [ ] `cli.py` — has `_handle_X_command()` method
- [ ] `gateway/run.py` main chain (~8136) — has `if canonical == "X":`
- [ ] `gateway/run.py` — has `async def _handle_X_command()` method
- [ ] `commands.py:ACTIVE_SESSION_BYPASS_COMMANDS` — has "X" (if needs to work during execution)
- [ ] `gateway/run.py` _DEDICATED_HANDLERS (~7902) — has dispatch for "X"
- [ ] Restart gateway after changes
