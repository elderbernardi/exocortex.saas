# F2 — Curador (charter)

> **Charter, não plano.** Plano detalhado após gate F1.

## Objetivo

Agente paralelo com contexto próprio que assiste o enquadramento e a execução sem poluir o contexto da tarefa: busca no acervo, sugestão de itens com memória viva das capacidades por microverso, pesquisa externa. A Sala só retém o destilado (P11).

## Entregáveis

1. **Contrato executor↔curador com semântica A2A** (Task/Message/Artifact + estados submitted/working/input_required/completed/failed/canceled), implementado **in-process** sobre o padrão worker/dispatcher do kanban (`api/kanban_bridge.py` como referência de claim/worker); serialização JSON idêntica à do A2A para upgrade futuro a HTTP real.
2. **Curador v1** (perfil Hermes próprio, LLM role `auxiliar`): responde delegações `buscar_acervo(query, escopo)` → artefato destilado citado (`acervoctl retrieve --budget`), `sugerir_itens(canvas)` → personas/templates/skills/workflows com por-quês e paths, `pesquisar(tema)` → síntese com fontes (last30days/agent-reach/firecrawl via Hermes).
3. **Memória viva de capacidades**: índice por microverso (o que cada um oferece por nature) derivado de `_meta/index.md` + `catalog.sqlite`; refresh idempotente; persistido no acervo (decisão de local na F2 — ver questão aberta #6 da meta issue).
4. **Cards proativos na Sala**: sugestões do Curador chegam como cards aceitar/dispensar (HITL classe 3); aceitar = aplicar ao canvas com citação.
5. **Prova de higiene de contexto**: medição antes/depois — tokens do contexto da sessão executor não crescem com o volume de busca do Curador.

## Gate de saída

Numa sala real: sugestão citada aplicada em 1 clique; delegação de busca retorna artefato destilado ≤ N tokens (budget explícito); medição de higiene de contexto anexada.

## Guardrails específicos

Curador NUNCA escreve no acervo (só lê/retrieve) — escrita é sempre da colheita (F4) com HITL; respeitar sharing constraints na busca (`acervo_validate_scope`); um worker por vez (limite single-user documentado).
