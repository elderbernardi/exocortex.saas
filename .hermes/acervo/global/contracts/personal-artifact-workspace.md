---
title: Personal Artifact Workspace
created: 2026-05-30
updated: 2026-05-30
nature: instrucoes
kind: contract
scope_mode: global
scope_slug: null
applies_to: [exocortex, hermes, acervo, artifacts, google-drive]
authority: canonical
operational_mode: blocking
stability: experimental
sources:
  - user:2026-05-30-artifact-delivery-design
derived_from: []
confidence: high
promotion_policy: none
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
tags: [artifact-workspace, drive, reproducibility, draft-first]
---

# Personal Artifact Workspace

## Decisão

O Exocórtex publica artefatos finais por uma área operacional do Acervo, não por sincronização de diretórios.

Drive, OneDrive e serviços semelhantes são ferramentas de publicação. O Acervo continua sendo a fonte cognitiva. O Drive guarda o arquivo utilizável pelo usuário.

## Contrato

1. O agente gera artefatos em um pacote local autocontido.
2. O pacote vive em `~/.hermes/acervo/_artifacts/{artifact_id}/`.
3. A fonte padrão de documentos é Markdown.
4. Assets ficam junto do pacote, em paths relativos.
5. Exports finais ficam em `exports/`.
6. O publisher envia exports finais ao Drive privado do usuário.
7. O publisher grava receipt local com IDs e links do Drive.
8. Compartilhamento com terceiros exige Draft-First.
9. Código versionável usa GitHub, não Drive como destino primário.
10. O fluxo precisa ser reproduzível em outro Exocórtex-Hermes.

## Estrutura de pacote

```text
~/.hermes/acervo/_artifacts/{artifact_id}/
├── source/
│   ├── source.md              # fonte canônica para documentos, quando aplicável
│   └── metadata.yaml          # metadados humanos/editáveis opcionais
├── assets/
│   ├── images/
│   ├── data/
│   ├── logos/
│   ├── fonts/
│   ├── raw/
│   └── generated/
├── exports/
│   ├── *.pdf
│   ├── *.html
│   ├── *.docx
│   ├── *.xlsx
│   └── *.zip
├── manifest.json
└── receipt.google_drive.json
```

## Manifesto mínimo

```json
{
  "artifact_id": "art_YYYYMMDD_HHMMSS_slug",
  "title": "Título humano",
  "microverso": "ensino",
  "status": "draft|ready|published|failed",
  "source_type": "markdown|xlsx|image|mixed|external",
  "source_path": "source/source.md",
  "assets_dir": "assets",
  "exports": [],
  "drive_target": {
    "provider": "google_drive",
    "folder_path": "exocortex/inbox",
    "visibility": "private"
  },
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

## Receipt mínimo

```json
{
  "provider": "google_drive",
  "published_at": "ISO-8601",
  "folder_path": "exocortex/inbox",
  "folder_id": "drive-folder-id",
  "files": [
    {
      "export_path": "exports/arquivo.pdf",
      "drive_file_id": "drive-file-id",
      "web_view_link": "https://drive.google.com/...",
      "mime": "application/pdf",
      "visibility": "private"
    }
  ]
}
```

## Fonte Markdown

Markdown é a fonte padrão para documentos, planos, ofícios, relatórios, roteiros e materiais didáticos.

O agente deve gerar primeiro `source/source.md` e exportar depois para o formato pedido.

Exceções válidas:

- Planilhas: `.xlsx`, `.csv`, `.json` ou script gerador podem ser fonte.
- Imagens: `.svg`, `.png`, `.html`, `.excalidraw` ou prompt visual podem ser fonte.
- Apresentações: `.md` Marp ou `.pptx` podem ser fonte.
- PDFs recebidos: o PDF original pode ser fonte, com extração textual em `source/`.
- Documentos colaborativos vivos: o Drive pode ser fonte externa; o Acervo guarda link e manifesto.

## Assets

Assets pertencem ao pacote do artefato, não a uma pasta global sem contexto.

Use paths relativos no Markdown:

```md
![Capa](../assets/images/capa.png)
```

Assets reutilizáveis de marca ou identidade visual continuam em `macro/assets/` ou no design system. O pacote deve copiar apenas o que precisa para reproduzir o export.

## Publicação

Publicar significa copiar exports finais para o workspace do usuário e gravar receipt.

Upload privado para o Drive do próprio usuário conta como entrega pessoal. Criar permissão pública, link compartilhável amplo, email, publicação institucional ou envio a terceiros exige Draft-First.

## Provider inicial

O provider inicial é Google Drive via OAuth local do Hermes, usando `productivity/google-workspace`.

Composio pode atuar como fallback ou conector opcional. Não é dependência do core do Personal Artifact Workspace.

## Política de pastas no Drive

Default:

```text
exocortex/inbox
```

Quando o microverso estiver claro:

```text
exocortex/{microverso}/{ano}/{tipo}
```

Exemplos:

```text
exocortex/ensino/2026/aulas
exocortex/gabinete/2026/oficios
exocortex/dev/2026/artefatos
```

Se faltar contexto, o agente publica em `exocortex/inbox` e registra a decisão no manifesto.

## Reprodutibilidade

Qualquer replicação em outro Exocórtex-Hermes precisa destes elementos:

1. Este contrato.
2. Diretório `_artifacts/`.
3. Ferramenta `artifact_publish.py` ou provider equivalente.
4. OAuth/credencial do provider de Drive.
5. Política de pastas.
6. Receipts locais.
7. Regra Draft-First para compartilhamento.

## Critérios de aceite

- O artefato final fica acessível ao usuário no Drive.
- O agente recebe `webViewLink` ou falha com erro rastreável.
- O arquivo publicado mantém hash registrado.
- A fonte e assets permitem regenerar o export.
- O Acervo semântico não vira depósito indiscriminado de binários.
- O processo pode ser instalado em outro Hermes com os mesmos passos.
