# Operational Memory Provider Integration Pattern

Use this reference when adding an agent-memory provider such as Hindsight, Honcho, Holographic, Mem0, or similar to an Exocórtex/Hermes installation.

## Core rule

Operational memory providers are auxiliary. They may observe, retain, recall, and synthesize context, but they do not become the canonical memory system.

Authority chain:

```text
SOUL / system rules
→ Acervo contracts with operational_mode: blocking
→ loaded skills and canonical workflows
→ built-in memory for compact invariants
→ Acervo Cognitivo v2 for canonical knowledge/decisions/processes
→ Session Search for literal episode recall
→ operational memory provider observations
```

If provider memory conflicts with higher authority, provider memory loses.

## Required Acervo artifacts

For a mature provider adoption, create or update the setup microverso, normally `micro/hermes-setup`:

1. `contracts/<provider>-operational-memory-contract.md`
   - `nature: instrucoes`
   - `kind: contract`
   - `operational_mode: blocking`
   - Define precedence, allowed/prohibited role, retention policy, recall policy, promotion policy, and reversibility.

2. `workflows/<provider>-operational-memory.md`
   - `nature: processos`
   - `kind: workflow`
   - Installation, guarded activation, config editing, validation, noise tuning, audit schedule, and deactivation.

3. `templates/<provider>-config.<mode>.json`
   - Copyable config templates with conservative defaults.
   - Use explicit placeholders such as `CHANGE_ME` for values that must be chosen per install.

4. `workflows/replicable-exocortex-setup.md`
   - Add the provider as an optional setup step, not as a hard requirement for the Exocórtex to boot.

5. `index.md` and `log.md`
   - Index every new artifact.
   - Log authority, files changed, setup impact, and whether activation is optional or default.

## Setup script pattern

When updating `~/.hermes/setup.sh`, keep the integration idempotent and guarded:

- Do not activate the provider by default.
- Use an explicit env flag, e.g. `EXOCORTEX_ENABLE_<PROVIDER>=1`.
- Copy templates only if config does not already exist.
- Preserve existing config.
- If config contains `CHANGE_ME`, do not set `memory.provider` yet.
- Print a clear next step instead of failing the whole setup.
- Keep the Exocórtex usable with built-in memory + Session Search + Acervo.

Example guard:

```bash
if [ -f "$target" ] && grep -q "CHANGE_ME" "$target"; then
  echo "Edit CHANGE_ME in $target before activating provider"
  echo "Provider not changed to avoid broken config"
  return 0
fi
```

## Hindsight conservative defaults

For Hindsight, start with low-noise settings:

```json
{
  "memory_mode": "hybrid",
  "auto_recall": true,
  "auto_retain": true,
  "retain_async": true,
  "retain_every_n_turns": 2,
  "recall_budget": "low",
  "recall_prefetch_method": "recall",
  "recall_types": "observation",
  "recall_max_tokens": 1200,
  "recall_max_input_chars": 800
}
```

`local_embedded` means the provider service/bank runs locally; the backend LLM can be local, self-hosted, or external API. Document this distinction explicitly to avoid implying that a full model must run on the same host.

## Audit cadence

After 7 days:

- Did recall reduce repeated questions?
- Did it add noise?
- Did latency change?
- Did it confuse observations with canonical decisions?
- Did any observation deserve promotion to Acervo or skill?

After 14 days:

- Keep as default, narrow to specific profiles, switch to tools-only, reduce auto-retain, or disable.

## Promotion funnel

```text
provider observation
→ validate against current context
→ candidate
→ Acervo decision/contract/workflow/reflection
→ skill if procedural
→ built-in memory if compact invariant
```

Never promote provider memory automatically to canonical authority.