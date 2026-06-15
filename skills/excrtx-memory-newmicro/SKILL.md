---
name: excrtx-memory-newmicro
description: Criar novos Microversos no Acervo Cognitivo com estrutura wiki completa
  (SCHEMA, index, log, raw, 7 Natures).
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

        - Preencha o ''SCHEMA.md'' e substitua todos os placeholders como ''{MICROVERSO_NAME}''
        e ''{slug}'' em todos os arquivos gerados.

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
cp -r $EXOCORTEX_HOME/acervo/micro/_template/ $EXOCORTEX_HOME/acervo/micro/{slug}/
```

### 4. Fill SCHEMA.md

Open `$EXOCORTEX_HOME/acervo/micro/{slug}/SCHEMA.md` and populate the frontmatter:

```yaml
---
domain: {name}
slug: {slug}
type: {client|project|domain|role}
description: {description}
created: {YYYY-MM-DD}
---
```

Fill domain-specific conventions, tag taxonomy, and writing rules.

### 5. Replace Placeholders in All Files

Replace `{MICROVERSO_NAME}` and `{slug}` across **all** files in the Microverso. Scope:

- **7 Nature files:** `context.md`, `decisions.md`, `processes.md`, `tools.md`, `people.md`, `goals.md`, `constraints.md`
- **index.md:** Catalog of 7 Natures (each starts as "Empty — awaiting context")
- **log.md:** First creation entry
- **SCHEMA.md:** Already filled in step 4

Verify no placeholders remain:
```bash
grep -r '{MICROVERSO_NAME}\|{slug}' $EXOCORTEX_HOME/acervo/micro/{slug}/
# Expected: no results
```

### 6. Initialize Log

Create first entry in `log.md`:
```
## [{YYYY-MM-DD}] create | Microverso {name} created
Type: {type}. Natures: 7. Onboarding: {complete|partial|minimal}.
```

### 7. Onboarding Interview (Optional)

If the executive is available, collect:

| Area | Question | Destination |
|---|---|---|
| Tools | Which MCPs/APIs for this domain? | `tools.md` |
| Persona | Different tone of voice from global? | `context.md` |
| Rules | Domain-specific constraints? | `constraints.md` |
| Processes | Recurring workflows? | `processes.md` |
| Visual style | Custom palette? | `DESIGN.md` via `excrtx-quality-designsys` |

### 8. Register in System

- Update `$EXOCORTEX_HOME/acervo/shared/groups.md`: add slug to the corresponding type alias (CLIENTS, PROJECTS, etc.)
- Update `$EXOCORTEX_HOME/acervo/shared/glossario.md`: domain-specific terms
- Register in MEMORY.md via `excrtx-harness-promptlog`

## Pitfalls

1. **Placeholder residue:** Forgetting `{MICROVERSO_NAME}` or `{slug}` in any file leaves broken references. Always run `grep -r '{MICROVERSO_NAME}' micro/{slug}/` after creation. If residue found, re-execute step 5.
2. **groups.md not updated:** Microverso exists on disk but `shared/groups.md` doesn't list it — alias resolution fails silently. Verify with `grep {slug} shared/groups.md`.
3. **Template drift:** If `_template/` is updated after existing microversos were created, older ones won't have new Nature files. Check template version before creating.
4. **Wrong type classification:** Using `domain` when it should be `client` breaks group alias routing. Confirm type with executive before creating.
5. **Incomplete SCHEMA.md:** All 5 fields (domain, slug, type, description, created) are required. Partial SCHEMA breaks `excrtx-memory-manager` lookups.
6. **Hardcoded path:** Use `$EXOCORTEX_HOME/acervo/micro/{slug}/` (resolved from env), not `~/.hermes/acervo/micro/`.
7. **Missing template:** If `_template/` doesn't exist, `cp -r` fails silently with an empty directory. Always verify prerequisite (step 1).

## Verification

- [ ] Directory `$EXOCORTEX_HOME/acervo/micro/{slug}/` exists
- [ ] SCHEMA.md has complete frontmatter (domain, slug, type, description, created)
- [ ] index.md catalogs all 7 Natures
- [ ] log.md has creation entry
- [ ] raw/ and _archive/ exist (empty)
- [ ] 7 Nature files present: context, decisions, processes, tools, people, goals, constraints
- [ ] No residual placeholders: `grep -r '{MICROVERSO_NAME}' micro/{slug}/` returns empty
- [ ] `grep -r '{slug}' micro/{slug}/` returns empty (except legitimate SCHEMA references)
- [ ] context.md has at least the current scenario filled
- [ ] `shared/groups.md` updated with slug in correct type
- [ ] MEMORY.md records the Microverso creation
