---
type: knowledge
title: "Mapa técnico — autonovel"
description: "Mapa dos scripts, formatos e dependências da referência autonovel."
tags: [autonovel, tools, editorial]
timestamp: "2026-07-07"
class: volátil
created_at: "2026-07-07T19:13:18Z"
created: "2026-07-07"
updated: "2026-07-07"
nature: tools
excrtx_type: tool
confidence: high
sources: [raw/autonovel-readme.md, raw/autonovel-pipeline.md]
---

# Mapa técnico — autonovel

## Repositório

- Atlas: https://hermesatlas.com/projects/NousResearch/autonovel
- GitHub: https://github.com/NousResearch/autonovel

## Dependências declaradas

- Python >= 3.12
- `uv`
- `httpx`
- `python-dotenv`
- `ANTHROPIC_API_KEY` para núcleo textual
- `FAL_KEY` para arte opcional
- `ELEVENLABS_API_KEY` para audiobook opcional

## Scripts-chave

- Fundação: `seed.py`, `gen_world.py`, `gen_characters.py`, `gen_outline.py`, `gen_canon.py`, `voice_fingerprint.py`.
- Rascunho: `draft_chapter.py`, `run_drafts.py`.
- Avaliação: `evaluate.py`, `reader_panel.py`, `review.py`, `compare_chapters.py`.
- Revisão: `adversarial_edit.py`, `apply_cuts.py`, `gen_brief.py`, `gen_revision.py`.
- Exportação: `typeset/build_tex.py`, `gen_art.py`, `gen_audiobook.py`, `gen_cover_print.py`.

## Status no Exocórtex

Fonte mapeada. Execução local e instalação runtime ainda pendentes de aprovação e teste isolado.
