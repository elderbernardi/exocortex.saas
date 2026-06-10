# DocBrain as Processing Engine for Intake

Context: DocBrain was born for DataBrain before Hermes + Exocórtex adoption. It carried its own wiki, but Exocórtex already has a semantic acervo/wiki. The correct adjustment was to avoid immediate fork and add a process-only mode, keeping wiki as an optional projection.

## Durable Decision

When a legacy documentary processor also has its own wiki, prefer:

```text
parser/processor -> structured result -> optional projections
```

Instead of:

```text
parser/processor -> own wiki -> intake server
```

The processor's wiki can continue existing, but must be a downstream projection. The intake server should consume an engine contract.

## Pattern Applied in DocBrain

- `IngestPipeline.ingest(input, { persistWiki: false })` returns result without writing `wiki/topics` or rebuilding index.
- CLI: `docbrain ingest <path> --process-only --json`.
- Old mode continues as default for compatibility.
- `IngestResult` keeps `pages` for compatibility and adds `documents[]` as the canonical engine contract.
- Fix internal adapter paths before trusting the fallback chain. In the observed case, `DoclingAdapter` pointed one directory above the project.
- The TypeScript/CLI layer needs to forward `scraper.mode` to the Python script; support hidden only in the script is not enough.

## `DocumentParseResult` Contract

Recommended initial shape for the intake server:

- `document_id`: sha256 hash when available.
- `source`: document provenance.
- `source_artifact_path`: preserved raw artifact.
- `mime_type`: inferred or detected type.
- `parser_attempts[]`: parser, status, start/end, duration, text size, quality, and error.
- `selected_parser`: last successful parser.
- `raw_text`: text extracted by the selected parser.
- `normalized_markdown`: normalized markdown for human/agent consumption.
- `sections[]`: headings extracted from markdown.
- `tables[]`: markdown tables as objects `{ columns, rows }`.
- `images[]`, `entities[]`, `citations[]`: structured lists, even if empty in the first version.
- `quality`: status, confidence, size, and warnings.
- `warnings[]`, `errors[]`: parsing and quality issues.
- `llm_enrichment`: `enabled`, `mode`, `model` when applicable.
- `projections.wiki_pages`: derived wiki pages, without requiring persistence.

Rule: `WikiPageDraft` is a projection. `DocumentParseResult` is a contract.

## Web Ingestion Policy

For web pages:

- `urllib`/fetch: simple static pages, no relevant JS.
- Playwright: deterministic rendering, no token consumption.
- `browser-use`: pages with interaction, consent/cookie banners, dynamic navigation, assisted login, or semantic extraction with LLM.
- `auto`: configurable escalation policy, with logging of the chosen path.

`browser-use` must not replace all scraping. It's a semantic track with explicit cost.

## Next Hardening

After `process-only` mode and `DocumentParseResult`, implement:

1. Dedicated `ParseJobStore` before the wiki projection.
2. Hash-based idempotency.
3. `skip | reprocess | new_revision` policy.
4. Job status: `pending | processing | completed | failed | partial`.
5. Persistence of intermediate artifacts per parser.
6. Smoke tests for declared fallbacks: Docling and Vision.

## Pitfalls

1. Forking early before trying `process-only` increases cost without delivering immediate value.
2. Making the intake server depend on wiki files couples the new product to legacy drift.
3. Having superficial chunking doesn't mean processing long documents; verify all chunks enter analysis and synthesis.
4. Declaring Vision or Docling fallback without smoke test creates false confidence.
5. Browser-use should be a semantic track with explicit cost, not an invisible substitute for all scraping.
6. Keeping `pages` as primary contract after creating `documents[]` perpetuates drift; migrate new consumers to `documents[]`.
