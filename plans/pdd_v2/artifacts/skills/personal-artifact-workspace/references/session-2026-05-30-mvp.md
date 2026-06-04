# Session 2026-05-30 — Personal Artifact Workspace MVP

## Contexto

O usuário queria uma forma orgânica de entregar artefatos finais gerados pelo Exocórtex em gateways remotos. A decisão inicial considerou signed URLs/S3, mas o usuário corrigiu a direção: em uso pessoal, o arquivo pertence ao usuário e deve ir para o esquema de trabalho dele.

## Decisões

1. Drive é ferramenta de publicação, não mecanismo de sincronização.
2. O Acervo não deve ser sincronizado inteiro com Drive.
3. Criar uma área operacional `_artifacts/` para pacotes autocontidos.
4. Markdown é fonte padrão para documentos, com exceções para planilhas, imagens, slides complexos e documentos externos.
5. Exports finais são publicados no Drive privado do usuário.
6. Receipts locais registram `file_id`, link, status, MIME, hash e provider.
7. Compartilhamento com terceiros continua Draft-First.
8. OAuth local do Hermes/Google Workspace é provider inicial; Composio fica como fallback futuro.

## Arquivos criados no Acervo

```text
~/.hermes/acervo/global/contracts/personal-artifact-workspace.md
~/.hermes/acervo/global/tools/personal-artifact-publisher.md
~/.hermes/acervo/global/tools/artifact_publish.py
~/.hermes/acervo/_artifacts/README.md
```

## Ferramenta criada

`artifact_publish.py` suporta:

```bash
python ~/.hermes/acervo/global/tools/artifact_publish.py init \
  --title "Título" \
  --microverso ensino \
  --source-md /caminho/source.md \
  --drive-path "exocortex/ensino/2026/aulas"

python ~/.hermes/acervo/global/tools/artifact_publish.py publish \
  --artifact-dir ~/.hermes/acervo/_artifacts/{artifact_id}
```

## Teste feito

Foi criado um pacote de teste:

```text
~/.hermes/acervo/_artifacts/art_20260530_141313_teste-personal-artifact-workspace
```

O pacote continha fonte Markdown e export HTML. A publicação falhou porque a Google Drive API estava desabilitada no projeto OAuth, apesar de o token local estar autenticado.

## Lição técnica

`setup.py --check` valida token OAuth. Não garante que a API específica do Google Cloud esteja habilitada.

Quando ocorrer `HttpError 403` com mensagem de API desabilitada:

1. Habilitar Google Drive API no projeto OAuth.
2. Aguardar propagação.
3. Reexecutar `publish`.
4. Manter `receipt.google_drive.failed.json` como trilha de auditoria.

## Preferência do usuário capturada

Decisões, harnesses e processos do Exocórtex-Hermes devem ser registrados de forma reprodutível para replicação em outros ambientes.
