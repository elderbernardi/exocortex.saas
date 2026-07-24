# ADR-CT-06 — Canvas v0.5: unificação de drifts + campos do método

status: proposta (aprovação = merge do PR collab/canvas-v05 pelo owner)
data: 2026-07-24
contexto: meta issue #130 · F0-RESULTADO §6 (drifts 1-4) · F1-CHARTER §Insumos (5º drift) · recon F1 2026-07-24

## Decisões

1. **Chave canônica: `vetor`** (termo do framework, EX-05) em todas as camadas — schema (já usa), template canvas.yaml (era `vector`), task.yaml (era `vector`), `register_task_from_canvas.py` (era `vector`). Leitura com **fallback `vector`** mantida por 1 ciclo no register (10 canvases-spike vivos em `_tasks/` usam `vector`; nunca são re-validados, mas podem ser registrados).
2. **Enum de `vetor`**: canvas = 4 valores (`execucao|evolucao|manutencao|ambiguo`) em schema E comentários de template. **task.yaml = 3 valores** — não é drift, é regra semântica explícita: *canvas pode ser ambiguo; tarefa registrada não pode*; o register rejeita `ambiguo` com erro acionável.
3. **Enum de `intent_type`: superset de 8** (`explorar|decidir|produzir|revisar|manter|publicar|ingestao|outro`) em schema, template, SKILL (body e compiled_rules) e espelhos do fork (F1b). Retrocompatível (só amplia).
4. **Núcleo v0.5 (+3 campos opcionais, emitidos pelo enquadrador)**: `shape` (`pergunta|tarefa|plano-primeiro`), `done_criteria` (string), `verification` (string — a verificação nomeada do fable-method). `focus.minLength: 3` mantido.
5. **Documento v0.5 (+6 campos)**: os 3 do núcleo + `scope: []`, `assumptions: []`, `authorization: []` (preenchidos durante a sessão — AUTH com palavras exatas do executivo; NÃO são emitidos pelo LLM).
6. `additionalProperties: false` mantido no schema do núcleo (novos campos declarados).
7. Correções de arrasto no register: `--from-stdin` passa a parsear campos (bug latente: hoje ignora e cai nos defaults da CLI); `task_id` ganha sufixo `_HHMMSS` (colisão mesmo-dia-mesmo-título hoje sobrescreve silenciosamente via `exist_ok=True`); template inline de fallback alinhado ao arquivo (`status: candidate`, era `registered`).

## Consequências

- F1b atualiza os espelhos do fork (`canvas_validate._ENUMS/_ALLOWED`, `canvas_store._CORE_TO_DOC` vira identidade em `vetor`, `_DEFAULTS`, JS lê `canvas.vetor`) SOMENTE após o merge deste PR.
- Propagação ao acervo vivo: re-rodar `bash setup.sh` (step-04 sobrescreve tools/templates incondicionalmente) OU cópia manual dirigida — passo T0 da F1b.
- `compile_soul.py --validate-compiled-rules --require-d1-pass` e `skill_judge --d1-only` são gates deste PR.
