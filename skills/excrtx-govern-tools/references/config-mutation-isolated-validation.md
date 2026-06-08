# Validação isolada para mutações de configuração via CLI

Use este padrão quando a automação vai chamar comandos como `hermes config set`, setup scripts, provisionadores ou roteadores que mudam provider/model/defaults.

## Objetivo
Validar lógica real sem tocar no runtime principal nem travar o agente que está conduzindo a sessão.

## Padrão recomendado

### 1. Teste unitário com fixtures locais
- Congele payloads mínimos das fontes externas em JSON local.
- Verifique:
  - filtro de elegibilidade
  - ordenação/ranking
  - fallback chain
  - exclusão de itens não elegíveis

### 2. Apply isolado com shim no PATH
Monte um diretório temporário assim:

```bash
$tmp/bin/hermes
$tmp/hermes-home
$tmp/report.json
$tmp/hermes-calls.log
```

Shim mínimo:

```bash
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$HERMES_CALLS_LOG"
exit 0
```

Depois:
- exporte `PATH="$tmp/bin:$PATH"`
- exporte `HERMES_HOME="$tmp/hermes-home"`
- execute o script real com `--apply`
- verifique o conteúdo de `hermes-calls.log`

Isso prova a mutação pretendida sem alterar a instalação real.

## Sequência de verificação que funcionou bem
1. Criar teste do script isolado.
2. Rodar em venv temporária separada do ambiente principal.
3. Fazer smoke com dados reais da fonte pública.
4. Se o smoke revelar bug, congelar em teste imediatamente.
5. Só depois integrar a chamada no `setup.sh`.
6. Rodar `bash -n setup.sh` e um teste textual/estrutural confirmando a integração.

## Pitfall promovido desta sessão

### Datetime naive vs aware
Quando a fonte remota expõe `expiration_date`, tratar timestamps sem timezone como UTC explícito antes de comparar com `datetime.now(timezone.utc)`.

Padrão seguro:

```python
expiration_dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
if expiration_dt.tzinfo is None:
    expiration_dt = expiration_dt.replace(tzinfo=timezone.utc)
```

Sem isso, o smoke real pode falhar com:
- `can't compare offset-naive and offset-aware datetimes`

## Quando aplicar este padrão
- roteador de modelos/providers
- provisionadores que executam `config set`
- bootstrap/setup scripts
- wrappers que escolhem defaults e persistem config
- migrações locais de runtime Hermes/Exocórtex

## Sinal de pronto
Só declarar pronto quando houver as três evidências:
1. testes de fixture passando
2. apply isolado registrando as chamadas exatas esperadas
3. smoke real confirmando que a lógica continua válida com dados atuais
