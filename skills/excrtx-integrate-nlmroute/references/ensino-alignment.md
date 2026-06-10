# Alignment with Teaching Workspace Standard (NLM)

## Validated Operational Decisions

1. **CLI-first**: use `nlm` as the default route for knowledge operations.
2. **MCP fallback**: use `notebooklm-mcp` only when the CLI route is not viable.
3. **Official installation**: `uv tool install notebooklm-mcp-cli`.
4. **Auth verification on current runtime**: `nlm login --check`.
   - Don't use `nlm auth status` in this environment.

## Minimum Recommended Flow

```bash
nlm --version
nlm login --check
nlm notebook create "<topic>"
nlm research start "<topic and focus>" --source web --mode fast --notebook-id <id> --auto-import
nlm source list <id> --full
nlm notebook query <id> "<main question>" --json
```

## Troubleshooting Observed at Runtime

- If `nlm login --check` returns `HTTP 400 Bad Request`, don't immediately assume MCP is healthy just because `hermes mcp test notebooklm` connects.
- `hermes mcp test` confirms stdio transport and tool discovery; it doesn't validate authenticated operation.
- Recommended repair order:
  1. Reload local tokens;
  2. Repeat `nlm login --check`;
  3. Redo `nlm login`;
  4. If CLI is outdated relative to the current release, update `notebooklm-mcp-cli` via the official channel (`uv tool upgrade notebooklm-mcp-cli`).

## Ingestion Rule When There Are No Sources

- Collect and import **10 sources** before the main query.
- `--mode fast` tends to return ~10 sources quickly; use `deep` when the topic requires greater breadth.

## Source Quality Criteria

- Prioritize authority, recency, coverage, and diversity.
- Avoid duplicates, SEO spam, and pages without traceability.

## Minimum Delivery

- Requested synthesis
- Explicit list of sources used
- Indication of deep research/web search usage when applicable
