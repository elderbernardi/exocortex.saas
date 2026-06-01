---
title: Personal Artifact Publisher
created: 2026-05-30
updated: 2026-05-30
nature: ferramentas
kind: tool
scope_mode: global
scope_slug: null
applies_to: [exocortex, hermes, acervo, artifacts, google-drive]
authority: canonical
operational_mode: executable
stability: experimental
sources:
  - global/contracts/personal-artifact-workspace.md
derived_from: []
confidence: high
promotion_policy: none
upstream:
  source_skill: productivity/google-workspace
  assumed_version: 1.1.0
  coupling: adapter-only
tags: [artifact-publisher, google-drive, oauth, reproducibility]
---

# Personal Artifact Publisher

Ferramenta local para publicar exports finais do Exocórtex no Drive privado do usuário.

## Local

```text
~/.hermes/acervo/global/tools/artifact_publish.py
```

## Pré-requisitos

```bash
python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
```

A saída precisa conter `AUTHENTICATED`.

## Uso mínimo

Publicar todos os arquivos em `exports/` de um pacote:

```bash
python ~/.hermes/acervo/global/tools/artifact_publish.py publish \
  --artifact-dir ~/.hermes/acervo/_artifacts/art_20260530_141000_teste \
  --drive-path "exocortex/inbox"
```

Criar um pacote a partir de Markdown:

```bash
python ~/.hermes/acervo/global/tools/artifact_publish.py init \
  --title "Plano de Aula - APIs REST" \
  --microverso ensino \
  --source-md /caminho/source.md
```

## Comportamento

- Cria pacote em `~/.hermes/acervo/_artifacts/{artifact_id}`.
- Mantém fonte em `source/`.
- Mantém assets em `assets/`.
- Publica apenas arquivos de `exports/`.
- Cria pastas no Drive se não existirem.
- Faz upload privado por padrão.
- Grava `manifest.json` e `receipt.google_drive.json`.
- Imprime JSON com links do Drive.

## Segurança

A ferramenta não cria permissão pública e não compartilha com terceiros.

Compartilhamento usa outro passo, com Draft-First obrigatório.

## Troubleshooting

### Google Drive API desabilitada

Sintoma:

```text
HttpError 403: Google Drive API has not been used in project ... or it is disabled
```

Correção:

1. Abrir o link indicado pelo erro no Google Cloud Console.
2. Habilitar Google Drive API no projeto OAuth usado pelo Hermes.
3. Aguardar a propagação por alguns minutos.
4. Rodar novamente:

```bash
python ~/.hermes/acervo/global/tools/artifact_publish.py publish \
  --artifact-dir ~/.hermes/acervo/_artifacts/{artifact_id}
```

A autenticação OAuth pode estar válida mesmo quando a API do projeto está desabilitada. `setup.py --check` valida token; não prova que cada API do Google Cloud está ativa.

## Notas

A ferramenta usa o wrapper `google_api.py` da skill `google-workspace`. Isso evita Composio no MVP e mantém o fluxo sob OAuth local do Hermes.
