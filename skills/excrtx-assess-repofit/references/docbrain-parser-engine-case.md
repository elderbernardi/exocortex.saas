# DocBrain Parser-Engine Case

Context: audit and hardening of DocBrain to serve as the documentary engine for the intake server, without abandoning its original wiki function.

## Verdict Used

- Sufficient as an exploratory ingestion base
- Insufficient, in its initial state, as a parser engine for the intake server
- Good foundation to evolve quickly if the operational contract is separated from the wiki projection

## Strong Positive Signals

- Parser escalation strategy was conceptually good
- LiteParse added proprietary value for PDF: OCR, spatial reconstruction, readability heuristic, and cipher detection
- Provenance concern already existed
- Reasonable separation between adapters, pipeline, wiki, scraper, and query
- Build, lint, and tests passed after fixes

## Structural Gaps Found

### 1. Wiki-first product, not engine-first

The main output was `WikiPageDraft` and persisted markdown. For an intake server, the primary contract needs to be a structured parsing result.

Fix applied as pattern: keep `pages[]` for backward compatibility and add `documents[]` with a canonical contract (`DocumentParseResult` or equivalent).

### 2. Missing process-only mode

An engine needs to be able to process and return JSON without writing to the wiki projection.

Fix applied as pattern: `processOnly` flag/config + `--json` output, preserving the old flow when mode is not active.

### 3. Cosmetic chunking

The system appeared to support long documents, but the actual orchestration didn't aggregate multiple chunks across all paths.

Lesson: always verify there's real aggregation between chunks, not just local split.

### 4. Declarative governance outside runtime

`purpose.md` and `schema.md` were described as LLM guides, but weren't loaded by the analyzed pipeline.

Lesson: look for effective reading of promised files; documentation without runtime consumption is not an operational contract.

### 5. Critical escalation broken by integration

The Docling adapter pointed to an incorrect Python script path. The escalation idea was valid; the step was broken.

Lesson: distinguish integration failure from design failure. Fix the path/adapter before discarding the architecture.

### 6. Vision fallback promised but not delivered

The pipeline looked for `pdf_to_images.py`, but the file didn't exist in the repo.

Lesson: validate each step to completion; a missing fallback invalidates the operational promise.

### 7. Web provenance degraded when becoming local file

The web origin was captured, but the local path took over the flow.

Lesson: separate `source_origin` from `source_artifact_path` and register lineage.

### 8. Absence of hash-based idempotency

For an intake engine, idempotency is a structural requirement. Without it, the same renamed document becomes multiple processings and automation loses predictability.

Fix applied as pattern:

- Calculate `document_id` via `sha256` of content when source is a local file
- Derive stable identity for web from URL/content
- Persist results in a dedicated store outside the wiki projection
- Make reprocessing policy explicit

## Implementation Pattern That Worked

### Canonical Contract

Create `DocumentParseResult` with, at minimum:

- Document identity/provenance
- Normalized text and markdown
- Sections
- Extracted tables
- Parser attempts (`parser_attempts`)
- Quality/diagnostics (`quality`)
- Entities/images when there's real support

### Job Store

Create a local store with predictable layout:

`.docbrain/parse-jobs/<document_id>/revision-N.json`

Recommended operational summary:

- `job_id`
- `document_id`
- `revision`
- `status`
- `policy`
- `created_at`
- `updated_at`

### Reprocessing Policies

- `skip`: if a completed job exists for the same hash, return persisted result and mark as skipped
- `reprocess`: process again and update the current revision
- `new_revision`: process again and create a new incremental revision

### CLI/config

Expose the policy as a flag/config, for example:

`--reprocess-policy skip|reprocess|new_revision`

Keep `--process-only --json` as the clean path for server/worker consumption.

### Minimum TDD

Before considering done:

- Store test saving and retrieving latest by `document_id`
- New revision test
- Pipeline test with `skip` without reprocessing
- Regression test ensuring old wiki mode still works
- Full build/lint/test

## Recommended Changes That Became Patterns

When a local wiki/CLI repo needs to become an engine:

1. Separate core engine from downstream projections
2. Create `DocumentParseResult` or equivalent
3. Move wiki/search/viewer to downstream consumers
4. Add jobs, status, retries, and idempotency
5. Persist parser attempts and intermediate artifacts
6. Harden real chunk aggregation
7. Validate fallbacks via smoke test
8. Expose API/worker only after the engine contract stabilizes

## Useful Synthesis Phrases

- "The problem isn't the idea; it's the operational contract"
- "Good foundation, engine not yet hardened"
- "Serves as a promising nucleus, not as a ready service"
- "Plugging the CLI into the server is not enough"
- "Preserve the wiki as a projection; promote the parser to primary contract"
