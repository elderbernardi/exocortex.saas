# Debug: Slash Command não funciona no Gateway (Telegram/Discord)

## Fluxo de Decisão

Quando um comando slash está registrado mas não funciona no gateway:

```
/comando digitado no Telegram
    │
    ├─ 1. Está em COMMAND_REGISTRY? (commands.py)
    │     └─ NÃO → Adicionar CommandDef
    │
    ├─ 2. cli_only=True? 
    │     └─ SIM → Remover ou adicionar gateway_config_gate
    │
    ├─ 3. Está em GATEWAY_KNOWN_COMMANDS?
    │     └─ NÃO → Verificar se cli_only bloqueia
    │
    ├─ 4. Handler existe no gateway? (_handle_*_command)
    │     └─ NÃO → Criar método async na classe Gateway
    │
    ├─ 5. ⚡ CADEIA PRINCIPAL (run.py ~linha 8136+)
    │     │   Bloco: if canonical == "new": ... if canonical == "voice":
    │     └─ NÃO → Adicionar if canonical == "meu_cmd": return await self._handle_...
    │               SEM ISSO O COMANDO CAI COMO MENSAGEM NORMAL PRO AGENTE
    │
    └─ 6. ⚡ ACTIVE_SESSION_BYPASS_COMMANDS (commands.py)
          │   Para funcionar ENQUANTO o agente está rodando
          └─ NÃO → Adicionar ao frozenset + handler no bloco _DEDICATED_HANDLERS (~7902)
```

## Os 3 Pontos de Dispatch no Gateway

### A) Cadeia Principal (~linha 8136-8310)
```python
# gateway/run.py — run_agent_message() ou similar
if canonical == "new":
    ...
if canonical == "help":
    ...
if canonical == "meu_comando":          # ← ADICIONAR AQUI
    return await self._handle_meu_comando(event)
if canonical == "voice":
    ...
```
**Quando dispara:** sessão sem agente ativo (usuário digitou comando antes de enviar mensagem).

### B) _DEDICATED_HANDLERS (~linha 7900-7912)
```python
# Dentro do bloco "agent is running"
if _cmd_def_inner and _cmd_def_inner.name in _DEDICATED_HANDLERS:
    if _cmd_def_inner.name == "meu_comando":     # ← ADICIONAR AQUI
        return await self._handle_meu_comando(event)
```
**Quando dispara:** sessão COM agente ativo (LLM está processando).

### C) ACTIVE_SESSION_BYPASS_COMMANDS (commands.py)
```python
ACTIVE_SESSION_BYPASS_COMMANDS: frozenset[str] = frozenset({
    "help", "commands", "tool", "meu_comando",  # ← ADICIONAR AQUI
    ...
})
```
**O que controla:** se o comando é reconhecido pelo bloco B acima.

## Caso Real: /tool

O comando `/tool` estava:
- ✅ No COMMAND_REGISTRY
- ✅ No GATEWAY_KNOWN_COMMANDS  
- ✅ Handler implementado (`_handle_tool_command`)
- ✅ No bloco _DEDICATED_HANDLERS
- ❌ **FALTAVA** na cadeia principal (A)

Resultado: `/tool` funcionava quando o agente estava rodando, mas caía como texto normal quando não estava.

## Checklist Rápido

Antes de concluir que "o comando está pronto", verifique:

- [ ] `COMMAND_REGISTRY` — tem `CommandDef`
- [ ] `cli.py:process_command()` — tem `elif canonical == "X":`
- [ ] `cli.py` — tem `_handle_X_command()` method
- [ ] `gateway/run.py` cadeia principal (~8136) — tem `if canonical == "X":`
- [ ] `gateway/run.py` — tem `async def _handle_X_command()` method
- [ ] `commands.py:ACTIVE_SESSION_BYPASS_COMMANDS` — tem "X" (se precisa funcionar durante execução)
- [ ] `gateway/run.py` _DEDICATED_HANDLERS (~7902) — tem dispatch para "X"
- [ ] Reiniciar gateway após mudanças
