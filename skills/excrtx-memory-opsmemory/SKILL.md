---
name: excrtx-memory-opsmemory
description: Govern, deploy, and audit operational memory providers for the agent in Exocórtex/Hermes without replacing the Acervo Cognitivo.
version: 1.0.0
category: excrtx
platforms: [linux]
author: Exocórtex
metadata:
  hermes:
    tags: [exocortex, hermes, memory, hindsight, operational-memory, acervo, setup, governance]
    related_skills: [excrtx-memory-manager, hermes-agent]
---

# Exocórtex Operational Memory

Use this skill when the user asks to evaluate, deploy, configure, compare, or audit operational memory providers for the agent in Hermes/Exocórtex, such as Hindsight, Holographic, Honcho, Mem0, Supermemory, RetainDB, ByteRover, or OpenViking.

## Principle

Operational memory aids agent operation. It does not replace the Exocórtex primary harness.

```text
Provider observes and retrieves.
Exocórtex interprets.
Acervo canonizes.
Skills proceduralize.
Built-in memory stores invariants.
Session Search preserves literal history.
```

## Precedence

In case of conflict, apply this order:

1. SOUL / system instructions.
2. Acervo contracts with `operational_mode: blocking`.
3. Loaded skills and canonical workflows.
4. Built-in memory for compact invariants.
5. Acervo Cognitivo v2 for canonical knowledge, decisions, and processes.
6. Session Search for literal history.
7. Operational memory provider for semantic observations.

Never treat a provider-retrieved observation as a canonical decision.

## Suitability Assessment

When comparing providers, evaluate:

- Plugin maturity;
- Local, self-hosted, or cloud mode;
- Auto-recall and auto-retain;
- Ability to consolidate observations;
- Context overload risk;
- Auditability;
- Reversibility;
- Acervo adherence;
- Cost/latency;
- Risk of creating a parallel source of truth.

## Adoption Pattern

For mature providers in production:

1. Create contract in the setup microverso.
2. Create operational workflow.
3. Create configuration templates.
4. Update replicable setup workflow.
5. Update `index.md` and `log.md` of the microverso.
6. Update `~/.hermes/setup.sh` with explicit, idempotent activation.
7. Validate without activating by default.
8. Activate only after configuring credentials/backend.
9. Audit at 7 and 14 days.

## `setup.sh` Pattern

Operational memory integrations must be optional and guarded by flag:

```bash
EXOCORTEX_ENABLE_<PROVIDER>=1 bash ~/.hermes/setup.sh
```

The script must:

- Preserve existing configs;
- Copy template only when config doesn't exist;
- Not overwrite credentials;
- Not activate provider if config contains `CHANGE_ME`;
- Not fail the entire setup if the provider isn't ready;
- Make the next step clear.

## Hindsight

### Validated Operational Pattern (Exocórtex)

When the priority is setup simplicity with local persistence:

1. Run Hindsight in a dedicated Docker container (single-container), separate from the Hermes process.
2. Maintain Hindsight's own directory (e.g., `~/.hermes/hindsight-local/`) with:
   - `docker-compose.yml`
   - `.env`
   - Persistent `data/`.
3. Execute this step **before** memory provider activation/configuration in setup.
4. Treat memory reset as a destructive action with explicit confirmation via parameters.

Recommended flags for safe reset:

- `EXOCORTEX_HINDSIGHT_RESET_DATA=1`
- `EXOCORTEX_HINDSIGHT_CONFIRM_DELETE=DELETE_HINDSIGHT_MEMORY`

Without both flags, memory must be preserved.

Operational reference: `references/hindsight-single-container-setup.md`.

State pattern after Hindsight activation in Hermes:

- `memory.provider=hindsight`
- `memory.memory_enabled=false`
- `memory.user_profile_enabled=false`

Scope pattern for this setup:

- One Hindsight per Hermes instance.
- `exec` and `evol` profiles share the same bank (`bank_id_template: exocortex`).

Initial preference for Exocórtex:

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

`local_embedded` means the Hindsight service/database runs locally. The LLM backend can be truly local, self-hosted, or external API. Explain this distinction to avoid the false requirement of running a full model on the same host.

### Critical Pitfall (Hermes + Hindsight plugin)

In the current Hermes integration state, the `hindsight` provider may require `HINDSIGHT_API_KEY` to be `available` in `hermes memory status`, even when `mode=local_embedded`.

Practical implication:
- `local_embedded` does NOT imply "no platform key" operation.
- Without `HINDSIGHT_API_KEY`, the provider may remain `not available`.

Mandatory diagnosis before concluding setup:
1. Run `hermes memory status`.
2. If `Missing: HINDSIGHT_API_KEY` appears, treat as provider activation blocker.
3. Decide explicitly:
   - Keep Hindsight and provision the required key, or
   - Migrate to an alternative local-first provider (e.g., holographic/honcho/mem0 local) when the cloud-key requirement is unacceptable.

Communication rule for the user:
- Don't say "just needs LLM backend".
- Always separate three layers: local storage, LLM backend, plugin-required authentication.

## Holographic

Use as a local-first, auditable alternative when sovereignty, SQLite, and explicit control matter more than self-organization. Start with `auto_extract: false` and use explicit facts until there's quality evidence.

## Promotion to Canonical Memory

Use this funnel:

```text
provider observation
→ validation against current context
→ candidate
→ Acervo decision/contract/workflow/reflection
→ skill, if procedural
→ built-in memory, if compact invariant
```

## References

- `references/operational-memory-provider-integration.md` — detailed integration pattern and repeatability checklist.
- `references/hindsight-local-embedded-key-requirement.md` — operational distinction between local storage, LLM backend, and plugin-required authentication in Hermes.

## Pitfalls

- Don't point memory provider to replace Acervo.
- Don't activate broad auto-recall in production without an audit period.
- Don't start with raw fact recall if the provider offers consolidated observations.
- Don't turn a setup error into a permanent rule against the provider.
- Don't register secrets, credentials, or unapproved drafts as operational memory.

## When to Use

Activate when working with this skill's domain. See procedure for details.

**Don't use for:** Unrelated domains or when a more specialized skill exists.

## Procedure

Follow the steps and rules defined in this skill's body sections above.

## Verification

- [ ] Skill trigger conditions were correctly matched
- [ ] Output follows the skill's defined format and rules
- [ ] No governance violations occurred
