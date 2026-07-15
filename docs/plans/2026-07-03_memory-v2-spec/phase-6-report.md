# Phase 6 — Execution Report (Evaluation & Self-improvement)

> **Executed:** 2026-07-10–13 · **Status:** complete and activated

## Delivered

- Deterministic, offline CI regression gate in `.github/workflows/ci.yml` using the catalog strategy and the committed `tests/memory-eval/baseline.json`.
- Regression policy implemented in `tests/memory-eval/run_eval.py`: a drop greater than 10 percentage points blocks; any contamination above zero blocks unconditionally.
- Custom live-evaluation mode over an isolated copy of the selected Acervo, with private golden questions excluded from git.
- Monthly wrapper `scripts/run-memory-live-eval.sh`, producing dated JSON/Markdown evidence and filing the result as canonical `knowledge` through `scripts/file_memory_eval_knowledge.py`.
- Monthly H7/H12 learning-loop report through `scripts/report_memory_learning_loops.py`:
  - H7 audits correction/reversal rates after governed auto-commit;
  - H12 reports use-decay readiness and candidates without making lifecycle changes.
- Idempotent cron provisioning for `memory-eval-live-monthly` and `memory-learning-loops-monthly`.
- H4 evidence run over the multi-hop fixture categories. Production retrieval reached 100% multi-hop recall with zero contamination, so conditional Phase 5 graph traversal is not justified.

## Evidence

### CI fixture gate

| Metric | Baseline | Current | Verdict |
|---|---:|---:|---|
| Recall@5 | 79.5% | 79.5% | pass |
| Precision@5 | 34.7% | 34.7% | pass |
| Abstention accuracy | 33.3% | 33.3% | pass |
| Contamination | 0.0% | 0.0% | pass |

### Live canonical run (2026-07-12, 10 questions)

| Strategy | Recall@5 | Precision@5 | Abstention | Contamination |
|---|---:|---:|---:|---:|
| catalog | 100.0% | 30.4% | 100.0% | 0.0% |
| production | 100.0% | 28.5% | 100.0% | 0.0% |

Evidence files:

- `tests/memory-eval/report/live-2026-07-12.json`
- `tests/memory-eval/report/live-2026-07-12.md`
- `tests/memory-eval/report/h4-2026-07-12.md`

## Verification

- Focused Phase 6 tests: 16 passed.
- Maintenance-cron idempotency tests: 4 passed.
- Memory v2 regression suite: passed.
- `run_eval.py --gate`: passed with no regression and zero contamination.
- Shell syntax checks and `git diff --check`: passed.

## Decisions

1. **Phase 6 is complete.** Evaluation now blocks measurable retrieval regressions in CI and has a monthly live path.
2. **Phase 5 remains cut.** Reopen only if a future live multi-hop battery drops below H4's 70% trigger.
3. **Next development milestone: Phase 7.** Briefing v2, decision/research postures, temporal conversational queries, and the executive one-page guide.

## Live activation receipt (2026-07-13)

- Pre-activation scheduler snapshot: `/tmp/hermes-crons-pre-phase6-20260713.txt`.
- `memory-eval-live-monthly`: job `f0289a5c897e`, active, `0 5 1 * *`, next run `2026-08-01T05:00:00Z`.
- `memory-learning-loops-monthly`: job `e127f4a26b2e`, active, `15 5 1 * *`, next run `2026-08-01T05:15:00Z`.
- Both jobs use workdir `/home/ubuntu/.exocortex-installer` and deliver locally.
- Rollback: `hermes cron delete <job_id>`; no live Acervo file was changed during activation.
