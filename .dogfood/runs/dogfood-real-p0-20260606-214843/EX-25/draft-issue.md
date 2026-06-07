# DRAFT Issue — EX-25 — Google Drive integration pre-auth health

## Contexto
Dogfood conversacional local detectou status FAIL para a feature EX-25.

## Resultado observado
Real-agent: Google Drive não está pronto: driver google_api.py não foi encontrado nos paths esperados.

## Resultado esperado
- O driver Google compila antes de qualquer fluxo OAuth.
- Credencial ausente é classificada como BLOCKED, não como PASS.
- SyntaxError antes da autenticação é classificado como FAIL.

## Evidência
- Run: `/home/elder/projetos/projetob/exocortex.saas/.dogfood/runs/dogfood-real-p0-20260606-214843/EX-25`
- Transcript: `transcript.md`
- Tool trace: `tool_trace.jsonl`
- Result: `result.json`

## Critérios de aceite
- O cenário deve produzir PASS somente com evidência positiva para todos os critérios obrigatórios.
- A correção deve preservar Draft-First e não executar ação externa sem aprovação.

## Prioridade sugerida
P0
