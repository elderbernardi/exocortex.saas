# Task 10: Documentation Updates

**Status:** pending
**Depends on:** Task 08 (migration complete), Task 09 (syndic cron operational)
**Produces:** Updated documentation across Acervo and repo

## Context

After the lifecycle system is implemented, migrated, and operational, all documentation must reflect the new reality. Existing docs describe the old frontmatter schema, have no mention of deprecation/quarantine, and don't reference OKF alignment. This task closes that gap.

## Deliverables

### 1. Update `acervo/README.md`

Add sections for:
- Frontmatter schema overview (reference ADR-013, link to schema-spec.md)
- OKF v0.1 compatibility statement
- Deprecation policy summary (reference ADR-014)
- Quarantine lifecycle summary (reference ADR-015)
- `log.md` convention (reference Task 02 spec)
- `.quarantine/` directory explanation

### 2. Update `CLAUDE.md`

- Add frontmatter schema to the "Acervo Memory Structure" section
- Add deprecation/quarantine/syndic to the "Architecture" section
- Add `excrtx-memory-deprecate`, `excrtx-memory-quarantine`, `excrtx-memory-syndic` to skills list
- Add `validate_frontmatter.py` and `migrate_frontmatter.py` to "Common Commands"
- Document the `excrtx_type` field and explain the distinction from OKF `type`

### 3. Update `excrtx-memory-manager` SKILL.md

- Document the semantic revision hook: `WRITE` operation now calls `excrtx-memory-deprecate` before commit
- Document new frontmatter fields in the WRITE procedure
- Add `excrtx_type` to the legacy fields note
- Update the YAML frontmatter template to include OKF canonical fields + Acervo extensions
- Add `last_accessed_at` update to the READ procedure (agent updates this field on every read)
- Add deprecation awareness to the SEARCH procedure (skip `deprecated: true` files unless explicitly requested)
- Add quarantine awareness to the SEARCH procedure (skip `.quarantine/` entirely)

### 4. Update `skill-bundles/exocortex-alpha.yaml`

- Add `excrtx-memory-deprecate`
- Add `excrtx-memory-quarantine`
- Add `excrtx-memory-syndic`

### 5. Create `docs/plans/2026-06-19_acervo-lifecycle-okf/SCHEMA.md`

Consolidate the final schema (from Task 01 spec) into a standalone reference file that can be linked from anywhere. This is the canonical source of truth for frontmatter format — ADR-013 is the decision, SCHEMA.md is the spec.

### 6. Update `shared/groups.md` (if exists)

- Document `.quarantine/` as excluded from all groups and scopes

### 7. Update `_template/` microverso

- Ensure template frontmatter includes all OKF canonical + Acervo extension fields
- Add `log.md` template
- Add `excrtx_type` placeholder

## Verification

- [ ] `acervo/README.md` has sections for schema, deprecation, quarantine, OKF
- [ ] `CLAUDE.md` updated with new skills, commands, and architecture
- [ ] `excrtx-memory-manager` SKILL.md documents semantic revision hook and new fields
- [ ] `skill-bundles/exocortex-alpha.yaml` includes 3 new skills
- [ ] `SCHEMA.md` exists as standalone reference
- [ ] `_template/` microverso updated with new frontmatter
- [ ] No documentation references the old `type` field without noting `excrtx_type` rename
- [ ] `compile_soul.py` run after all skill updates
