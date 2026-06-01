
---
title: Workflow — Ingestão Multicanal de Inputs
author: Exocórtex
created: 2026-05-30
updated: 2026-05-30
nature: processos
kind: workflow
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global, exocortex, acervo, intake]
authority: canonical
operational_mode: executable
stability: active
sources:
  - /home/elder/.hermes/acervo/global/tools/intake_ingest.py
  - /home/elder/.hermes/skills/exocortex/personal-intake-workspace/SKILL.md
derived_from:
  - personal-intake-workspace
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: exocortex/personal-intake-workspace
  assumed_version: 1.0.0
  coupling: adapter-only
tags: [intake, inbox, workflow, multichannel, triage]
---

# Workflow — Ingestão Multicanal de Inputs

## Quando usar

Use quando o Exocórtex precisar receber arquivo, áudio, imagem, ZIP, link ou texto bruto antes de decidir se aquilo vira memória, tarefa ou artefato derivado.

## Procedimento

1. Receber o item via canal disponível.
2. Persistir em `_inbox/{intake_id}/original/`.
3. Criar `manifest.json` com hash, MIME, tamanho, canal e status.
4. Extrair texto ou preview útil em `derived/`.
5. Gerar `routing.json` com hipótese de microverso, diretório funcional e próxima ação.
6. Responder ao usuário em linguagem curta: recebi, extraí, parece ser X, sugiro Y.
7. Promover apenas se o material tiver valor cognitivo durável e escopo claro.
8. Se virar saída final, encaminhar para o Personal Artifact Workspace.

## Comandos mínimos

```bash
python ~/.hermes/acervo/global/tools/intake_ingest.py ingest   --input /caminho/arquivo.pdf   --channel telegram   --caption "Plano de ensino"

python ~/.hermes/acervo/global/tools/intake_ingest.py show   --intake-id int_20260530_120000_plano-de-ensino

python ~/.hermes/acervo/global/tools/intake_ingest.py promote   --intake-id int_20260530_120000_plano-de-ensino   --microverso ensino
```

## Saída esperada

- pacote local em `~/.hermes/acervo/_inbox/{intake_id}`;
- manifesto e roteamento atualizados;
- extração em `derived/` quando aplicável;
- promoção semântica opcional com atualização de `index.md` e `log.md` do microverso alvo.
