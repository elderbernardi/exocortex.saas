# ADR-CT-05 — Frontend do canvas: vanilla JS vs ilha Preact IIFE

status: decidida
data: 2026-07-23
contexto: meta issue #130 · constraint no-build do fork · caminho "ilha pré-bundlada" já previsto no RFC acervo-studio

## Questão

O canvas completo (F1+: zonas editáveis in loco, fila de gaps, bandeja de colheita, trace cards) fica em vanilla JS (padrão do fork) ou numa ilha Preact IIFE pré-bundlada (commitada, sem build step no deploy)?

## Regra de decisão (aplicar ao resultado da T5)

- Se `static/canvas-tarefas.js` do spike ficou **≤ ~400 linhas** e o render é praticamente stateless (re-render total a cada delta foi suficiente, sem estado local complexo): **vanilla** na F1, com gatilho de migração registrado: "migrar para ilha quando houver ≥3 stores mutáveis interdependentes (canvas + fila de gaps + colheita) OU o arquivo cruzar ~900 linhas".
- Se o spike já exigiu gerência de estado dolorosa (bugs de sincronização render×patch): **ilha Preact IIFE** desde a F1.

## Decisão

**Vanilla JS** na F1.

`wc -l static/canvas-tarefas.js` = **80 linhas** (≤ ~400, dentro do limite da regra por larga margem).

Avaliação de dor de estado: o render é praticamente stateless. Há uma única variável global `canvas` (o documento JSON completo); `applyPatch()` aplica os ops JSON-Patch recebidos por `canvas_delta` diretamente sobre esse objeto, e `render()` faz um **re-render total** de `#cvt-canvas` a cada `canvas_snapshot`/`canvas_delta` — não há estado local por zona/componente, não há memoização, não há divergência entre múltiplas fontes de verdade. Na verificação E2E do Task 5 e nesta corrida com LLM real (3/3 chamadas, ver ADR-CT-04) não houve nenhum bug de sincronização render×patch nem exceção no cliente — o padrão "recebe patch, aplica no objeto, redesenha tudo" se mostrou suficiente e sem dor perceptível.

Como o arquivo ficou bem abaixo de ~400 linhas e o estado é trivial, a regra aponta diretamente para **vanilla**.

## Consequências

- O canvas completo da F1+ (zonas editáveis in loco, fila de gaps, bandeja de colheita, trace cards) continua em vanilla JS, no padrão do fork (sem build step no deploy).
- Gatilho de migração registrado (e a ser respeitado nas próximas features): migrar para ilha Preact IIFE pré-bundlada quando **qualquer** um destes ocorrer:
  - houver ≥3 stores mutáveis interdependentes (ex.: canvas + fila de gaps + bandeja de colheita evoluindo cada uma com estado próprio e precisando ficar em sincronia); ou
  - o arquivo `static/canvas-tarefas.js` (ou seu sucessor) cruzar ~900 linhas.
- Cada feature nova da F1 que adicionar estado mutável (fila de gaps, colheita) deve reavaliar contra esse gatilho antes de crescer o arquivo livremente — o padrão atual de "re-render total por delta" só se sustenta enquanto o custo de re-render for barato e o estado permanecer num único objeto central.
