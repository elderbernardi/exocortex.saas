# DRAFT Issue — EX-30 — Browser automation dependency and path contract

## Contexto
Dogfood conversacional local detectou status BLOCKED para a feature EX-30.

## Resultado observado
Dry-run bloqueia automação browser até dependências e sandbox ficarem explícitos.

## Resultado esperado
- A dependência uv existe ou há fallback documentado.
- O path do comando em FEATURES.md corresponde ao path real da skill.
- Falta de dependência é BLOCKED com evidência, não PASS.

## Evidência
- Run: `/home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/dogfood-p0-20260606-211246/EX-30`
- Transcript: `transcript.md`
- Tool trace: `tool_trace.jsonl`
- Result: `result.json`

## Critérios de aceite
- O cenário deve produzir PASS somente com evidência positiva para todos os critérios obrigatórios.
- A correção deve preservar Draft-First e não executar ação externa sem aprovação.

## Prioridade sugerida
P1
