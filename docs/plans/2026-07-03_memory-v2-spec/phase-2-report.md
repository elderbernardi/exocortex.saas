# Phase 2 — Execution Report (Safe Ingestion & Write Pipeline)

> **Executed:** 2026-07-04→05 · **Status:** ✅ complete (installer) · Live rollout: pending explicit go (behavioral skills touch the running agent)

## Delivered — two coordinated fronts

### A. Control plane (`acervoctl` + `acervo_semantic_core.py`)

Four new deterministic write verbs (no LLM in the pipeline — the dispute-vs-coexist judgment is the agent's, by design):

| Verb | Contract | Guardrails |
|---|---|---|
| `conflict-check --file/--stdin [--scope]` | catalog-backed overlap detection → per-overlap verdict `enrich` \| `supersession` \| `overlap` + signals (shared entities/tags, title similarity) | pure read; requires catalog |
| `apply-supersede --new --old` | atomic pairing: old→`status: superseded`+`superseded_by`, new→`supersedes+=old`; journals SUPERSEDED; catalog upsert | **refuses** perene decision/contract (→ dispute) and already-superseded old |
| `open-dispute --a --b --title --scope` | creates `type: conflict` object, stamps `disputed_by` on both sides, journals DISPUTED | conflict object is v0.2-valid |
| `new-object --type episode\|entity\|intention ...` | lazy-dir scaffold, v0.2-valid, journal + catalog + best-effort Hindsight | entity **requires aliases + dedup check**; intention requires `--due`/`--trigger`; `--source-trust untrusted`→draft; secret scan (V2-060) refuses |

Wired into `acervoctl` (JSON/`ok`/exit contract); refusals return `ok:false` exit 1.

### B. Behavior (skills + workflow)

- **`excrtx-memory-manager` v2.2→v3.0**: RETRIEVE operation (`acervoctl retrieve` preferred, manual ladder fallback); WRITE's old deprecate-on-insert hook **replaced by the conflict protocol** (conflict-check → enrich/apply-supersede/open-dispute/coexist); trust & risk gates; v0.2 frontmatter; episode/entity/intention write rules; 14-type lazy natures; 8-rule `compiled_rules` (skill had none before).
- **`excrtx-memory-deprecate` v1.0→v2.0**: narrowed to junk/wrongness only; supersession/dispute explicitly redirected to the new verbs; 4-rule `compiled_rules`.
- **`excrtx-memory-newmicro` v2.0→v3.0**: core-6 lazy scaffold (`_meta, context, knowledge, decisions, episodes, raw`).
- **`rtn_inbox_triage.yaml`**: report-only → propose-and-commit-on-approval (drafts + digest; `can_modify_acervo: false` kept as the sanctioned proposal channel).
- **`microverso-directory-structure.md`** contract: updated to lazy core-6 (was the last doc still mandating all 14 dirs — the coherence gap the skills front flagged).
- `SOUL_SEED.md` recompiled; D1 PASS on all three skills.

## Verification (raw)

```
Regression (11 memory suites):        133 passed in 15.82s
  incl. tests/test_acervo_write.py:    10 passed  (4 verbs: overlap, atomic
         supersede + perene refusal, dispute stamping, entity alias-dedup,
         intention due-gate, untrusted→draft, secret refusal, v2-valid output)
skill_judge --d1-only:                 PASS × 3 (manager/deprecate/newmicro)
validate_frontmatter --dir acervo:     exit 0
CLI↔skill verb coherence:              5/5 verbs the skill invokes exist in acervoctl
compile_soul.py:                       clean (my 3 skills; 6 pre-existing desyncs in unrelated skills)
```

End-to-end CLI demo (scratchpad copy of fixture): `new-object intention` (active) → `new-object entity` (refused, no aliases) → `conflict-check` price file (4 overlaps, correct verdicts) → `apply-supersede` v4→v3 (paired) → refuse superseding perene decision → `doctor` **0 errors / 0 warnings**.

## Not done here (by design)

- **Live rollout**: the skills govern the running agent; per the standing boundary they are not synced to `~/.hermes`/`~/exocortex` until explicitly authorized. Control-plane tools (`acervo_semantic_core`, `acervoctl`) are installer-only until the same go.
- **LLM skill-judge (D2–D5)**: creds resolve but returned 429; D1 gate passed, full judge deferred.

## Next

Phase 4 (consolidation loop: daily episode distillation + entity refresh + intention sweep + dedup audit; weekly digest with open disputes) — now buildable on these verbs. Phase 6 (eval harness in CI) can gate on the 133-test suite already in place.
