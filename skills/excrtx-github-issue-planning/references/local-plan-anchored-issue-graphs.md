# Local-plan anchored issue graphs

Use this pattern when a roadmap must serve both humans and future agents.

## When to use

Use when the executive asks for issues/epics and also wants local continuity between agents. The local plan becomes the source of truth; GitHub issues mirror it for tracking.

## Pattern

1. Create a local plan first.
   - Preferred path for repo-local plans: `docs/plans/<slug>-YYYY-MM-DD.md` when the plan is meant to be project documentation.
   - Use `.hermes/plans/` only for temporary implementation plans that should not become repo docs.

2. Make the plan agent-readable.
   Include:
   - decision record;
   - current observed state;
   - model/architecture target;
   - rules for future agents;
   - META issue draft;
   - subissue drafts;
   - dependency graph;
   - progress checklist;
   - publication instructions.

3. Publish only after explicit approval.
   GitHub issue creation is external. Draft the issue set first; wait for an approval such as "aprovado para publicação".

4. Publish as a graph.
   - Create META first.
   - Create subissues.
   - Edit META with real issue numbers.
   - Edit subissues with links back to META and the local plan.
   - Add dependency comments. Do not rely on issue order.

5. Update the local plan after publication.
   Mark publication checklist items complete, record issue numbers, record comments/dependencies, and note that publication happened after approval.

## Dependency comment examples

- `Blocked by: #69. Motivo: backup/restore precisa conhecer slug, paths, env e diretórios da instância.`
- `Blocks: #71, #72. Motivo: modelo de instância define paths e nomes usados pelos fluxos posteriores.`
- `Pesquisa independente. Não bloqueia os P0. Se encontrar caminho executável, deve gerar issue separada de implementação.`

## Verification

After publication, verify:

```bash
gh issue view <number> --json number,title,state,url,comments
```

Check that every issue is open, every subissue links to the META and local plan, and dependency comments exist.
