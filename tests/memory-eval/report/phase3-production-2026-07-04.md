# Phase 3 — production retrieval vs catalog baseline (run 2026-07-04)

Command: `python3 tests/memory-eval/run_eval.py --strategies catalog,production --no-report`
(`--no-report` used so this run would not overwrite the H2 resolution report
`h2-2026-07-04.*`, which shares the date-stamped filename; results filed here instead.)

`production` = `acervo/global/tools/acervo_retrieve.py` (07-retrieval-policy §2/§3:
query-shape routing, catalog-primary per H2, scope guard + restricted enforcement,
shared-bridge one-hop expansion, abstention floors). Hindsight OFF (default).

## Overall (top-k = 5, 25 golden questions)

| Strategy | Recall@5 | Precision@5 | Contamination | Abstention acc. | Avg token cost (chars) |
|---|---:|---:|---:|---:|---:|
| catalog (baseline) | 79.5% | 34.7% | 0.0% | 33.3% (1/3) | 2,693 |
| **production** | **100.0%** | **39.0%** | **0.0%** | **66.7% (2/3)** | 2,925 |

Acceptance targets (Phase 3): recall@5 ≥ 0.90 ✅ · contamination = 0 ✅ ·
abstention ≥ 2/3 ✅ · precision reported (no gate). Met on iteration 1; no
routing/floor re-tuning was required.

## Per category (recall@5 · precision@5)

| Category | n | catalog | production | production route(s) |
|---|---:|---|---|---|
| factual | 4 | R 100% · P 42.5% | R 100% · P 36.3% | factual / entity (alias) |
| decision_rationale | 3 | R 100% · P 21.7% | R 100% · P 21.7% | factual (por-que guard) / entity |
| temporal | 3 | R 100% · P 34.4% | R 100% · P 34.4% | temporal (as_of + superseded) |
| entity | 3 | R 83.3% · P 48.3% | R 100% · P 38.3% | entity (alias / entities-of-candidate) |
| cross_scope_allowed | 2 | R 75% · P 20% | R 100% · P 30% | factual + shared-bridge expansion |
| cross_scope_trap | 2 | R 50% · P 10% | R 100% · P 20% | entity; restricted guard + contract authority bonus |
| prospective | 3 | R 33.3% · P 33.3% | R 100% · P 63.3% | prospective (intentions by due + open conflicts) |
| continuity | 1 | R 50% · P 20% | R 100% · P 40% | continuity (context head + episodes desc) |
| literal | 1 | R 100% · P 100% | R 100% · P 100% | literal (grep exact phrase) |
| absent | 3 | abst 33.3% | abst 66.7% | — |

## Notes

- The remaining abstention miss (G23, "contrato da Atlântico com a Marinha") is an
  entity-route effect: the alias "Atlântico" resolves and the entity page (plus a
  2-term lexical hit on norte-mineracao) legitimately surfaces. Contamination is 0
  — the failure is returning a related entity page instead of abstaining. Known
  limit; target is ≥ 2/3.
- Floors: same as the catalog baseline (≥ 2 distinct terms OR 1 rare term,
  df ≤ 5) plus one tightening: purely numeric terms (years) no longer qualify as
  "rare" evidence — this fixed G25 ("multa da ANTT ... 2025") without hurting recall.
- Token cost is the chars proxy over the top-5 files (same as the H2 report); the
  production packer additionally enforces the token budget with pointer-stub
  degradation, which this proxy does not measure.
