# Registration Audit Pattern for Acervo/LLM Wiki Changes

Use when LLM Wiki integration, adapter behavior, Acervo ontology, or Hermes setup contracts change.

## Lesson

A structural change is not fully registered just because files exist. The target microverso must make the change discoverable through `index.md`, auditable through `log.md`, and enforceable through `contracts/` when the rule is blocking.

## Required audit trail

- `SCHEMA.md`: current ontology and path contracts.
- `index.md`: links to every relevant contract, decision, workflow, tool, template, or skill.
- `log.md`: explicit entry describing the scope, files, authority chain, and operational impact.
- `contracts/`: blocking or advisory rules, especially around upstream tools.
- `decisions/`: ADR summaries or architecture choices.
- `workflows/`: reproducible setup or operational procedures.

## Log checklist

For changes involving adapter or ontology, log:

1. Native upstream involved, if any.
2. Adapter/gatekeeper rule.
3. Canonical destination in the Acervo.
4. New or changed files.
5. Blocking rules and prohibited paths.
6. ADRs or source documents that carry authority.
7. Legacy structures deprecated or archived.

## Specific rule from 2026-05-30

For the Hermes setup microverso, a terse line such as “contratos, decisões e workflow registrados” is insufficient. The log must state that:

- `hermes-setup` records setup, replicability, and harness evolution.
- Ontologia Multifocal v2 is active.
- LLM Wiki native remains mechanical upstream only.
- Writing goes through `acervo-llm-wiki-adapter` then `acervo-manager`.
- Flat Nature files are deprecated in favor of functional directories with semantic frontmatter.
