# F4 — Colheita & canonização (charter)

> **Charter, não plano.** Plano detalhado após gate F3.

## Objetivo

Fechar o ciclo de crescimento: conhecimentos e artefatos intermediários da sala são canonizados ao acervo com HITL em lote; canvases viram receitas reutilizáveis.

## Entregáveis

1. **Bandeja de colheita**: durante a execução, `promotion_candidates` (conhecimento/decisões/reflexões) e artefatos intermediários acumulam como cards (destino microverso/nature proposto, classe de gate risk/trust, diff sob demanda). Zero interrupção durante o trabalho.
2. **Checkout de fechamento**: 1 momento de HITL em lote — aprovar tudo / revisar item a item / rejeitar; execução via `acervoctl new-object/commit-write` (propose-then-approve, ADR-022); risk gate (perene/persona/macro = DRAFT-first) e trust gate (origem web = untrusted/draft) aplicados por item.
3. **fable-judge no checkout**: antes do report final, passe de juiz que verifica por execução/diff (nunca lendo o relatório); resultado anexado à sala.
4. **Canvas → receita**: transformação clean-portable (modelo EX-58/fable-domain: muda os substantivos, nunca o loop) — remove instância, preserva estrutura (vetor, slots de microverso, personas, perguntas de intake derivadas dos gaps recorrentes, artefatos esperados, verificação nomeada) → acervo nature `templates`/`workflows` com OKF v0.2 → galeria do Átrio; iniciar sala a partir de receita pré-preenche o canvas.
5. **Report outcome-first** da sala (formato Step 6 do método: resultado na primeira frase, caveats honestos, artefatos INTENT/AUTH/TWINS/PENDING quando devidos).

## Gate de saída

1 sala real fechada com: colheita aprovada em lote gravada no acervo (log.md do container mostra as entradas); 1 receita canonizada; nova sala iniciada a partir dessa receita.

## Guardrails específicos

NUNCA auto-commit de promoção (propose-then-approve sempre); receita não carrega dados de instância nem segredos (gate clean-portable com validação OKF antes de gravar).
