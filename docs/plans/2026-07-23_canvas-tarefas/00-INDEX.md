# Canvas de Tarefas — Programa de execução (meta issue #130)

> Índice do programa. **Fonte da verdade das fases**: este diretório. Meta issue: [#130](https://github.com/elderbernardi/exocortex.saas/issues/130). Draft de requisitos: `docs/drafts/2026-07-23_issue-canvas-tarefas-meta.md`.

## Estrutura dos artefatos

| Arquivo | O que é |
|---|---|
| `F0-PLANO.md` | Plano do spike (EXECUTADO 2026-07-24; gate fechado em #131; resultado em `F0-RESULTADO.md`). |
| `F1a-PLANO.md` | **Patch harness canvas v0.5 (ADR-CT-06)** — grau-execução; termina em PR OWNER-GATED (`collab/canvas-v05`). Executável agora. |
| `F1b-PLANO.md` | **MVP Sala no fork** — grau-execução; pré-condição dura: PR do F1a mergeado (T0 aborta sem ele). |
| `F1-CHARTER.md` … `F5-CHARTER.md` | Charters: objetivo, entregáveis, gate, guardrails. Plano detalhado de cada fase **somente após o gate da fase anterior**. |
| `adr/ADR-CT-*.md` | Decisões de arquitetura do programa (propostas → decididas com evidência). |

Precedente deste formato: `hermes-webui/docs/acervo-studio/PLAN-phase0..5.md` (MOD-010, fases gated).

## Fases e gates

| Fase | Issue | Entrega | Gate de saída |
|---|---|---|---|
| F0 · Spike | (filha de #130) | Enquadrador estruturado + deltas SSE + render mínimo | 1 frase real → canvas válido renderizado; ADR-CT-04 e ADR-CT-05 decididas com medição |
| F1 · MVP Sala | (filha) | Átrio mínimo + canvas editável/verificável + Compile & Launch | 1 frase → sala lançada → sessão com brief; `_tasks/` populado |
| F2 · Curador | (filha) | Agente paralelo (acervo + capacidades + pesquisa), semântica A2A | Sugestões citadas aplicáveis em 1 clique; contexto da sessão não cresce com a busca |
| F3 · Sala viva | (filha) | Loop de condução + bounds + trace cards + Draft-First/AUTH | Execução real com HITL restrito às 3 classes |
| F4 · Colheita & canonização | (filha) | Bandeja + checkout em lote + fable-judge + canvas→receita | 1 sala real canonizada como receita reutilizada |
| F5 · Polish | (filha) | a11y, i18n, docs, calibração EX-ID + dogfood | Dogfood PASS; auditoria interativa GO |

## Contrato de execução para agentes (leia antes de qualquer tarefa)

Este programa foi desenhado para ser executado por agentes de qualquer porte, **um task por vez**, com segurança. Regras vinculantes (violação = parar e reportar, nunca improvisar):

1. **Execute apenas a fase que tem PLANO detalhado.** Charter não é plano — não implemente a partir de charter.
2. **Escopo é fechado**: toque somente os arquivos listados na tarefa. Precisar de um arquivo fora da lista = surpresa → **pare e reporte**, nunca expanda em silêncio.
3. **Nunca toque** (zona quente de rebase / fora do escopo do programa): `hermes-webui/static/{ui,messages,sessions,panels,boot}.js`, `static/style.css`, `static/index.html`, e `api/routes.py` além dos hooks explicitamente indicados no plano (máx. 8 linhas novas ao todo).
4. **Zero dependências novas** (pip/npm), **zero build step**, strings de UI em **PT-BR**.
5. **Prova bruta por tarefa (EX-49)**: toda tarefa termina com o output real do comando de verificação. Sem output, a tarefa não está concluída — não marque.
6. **Bounds (fable-method)**: 3 ciclos falha-conserto na mesma verificação → pare, registre o que tentou, a saída real e sua hipótese, e devolva. 2 buscas sem informação nova → pare de buscar e registre a lacuna.
7. **Segredos nunca** aparecem em logs, commits ou relatórios (chaves mascaradas).
8. **`.quarantine/` não existe para você** — nunca ler, listar ou escrever.
9. Commits pequenos e frequentes na branch **`collab/canvas-tarefas`** do repo indicado pela tarefa; mensagens em inglês, prefixo convencional (`feat:`, `test:`, `docs:`); **nunca** `git push` sem instrução explícita da tarefa.
10. Ações externas (push, comentário em issue, deploy) só quando a tarefa manda — e o relatório final da fase cita cada uma.

## Estado

- 2026-07-23 — Programa criado; F0 planejado; F1–F5 em charter. COLLAB registrado no umbrella (`.harness/changes/2026-07-23_collab_canvas-tarefas.md`).
- 2026-07-24 — **F0 EXECUTADO e gate FECHADO** (#131; merge ff `exocortex/stable` @ 73b62042). ADR-CT-04 = job+poll; ADR-CT-05 = vanilla. **F1 planificado em duas partes**: F1a (harness v0.5, PR owner-gated) e F1b (MVP Sala; bloqueado até o merge do F1a). Recon 2026-07-24 embutido nos planos; achado extra: bug pré-existente do ctxTray (MOD-008) documentado no F1b.
