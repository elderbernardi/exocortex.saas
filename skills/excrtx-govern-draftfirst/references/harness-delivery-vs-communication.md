# Harness: delivery vs communication

## Learning from the session

A behavior bug exposed by conversational dogfood should not be patched only at the test layer when the real ambiguity lives in the Exocórtex harness.

The durable distinction is:

- **Channel capability**: the system can technically call a delivery tool.
- **Delivery permission**: whether it may actually send now.
- **Representation scope**: whether the payload is merely a system response to the executive or speech in the executive's name to third parties.

## Required categories

### self_delivery
Use when all are true:
- recipient is the executive themself
- destination is the executive's home channel
- content is an operational response, receipt, reminder, or explicit self-test payload
- message does not represent the executive speaking to third parties

Default policy: may be allowed without DRAFT if the request is explicit.

### third_party_message
Any direct message to another person.

Default policy: DRAFT required.

### shared_channel_post
Any group, topic, shared thread, or channel where others can see the content.

Default policy: DRAFT required.

### public_publication
Any public or semi-public surface: social posts, PR comments as positioning, shared docs, public issue comments, etc.

Default policy: DRAFT required.

## Design rule

If the observed failure is 'the harness blocks communication entirely and therefore cannot distinguish preparation from delivery', fix the harness classification first. Dogfood should validate the rule, not invent it.

## Conservative fallback

If recipient, scope, or representational status is ambiguous, classify as external communication and require DRAFT.
