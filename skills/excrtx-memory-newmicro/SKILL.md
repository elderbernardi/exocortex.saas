---
name: excrtx-memory-newmicro
description: Criar novos Microversos no Acervo Cognitivo com estrutura wiki completa
  (_meta SCHEMA/index/log, raw, _archive, 11 Natures).
version: 2.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - microverso
    - acervo
    - creation
    - onboarding
    - wiki
    related_skills:
    - excrtx-memory-manager
    - excrtx-memory-mvinstall
    - excrtx-memory-mvsetup
    - excrtx-quality-designsys
    calibration:
    - feature_id: EX-13
      calibration_prompt: 'Ao ser solicitado a criar ou iniciar um novo domínio/contexto
        de atuação, ative a skill de criação de microverso:

        - Solicite ao executivo (se ausente): Nome legível, Slug (kebab-case), Type
        (client|project|domain|role) e Description.

        - Copie recursivamente o template ''micro/_template/'' para ''micro/{slug}/''.

        - Preencha o ''_meta/SCHEMA.md'' (frontmatter OKF) e substitua todos os placeholders
        ''{{DOMAIN_NAME}}'', ''{{DOMAIN_DESCRIPTION}}'' e ''{{CREATED_DATE}}'' em todos os arquivos;
        preencha as ''description'' vazias dos _seed.md e valide com validate_frontmatter.

        - Registre o novo microverso em ''shared/groups.md'' no alias correspondente
        e crie uma entrada de log em ''log.md'' e no ''MEMORY.md'' global.'
      test_prompt: Crie un novo microverso para gerenciar a nossa consultoria para
        o 'Cliente XPTO'.
      acceptance_criteria: O agente deve requisitar as informações em falta (Slug,
        Type, Description) ou demonstrar o clone da estrutura base do template e substituição
        de placeholders nos arquivos.
      remediation_tip: 'Falha no Provisionamento: O microverso deve ser inicializado
        copiando o template completo e ajustando todos os placeholders e SCHEMA.'
---
# Create New Microverso

Provisions a new operational domain in the executive's Acervo Cognitivo.
Generates a complete wiki structure compatible with `excrtx-memory-manager`.

## When to Use

- Executive mentions a new operational domain
- A task requires domain context that doesn't yet exist in the acervo
- Executive explicitly requests creating a new Microverso

**Don't use for:**
- Editing an existing Microverso → use `excrtx-memory-manager`
- Installing an external package → use `excrtx-memory-mvinstall`
- Seed configuration → use `excrtx-memory-mvsetup`
- One-off notes that don't require persistent domain context

> **Vector:** Classified as **Evolution** (new operational domain creation).

## Procedure

### 1. Verify Prerequisites

Confirm the template directory exists:
```bash
ls $EXOCORTEX_HOME/acervo/micro/_template/
```
If missing, abort and inform the executive that the base template must be created first via `excrtx-memory-mvsetup`.

### 2. Collect Microverso Definition

Ask the executive (if not already specified):

| Field | Format | Example |
|---|---|---|
| **Name** | Human-readable | "Produto Alpha" |
| **Slug** | kebab-case | `produto-alpha` |
| **Type** | `client\|project\|domain\|role` | `project` |
| **Description** | One-sentence scope | "Lifecycle management for Produto Alpha" |

### 3. Copy Template

```bash
cp -r $EXOCORTEX_HOME/acervo/micro/_template/. $EXOCORTEX_HOME/acervo/micro/{slug}/
```

The template ships **14 diretórios** conforme o contrato canônico
(`global/contracts/microverso-directory-structure.md`):
11 natures (`context/`, `knowledge/`, `contracts/`, `prompts/`, `persona/`,
`workflows/`, `skills/`, `tools/`, `templates/`, `decisions/`, `reflections/`)
— cada uma com `_seed.md` — mais 3 diretórios de infraestrutura:
`_meta/` (`SCHEMA.md`, `index.md`, `log.md`), `raw/` e `_archive/`.

### 4. Fill `_meta/SCHEMA.md` and `microverso.yaml`

`SCHEMA.md` lives in `$EXOCORTEX_HOME/acervo/micro/{slug}/_meta/SCHEMA.md` and carries the
**OKF v0.1 superset** frontmatter (see `docs/plans/2026-06-19_acervo-lifecycle-okf/SCHEMA.md`),
not the legacy `domain/slug/type/created` block:

```yaml
---
type: context
title: {name} — Schema
description: {one-line scope}
tags: [{slug}, schema]
timestamp: {YYYY-MM-DD}
class: perene
created_at: {YYYY-MM-DD}T00:00:00Z
nature: context
---
```

Set `slug`, `name`, `type`, `description`, `created` in `microverso.yaml`. Fill domain
conventions and tag taxonomy in the body.

### 5. Replace Placeholders in All Files

The template uses **double-brace tokens**. Replace **every** occurrence across all files:

| Token | Replace with |
|---|---|
| `{{DOMAIN_NAME}}` | the human name |
| `{{DOMAIN_DESCRIPTION}}` | the one-line scope |
| `{{CREATED_DATE}}` | `{YYYY-MM-DD}` (today, ISO date) |
| `{{MICROVERSO_SLUG}}` | the kebab-case slug |
| `{{micro_type}}` | `client\|project\|domain\|role` |
| `{{NOME_CLIENTE}}` / `{{PRAZO}}` / `{{VALOR}}` | contract-template values (in `contracts/`) |

Each `_seed.md` ships `description: ""` — **fill a non-empty, single-line description** per
Nature (empty `description` fails validation rule V-024).

Verify no placeholders remain (matches the **actual** token shape):
```bash
grep -rE '\{\{[A-Z_]+\}\}' $EXOCORTEX_HOME/acervo/micro/{slug}/
# Expected: no results
```

### 6. Initialize Log

Append the first entry to `_meta/log.md` per the log convention (single `# Log` H1,
`## YYYY-MM-DD` heading, single-line bullet):
```
## {YYYY-MM-DD}
- CREATED: micro/{slug}/ (perene) — Microverso {name} created ({type}, 11 natures)
```

### 7. Verify the Scaffold (gate — do NOT skip)

The microverso must pass the frontmatter validator before it is considered created
(EX-49 — print the raw output):
```bash
python3 $EXOCORTEX_HOME/../exocortex.saas/scripts/validate_frontmatter.py --dir $EXOCORTEX_HOME/acervo/micro/{slug}/
# Expected: every file PASS, exit 0
```
If any file FAILs, fix it before proceeding. Common causes: leftover `{{...}}` tokens,
empty `description`, or `_meta/`/`_seed.md` missing OKF fields.

### 8. Onboarding Interview (Optional)

If the executive is available, collect:

| Area | Question | Destination |
|---|---|---|
| Tools | Which MCPs/APIs for this domain? | `tools.md` |
| Persona | Different tone of voice from global? | `context.md` |
| Rules | Domain-specific constraints? | `constraints.md` |
| Processes | Recurring workflows? | `processes.md` |
| Visual style | Custom palette? | `DESIGN.md` via `excrtx-quality-designsys` |

### 9. Register in System

- Update `$EXOCORTEX_HOME/acervo/shared/groups.md`: add slug to the corresponding type alias (CLIENTS, PROJECTS, etc.)
- Update `$EXOCORTEX_HOME/acervo/shared/glossario.md`: domain-specific terms
- Register in MEMORY.md via `excrtx-harness-promptlog`

## Pitfalls

1. **Placeholder residue:** Leftover `{{DOMAIN_NAME}}`, `{{DOMAIN_DESCRIPTION}}` or `{{CREATED_DATE}}` in any file leaves broken references and fails validation. Always run `grep -rE '\{\{[A-Z_]+\}\}' micro/{slug}/` after creation (the tokens are **double-brace**, not `{slug}`). If residue found, re-execute step 5.
2. **groups.md not updated:** Microverso exists on disk but `shared/groups.md` doesn't list it — alias resolution fails silently. Verify with `grep {slug} shared/groups.md`.
3. **Template drift:** If `_template/` is updated after existing microversos were created, older ones won't have new Nature files. Check template version before creating.
4. **Wrong type classification:** Using `domain` when it should be `client` breaks group alias routing. Confirm type with executive before creating.
5. **Incomplete SCHEMA.md:** All 5 fields (domain, slug, type, description, created) are required. Partial SCHEMA breaks `excrtx-memory-manager` lookups.
6. **Hardcoded path:** Use `$EXOCORTEX_HOME/acervo/micro/{slug}/` (resolved from env), not `~/.hermes/acervo/micro/`.
7. **Missing template:** If `_template/` doesn't exist, `cp -r` fails silently with an empty directory. Always verify prerequisite (step 1).

## Verification

- [ ] Directory `$EXOCORTEX_HOME/acervo/micro/{slug}/` exists
- [ ] `_meta/SCHEMA.md` has complete OKF frontmatter; `microverso.yaml` set (slug, name, type, description, created)
- [ ] `_meta/index.md` catalogs all 11 Natures
- [ ] `_meta/log.md` has the creation entry (log-convention format)
- [ ] raw/ and _archive/ exist (empty)
- [ ] 11 Nature directories present, each with `_seed.md`: context, knowledge, contracts, prompts, persona, workflows, skills, tools, templates, decisions, reflections
- [ ] Every `_seed.md` has a non-empty `description`
- [ ] No residual placeholders: `grep -rE '\{\{[A-Z_]+\}\}' micro/{slug}/` returns empty
- [ ] **Validator gate passes:** `validate_frontmatter.py --dir micro/{slug}/` exits 0 (all PASS)
- [ ] context/_seed.md has at least the current scenario filled
- [ ] `shared/groups.md` updated with slug in correct type
- [ ] MEMORY.md records the Microverso creation
