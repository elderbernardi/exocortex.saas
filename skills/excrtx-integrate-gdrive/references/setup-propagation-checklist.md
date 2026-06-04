# Setup propagation checklist (Google Drive hardening)

Objetivo: garantir que o hardening de `drive search` não se perca em reprovisionamento.

## Escopo mínimo de propagação

Aplicar a função idempotente `patch_google_drive_search` em:
- setup do projeto (`.../exocortex.saas/setup.sh`)
- setup canônico do Hermes (`~/.hermes/setup.sh`)
- setup seed de artifacts (`.../plans/pdd_v2/artifacts/setup.sh`)

## Requisitos da função

1. Detecta estado já hardenizado (não reaplica).
2. Se `google_api.py` não existir, emite aviso e não quebra setup.
3. Substitui o bloco `drive_search` por versão com:
   - escape de query textual (`'`, `\\`)
   - `trashed = false` no modo não-raw
   - paginação por `nextPageToken`
   - validação `--max >= 1`

## Smoke test pós-setup

1. Auth:
`python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`

2. Busca acento:
`python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py drive search "relatório" --max 3`

3. Busca apóstrofo:
`python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py drive search "O'Reilly" --max 2`

4. Sintaxe setups:
`bash -n <setup.sh-alvo>`

## Pitfall

Aplicar hardening só no arquivo runtime (`google_api.py`) e esquecer setup gera regressão silenciosa na próxima máquina/perfil limpo.
