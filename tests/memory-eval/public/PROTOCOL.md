# Preregistered protocol: Acervo and microverse memory evaluation

Protocol version: **1.0**
Fixed seed: **20260713**

## Research question and primary hypothesis

Does the complete Acervo pipeline, including consolidation, improve long-term
question-answering accuracy over the identical pipeline with consolidation
disabled, without cross-microverse contamination?

The preregistered primary contrast is `full − no-consolidation` on official
LongMemEval-S QA accuracy in the untouched 450-question confirmatory split.
Benefit is claimed only when all three conditions hold:

1. the paired absolute effect is at least +5 percentage points;
2. the lower endpoint of the 95% paired-bootstrap interval is above zero;
3. observed contamination is exactly zero.

If the interval includes zero, the result is inconclusive. Any contamination is
an operational failure regardless of aggregate accuracy.

## Design

- Public primary: LongMemEval-S, using its official cleaned release and official
  evaluator, pinned by dataset hash, evaluator commit, model and prompt.
- Public replication: all LoCoMo QA annotations, with conversation-clustered
  bootstrap intervals.
- Private validation: the existing live Acervo battery; only aggregate metrics
  are publishable. Questions, answers, values, and paths remain private.
- Pilot: 50 LongMemEval-S questions, allocated equally across information
  extraction, multi-session reasoning, knowledge update, temporal reasoning,
  and abstention.
- Confirmation: the remaining 450 questions. No prompt, policy, threshold,
  model, or code tuning is permitted after the pilot freeze.
- Stochastic ingestion/reader stages: three independent repeats. Deterministic
  retrieval is run once and hash-checked.

Only histories are available during ingestion. Questions are presented after
ingestion. Expected answers and evidence locations remain in the sealed scoring
partition and are not passed to the system under test.

## Conditions and estimands

1. `full`: the complete, pinned Acervo ingestion, consolidation, scoped
   retrieval, and frozen reader.
2. `no-consolidation`: identical components and parameters with consolidation
   disabled. This is the primary causal control.
3. `catalog-only`: deterministic catalog/lexical retrieval without semantic
   supplements.
4. `flat-no-microverse`: same stored sessions without microverse boundaries.
5. `long-context`: all sessions supplied to the same frozen reader.
6. `oracle`: only annotated evidence sessions supplied to the same reader.

The adapter refuses `full` without a named consolidation implementation. This
prevents a scientifically invalid comparison between two identical raw stores.

## Outcomes

Primary outcome: official QA correctness. Secondary outcomes are QA accuracy by
ability; Recall@5, Precision@5, MRR and evidence-session recall; abstention
precision/recall/F1; temporal/update accuracy; citation fidelity; authorized
cross-scope recall; forbidden-scope contamination; consolidation extraction,
supersession and conflict quality; input/output tokens; end-to-end latency;
ingestion time; catalog size; and compression ratio.

The separate Acervo-native suite must contain 400 forbidden-scope traps, 100
explicitly authorized bridge queries, active/superseded/disputed temporal
chains, extraction ground truth, and absent/adversarial questions. Restricted
content must never leave its home scope.

Operational acceptance thresholds are: contamination 0/400, authorized
cross-scope recall ≥80%, temporal/update accuracy ≥90%, citation fidelity ≥95%,
at least 25% fewer input tokens than long-context with at most 2 points of QA
loss, catalog retrieval p95 ≤5 seconds, and consolidation correction rate ≤10%.

## Statistical analysis

- The primary 95% interval is a 10,000-resample percentile bootstrap paired by
  question. LoCoMo resamples its ten conversation clusters.
- A two-sided paired randomization test with 100,000 sign permutations tests
  the primary null. Effect size and interval govern interpretation; p-values do
  not stand alone.
- Preregistered secondary hypothesis p-values use Holm–Bonferroni family-wise
  correction. All other subgroup analyses are explicitly exploratory.
- Zero observed contamination is accompanied by the one-sided exact binomial
  95% upper bound, `1 − 0.05^(1/n)`; zero observations do not imply zero risk.
- The automatic evaluator is audited on a stratified 10% sample by two blind
  human raters. Cohen's kappa is calculated before adjudication. Automatic
  agreement against adjudicated consensus is reported.

The approach follows accepted information-retrieval practice of reporting
uncertainty rather than only point estimates; see NIST's guidance on
[confidence intervals for common IR measures](https://www.nist.gov/publications/computing-confidence-intervals-common-ir-measures).

## Freeze record (complete after pilot)

| Item | Frozen value |
|---|---|
| Source dataset SHA-256 | pending |
| Split manifest SHA-256 | pending |
| Acervo commit | pending |
| Adapter/version | pending |
| Consolidator/version | pending |
| Reader model/prompt/temperature | pending |
| Official evaluator commit | pending |
| Judge model/prompt/temperature | pending |
| Top-k and token budget | pending |
| Deviations from protocol | none / pending |
