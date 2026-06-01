---
title: Workflow — Publicação de Artefatos Finais
author: Exocórtex
created: 2026-05-30
updated: 2026-05-30
nature: processos
kind: workflow
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global, exocortex, acervo, google-drive]
authority: canonical
operational_mode: executable
stability: active
sources:
  - /home/elder/.hermes/acervo/global/tools/artifact_publish.py
  - /home/elder/.hermes/skills/exocortex/personal-artifact-workspace/SKILL.md
derived_from:
  - personal-artifact-workspace
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: exocortex/personal-artifact-workspace
  assumed_version: 1.0.1
  coupling: adapter-only
tags: [artifacts, drive, workflow, exports, receipts]
---

# Workflow — Publicação de Artefatos Finais

## Quando usar

Use este workflow quando o usuário pedir um artefato final para consumo humano: PDF, HTML, DOCX, XLSX, imagem, slide, ZIP, relatório, ofício ou material de aula.

Se o resultado for código versionável, use GitHub como destino primário. Se houver export final para consumo humano, publique esse export no Drive e registre no Acervo.

## Pré-requisitos

1. Carregar `personal-artifact-workspace`.
2. Carregar `acervo-manager`.
3. Carregar `productivity/google-workspace` se houver upload no Drive.
4. Aplicar `stop-slop` em prosa final.
5. Aplicar design/taste gate quando houver visual.

## Procedimento

1. Resolver microverso, tipo de artefato e destino humano.
2. Criar pacote com `artifact_publish.py init` ou equivalente.
3. Preservar fonte em `source/`.
4. Copiar assets para `assets/` com paths relativos.
5. Gerar exports finais em `exports/`.
6. Validar cada export: existência, tamanho, MIME e SHA-256.
7. Atualizar `manifest.json`.
8. Publicar exports no Drive privado do usuário.
9. Gravar `receipt.google_drive.json`.
10. Entregar ao usuário o link do Drive e o caminho local do pacote.
11. Se o artefato tiver valor cognitivo, criar página semântica no microverso apontando para o `artifact_id`.

## Comandos mínimos

```bash
python ~/.hermes/acervo/global/tools/artifact_publish.py init \
  --title "Título" \
  --microverso ensino \
  --source-md /caminho/source.md \
  --drive-path "exocortex/ensino/2026/aulas"

python ~/.hermes/acervo/global/tools/artifact_publish.py publish \
  --artifact-dir ~/.hermes/acervo/_artifacts/{artifact_id}
```

## Falha esperada já observada

OAuth válido não garante Drive API habilitada. Se o publish falhar com 403 de API desabilitada, registrar `receipt.google_drive.failed.json`, manter `manifest.status = failed`, habilitar Google Drive API no projeto OAuth e repetir o publish.

## Saída esperada

- pacote local em `~/.hermes/acervo/_artifacts/{artifact_id}`;
- `manifest.json` atualizado;
- `receipt.google_drive.json` ou `receipt.google_drive.failed.json`;
- link privado do Drive quando a publicação tiver sucesso;
- página semântica no microverso somente quando houver valor cognitivo.
