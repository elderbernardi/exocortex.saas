# Task 04: Write `excrtx-memory-deprecate` Skill

**Status:** pending
**Depends on:** Task 01 (schema spec), ADR-014, ADR-016
**Produces:** `skills/excrtx-memory-deprecate/SKILL.md`
**Judge required:** Yes — must reach verdict `PASS` before promotion

## Context

This skill implements the semantic revision protocol (ADR-016). It is called by `excrtx-memory-manager` during the `WRITE` operation, after the Domain Filter and before the file is committed to disk. Its job: detect if the new file contradicts an existing one, and if so, deprecate the old one.

## Skill Specification

### Frontmatter Requirements

```yaml
---
name: excrtx-memory-deprecate
description: "Semantic revision on insert — detects contradictions between new and existing Acervo memories, deprecates superseded files automatically."
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, acervo, deprecation, semantic-revision, lifecycle]
    related_skills: [excrtx-memory-manager, excrtx-memory-quarantine, excrtx-memory-syndic]
compiled_rules: |
  - On every new file creation in knowledge/, context/, contracts/, tools/ natures, run semantic revision check.
  - Search target microverso for overlapping files (tag overlap, title similarity, entity matching).
  - If direct contradiction found: deprecate old file (set deprecated: true, deprecated_at, deprecated_reason), add Supersedes link in new file.
  - If ambiguity: do not deprecate, flag for executive review.
  - Never deprecate perene files or files with promoted_at set.
  - Never deprecate across microversos (domain isolation).
  - Log every deprecation in the microverso's log.md.
---
```

### Required Body Sections

The SKILL.md body must include:

1. **`## When to Use`** — triggers: new file creation in applicable natures, called by memory-manager.
2. **`## When NOT to Use`** — don't trigger for decisions/, reflections/, raw/, macro/.
3. **`## Procedure`** — the 4-step protocol from ADR-016 (detect overlap → compare truth → deprecate predecessor → handle ambiguity).
4. **`## Scope Rules`** — domain isolation, search scope per write target (from ADR-016).
5. **`## Deprecation Format`** — exact YAML fields to set on old file, exact markdown link to add to new file, exact log.md entry format.
6. **`## Pitfalls`** — false positive deprecations, cross-microverso contamination, forgetting to update log.md, deprecating perene files.
7. **`## Verification`** — checklist: overlap search performed, contradiction confirmed before deprecating, old file has all deprecation fields, new file has Supersedes link, log.md updated.

### Key Behavioral Rules

- **Conservative detection:** Only deprecate on clear, direct contradictions. When in doubt, flag — don't deprecate.
- **Domain isolation:** Never search or deprecate across microverso boundaries.
- **Perene immunity:** `class: perene` and `promoted_at` files are never auto-deprecated.
- **Log everything:** Every deprecation produces a `log.md` entry.
- **Idempotent:** Running the check twice on the same file should not produce duplicate deprecations.

## Skill Judgment Pipeline

After drafting the SKILL.md:

```bash
# D1 structural check (deterministic)
python3 scripts/skill_judge.py --skill excrtx-memory-deprecate --d1-only

# If D1 passes, full 5-dimension judge
python3 scripts/skill_judge.py --skill excrtx-memory-deprecate
```

- D1 failing → fix mechanically (add missing sections, fix frontmatter).
- Verdict `IMPROVE` → apply judge recommendations, re-run.
- Verdict `REWRITE` → structural rewrite.
- **Verdict `PASS` required before promotion to bundle.**

### Integration Test

After judge passes:
1. Create a test microverso with 2 knowledge files (one about "model is X").
2. Write a new file saying "model is Y".
3. Trigger the deprecate skill.
4. Verify: old file has `deprecated: true`, new file has `Supersedes` link, `log.md` has entry.

## Verification

- [ ] SKILL.md exists at `skills/excrtx-memory-deprecate/SKILL.md`
- [ ] D1 structural check passes
- [ ] Full judge verdict = `PASS`
- [ ] Integration test: old file deprecated on contradiction
- [ ] Integration test: ambiguous overlap does not deprecate
- [ ] Integration test: perene file not deprecated
- [ ] Skill added to `skill-bundles/exocortex-alpha.yaml`
- [ ] `compile_soul.py` run after adding compiled_rules
