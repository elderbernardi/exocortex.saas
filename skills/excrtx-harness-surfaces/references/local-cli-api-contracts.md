# Local CLI API contracts for Hermes-operated engines

Use this reference when Hermes needs to operate a sibling local project as an engine without adding an HTTP service.

## Pattern

Prefer a machine-oriented CLI API alongside the human CLI:

```bash
<tool> api <resource> <action> [flags]
```

Keep the human command intact:

```bash
<tool> ingest file.pdf
```

Expose the machine contract separately:

```bash
<tool> api parse create --input file.pdf --output json
```

This avoids coupling Hermes to human-facing naming, progress output, prompts, or presentation semantics.

## Contract rules

1. stdout contains only JSON.
2. logs, progress, and diagnostics go to stderr.
3. every response uses a stable envelope.
4. every error uses a stable error schema.
5. idempotent policy is the default for agent calls.
6. large fields are opt-in through `--include`.
7. stdin JSON requests are supported for complex calls.
8. exit codes represent operational state; semantic quality stays in the JSON payload unless the caller requested `--fail-on-low-quality`.

## Recommended envelope

```json
{
  "ok": true,
  "api_version": "tool.cli.v1",
  "command": "parse.create",
  "request_id": "req_...",
  "job": null,
  "data": {},
  "warnings": [],
  "errors": []
}
```

Error shape:

```json
{
  "ok": false,
  "api_version": "tool.cli.v1",
  "command": "parse.create",
  "request_id": "req_...",
  "job": null,
  "data": null,
  "warnings": [],
  "errors": [
    {
      "code": "INPUT_NOT_FOUND",
      "message": "Input file not found",
      "detail": { "path": "/abs/path/file.pdf" },
      "retryable": false
    }
  ]
}
```

## Flags that make CLIs agent-safe

- `--output json`
- `--request -` for JSON via stdin
- `--project-root <path>` to avoid cwd ambiguity
- `--include <parts>` to control payload size
- `--reprocess-policy skip|reprocess|new_revision`
- `--fail-on-low-quality` only when the caller wants quality as an exit-code gate

## TDD check for JSON purity

Add a subprocess test that executes the real CLI and immediately parses stdout as JSON. This catches accidental progress logs in stdout.

Example test intent:

- run `<tool> api health --output json`
- assert `JSON.parse(stdout)` succeeds
- assert `stdout.trim().startsWith('{')`
- assert `ok`, `api_version`, and `command`

Then run a representative engine call through the same path.

For Node/Vitest CLIs, prefer testing the API through the actual executable path (`npx tsx src/cli/index.ts ...` during development or the built bin after build). If tests that spawn CLI subprocesses hang or time out under the default worker pool, validate with an isolated process/fork pool before rewriting production code; subprocess-heavy tests can interact badly with threaded test pools.

## Implementation notes

- Redirect structured or pretty loggers to stderr in API mode, or globally if the tool is CLI-first.
- Keep the API wrapper thin at first; reuse the existing pipeline internally.
- Add store methods for machine lookup, usually `getByJobId`, `list`, and `listRevisions`.
- Do not expose raw extracted text by default when documents can be large; require `--include raw_text`.
- Prefer request JSON via stdin for complex or shell-sensitive calls: `<tool> api parse create --request -`.
- Keep human verbs and machine verbs distinct. `ingest` may be correct for humans; `parse.create` is clearer for a parser engine contract.

## Example: parser engine consumed by Hermes

A local document parser engine should expose at least:

```bash
<tool> api health --output json
<tool> api capabilities --output json
<tool> api parse create --input /abs/file.pdf --include tables,sections --output json
<tool> api parse create --request -
# optional/deferred in early runtimes: get/list/revisions only after the engine actually ships them
```

Default parse output should return the structured document contract and job metadata. Raw text, markdown-only views, wiki projections, entities, sections, and tables should be selectable through `--include` so Hermes can control token and payload size.

## Exit-code guidance

- `0`: command executed and `ok=true`
- `1`: operational failure and `ok=false`
- `2`: semantic quality gate failed only when explicitly requested
- `3`: invalid input/schema/request
- `4`: required dependency unavailable for an explicitly forced policy
- `124`: timeout
