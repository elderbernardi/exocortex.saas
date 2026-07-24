# ADR-CT-05 — Frontend do canvas: vanilla JS vs ilha Preact IIFE

status: proposta (decidir no F0/T6)
data: 2026-07-23
contexto: meta issue #130 · constraint no-build do fork · caminho "ilha pré-bundlada" já previsto no RFC acervo-studio

## Questão

O canvas completo (F1+: zonas editáveis in loco, fila de gaps, bandeja de colheita, trace cards) fica em vanilla JS (padrão do fork) ou numa ilha Preact IIFE pré-bundlada (commitada, sem build step no deploy)?

## Regra de decisão (aplicar ao resultado da T5)

- Se `static/canvas-tarefas.js` do spike ficou **≤ ~400 linhas** e o render é praticamente stateless (re-render total a cada delta foi suficiente, sem estado local complexo): **vanilla** na F1, com gatilho de migração registrado: "migrar para ilha quando houver ≥3 stores mutáveis interdependentes (canvas + fila de gaps + colheita) OU o arquivo cruzar ~900 linhas".
- Se o spike já exigiu gerência de estado dolorosa (bugs de sincronização render×patch): **ilha Preact IIFE** desde a F1.

## Decisão

_(preencher no F0: `wc -l static/canvas-tarefas.js` + avaliação de dor de estado)_

## Consequências

_(preencher no F0)_
