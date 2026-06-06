# DRAFT Issue — Artifact ID preserva acento no slug

## Feature

EX-22 — Artifacts Manager

## Prioridade

P2

## Comportamento observado

O artifact package criado no dogfood gerou ID com caractere acentuado:

`art_20260606_145903_dogfood-ex22-relatório-pedagóg`

## Comportamento esperado

`artifact_id` deve ser ASCII-safe e URL/shell-safe. O nome humano pode manter acentos via `friendly_name`.

## Impacto

Paths, URLs, ZIPs, manifests e integrações externas podem falhar ou ficar inconsistentes.

## Critérios de aceite

- [ ] Slugify remove acentos e caracteres inseguros no `artifact_id`.
- [ ] `friendly_name` preserva nome humano com acentos.
- [ ] Teste cobre entrada com acento.
