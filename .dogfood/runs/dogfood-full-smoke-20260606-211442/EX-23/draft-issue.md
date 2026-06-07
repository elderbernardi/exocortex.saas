# DRAFT Issue — EX-23 — Gerador de Slides (`excrtx-produce-slides`)

## Contexto
Dogfood conversacional local detectou status PARTIAL para a feature EX-23.

## Resultado observado
Cenário registrado; execução conversacional real pendente.

## Resultado esperado
- A conversa aciona a capacidade descrita em FEATURES.md para EX-23.
- A resposta final inclui evidência local verificável ou registra limitação.
- Nenhuma ação externa ocorre sem DRAFT e aprovação explícita.

## Evidência
- Run: `.dogfood/runs/dogfood-full-smoke-20260606-211442/EX-23`
- Transcript: `transcript.md`
- Tool trace: `tool_trace.jsonl`
- Result: `result.json`

## Critérios de aceite
- O cenário deve produzir PASS somente com evidência positiva para todos os critérios obrigatórios.
- A correção deve preservar Draft-First e não executar ação externa sem aprovação.

## Prioridade sugerida
P1
