---
type: knowledge
title: "Síntese — NousResearch/autonovel"
description: "Síntese operacional da referência autonovel para uso editorial."
tags: [autonovel, pipeline, editorial]
timestamp: "2026-07-07"
class: volátil
created_at: "2026-07-07T19:13:18Z"
created: "2026-07-07"
updated: "2026-07-07"
nature: knowledge
excrtx_type: fact
confidence: high
sources: [raw/autonovel-atlas-snapshot.md, raw/autonovel-pipeline.md, raw/autonovel-workflow.md]
---

# Síntese — NousResearch/autonovel

`NousResearch/autonovel` é um pipeline autônomo para gerar, revisar, diagramar, ilustrar e narrar romances a partir de uma ideia-semente.

## Núcleo metodológico

- Fundação antes da prosa: mundo, personagens, outline, voz e canon.
- Rascunho sequencial com avaliação por capítulo.
- Revisão em ciclos: diagnóstico, cortes, painel de leitores, briefs e reescrita.
- Revisão dual-persona com crítico literário e professor de ficção.
- Exportação para PDF, ePub, audiobook, arte e landing page.

## Elementos transferíveis ao Estúdio Editorial

- `voice.md` → guia de voz autoral.
- `canon.md` → banco de verdade textual.
- `outline.md` → arquitetura da obra ou pauta.
- `evaluate.py` → avaliação mecânica + juiz LLM.
- `reader_panel.py` → painel de personas leitoras.
- `review.py` → crítica por personas especialistas.
- `state.json` → rastreador de fase, dívidas e propagação.

## Limite

A referência é forte como método de produção longa. Não deve ser importada como licença para automação cega. O Estúdio Editorial adapta o pipeline com HITL, preservação de autoria e validação de fontes.
