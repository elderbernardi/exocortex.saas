---
name: excrtx-harness-tooldev
description: "Desenvolvimento de Tools Hermes e extensão via chamada direta (sem LLM)."
version: 1.0.0
author: Exocórtex.IA
license: MIT
tags: [hermes, tool-development, harness, extension, python]
trigger:
  - "criar uma tool no hermes"
  - "desenvolver ferramenta hermes"
  - "chamada direta de tool"
  - "implementar /tool"
  - "entender harness do hermes"
  - "como criar uma tool"
---

# Hermes Tool Development (Harness Extension)

Skill de nível de classe para criar ferramentas no Hermes Agent e estender o comportamento via chamada direta (slash command `/tool`), sem passar pelo LLM.

## Quando Usar

- Quando o Exocórtex precisa de uma nova capacidade que o Hermes não tem nativamente.
- Quando se quer economizar tokens chamando uma tool diretamente via chat.
- Quando se quer entender as camadas do Harness do Hermes para propósitos de extensão.

## Arquitetura (Resumo)

1. **Entrada:** Gateway/CLI (`commands.py`, `cli.py`).
2. **Agent Loop:** `run_agent.py` (classe `AIAgent`).
3. **Especialização:** `SOUL.md`, Skills, Memória.
4. **Ferramentas:** `tools/registry.py`, `model_tools.py`.

## Criando uma Tool (Hello World)

### 1. Arquivo da Tool (`tools/hello_world_tool.py`)

```python
import json
from tools.registry import registry

def check_requirements() -> bool:
    return True

def hello_world_tool(name: str = "World", uppercase: bool = False, task_id: str = None) -> str:
    try:
        greeting = f"Olá, {name}! Bem-vindo ao Exocórtex."
        if uppercase:
            greeting = greeting.upper()
        return json.dumps({"status": "sucesso", "message": greeting})
    except Exception as e:
        return json.dumps({"error": str(e)})

# Registro no Registry
registry.register(
    name="hello_world",
    toolset="exocortex_dev",
    schema={"name": "hello_world", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: hello_world_tool(...),
    check_fn=check_requirements
)
```

### 2. Passagem de Parâmetros

- **Via LLM:** O modelo envia JSON `{function_name, function_args}`.
- **Via Código:** `handle_function_call(function_name, function_args)` (em `model_tools.py`).
- **Parse de argumentos:** Aceita JSON puro ou formato `key=value`.

## Implementando Chamada Direta (`/tool`)

### 1. Registro (`hermes_cli/commands.py`)

Adicione ao `COMMAND_REGISTRY`:
```python
CommandDef("tool", "Call a tool directly without LLM", "Tools & Skills",
           args_hint="<tool_name> [arg1=val1] ..."),
```

### 2. Handler (`cli.py`)

No método `process_command`, adicione:
```python
elif canonical == "tool":
    self._handle_tool_command(cmd_original)
```

### 3. Lógica de Parse (`cli.py`)

Crie o método `_handle_tool_command`:
- Fazer split de `command`.
- Se 1 arg + inicia com `{` ou `[`, tentar `json.loads`.
- Senão, iterar `parts[2:]` fazendo split em `=`.
- Converter tipos básicos (int, float, bool).
- Chamar `handle_function_call(function_name, function_args)`.
- Imprimir resultado (formatado ou raw).

## Pitfalls

- **Linter Errors:** Sempre use `Optional[T]` para argumentos que podem ser `None` (ex: `task_id: Optional[str]`).
- **Tool Discovery:** Ferramentas em `tools/*.py` são auto-descobertas via `import` em `model_tools.py`. Se a tool não aparecer, verifique o `check_fn`.
- **Gateway:** Para usar `/tool` no Telegram/Discord, o dispatch deve ser adicionado em `gateway/run.py` (procurar por `resolve_command` ou `message.text.startswith('/')`).

## Referencias

- `references/hermes-tool-anatomy.md`: Anatomia de uma Tool Hermes.
- `references/direct-call-pattern.md`: Padrão de chamada direta sem LLM.
- Skill `hermes-agent` (documentação oficial, protegida).
