# Hindsight Single-Container Setup (Exocórtex Default)

Goal: simple, persistent, and reversible local setup for a single Hermes per machine.

## Default Topology

- 1 Hindsight container (`exocortex-hindsight`)
- Directory: `~/.hermes/hindsight-local`
- Persistence: `~/.hermes/hindsight-local/data`
- Local API: `localhost:8888`
- Local UI: `localhost:9999`

## Mandatory Setup Order

1. Provision local Hindsight Docker.
2. Prepare `~/.hermes/hindsight/config.json` from template.
3. Sync `llm_model` and `llm_base_url` with `~/.hermes/config.yaml`.
4. Only then activate `memory.provider=hindsight`.
5. After activation, disable simple local memory:
   - `memory.memory_enabled=false`
   - `memory.user_profile_enabled=false`

## Memory Scope in This Pattern

- One Hindsight per Hermes instance.
- Profiles `exec` and `evol` share the same bank.
- Recommended `bank_id_template`: `exocortex`.

## Destructive Reset (guardrail)

Delete local memory only with double confirmation:

- `EXOCORTEX_HINDSIGHT_RESET_DATA=1`
- `EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY`

Without both flags, preserve data.

## Minimum Validation

1. `hermes memory status` without availability error.
2. New session after surface restart (CLI/Gateway).
3. Useful recall without excessive noise.

## Compatibility Note

`local_embedded` describes local storage. There may still be a plugin authentication requirement to become `available`.
