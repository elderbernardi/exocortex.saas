# 10 — Evaluation Framework

> EX-49 applied to memory: no claim that "memory works" without a command whose raw output proves it. Two tracks: **synthetic** (fixture acervo, deterministic, CI-runnable) and **live** (golden questions against the real acervo, run after every schema/retrieval change and monthly).

## 1. Harness

`tests/memory-eval/` in the installer:

```text
tests/memory-eval/
  fixture/           # synthetic acervo: 3 microversos, ~80 objects, planted
                     # facts, planted contradictions, planted stale items,
                     # planted cross-scope traps, superseded chains
  golden/questions.yaml   # per-question: query, expected paths, forbidden paths,
                          # expected answer fragments, category
  run_eval.py        # drives hermes chat -q / acervoctl retrieve; scores; JSON report
  report/            # dated results — the metric history IS acervo knowledge
```

Fixture planting is the trick that makes contamination measurable: e.g. client-alfa's price in `micro/alfa/`, client-beta's in `micro/beta/`, question asked in beta-scope must cite beta's file and **must not** contain alfa's number.

## 2. Metrics & targets

| Metric | Definition | Target v2 | How measured |
|---|---|---:|---|
| Context precision | retrieved items actually relevant | ≥ 0.8 | golden set, judged |
| Context recall | expected paths retrieved | ≥ 0.9 | golden set, deterministic |
| **Contamination rate** | answers containing forbidden-scope content | **0** | planted traps |
| Stale-answer rate | answers using superseded/expired facts w/o flag | < 5% | superseded chains in fixture |
| Contradiction handling | planted disputes surfaced with banner (not silently merged/picked) | 100% surfaced | fixture |
| Temporal correctness | "as of March" questions answer from the right validity window | ≥ 90% | fixture chains |
| Citation fidelity | claims in answer traceable to cited path | ≥ 95% | judged |
| Token efficiency | tokens packed / tokens available; answers within 07 §4 budgets | 100% within budget | logged by pack_context |
| Retrieval latency | question → packed context | p95 ≤ 10s (Hindsight up), ≤ 5s (catalog-only) | logged |
| Fallback correctness | Hindsight down → same golden recall via catalog+grep | recall ≥ 0.8 | run with container stopped |
| Write quality | new objects passing validator + checklist on first commit | ≥ 95% | journal audit |
| Index drift | reconcile findings per week (orphans, hash mismatches) | trend → 0 | existing daily report |
| Abstention | questions with no acervo answer → explicit "não há registro" (no confabulation) | 100% | planted-absent questions |
| **Executive trust** (the real metric) | corrections issued per week; "asks the system before asking a human" frequency | trend | weekly digest self-report |

## 3. Golden question categories (live set, ~25 questions, PT-BR)

factual · decision+rationale · temporal ("em março") · entity/relationship · cross-scope synthesis (allowed path) · cross-scope trap (forbidden) · prospective ("o que prometi para…") · continuity ("onde paramos em…") · literal ("qual foi a frase exata…") · absent ("qual nosso contrato com a NASA?" → deve abster-se).

Seed battery: the 10-prompt battery from `memory-excellence-execution-plan.md` Fase 7 (never executed — it becomes the first live run), extended to 25.

## 4. Cadence & regression rule

- CI (installer repo): fixture eval must pass before merging changes to memory skills/schema/scripts.
- Live: monthly + after any schema migration, retrieval change, or provider change.
- **Regression rule:** any metric dropping > 10 points blocks the change (revert or fix); results filed as `knowledge` in `micro/exocortex-ops/` with `observed_at` — the system remembers its own measurements.
