# Drive path governance for final artifact publishing

Contexto consolidado da sessão:

- Upload direto com `google_api.py drive upload` pode cair na raiz do Drive quando `--parent` não é resolvido.
- Para artefato final do Exocórtex, o fluxo correto é `artifact_publish.py` com manifesto + receipt.

## Regra operacional durável

1. Resolver `drive_target.folder_path` antes do upload.
2. Garantir parent explícito no upload final.
3. Considerar upload em raiz do Drive como falha de governança.
4. Corrigir com republicação em pasta correta e registrar receipt.

## Convenção de path

Use paths em lowercase para consistência:

- `exocortex/inbox` (fallback)
- `exocortex/microverso/<dominio>/...` quando o microverso estiver claro

## Verificação mínima

- `manifest.json` contém `drive_target.folder_path` não vazio.
- `receipt.google_drive.json` contém `folder_id` e `folder_path`.
- `drive get <file_id>` retorna `parents` igual ao folder de destino (não raiz).
