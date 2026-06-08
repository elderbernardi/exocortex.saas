---
subproject: exocortex
monorepo_harness: "../.harness/MONOREPO.md"
---

# Exocortex — Local Harness

> This file provides local orientation for agents working within the Exocortex subproject. For full ecosystem context, see the [Monorepo Harness](../.harness/MONOREPO.md).

## Quick Summary

Exocortex is a **cognitive extension framework** configured as a skill/personality package for the Hermes Agent runtime. It is NOT a traditional code project — it is a configuration, skill, and behavioral specification package.

## Full Identity

See [IDENTITY.md](../.harness/subprojects/exocortex/IDENTITY.md) for complete subproject specification.

## Contracts

| Contract | Role | Counterpart |
|---|---|---|
| [exocortex-to-docbrain](../.harness/contracts/exocortex-to-docbrain.md) | **Consumer** | DocBrain |

## ⚠ Important: Hermes Runtime Configuration

This subproject contains **Hermes Agent runtime configuration files**. The following files define the agent's identity, behavior, and skill set and follow Hermes-specific conventions:

- `SOUL_SEED.md` — Agent identity and behavioral contract
- `FEATURES.md` — 35-feature catalog (EX-01 to EX-35)
- `BACKLOG_TEMPLATE.md` — Deferred integrations backlog
- `acervo/` — Acervo seed (synced from ~/exocortex/acervo)
- `skills/` — 37 skill directories (excrtx-* naming)
- `profiles/` — Hermes profiles (manut)
- `skill-bundles/` — Bundle definitions
- `install.sh` / `setup.sh` — Automated provisioning scripts

**These files must NOT be modified to conform to the monorepo harness.** They follow Hermes conventions and are managed separately.

## When Working Here

1. Read `SOUL_SEED.md` first — it defines the agent's behavioral boundaries
2. Read `FEATURES.md` for the complete skill catalog
3. Follow Hermes runtime conventions for any skill or configuration changes
4. If changing DocBrain integration (EX-27), check the [exocortex-to-docbrain contract](../.harness/contracts/exocortex-to-docbrain.md)
