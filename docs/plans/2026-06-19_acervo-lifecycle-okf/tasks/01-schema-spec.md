# Task 01: Define Frontmatter Schema Specification

**Status:** pending
**Depends on:** ADR-013, ADR-017
**Produces:** `docs/plans/2026-06-19_acervo-lifecycle-okf/schema-spec.md`

## Context

The Acervo Cognitivo needs a standardized frontmatter schema. ADR-013 defines the schema at a high level. This task produces the **detailed specification** — field-by-field documentation with types, constraints, examples, and edge cases — that downstream tasks (validator script, migration, skills) will reference.

## Deliverable

Create `docs/plans/2026-06-19_acervo-lifecycle-okf/schema-spec.md` containing:

### Section 1: Field Reference Table

For each field (OKF canonical + Acervo extension + deprecation + quarantine):
- Field name
- Type (string, boolean, ISO 8601 datetime, list[string])
- Required vs. optional vs. conditional
- Constraints (e.g., `type` must be one of: `decision`, `memory`, `reflection`, `context`, `knowledge`, `artifact`)
- Example value

### Section 2: Complete Examples

Provide 4 complete frontmatter examples:
1. **New volatile knowledge** — freshly created, no deprecation.
2. **Deprecated memory** — superseded by a newer file.
3. **Promoted artifact** — was volatile, now promoted to perene.
4. **Quarantined file** — in quarantine with expiry.

### Section 3: Migration Rules

For each legacy field, document the migration rule:
- Old field name → new field name (or "retained").
- Default value if old field is missing (e.g., if no `class` → default to `volátil` for `knowledge/` and `context/`, `perene` for `decisions/` and `reflections/`).
- How to derive `timestamp` and `created_at` if missing (use git log first-commit date).

### Section 4: Validation Rules

List all deterministic validation rules that the validator script (Task 03) will check:
- OKF canonical fields present (type, title, description, tags, timestamp)
- `class` present and is `perene` or `volátil`
- `created_at` present and valid ISO 8601
- If `deprecated: true` → `deprecated_at` and `deprecated_reason` present
- If `quarantined_at` present → `quarantine_reason` and `quarantine_expires_at` present
- `type` value is from the allowed vocabulary

## Verification

- [ ] Spec file exists at the expected path
- [ ] All fields from ADR-013 are documented
- [ ] 4 complete examples provided
- [ ] Migration rules cover all legacy fields
- [ ] Validation rules are deterministic and testable
