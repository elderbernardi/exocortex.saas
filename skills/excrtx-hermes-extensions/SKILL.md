---
name: excrtx-hermes-extensions
description: "Deep-dive: Adicionar slash commands (CLI + Gateway) e chamar tools diretamente (bypass LLM) no Hermes Agent."
version: 1.1.0
created_by: agent
platforms: [linux]
metadata:
  intent: class-level
---

# Estendendo o Hermes Agent

Skill de nível avançado para desenvolvedores que precisam modificar o comportamento do Hermes ou adicionar novas capacidades via comandos slash e tools personalizadas.

## Quando Usar

- Você precisa adicionar um novo comando slash (`/meu_comando`) que funcione tanto no CLI quanto no Gateway (Telegram).
- Você quer chamar uma ferramenta (tool) diretamente sem gastar tokens com o LLM.
- Você está depurando o fluxo de execução de comandos no Hermes.

## Anatomia de um Slash Command

Um comando slash no Hermes possui duas partes: o **registro** (para o usuário ver no `/help`) e o **handler** (a lógica executada).

### 1. Registro (CLI e Gateway)

Edite `~/.hermes/hermes-agent/hermes_cli/commands.py`:

```python
from dataclasses import dataclass

@dataclass
class CommandDef:
    name: str
    description: str
    category: str
    args_hint: str = ""

# Adicione na lista COMMAND_REGISTRY:
COMMAND_REGISTRY.append(CommandDef("tool", "Chamar tool diretamente", "Tools & Skills", "<tool_name> [args...]"))
```

### 2. Bypass de Sessão Ativa (Apenas Gateway)

Para que o Gateway não enfileire seu comando enquanto o LLM está ocupado, adicione o nome na `ACTIVE_SESSION_BYPASS_COMMANDS` (também em `commands.py`):

```python
ACTIVE_SESSION_BYPASS_COMMANDS: frozenset[str] = frozenset({
    "help", "tool", ...
})
```

### 3. Handler no CLI

Edite `~/.hermes/hermes-agent/cli.py`:
1.  Procure por `process_command`.
2.  Adicione um `elif canonical == "tool":`.
3.  Crie o método `_handle_tool_command(self, cmd_original)`.

### 4. Handler no Gateway

Edite `~/.hermes/hermes-agent/gateway/run.py` — **DUAS localizações obrigatórias**:

**A) Cadeia principal (~linha 8136):**
```python
# Dentro do bloco if/elif dos comandos canônicos
if canonical == "tool":
    return await self._handle_tool_command(event)
```

**B) _DEDICATED_HANDLERS (~linha 7902) — para funcionar durante execução do agente:**
```python
if _cmd_def_inner.name == "tool":
    return await self._handle_tool_command(event)
```

**C) Em `commands.py`, adicione ao `ACTIVE_SESSION_BYPASS_COMMANDS`:**
```python
ACTIVE_SESSION_BYPASS_COMMANDS: frozenset[str] = frozenset({
    "help", "tool", ...
})
```

Crie o método handler:
```python
async def _handle_tool_command(self, event: MessageEvent) -> str:
    # Sua lógica aqui
    return "resultado"
```

**Atenção com `MessageEvent`:** Não use `event.session_id`. Use `event.source` para acessar plataforma, chat_id e user_id.

## Padrão de Chamada Direta de Tools (Bypass LLM)

Se você quer executar uma tool sem passar pelo loop do LLM (economizando tokens e latência), use a função `handle_function_call` diretamente.

Local: `tools/model_tools.py`

```python
from tools.model_tools import handle_function_call
import json

def execute_tool_directly(tool_name: str, params: dict) -> dict:
    result_json = handle_function_call(
        function_name=tool_name,
        function_args=params,
        task_id=None,
        tool_call_id="direct-call",
        session_id=None,  # Ou session_id se precisar de contexto
        agent_state=None,
        tool=None
    )
    return json.loads(result_json)
```

## Criando uma Tool Personalizada

1.  Crie `tools/minha_tool.py`.
2.  Use `registry.register()` para torná-la visível para o Hermes.
3.  Retorne sempre um JSON string (o Hermes espera um JSON válido).

Exemplo mínimo:

```python
from tools.registry import registry
import json

def minha_tool_handler(param1: str, task_id: str = None) -> str:
    return json.dumps({"result": f"Você enviou {param1}"})

def check_requirements():
    return True  # Sem dependências externas

registry.register(
    name="minha_tool",
    toolset="custom",
    schema={"name": "minha_tool", "parameters": {"type": "object", "properties": {"param1": {"type": "string"}}, "required": ["param1"]}},
    handler=lambda args, **kw: minha_tool_handler(param1=args.get("param1"), task_id=kw.get("task_id")),
    check_fn=check_requirements
)
```

## Pitfalls (Aprendidos em Produção)

1.  **LSP Errors em `gateway/run.py`:** O Pyright pode reclamar de imports ou atributos que só existem em runtime. Ignore se o teste funcionar.
2.  **`event.session_id` inexistente:** Sempre use `event.source` para obter contexto no Gateway.
3.  **`frozenset` mutabilidade:** `ACTIVE_SESSION_BYPASS_COMMANDS` é imutável. Para adicionar itens, recrie o frozenset ou edite o arquivo fonte.
4.  **Reinicialização:** Após mudar `commands.py` ou `cli.py`, reinicie o CLI/Gateway para que as mudanças façam efeito.
5.  **Handler existe mas nunca é chamado (armadilha principal):** O gateway tem DUAS cadeias de dispatch independentes. Escrever o handler e adicionar ao `_DEDICATED_HANDLERS` NÃO basta — você PRECISA adicionar `if canonical == "nome_do_comando":` na **cadeia principal** (bloco `if canonical == "new":` ... `if canonical == "voice":` em `run.py` ~linha 8136+). Sem isso, o comando cai como mensagem normal para o agente. Verifique SEMPRE as duas localizações:
    - **Cadeia principal** (~linha 8136): dispatch para sessões sem agente rodando
    - **`_DEDICATED_HANDLERS`** (~linha 7902): dispatch para sessões COM agente rodando
    Se faltar em qualquer uma das duas, o comando funciona só em metade dos cenários.

## Referências

- `references/harness-layers.md` (Camadas do Hermes: Entrada, Agent, Especialização, Tools)
- `references/direct-tool-call.md` (Implementação do comando /tool)
- `references/slash-command-dispatch-debug.md` (Fluxo de debugging quando slash command não funciona no gateway)
