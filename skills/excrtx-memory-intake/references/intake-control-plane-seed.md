# Intake Control Plane Seed

Summary of the consolidated operational lesson from this session.

## When to Apply

When the Exocórtex already has the cognitive intake capability, but doesn't yet have a final GUI or gateway adapter ready.

## Pattern

Interpose a minimal HTTP layer between the channel and `intake_ingest.py`.

```text
USER -> GUI/gateway -> intake control plane -> intake_ingest.py -> _inbox -> triage -> promotion
```

## Minimum Contract

Useful endpoints for seed:

- `GET /health`
- `POST /v1/intake/upload`
- `POST /v1/intake/text`
- `POST /v1/intake/link`
- `GET /v1/intake/{intake_id}`
- `POST /v1/intake/{intake_id}/analyze`
- `POST /v1/intake/{intake_id}/promote`

Convergent metadata:

- `title`
- `channel`
- `caption`
- `content_type`
- `correlation_id`
- `session_ref`
- `microverso_hint`

## Separation Rule

- The channel receives the human gesture;
- The server normalizes upload and metadata;
- The cognitive tool decides extraction, routing, and promotion.

Don't let bot, GUI, or webhook call the cognitive tool directly.

## Rollout Heuristic

1. Validate the HTTP contract and `_inbox` first.
2. Plug in a simple dropzone or bot adapter.
3. Only then add sophistication with web framework, auth, queue, or additional persistence.

## Seed Value

This seed reduces premature architecture risk: it enables real usage now and preserves the ability to migrate the implementation without breaking the intake contract.