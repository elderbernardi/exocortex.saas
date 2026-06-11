# Contingency surface activation

Use this note when packaging a degraded-mode or emergency-mode surface for Hermes/Exocórtex.

## Durable rule

Contingency modes should be **opt-in**, not default.

A reliable pattern is to mirror the same activation across surfaces:
- CLI/setup: `--imbroke`
- chat/gateway: `/xc imbroke`

This keeps the operator path and the end-user command semantically aligned.

## Activation contract

1. Default path remains untouched.
2. Contingency path is explicit.
3. Write/apply actions require the contingency flag.
4. Read-only ranking/reporting can exist without applying config.

## Example shape

- `bash setup.sh --imbroke`
- `python scripts/openrouter_free_model_router.py --imbroke --apply`
- `/xc imbroke`

## Why this matters

If setup auto-switches to fallback mode whenever a provider key exists, the fallback stops being contingency and becomes accidental default behavior. That breaks product intent and makes recovery paths indistinguishable from primary paths.

## Good review question

Before shipping any fallback surface, ask:
- "If the user does nothing special, does the main path still win?"
- "Can the same emergency intent be triggered from both CLI and gateway with matching language?"
- "Is there a hard guard preventing apply/write behavior without the explicit contingency trigger?"
