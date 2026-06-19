# Task 08: Migrate Canonical Microversos to New Schema

**Status:** pending
**Depends on:** Task 01 (schema spec), Task 03 (validator)
**Produces:** All Acervo `.md` files with OKF-aligned frontmatter

## Context

All existing Acervo files need retroactive migration to the new frontmatter schema (ADR-013). This is a one-time operation. The migration must be best-effort: derive missing fields from git log where possible, apply sensible defaults where not.

## Scope

Migrate all `.md` files in:
- `$ACERVO/micro/` — all microversos except `_template/`
- `$ACERVO/global/` — all natures
- `$ACERVO/shared/` — cross-references

**Excluded:** `macro/` (identity — handled separately), `raw/` (immutable sources), `_archive/` (already archived), `_inbox/` (transient), `_artifacts/` (artifacts have their own manifest), `.quarantine/` (not yet populated).

## Migration Rules

### For each file:

1. **Parse existing frontmatter** (if any).

2. **Add OKF canonical fields:**
   - `type`: Derive from `nature` field if present:
     - `decisions` → `decision`
     - `knowledge` → `knowledge`
     - `context` → `context`
     - `reflections` → `reflection`
     - `contracts` → `memory` (contracts are conditional rules — closest OKF type)
     - `tools` → `artifact`
     - `workflows` → `artifact`
     - `templates` → `artifact`
     - `persona` → `context`
     - `prompts` → `artifact`
     - `skills` → `artifact`
     - If no `nature`: default to `memory`
   - `title`: Use existing `title` field, or derive from H1 heading, or from filename.
   - `description`: Use first non-heading line of body, truncated to 100 chars. If no body, use title.
   - `tags`: Use existing `tags` field, or `[]`.
   - `timestamp`: Use existing `created` field (date only), or derive from `git log --format=%ai --diff-filter=A -- <file>` (first commit date).

3. **Add Acervo extension fields:**
   - `class`: Derive from nature directory:
     - `decisions/`, `reflections/` → `perene`
     - Everything else → `volátil`
     - If file already has `class`, respect existing value.
   - `created_at`: Use existing `created` field + `T00:00:00Z` if no time, or derive from git log.
   - `last_accessed_at`: Set to `created_at` value (will be updated by agent at runtime).
   - `promoted_at`: Leave empty (only set on explicit promotion).

4. **Rename legacy `type` to `excrtx_type`:** The old `type` field (e.g., `type: fact`) collides with the OKF `type` field. Rename it to `excrtx_type` to preserve the data point without collision. If the old `type` field is absent, do not create `excrtx_type`.

5. **Retain other legacy fields:** `nature`, `confidence`, `sources`, `updated` — keep as-is. They coexist with new fields.

6. **Do NOT add deprecation/quarantine fields** — these are conditional and only added when triggered.

## Migration Script

Create `scripts/migrate_frontmatter.py`:

### Arguments:
- `--dry-run` — show what would change without modifying files
- `--dir <path>` — target directory (default: `$ACERVO`)
- `--verbose` — show per-file changes

### Logic:
1. Walk directory tree, find all `.md` files.
2. Skip excluded paths.
3. For each file: parse frontmatter, apply migration rules, write back.
4. Track statistics: files scanned, files modified, files already compliant.
5. After migration, run `validate_frontmatter.py --dir <path> --report` to verify.

## Canonical Microversos to Migrate

Based on current Acervo structure:

| Microverso | Slug | Estimated Files |
|------------|------|-----------------|
| Comercial | `comercial` | TBD |
| Ensino | `ensino` | TBD |
| Estúdio Criativo | `estudio-criativo` | TBD |
| Exocórtex | `excrtx` | TBD |
| Exocórtex Dev | `exocortex-dev` | TBD |
| Exocórtex Ops | `exocortex-ops` | TBD |
| Gabinete | `gabinete` | TBD |
| Hermes Setup | `hermes-setup` | TBD |
| Projeto Alpha | `projeto-alpha` | TBD |
| Sales AI | `sales-ai` | TBD |

Plus `global/` natures.

## Verification

```bash
# Dry run first
python3 scripts/migrate_frontmatter.py --dry-run --dir "$ACERVO" --verbose

# Actual migration
python3 scripts/migrate_frontmatter.py --dir "$ACERVO"

# Validate
python3 scripts/validate_frontmatter.py --dir "$ACERVO" --report
echo "Exit: $?"  # should be 0 if all files migrated correctly
```

- [ ] Migration script exists at `scripts/migrate_frontmatter.py`
- [ ] Dry run produces report without modifying files
- [ ] All microverso files have `type`, `title`, `description`, `tags`, `timestamp`
- [ ] All files have `class` and `created_at`
- [ ] `class` derived correctly from nature directory
- [ ] `timestamp` derived from git log where `created` was missing
- [ ] Validator passes on 100% of migrated files
- [ ] No file content (body) modified — only frontmatter
- [ ] Legacy fields retained
