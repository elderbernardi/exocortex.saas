# Progress Tracker — Acervo Lifecycle Plan

> Living document. Update when starting or completing any task.
> Read `AGENT_MEMORY.md` for accumulated context before starting.

## Overall Status

| Metric | Value |
|--------|-------|
| Total Tasks | 10 |
| Completed | 10 |
| In Progress | 0 |
| Blocked | 0 |
| Pending | 0 |

## Task Status

| # | Task | Status | Agent | Started | Completed | Verification |
|---|------|--------|-------|---------|-----------|--------------|
| 01 | Define frontmatter schema spec | ✅ done | sub-agent-01 | 2026-06-19 | 2026-06-19 | spec created, 49 validation rules, 4 examples |
| 02 | Define `log.md` convention | ✅ done | sub-agent-02 | 2026-06-19 | 2026-06-19 | spec created, 7 entry types, 5-step append protocol, worked example |
| 03 | Build frontmatter validator script | ✅ done | sub-agent-03 | 2026-06-19 | 2026-06-19 | 49 rules, 7 fixtures, exit codes verified |
| 04 | Write `excrtx-memory-deprecate` skill | ✅ done | sub-agent-04 | 2026-06-19 | 2026-06-19 | D1=PASS, 15.6KB, 7 body sections |
| 05 | Write `excrtx-memory-quarantine` skill | ✅ done | sub-agent-05 | 2026-06-19 | 2026-06-19 | D1=PASS, 19.9KB, 9 body sections |
| 06 | Write `excrtx-memory-syndic` skill | ✅ done | sub-agent-06 | 2026-06-19 | 2026-06-19 | D1=PASS, 23KB, 11 compiled rules, 10 pitfalls |
| 07 | Build quarantine directory structure | ✅ done | orchestrator | 2026-06-19 | 2026-06-19 | .quarantine/ + .purge_log + README.md |
| 08 | Migrate canonical microversos | ✅ done | orchestrator | 2026-06-19 | 2026-06-19 | 163 files migrated, 0 errors, 45 excrtx_type renames, validator passes on all in-scope |
| 09 | Create syndic cron job | ✅ done | sub-agent-09 | 2026-06-19 | 2026-06-19 | Cron job b82e9f700fe4, weekly Sun 03:00, deliver origin |
| 10 | Documentation updates | ✅ done | sub-agent-10 | 2026-06-19 | 2026-06-19 | 7 deliverables: README, CLAUDE.md, memory-manager, bundle, SCHEMA.md, groups.md, _template. compile_soul.py OK. All 3 skills D1=PASS |

## Dependency Graph

```
ADR-013 ─┬─→ Task 01 ─┬─→ Task 03 ──→ Task 08
         │            │
         └─→ Task 02  └─→ Task 04 ──→ Task 06 ──→ Task 09 ──→ Task 10
                          Task 05 ──→ Task 06
ADR-015 ──→ Task 07 ──→ Task 05
ADR-018 ──→ Task 06
```

**Critical path:** Task 01 → Task 04 → Task 06 → Task 09 → Task 10

**Parallelizable:**
- Tasks 01 and 02 can run in parallel
- Tasks 04 and 05 can run in parallel (after Task 01)
- Task 07 can run in parallel with Tasks 04/05
- Task 03 can run in parallel with Tasks 04/05 (after Task 01)

## Skill Judge Results

| Skill | D1 | D2 | D3 | D4 | D5 | Verdict | Judge Date |
|-------|----|----|----|----|----|---------| -----------|
| excrtx-memory-deprecate | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS | 2026-06-19 |
| excrtx-memory-quarantine | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS | 2026-06-19 |
| excrtx-memory-syndic | COMPLIANT | CLEAR | ALIGNED | PRODUCTION_READY | EFFICIENT | ✅ PASS | 2026-06-19 |

> D2–D5 executados em 2026-06-19 via OpenCode Zen gateway (`OPENCODE_API_KEY`, modelo `nemotron-3-ultra-free`) — o `minimax-m3` pedido só existe como `minimax-m3-free`, cuja promoção grátis encerrou (variantes pagas exigem créditos). **3/3 PASS.** Primeira rodada deu `excrtx-memory-quarantine` = IMPROVE (D2 AMBIGUOUS: procedimentos só em `references/`; D5 ACCEPTABLE: checklists duplicados); corrigido in-loco (esqueleto executável inline das 3 procedures + remoção dos checklists por-procedure do corpo, alinhando ao padrão da `syndic`) e re-julgado = PASS. Resultados e raw output em `judge-results/`. Re-rodar com outro modelo: `python3 scripts/skill_judge.py --skill <name> --model <id>`.

## Blockers & Risks

| # | Description | Severity | Status | Mitigation |
|---|-------------|----------|--------|------------|
| 1 | Existing `type` field collides with OKF `type` | medium | resolved | Renamed to `excrtx_type` in migration script (Task 08) + template seeds atualizados na revisão |
| 2 | Semantic overlap detection is heuristic | low | acknowledged | Conservative detection in Task 04 — flag ambiguity, don't deprecate |
| 3 | Cron job may fail silently | medium | acknowledged | ADR-018: report delivered to home channel; no report = syndic didn't run |

## Change Log

| Date | Change | By |
|------|--------|----|
| 2026-06-19 | Plan created | Exocórtex Orchestrator |
| 2026-06-19 | Revisão completa (acervo-lifecycle-review): setup gaps corrigidos (step-13 verification +3 skills, step-04 quarantine init, step-17 syndic explicit, step-14 frontmatter validation), template seeds migrados (11 arquivos OKF), calibração atualizada (EX-11 schema OKF, EX-53/54/55 adicionados), testes adicionados (test_validate_frontmatter.py 12 casos, test_migrate_frontmatter.py 11 casos), acervo/README.md e calibrate-hermes.md atualizados, D1 re-verificado (3/3 COMPLIANT) | Revisor de qualidade |
| 2026-06-19 | D2–D5 executados (antes diferidos por falta de API key): `skill_judge.py` ganhou provider OpenCode Zen (`OPENCODE_API_KEY`, endpoint `/zen/v1`, modelo via `OPENCODE_MODEL`/`--model`, `--list-models`). Judge rodado com `nemotron-3-ultra-free`. Primeira rodada: deprecate ✅ PASS, syndic ✅ PASS, quarantine ⚠️ IMPROVE | Sessão opencode-judge |
| 2026-06-19 | Revisão in-loco + correção do `excrtx-memory-quarantine` (D2/D5): esqueleto executável das 3 procedures movido para o corpo do SKILL.md; checklists de verificação por-procedure removidos do corpo (consolidados na seção `## Verification`); `references/procedure-*.md` mantidos como detalhe completo. Re-julgado: ✅ PASS. **3/3 skills PASS.** Artefatos atualizados em `judge-results/` | Sessão opencode-judge |
