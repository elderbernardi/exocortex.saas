---
name: excrtx-harness-tooldev
description: Hermes Tool development and extension via direct invocation (no LLM).
  Build, test, and deploy tools.
version: 1.1.0
category: excrtx
platforms:
- linux
author: Exocórtex.IA
license: MIT
tags:
- hermes
- tool-development
- harness
- extension
- python
trigger:
- criar uma tool no hermes
- desenvolver ferramenta hermes
- chamada direta de tool
- implementar /tool
- entender harness do hermes
- como criar uma tool
metadata:
  hermes:
    tags:
    - exocortex
    - harness
    - tooldev
    calibration:
    - feature_id: EX-50
      calibration_prompt: 'Você é capaz de projetar e estender o harness do Hermes
        criando ferramentas diretas.

        - Toda nova ferramenta em Python deve ser criada em ''tools/'' e se registrar
        usando ''registry.register()'' especificando nome, schema JSON de parâmetros,
        handler em lambda e uma função de pré-requisitos ''check_fn()''.

        - Evite o loop do LLM implementando a chamada direta via comando ''/tool <nome>
        [argumentos]''. Os argumentos devem ser parseados como JSON ou no formato
        ''chave=valor'' no interpretador CLI/Gateway.'
      test_prompt: Como faço para registrar uma nova tool chamada 'gerar_uuid' e chamá-la
        diretamente sem passar pelo LLM?
      acceptance_criteria: O agente deve apresentar a chamada do 'registry.register'
        estruturada com schema JSON e descrever o acionamento direto usando o slash
        command '/tool gerar_uuid'.
      remediation_tip: 'Convenção Violada: Ferramentas do Hermes exigir o registro
        explícito usando a instância registry central e podem ser acionadas via /tool
        bypass.'
---
# Hermes Tool Development (Harness Extension)

Skill for creating tools in Hermes Agent and extending behavior via direct call (slash command `/tool`), bypassing the LLM.

## When to Use

- When the Exocórtex needs a new capability that Hermes doesn't have natively.
- When you want to save tokens by calling a tool directly via chat.
- When you need to understand the Hermes Harness layers for extension purposes.

**Don't use for:** Modifying SOUL.md or skills (use `excrtx-hermes-extensions`). Configuring MCP servers (use `excrtx-integrate-oauth`). Building standalone scripts outside Hermes.

## Procedure

### Step 1 — Create the Tool File

Create `tools/<tool_name>_tool.py` in the Hermes installation:

```python
import json
from tools.registry import registry

def check_requirements() -> bool:
    """Return True if all dependencies are available."""
    return True

def my_tool(name: str = "World", task_id: str = None) -> str:
    try:
        result = f"Hello, {name}!"
        return json.dumps({"status": "success", "message": result})
    except Exception as e:
        return json.dumps({"error": str(e)})

registry.register(
    name="my_tool",
    toolset="exocortex_dev",
    schema={
        "name": "my_tool",
        "description": "Example tool",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name to greet"}
            }
        }
    },
    handler=lambda args, **kw: my_tool(**args),
    check_fn=check_requirements
)
```

### Step 2 — Register the Slash Command

In `hermes_cli/commands.py`, add to `COMMAND_REGISTRY`:

```python
CommandDef("tool", "Call a tool directly without LLM", "Tools & Skills",
           args_hint="<tool_name> [arg1=val1] ..."),
```

### Step 3 — Implement the Handler

In `cli.py`, add the handler method:

```python
elif canonical == "tool":
    self._handle_tool_command(cmd_original)
```

The handler must: split the command, parse `key=value` pairs (or JSON if input starts with `{`), convert basic types (int, float, bool), call `handle_function_call(function_name, function_args)`, and print the result.

### Step 4 — Test the Tool

```bash
# Verify tool appears in registry
python3 -c "from tools.registry import registry; print([t for t in registry.list_tools() if 'my_tool' in t])"

# Test via direct call
hermes /tool my_tool name=Elder

# Verify JSON output format
hermes /tool my_tool name=Elder | python3 -m json.tool
```

### Step 5 — Gateway Integration (if needed)

For Telegram/Discord, add dispatch in `gateway/run.py` — search for `resolve_command` or `message.text.startswith('/')`.

## Pitfalls

- **`Optional[T]` for nullable args:** Always use `Optional[str]` for arguments that can be `None` (e.g., `task_id`). Linter errors otherwise.
- **Tool not discovered:** Tools in `tools/*.py` are auto-discovered via import in `model_tools.py`. If the tool doesn't appear, check that `check_fn` returns `True` and the file has no import errors.
- **JSON parse failure:** If args start with `{` but are malformed JSON, the handler will crash. Always wrap `json.loads` in try/except.
- **Gateway dispatch:** `/tool` won't work in Telegram/Discord unless explicitly added to the gateway command dispatcher.

## Verification

- [ ] `python3 -c "from tools.<tool>_tool import *"` imports without errors
- [ ] Tool name appears in `registry.list_tools()` output
- [ ] `/tool <name> arg=value` returns valid JSON with `status: success`
- [ ] `check_fn` returns `True` in the target environment
- [ ] Gateway dispatch works (if applicable)
