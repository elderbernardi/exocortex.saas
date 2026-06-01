---
name: exocortex-google-drive-hardening
description: Hardening operacional do Google Drive search no skill google-workspace. Garante escape de query, filtro de lixeira por padrão, paginação e validação de input no setup.
version: 1.0.0
category: exocortex
metadata:
  hermes:
    tags: [exocortex, google-drive, setup, hardening, reproducibility]
---

# Exocórtex — Google Drive Hardening

## Objetivo

Padronizar e tornar reprodutível o hardening do comando `drive search` no `google-workspace`, sem depender de ajuste manual pós-setup.

## Quando usar

Use quando:
- for preparar ou atualizar setup do Exocórtex (`setup.sh` do projeto, microverso ou seed);
- houver regressão no `drive search` (erro com apóstrofo, retorno parcial, lixo misturado);
- for portar o ambiente para novo Hermes.

Não use quando:
- o objetivo for mudar comportamento de API de escrita (upload/share/delete);
- a mudança for específica de um único projeto temporário.

## Escopo técnico do hardening

Ajustes exigidos no `drive search` de `google_api.py`:
1. Escape seguro de aspas simples na query (`'` → `\'`).
2. Filtro padrão `trashed = false` no modo não-raw.
3. Paginação automática com `nextPageToken` até cumprir `--max`.
4. Validação de entrada (`--max >= 1`).

## Arquivos-alvo de setup

- `/home/elder/projetos/pessoal/exocortex.saas/setup.sh`
- `/home/elder/.hermes/setup.sh`
- `/home/elder/projetos/pessoal/exocortex.saas/plans/pdd_v2/artifacts/setup.sh`

Cada setup deve conter função idempotente `patch_google_drive_search` e executá-la no fluxo principal.

## Verificação rápida

1) Auth
`python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`

2) Busca com acento
`python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py drive search "relatório" --max 3`

3) Busca com apóstrofo
`python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py drive search "O'Reilly" --max 2`

4) Smoke de setup
`bash -n /home/elder/projetos/pessoal/exocortex.saas/setup.sh`
`bash -n /home/elder/.hermes/setup.sh`
`bash -n /home/elder/projetos/pessoal/exocortex.saas/plans/pdd_v2/artifacts/setup.sh`

## Regra de publicação de artefato final

Hardening de busca não substitui governança de publicação.

Para artefato final do Exocórtex:
- usar `artifact_publish.py` (manifest + receipt);
- resolver `drive_target.folder_path` antes do upload;
- publicar com parent explícito;
- tratar upload na raiz do Drive como falha de processo.

## Critério de pronto

- setup aplica patch automaticamente;
- execução repetida não duplica patch (idempotência);
- `drive search` suporta query com apóstrofo;
- resultados não incluem itens na lixeira por padrão;
- paginação retorna até o limite de `--max`;
- publicação final usa pasta resolvida (nunca raiz) e gera receipt.
