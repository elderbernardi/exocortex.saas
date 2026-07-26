# Phase 8 — Scientific public evaluation harness

Date: 2026-07-13
Status: implemented; public model-bearing runs not yet executed

## Delivered

- Preregistered LongMemEval-S primary design: 50-question stratified pilot and
  untouched 450-question confirmation.
- LoCoMo replication path with conversation-cluster bootstrap.
- Six experimental conditions: full, no-consolidation, catalog-only,
  flat/no-microverse, long-context, and oracle.
- Strict separation of ingestion histories, query files, sealed gold records,
  immutable per-run receipts, and official judge imports.
- Disposable Acervo adapter, one isolated repository per benchmark case.
- Mandatory explicit consolidation command/version for the full condition and
  source-session provenance on consolidated objects.
- Paired percentile bootstrap, paired randomization test, Holm–Bonferroni
  utility, exact zero-event upper bound, per-ability results, p95 latency,
  resource metrics, and operational gates.
- Official QA export/judge-import flow and stratified 10% double-human audit
  with Cohen's kappa.
- Deterministic 800-case native suite: 400 forbidden-scope traps, 100 authorized
  bridges, 100 update chains, 100 extraction cases, and 100 abstention cases.
- Reproducibility manifest with dataset/artifact SHA-256 hashes and a freeze
  record template.

## Verification

- New benchmark tests: 8 passed.
- Focused memory/benchmark regression selection: 50 passed.
- Full repository suite: 485 passed, 1 skipped, 18 failed for pre-existing
  environment/integration prerequisites (missing `/tmp/last30days-skill`,
  missing `python` alias/`yt-dlp`, and a live ReclameAqui response-code
  expectation). No full-suite failure referenced the new benchmark files.

## Not claimed

No performance or consolidation benefit is claimed by this implementation.
That conclusion requires the frozen pilot, official QA judging, human audit,
and confirmatory run. The harness intentionally refuses to substitute the raw
store for the missing model-bearing consolidator.
