# Skill Judge — D2–D5 Results (deferred dimensions)

These are the previously-deferred LLM-as-Judge dimensions (D2 Clarity, D3 Alignment,
D4 Fitness, D5 Economy) for the three memory-lifecycle skills. D1 (structural) had
already passed deterministically; D2–D5 were blocked by the absence of an LLM API key.

## Run metadata

| Field | Value |
|-------|-------|
| Date | 2026-06-19 |
| Provider | OpenCode Zen gateway (`https://opencode.ai/zen/v1`) |
| Auth | `OPENCODE_API_KEY` |
| Model | `nemotron-3-ultra-free` |
| Command | `python3 scripts/skill_judge.py --skill <name> --output <name>.json` |

> The originally requested model `minimax-M3` is published only as `minimax-m3-free`,
> whose free promotion has ended; paid variants (`minimax-m2.7`, …) require account
> credits. `nemotron-3-ultra-free` was selected as the available free judge. To re-run
> on a different model: `python3 scripts/skill_judge.py --skill <name> --model <id>`
> (list ids with `--list-models`).

## Results (after remediation)

| Skill | D1 | D2 Clarity | D3 Alignment | D4 Fitness | D5 Economy | Verdict |
|-------|----|-----------|--------------|-----------|-----------|---------|
| `excrtx-memory-deprecate` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-quarantine` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |
| `excrtx-memory-syndic` | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS |

All three skills are PASS. The per-skill `*.json` files in this directory hold the raw
judge output (full reasoning per dimension) for the final run.

## `excrtx-memory-quarantine` — remediated (was IMPROVE)

The first judge run scored quarantine **⚠️ IMPROVE** on two dimensions; both were fixed
in-loco and the re-run scored **✅ PASS**.

**D2 was AMBIGUOUS** — The `## Procedure: Quarantine/Purge/Restore` sections were one-line
pointers to `references/procedure-*.md`; an agent reading only `SKILL.md` could not
execute the operations from the body alone (deprecate and syndic inline their procedures).
- *Fix:* inlined a condensed executable skeleton (numbered steps) for each of the three
  procedures in the body, matching the `syndic` pattern. `references/procedure-*.md` retain
  the full inputs/formats/edge-cases.

**D5 was ACCEPTABLE** — Per-procedure verification checklists in the body duplicated the
final `## Verification` section.
- *Fix:* removed the three per-procedure `### X — Verification` checklists from the body;
  the consolidated `## Verification` section already gates all three operations.
