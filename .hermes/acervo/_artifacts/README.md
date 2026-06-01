# Exocortex Artifacts

Área operacional para pacotes de artefatos finais do Exocórtex.

Esta pasta não substitui a ontologia do Acervo. Ela guarda fontes, assets, exports, manifestos e receipts necessários para reproduzir e publicar artefatos.

Contrato canônico:
`global/contracts/personal-artifact-workspace.md`

Ferramenta inicial:
`global/tools/artifact_publish.py`

Regras:

1. Cada artefato vive em um diretório `art_*` autocontido.
2. Documentos usam `source/source.md` como fonte padrão.
3. Assets ficam em `assets/` com paths relativos.
4. Exports finais ficam em `exports/`.
5. Publicação em Drive grava `receipt.google_drive.json`.
6. Falhas de publicação gravam `receipt.google_drive.failed.json`.
7. Compartilhamento com terceiros exige Draft-First.
