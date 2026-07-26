# Public evaluation of Acervo memory

This directory defines the reproducible, public track. Generated datasets and
runs live under `workspace/`, which is intentionally git-ignored. The private
live battery remains separate under `tests/memory-eval/live/`.

The primary benchmark is
[LongMemEval-S](https://github.com/xiaowu0162/LongMemEval) (500 questions and
five long-term-memory abilities). [LoCoMo](https://github.com/snap-research/locomo)
is an external replication whose confidence intervals are clustered by its ten
conversations. The design follows paired evaluation and percentile bootstrap
confidence intervals; the statistical rationale is recorded in
[`PROTOCOL.md`](PROTOCOL.md).

## 1. Prepare without test leakage

```bash
python3 scripts/run_public_memory_benchmark.py prepare \
  --dataset longmemeval-s --download --pilot-size 50 --seed 20260713
```

This creates a stratified 50-question pilot (10 per official ability) and an
untouched 450-question confirmatory split. Histories and queries go under
`prepared/`; answers and evidence locations go under `sealed/`. The manifest
pins the source and every derived artifact by SHA-256. Do not inspect or tune
against the confirmatory gabarito before freezing the configuration.

For LoCoMo, use a different workspace and its entire dataset as the replication
split:

```bash
python3 scripts/run_public_memory_benchmark.py prepare \
  --workspace /tmp/acervo-locomo --dataset locomo --download
```

Generate and prepare the deterministic Acervo-native isolation and
consolidation suite (800 cases: 400 traps, 100 authorized bridges, 100 update
chains, 100 extraction cases, and 100 abstentions):

```bash
python3 scripts/generate_acervo_native_benchmark.py --output /tmp/acervo-native.json
python3 scripts/run_public_memory_benchmark.py prepare \
  --workspace /tmp/acervo-native-workspace --dataset acervo-native \
  --source /tmp/acervo-native.json
```

## 2. Run conditions

The public runner never passes gold answers to an adapter. `long-context` and
`oracle` are built in. The four Acervo conditions use the included disposable
adapter; every question receives a new temporary Acervo, preventing fictional
memories from leaking into another question or the live repository.

```bash
ADAPTER="python3 scripts/acervo_public_benchmark_adapter.py"

python3 scripts/run_public_memory_benchmark.py run \
  --condition no-consolidation --split pilot --repeat 1 \
  --adapter-command "$ADAPTER" --adapter-id acervo-raw-v1 \
  --code-version "$(git rev-parse HEAD)"

python3 scripts/run_public_memory_benchmark.py run \
  --condition full --split pilot --repeat 1 \
  --adapter-command "$ADAPTER --consolidator-command 'YOUR_COMMAND'" \
  --adapter-id acervo-full-v1 --consolidator-id YOUR_PINNED_VERSION \
  --code-version "$(git rev-parse HEAD)"
```

The consolidator receives the case request on stdin and these environment
variables: `ACERVO_ROOT`, `ACTIVE_MICROVERSO`, and
`ACERVO_BENCHMARK_CASE_ID`. It must write only to the disposable root. A `full`
run is refused unless both the command and its version identifier are supplied;
raw retrieval is never mislabeled as consolidation.

Every consolidated object must declare the evidence provenance in frontmatter,
for example `benchmark_session_ids: [session-123, session-456]`. The adapter
uses this field to score evidence-session retrieval and supplies the consolidated
object itself to the reader. Missing provenance counts as a retrieval miss.

Use `--reader-command` for the frozen answer model. It receives JSON containing
only `case_id`, `question`, `question_date`, and retrieved `contexts`, and must
return JSON with `hypothesis` plus optional token counts. Run stochastic stages
three times with `--repeat 1`, `2`, and `3`. Deterministic retrieval needs one
run; verify identical receipt content apart from timestamps and latency.

## 3. Official judge and human audit

Export the exact official hypothesis format:

```bash
python3 scripts/run_public_memory_benchmark.py export-qa \
  --condition full --split pilot --repeat 1
```

Run the version-pinned official `src/evaluation/evaluate_qa.py` from the
LongMemEval repository, then import its JSONL log without changing raw receipts:

```bash
python3 scripts/run_public_memory_benchmark.py import-judge \
  --input OUTPUT.eval-results.jsonl --condition full --split pilot --repeat 1 \
  --judge-id longmemeval-official-COMMIT-MODEL-PROMPT
```

After evaluation, create the preregistered stratified 10% double-blind audit:

```bash
python3 scripts/run_public_memory_benchmark.py audit-sample \
  --condition full --split confirmatory --fraction 0.10
```

Two raters independently fill `rater_1` and `rater_2`; disagreements are then
adjudicated in `adjudicated_label`, preserving both original labels. Report
Cohen's kappa and automatic-judge agreement with:

```bash
python3 scripts/run_public_memory_benchmark.py audit-score \
  --input tests/memory-eval/public/workspace/audit/confirmatory-full.jsonl
```

## 4. Confirmatory analysis

```bash
python3 scripts/run_public_memory_benchmark.py evaluate \
  --split confirmatory --bootstrap 10000 --randomizations 100000
python3 scripts/run_public_memory_benchmark.py report --split confirmatory
```

For LoCoMo add `--cluster-bootstrap`; the conversation, rather than each QA
item, is the resampling unit. Publish the protocol, manifest, source hashes,
adapter/config versions, immutable receipts where licensing permits, official
judge logs, audit statistics, and the generated JSON/Markdown report.

## Adapter response contract

An adapter returns one JSON object with:

- `retrieved_session_ids` (required for retrieval scoring);
- `contexts` (required when a reader is used);
- optional `latency_ms`, `input_tokens`, `output_tokens`,
  `citation_correct`, `contaminated`, and `correction_required`.

Any failure becomes a retained error row. With `--fail-on-error`, the command
also exits nonzero after writing all observations.
