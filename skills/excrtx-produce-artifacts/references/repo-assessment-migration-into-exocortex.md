# Repo assessment migration into `exocortex.saas`

## When this pattern applies

Use this pattern when work starts in an external assessment workspace or throwaway clone, but the conclusion is meant to become durable Exocórtex implementation context.

Typical triggers:

- repository fit / due diligence work;
- provisioning plans for a new Hermes surface;
- operator-cockpit evaluations;
- architecture studies that should inform `exocortex.saas` setup or roadmap.

## Durable packaging pattern

Persist two artifacts, not one:

1. **Full artifact** in `docs/research/`
   - Keep the deep narrative, phase plan, risks, evidence, and recommended rollout path.
   - Filename pattern: `subject-or-system-topic-YYYY-MM-DD.md` or `topic-YYYY-MM-DD.md`.

2. **Distilled operational note** in `acervo/micro/exocortex-ops/knowledge/`
   - Capture only the parts worth retrieving later during setup or architectural decisions:
     - verdict;
     - what was actually validated;
     - major risks/blockers;
     - recommended surface split (executive vs operator vs admin);
     - pointer to the full artifact.

This separation prevents the Acervo from becoming a dump of long reports while still preserving actionable operational knowledge.

## Minimal migration checklist

- Copy the canonical long-form document into `docs/research/`.
- Write a shorter Exocórtex-facing note into `acervo/micro/exocortex-ops/knowledge/`.
- Review the diff before commit.
- If the user asked to commit, create a local git commit with a generic, durable message.
- Stop before push unless the user explicitly authorizes remote publication.

## Example from session

`hermes-web-ui` assessment was migrated as:

- `docs/research/hermes-web-ui-provisioning-plan-2026-06-12.md`
- `acervo/micro/exocortex-ops/knowledge/hermes-web-ui-evaluation.md`

The useful lesson is not the specific repository name; it is the dual-artifact migration pattern for turning external analysis into durable Exocórtex implementation context.
