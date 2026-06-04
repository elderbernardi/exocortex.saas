# Hindsight single-container setup (Exocórtex default)

Objetivo: setup local simples, persistente e reversível para um único Hermes por máquina.

## Topologia padrão

- 1 container Hindsight (`exocortex-hindsight`)
- diretório: `~/.hermes/hindsight-local`
- persistência: `~/.hermes/hindsight-local/data`
- API local: `localhost:8888`
- UI local: `localhost:9999`

## Ordem obrigatória no setup

1. Provisionar Docker local do Hindsight.
2. Preparar `~/.hermes/hindsight/config.json` a partir de template.
3. Sincronizar `llm_model` e `llm_base_url` com `~/.hermes/config.yaml`.
4. Só então ativar `memory.provider=hindsight`.
5. Após ativação, desativar memória simples local:
   - `memory.memory_enabled=false`
   - `memory.user_profile_enabled=false`

## Escopo de memória neste padrão

- Um Hindsight por instância Hermes.
- Perfis `exec` e `evol` compartilham o mesmo bank.
- `bank_id_template` recomendado: `exocortex`.

## Reset destrutivo (guardrail)

Excluir memória local apenas com confirmação dupla:

- `EXOCORTEX_HINDSIGHT_RESET_DATA=1`
- `EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY`

Sem as duas flags, preservar dados.

## Validação mínima

1. `hermes memory status` sem erro de disponibilidade.
2. Nova sessão após restart da superfície (CLI/Gateway).
3. Recall útil sem ruído excessivo.

## Observação de compatibilidade

`local_embedded` descreve storage local. Pode ainda existir exigência de autenticação do plugin para ficar `available`.
