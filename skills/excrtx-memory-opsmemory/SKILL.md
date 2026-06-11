---
name: excrtx-memory-opsmemory
description: Govern, deploy, and audit operational memory providers for the agent
  in Exocórtex/Hermes without replacing the Acervo Cognitivo.
version: 1.1.0
category: excrtx
platforms:
- linux
author: Exocórtex
metadata:
  hermes:
    tags:
    - exocortex
    - hermes
    - memory
    - hindsight
    - operational-memory
    - acervo
    - setup
    - governance
    related_skills:
    - excrtx-memory-manager
    - hermes-agent
    calibration:
    - feature_id: EX-16
      calibration_prompt: Você deve garantir que as operações e regras da skill Memória
        Operacional (excrtx-memory-opsmemory) estão totalmente ativas no seu comportamento
        e integridade.
      test_prompt: Verifique se a skill define precedência de providers de memória.
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill Memória Operacional.
      remediation_tip: Certifique-se de que a documentação e os limites da skill Memória
        Operacional em seu SKILL.md estão sendo estritamente seguidos.
---
# Exocórtex Operational Memory

Govern, deploy, and audit operational memory providers (Hindsight, Holographic, Mem0, etc.) that aid agent operation without replacing the Acervo Cognitivo.

## When to Use

- Evaluating, deploying, configuring, comparing, or auditing operational memory providers
- Setting up Hindsight, Holographic, Honcho, Mem0, or similar
- Diagnosing memory provider status issues

**Don't use for:** Managing the Acervo Cognitivo directly (use `excrtx-memory-manager`). Creating microversos (use `excrtx-memory-newmicro`). Configuring session history or built-in memory.

## Core Principle

```text
Provider observes and retrieves.  Exocórtex interprets.
Acervo canonizes.                 Skills proceduralize.
Built-in memory stores invariants. Session Search preserves literal history.
```

**Precedence (in case of conflict):**

| Priority | Layer | Role |
|----------|-------|------|
| 1 | SOUL / system instructions | Absolute authority |
| 2 | Acervo contracts (`operational_mode: blocking`) | Blocking rules |
| 3 | Loaded skills and canonical workflows | Active procedures |
| 4 | Built-in memory | Compact invariants |
| 5 | Acervo Cognitivo v2 | Canonical knowledge |
| 6 | Session Search | Literal history |
| 7 | Operational memory provider | Semantic observations |

Never treat a provider-retrieved observation as a canonical decision.

## Procedure

### Step 1 — Assess Provider Suitability

Evaluate using this matrix:

| Criterion | Question to Answer |
|-----------|-------------------|
| Plugin maturity | Is the Hermes plugin stable (not alpha)? |
| Hosting mode | Local, self-hosted, or cloud? Acceptable for sovereignty? |
| Auto-recall | Does it inject context automatically? Risk of overload? |
| Consolidation | Can it merge observations into summaries? |
| Auditability | Can you inspect what it stores/retrieves? |
| Cost/latency | Acceptable for production use? |
| Acervo adherence | Does it respect the precedence hierarchy? |

### Step 2 — Deploy (Hindsight Example)

1. Create Hindsight directory: `mkdir -p ~/.hermes/hindsight-local/{data}`
2. Create `docker-compose.yml` and `.env` in that directory
3. Start container: `docker compose up -d`
4. Configure in Hermes:
   ```bash
   hermes config set memory.provider hindsight
   hermes config set memory.memory_enabled false
   hermes config set memory.user_profile_enabled false
   ```
5. Verify: `hermes memory status`

> **Critical:** Hindsight may require `HINDSIGHT_API_KEY` even in `local_embedded` mode. If `hermes memory status` shows `Missing: HINDSIGHT_API_KEY`, provision the key or switch providers.

### Step 3 — Integrate into Setup

Add to `~/.hermes/setup.sh` with opt-in guard:

```bash
EXOCORTEX_ENABLE_<PROVIDER>=1 bash ~/.hermes/setup.sh
```

The script must: preserve existing configs, not overwrite credentials, not activate if config contains `CHANGE_ME`, not fail setup if provider isn't ready.

### Step 4 — Validate and Activate

1. Run `hermes memory status` — provider must show `available`
2. Test recall: send a message, verify observation is stored
3. Test retrieval: ask about a previous topic, verify recall
4. Activate only after successful validation

### Step 5 — Audit (7 and 14 days)

1. Review stored observations for relevance and accuracy
2. Check context overload (is recall injecting too much?)
3. Verify no provider observations overrode Acervo decisions
4. Adjust `recall_budget`, `retain_every_n_turns` as needed

### Promotion to Canonical Memory

```text
provider observation → validation → candidate
→ Acervo decision/contract/workflow → skill (if procedural)
→ built-in memory (if compact invariant)
```

## Pitfalls

- **`HINDSIGHT_API_KEY` required even locally:** `local_embedded` does NOT mean "no platform key." Without the key, provider stays `not available`. Always check `hermes memory status`.
- **Three layers confusion:** Separate local storage, LLM backend, and plugin-required authentication. Don't tell the user "just needs LLM backend."
- **Parallel source of truth:** Provider observations must never override Acervo decisions. Enforce precedence hierarchy.
- **Auto-recall overload:** Broad auto-recall injects stale or irrelevant context. Start with `recall_budget: low` and `retain_every_n_turns: 2`.
- **Setup error ≠ permanent rule:** A failed provider deployment doesn't mean the provider is permanently unsuitable. Diagnose root cause first.

## Verification

- [ ] `hermes memory status` shows provider as `available`
- [ ] `docker ps` shows Hindsight container running (if using Hindsight)
- [ ] Test message produces a stored observation
- [ ] Recall returns relevant past context
- [ ] No provider observation treated as canonical decision
- [ ] Setup script is idempotent (running twice produces same result)

## References

- `references/operational-memory-provider-integration.md` — detailed integration pattern and repeatability checklist.
- `references/hindsight-local-embedded-key-requirement.md` — operational distinction between local storage, LLM backend, and plugin-required authentication.
