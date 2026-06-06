# DRAFT Issue — Google Drive quebra por SyntaxError em google_api.py

## Feature

EX-25 — Google Drive

## Prioridade

P0

## Comportamento observado

`python3 -m py_compile ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py` falhou com `SyntaxError` na linha 581.

Também estavam ausentes:

- `~/.hermes/google_token.json`
- `~/.hermes/google_client_secret.json`
- ADC/gcloud credentials

## Impacto

A integração de Google Workspace/Drive quebra antes de autenticar. Isso bloqueia busca, upload e publicação privada de artefatos.

## Critérios de aceite

- [ ] Corrigir string Python inválida no escape de query.
- [ ] Setup roda `py_compile` após patch de Drive.
- [ ] Search com apóstrofo (`O'Reilly`) funciona.
- [ ] Fluxo de auth ausente gera diagnóstico claro, não erro de sintaxe.
