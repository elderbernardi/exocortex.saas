# F1 — MVP Sala (charter)

> **Charter, não plano.** O plano detalhado (formato F0-PLANO) é escrito após o gate do F0, consumindo ADR-CT-04/05. Não implementar a partir deste arquivo.

## Objetivo

Do intake à sessão: o executivo escreve 1 frase no Átrio, o canvas nasce verificável e editável in loco, e "Lançar" cria a tarefa (`_tasks/`) + sessão Hermes com o brief compilado como contexto de abertura.

## Entregáveis

1. **Átrio mínimo** dentro do Acervo Studio (entrada via command bar do Studio; a página dev do F0 é aposentada): lista de salas (leitura de `_tasks/`) + intake de 1 frase.
2. **Canvas editável**: zonas Foco/Pronto, Vetor (com seletor de 3 botões quando `ambiguo`), Microversos (âncora + apoios com badge de sharing constraint via `acervo_validate_scope`), Lacunas, Artefatos esperados; edição in place → JSON Patch → persistência + re-validação; badges de validade e explícito×inferido.
3. **Campos v0.5 no documento**: `shape`, `done_criteria` + `verification` nomeada, `scope`, `assumptions` — **inclui patch upstream do harness** (template + `canvas_schema.py` unificados, resolvendo o drift `vetor`×`vector` documentado no F0-RESULTADO; retrocompatível com v0.4).
4. **Enquadrador definitivo**: substitui o seam `CANVAS_LLM_CMD` pela invocação decidida na ADR-CT-04; propõe `done_criteria`; "não consigo nomear verificação" vira gap card.
5. **Compile & Launch**: preview diff-able do brief compilado → `register_task_from_canvas.py` → `POST /api/session/new` + staged context (ponte MOD-008) + model/profile pelo vetor → `links.yaml` liga sessão↔tarefa.
6. **Contrato COLLAB**: criar `.harness/contracts/exocortex-hermes-webui.md` (superfícies: provisionamento, canvas v0.5, endpoints `/api/canvas/*`, eventos SSE).

## Esboço de tarefas (será detalhado)

Patch harness v0.5 (exocortex.saas, com testes de validador) → invocação definitiva do enquadrador → endpoints CRUD/patch do canvas → UI de zonas com edição in place → seletor de vetor ambíguo → badges/citações → preview do brief → launch pipeline → entrada no Studio → MOD-012 + contrato + docs.

## Gate de saída

1 frase real → sala lançada → sessão aberta com brief visível no chat nativo; `_tasks/{id}/` completo (task.yaml, canvas.yaml, links.yaml); edição in loco persiste e re-valida; suíte do fork sem falhas novas.

## Guardrails específicos

Os do `00-INDEX.md` +: não tocar no fluxo de chat nativo (a ponte é o staged context existente); o patch do harness v0.5 é PR separado no exocortex.saas com aprovação do owner ANTES de a UI depender dele (risk gate — o schema é contrato do framework).
