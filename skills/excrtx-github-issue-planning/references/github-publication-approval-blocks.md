# GitHub publication when external-action approval is blocked

Use this when an issue-publication plan is approved in chat, but the runtime/harness blocks `gh issue create`, `gh issue comment`, or another GitHub write with a denial such as `User denied this command`.

## Rule

Treat the harness denial as authoritative. Do not retry the same publication, do not split it into smaller `gh` calls, do not switch to the REST API, and do not attempt to publish through another tool.

## Correct fallback

1. Stop the publication workflow.
2. Report exactly what did and did not happen:
   - issues created: yes/no and numbers if any;
   - comments posted: yes/no;
   - local plan/files updated: yes/no.
3. Preserve the publication package locally:
   - issue titles;
   - labels;
   - bodies;
   - dependency comments;
   - target repo;
   - source plan path.
4. Offer one of these next steps:
   - user approves through the runtime approval prompt if available;
   - generate local `.md` files for manual publication;
   - keep only the local plan and do not publish.

## Pitfall

Chat approval and harness approval are not the same thing. If the runtime records a denial, repeated attempts become an attempt to bypass an external-action guardrail.

## Recommended local package layout

```text
docs/plans/<initiative>.md
.hermes/plans/github-publication/<initiative>/
  00-meta.md
  01-subissue.md
  02-subissue.md
  dependency-comments.md
  publish-notes.md
```

Use `docs/plans/` for durable roadmap anchors. Use `.hermes/plans/` for temporary publication payloads that should not become project documentation.
