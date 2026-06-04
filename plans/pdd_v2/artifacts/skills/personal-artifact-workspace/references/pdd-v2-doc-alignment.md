# PDD v2 + Microverso Documentation Alignment

Session learning from 2026-05-30.

## Durable decision

Personal Artifact Workspace must be documented in both places:

1. The replicable setup plan/harness, so another Exocórtex-Hermes can reproduce the capability.
2. The Acervo microverso that owns the operational meaning, so the current Exocórtex keeps the decision, workflow, and context discoverable.

For the current architecture:

- PDD v2 addendum: `plans/pdd_v2/ARTIFACT_WORKSPACE.md`.
- PDD v2 anchors: `PLAN.md`, `phases/P5_PRODUCTION.md`, `provisioner/RUNBOOK.md`, `provisioner/prompts/*`.
- Microverso: `~/.hermes/acervo/micro/hermes-setup/decisions/personal-artifact-workspace.md` and `workflows/publish-final-artifacts.md`.

## Replication rule

When updating artifact publication behavior, do not only patch the runtime skill. Also update:

- the setup/provisioning plan;
- the microverso decision/workflow;
- the microverso index/log;
- any phase/prompt files that carry skill counts, Acervo structure, or promotion criteria.

## Consistency checks

After edits, search for old drift markers:

```text
13 skills
13 total
todas as 13
4 de P1
esperado = 13
6 skills
15 skills core
15 no bundle
15+1
```

The corrected model used in this session:

- P1 = 5 skills: self-test, prompt-log, stop-slop, taste-skill, design-system.
- P2 = 7 total after acervo-manager + new-microverso.
- P3 = 14 core skills after 7 behavior skills.
- 15 when `browser-use` is available as an external/bundled capability.
- `personal-artifact-workspace` is post-P5 until promoted into a future golden image/PDD v2.1.

## Pitfall

Do not collapse `_artifacts/` into the semantic ontology. Treat it as an operational package area. The semantic microverso should point to `artifact_id` only when the artifact has cognitive value.
