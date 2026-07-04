---
schema: acervo/v0.2
type: contract
title: Especificação do pacote de microverso (excrtx/v1 + formato .mvpkg)
description: Schema do microverso.yaml e formato portátil .mvpkg para export/import de microversos.
tags: [exocortex, microverso, package, excrtx-v1, mvpkg, okf]
timestamp: 2026-06-20
class: perene
status: active
created_at: 2026-06-20T00:00:00Z
last_accessed_at: 2026-06-20T00:00:00Z
updated: 2026-06-20
nature: contracts
excrtx_type: rule
kind: contract
scope_mode: global
scope_slug: null
authority: canonical
operational_mode: blocking
stability: stable
sources: [issue-55, issue-87, issue-88, issue-95, issue-96, adr-013, adr-017]
---

# Especificação do pacote de microverso — `excrtx/v1` + formato `.mvpkg`

Define como um microverso é **empacotado** (export) e **instalado** (import) de
forma portátil e autossuficiente — análogo a uma imagem Docker: *"se roda no meu
Exocortex, roda no seu"*. Resolve #55 sob as verdades atuais (formato `excrtx/v1`,
épico #87, e conformidade OKF v0.1 — `docs/plans/2026-06-19_acervo-lifecycle-okf/`).

Ferramentas de referência: `acervo/global/tools/microverso_package.py` (export),
`acervo/global/tools/microverso_install.py` (import),
`acervo/global/tools/microverso_schema.py` (validador de manifesto).

## Manifesto `microverso.yaml` (`excrtx/v1`)

```yaml
apiVersion: excrtx/v1          # obrigatório, valor fixo
kind: Microverso               # obrigatório, valor fixo
metadata:
  name: <slug>                 # obrigatório, kebab-case
  version: <semver X.Y.Z>      # obrigatório
  description: <string>        # obrigatório
  author: <string>            # opcional
  tags: [<string>, ...]        # opcional
requires:                      # opcional — dependências (verificadas no import)
  skills: [excrtx-..., ...]    # skills referenciadas; str ou {name, bundled, version}
  python_packages: [pkg>=x]    # pins Python (vão para deps/requirements.txt)
  node_packages: [...]
  mcps: [...]                  # integrações MCP (config em integrations/mcps.yaml)
  env: [VAR_NAME, ...]         # nomes de segredos exigidos (env.example) — NUNCA valores
  system: [git, python3, ...]  # binários de sistema exigidos (preflight)
compat:                        # checado no import ("roda aqui?")
  exocortex_version: <range>
  hermes_version: <range>
  platforms: [linux, ...]
tree:                          # diretório -> descrição (documentação)
  knowledge/: "..."
hooks:                         # opcional — paths relativos, sem '..' nem absolutos
  post_install: "scripts/post_install.sh"
  validate: "scripts/validate.sh"
provenance:                    # preenchido pelo export
  built_at: <ISO8601>
  builder_version: <string>
  content_digest: <sha256>     # digest do payload (acervo + skills)
```

## Formato `.mvpkg` (Docker-like)

Diretório `{slug}-v{version}.mvpkg/` (ou tarball `.mvpkg.tar.gz`):

```
microverso.yaml      # manifesto enriquecido (= Dockerfile + image meta)
MANIFEST.sum         # sha256 de cada arquivo (= digest/integridade)
INSTALL.md           # resumo humano do que será instalado
env.example          # nomes de env vars/segredos (= ENV); sem valores
acervo/              # dados cognitivos do microverso (clean portable)
skills/              # skills excrtx-* embutidas (SKILL.md + scripts)
deps/requirements.txt# pins Python (e node-packages.txt se houver)
integrations/mcps.yaml# configs de MCP/integração (sem segredos)
```

## Regras de empacotamento (clean portable)

- **Excluir**: `.quarantine/`, `_archive/`, `__pycache__/`, `.git/`, `_meta/snapshots|drafts/`,
  `.DS_Store`; `raw/` salvo `--include-raw`.
- **Remover** `last_accessed_at` do frontmatter (estado de runtime por instância).
- **Descartar** arquivos `deprecated: true` salvo `--include-deprecated`.
- **Gate OKF**: todo `.md` deve passar `scripts/validate_frontmatter.py` **antes** de empacotar.
- **Segredos** nunca entram no pacote — só os *nomes* das env vars em `env.example`.
- **Software de sistema** é declarado (`requires.system`) e verificado no import, **não** embutido.

## Resolução de colisão de skill (import)

Para cada skill embutida em `skills/<name>/`, contra `$HERMES_HOME/skills/excrtx/<name>/`:

| Situação | Ação |
|---|---|
| Não existe no alvo | instalar |
| Existe, conteúdo idêntico (hash) | skip |
| Existe, incoming com **semver maior** (mesma linhagem) | UPDATE (só com `--update-skills`; senão report) |
| Existe, conteúdo divergente / não-upgrade | **renomear** incoming para `<name>-<slug>`, reescrever referências no microverso, manter a existente |

## Contrato de round-trip

`export → import` em instância limpa deve produzir um microverso íntegro:
manifesto válido (`excrtx/v1`), `MANIFEST.sum` confere, OKF passa, skills
resolvidas e registro em `global/_meta/microversos.yaml` (append-only).
