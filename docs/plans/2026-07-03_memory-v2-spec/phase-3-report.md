# Phase 3 — Execution Report (Hybrid Retrieval)

> **Executed:** 2026-07-04 · **Status:** ✅ complete · Informed by H2 (resolvido no mesmo dia: catálogo primário)

## Delivered

- **`acervo/global/tools/acervo_retrieve.py`** — retrieval de produção por rota (`classify_query`: literal / continuity / prospective / temporal / procedural / entity / semantic / factual), scope guard (`micro/{scope}/ + shared/ + global/`; `restricted` nunca sai do escopo-casa, nem via bridges nem via Hindsight), packing U-curve com headers epistêmicos (`⚠ STALE` / `⏳ HISTORICAL` / `⚠ DISPUTED`), degradação para stubs sob budget, abstenção explícita ("não há registro no Acervo sobre…"). Hindsight só com `--with-hindsight` (H2), pós-filtrado e nunca acima de hit léxico.
- **`acervoctl retrieve`** — `--query --scope --budget --k --with-hindsight --allow-scope --json`; abstenção = `found: false`, exit 0.
- **`run_eval.py`** ganhou a estratégia `production`; 20 testes novos (`test_acervo_retrieve.py`).

## Placar (25 perguntas-ouro, k=5) — reproduzido independentemente

| Estratégia | Recall@5 | Precision@5 | Contaminação | Abstenção | Tokens (chars) |
|---|---:|---:|---:|---:|---:|
| catalog (baseline H2) | 79,5% | 34,7% | 0,0% | 33,3% | 2.693 |
| hindsight (H2) | 81,8% | 18,2% | **8,0%** | 0,0% | 4.076 |
| **production** | **100,0%** | **39,0%** | **0,0%** | **66,7%** | 2.925 |

Metas do roadmap: recall ≥ 0,90 ✅ · contaminação = 0 ✅ · abstenção ≥ 2/3 ✅ — **1 iteração de tuning** (de até 3). Ganhos por categoria: prospective 33→100% (rota de metadados: intenções por `due`), continuity 50→100%, entity 83→100%, cross-scope traps 50→100% (bridge de `shared/` + bônus de autoridade traz o contrato de confidencialidade à tona nas perguntas-armadilha).

## Degradação (aceite "Hindsight parado")

Satisfeito por construção: a rota primária não usa Hindsight (H2); `--with-hindsight` é aditivo e falha silenciosa-mas-logada. Verificado nos testes e no placar (produção rodou 100% sem Hindsight).

## Smoke no acervo vivo

- Pergunta canônica (`exocortex-ops`): rota factual, ADR-019 + memory-routing-contract + contratos no topo, 2.823 tokens. ✅
- Abstenção ("contrato com a NASA", escopo comercial): `found: false` com mensagem explícita. ✅
- `acervo_retrieve.py` sincronizado para o vivo.

## Pendência conhecida (documentada, não bloqueante)

- G23 (abstenção): alias "Atlântico" legitimamente traz a página da entidade → 1 das 3 perguntas de ausência não abstém; contaminação segue 0. Refinamento fica para o harness contínuo (Phase 6).
- A rota de produção existe no **control plane** (`acervoctl retrieve`); o **agente** ainda recupera via skill v2.2 (boot + busca manual). Ligar a skill à rota nova é trabalho da Phase 2/7 (memory-manager v3).

## Próximo

Phase 2 — write pipeline em produção: `excrtx-memory-manager` v3 (tipos episode/entity/intention, verbos supersede/dispute/coexist, trust gate), triagem do `_inbox/` e superfície de disputas no digest.
