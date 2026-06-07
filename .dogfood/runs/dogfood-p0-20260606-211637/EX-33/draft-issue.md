# DRAFT Issue — EX-33 — Codex Core Harness wrapper evidence

## Contexto
Dogfood conversacional local detectou status PARTIAL para a feature EX-33.

## Resultado observado
Dry-run registrou verificação de wrappers Codex declarados.

## Resultado esperado
- O wrapper run_codex_with_learning.py existe no path declarado.
- O wrapper review_latest_run.py existe no path declarado.
- O diretório ~/.hermes/codex-learning existe ou é criado pelo setup documentado.
- O harness não declara PASS quando esses artefatos centrais faltam.

## Evidência
- Run: `/home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/dogfood-p0-20260606-211637/EX-33`
- Transcript: `transcript.md`
- Tool trace: `tool_trace.jsonl`
- Result: `result.json`

## Critérios de aceite
- O cenário deve produzir PASS somente com evidência positiva para todos os critérios obrigatórios.
- A correção deve preservar Draft-First e não executar ação externa sem aprovação.

## Prioridade sugerida
P0
