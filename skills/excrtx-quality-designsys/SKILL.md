---
name: excrtx-quality-designsys
description: Persist, resolve, and validate visual tokens in the Acervo Cognitivo. Fork of design-md adapted to the macro→micro
  cascade of Exocórtex.
version: 1.0.0
author: Exocórtex
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - design
    - tokens
    - style
    - brand
    - visual
    - cascade
    related_skills:
    - excrtx-memory-manager
    - excrtx-quality-taste
    - design-md
    - brandkit
    calibration:
    - feature_id: EX-20
      calibration_prompt: 'Você persiste, resolve e valida tokens visuais no Acervo Cognitivo. Formato Google DESIGN.md (YAML
        frontmatter + markdown prosa). Cascade: global/DESIGN.md (base) → micro/{slug}/DESIGN.md (override por deltas). Operações:
        RESOLVE (cascade tokens), WRITE (create/update), LINT (WCAG), EXPORT.'
      test_prompt: Preciso de uma paleta de cores para o microverso 'estudio-criativo'. Deve herdar a base do design global
        mas com cores mais vibrantes.
      acceptance_criteria: '1. O agente resolve primeiro os tokens globais (global/DESIGN.md) como base

        2. Propõe override no micro/estudio-criativo/DESIGN.md com ''extends: global''

        3. Os tokens propostos passam validação WCAG AA (contraste ≥ 4.5:1)

        4. O formato é DESIGN.md com YAML frontmatter correto'
      remediation_tip: 'FALHA: Tokens criados sem cascade ou validação. O Design System exige: 1) Ler global/DESIGN.md como
        base, 2) Criar override em micro/{slug}/DESIGN.md com ''extends: global'', 3) Validar contraste WCAG AA. Nunca crie
        tokens do zero sem resolver o cascade global primeiro.'
---
# Exocórtex Design System

Skill for managing visual tokens in the Acervo Cognitivo.
Based on the Google DESIGN.md format (YAML tokens + markdown prose).

Complements the ecosystem:
- **brandkit** (taste sub-skill) → creative guide to *define* visual identity
- **excrtx-quality-designsys** (this one) → *persists and resolves* tokens in the Acervo
- **excrtx-quality-taste** → *validates quality* of visual output

## When to Use

Activate when:
- A task needs visual tokens (colors, typography, spacing) to generate output
- The executive wants to define, review, or update the visual style
- The agent needs to resolve style cascade (global + micro override)
- Token WCAG lint or validation is needed
- Token export to external format (Tailwind, DTCG) is requested

## Acervo Paths

```
ACERVO="${HERMES_HOME:-$HOME/.hermes}/acervo"

# Source of truth (base tokens)
DESIGN_GLOBAL="$ACERVO/global/DESIGN.md"

# Per-microverso overrides (optional — deltas only)
DESIGN_MICRO="$ACERVO/micro/{slug}/DESIGN.md"

# Identity assets (binaries: logo, favicon)
ASSETS="$ACERVO/macro/assets/"
```

## Format: Google DESIGN.md

The format combines YAML frontmatter (machine-readable tokens) with markdown body
(human-readable rationale). Spec: `google-labs-code/design.md` (Apache-2.0).

### Token Types

| Type | Format | Example |
|------|--------|---------|
| Color | `#` + hex (sRGB) | `"#1A1C1E"` |
| Dimension | number + unit | `48px`, `-0.02em` |
| Token reference | `{path.to.token}` | `{colors.primary}` |
| Typography | object | `fontFamily`, `fontSize`, `fontWeight`, `lineHeight` |

### Canonical Section Order

1. Overview
2. Colors
3. Typography
4. Layout & Spacing
5. Elevation & Depth
6. Shapes
7. Components
8. Do's and Don'ts

---

## Operation: RESOLVE

Resolve visual tokens for the active context (cascade global → micro).

### Procedure

1. **Read `global/DESIGN.md`** — base tokens (mandatory):
   ```bash
   cat "$DESIGN_GLOBAL"
   ```

2. **Check if active microverso has override:**
   ```bash
   test -f "$ACERVO/micro/{slug}/DESIGN.md"
   ```

3. **If override exists:**
   - Read `micro/{slug}/DESIGN.md`
   - Verify `extends: global` field in frontmatter
   - Merge: micro tokens override global tokens
   - Tokens not declared in micro → inherited from global

4. **If override does NOT exist:**
   - Use pure global (100% inheritance)

5. **Return resolved tokens** to the requesting skill.

### Merge Logic

```
For each token in global DESIGN.md:
  IF micro declares the same token → use micro value
  ELSE → use global value

Tokens that exist ONLY in micro (e.g., specific components)
→ add to result (extension, not conflict)
```

### Verification

- [ ] global/DESIGN.md read
- [ ] Override detected correctly (exists or not)
- [ ] Merge respects cascade (micro overrides global)
- [ ] Resolved tokens are complete (no global token lost)

---

## Operation: WRITE

Create or update DESIGN.md in the Acervo.

### Procedure

1. **Determine scope:**
   - Executive's tokens (base palette) → `global/DESIGN.md`
   - Microverso override → `micro/{slug}/DESIGN.md`

2. **If writing micro override:**
   - Add `extends: global` in YAML frontmatter
   - Include ONLY tokens that differ from global
   - Do NOT copy unchanged tokens

3. **Validate format:**
   - Valid YAML frontmatter
   - Hex colors in quotes (`"#1a73e8"`)
   - Negative dimensions in quotes (`"-0.02em"`)
   - Sections in canonical order

4. **Log operation** via `excrtx-memory-manager`:
   ```bash
   # Append to log.md with timestamp and scope
   echo "## [$(date +%Y-%m-%d)] write | DESIGN.md updated ({scope})" >> "$ACERVO/{scope}/log.md"
   ```

5. **Update index.md** if new file.

### Integration with brandkit

When the executive wants to define visual identity:

1. Activate `brandkit` (taste sub-skill) as creative guide
2. brandkit collects: positioning, personality, visual tension, audience
3. brandkit defines: proprietary colors, typographic system, visual language
4. **This skill persists** the result as DESIGN.md in the Acervo

Flow: `brandkit` (creation) → `excrtx-quality-designsys` (persistence)

### Rules

- NEVER duplicate global tokens in micro override
- Micro override MUST have `extends: global`
- Hex colors ALWAYS in quotes (YAML requirement)
- Token references use dotted path: `{colors.primary}`, never `{primary}`

---

## Operation: LINT

Validate DESIGN.md using Google CLI.

### Procedure

```bash
# Validate structure + token references + WCAG contrast
npx -y @google/design.md lint "$DESIGN_GLOBAL"

# If override exists
npx -y @google/design.md lint "$ACERVO/micro/{slug}/DESIGN.md"
```

### What Lint Catches

- `broken-ref` — reference to nonexistent token
- `duplicate-section` — duplicate heading
- `invalid-color`, `invalid-dimension`, `invalid-typography` — wrong format
- `wcag-contrast` — textColor vs backgroundColor contrast below WCAG AA (4.5:1)
- `unknown-component-property` — property outside whitelist

### Verification

- [ ] Lint command ran without errors
- [ ] Zero `wcag-contrast` violations (or justified exceptions documented)
- [ ] Zero `broken-ref` issues
- [ ] Output format matches expected (no JSON parse errors)

---

## Operation: EXPORT

Generate consumable format from resolved tokens.

### Procedure

```bash
# Export to Tailwind theme JSON
npx -y @google/design.md export --format tailwind "$DESIGN_GLOBAL" > tailwind.theme.json

# Export to W3C DTCG (Design Tokens Format Module) JSON
npx -y @google/design.md export --format dtcg "$DESIGN_GLOBAL" > tokens.json
```

### CSS Custom Properties (manual)

If native export doesn't suffice, generate CSS manually from YAML tokens:

```css
:root {
  --color-primary: {colors.primary};
  --color-secondary: {colors.secondary};
  --font-heading: {typography.h1.fontFamily};
  /* ... */
}
```

---

## Pitfalls

- **Hex colors must be quoted strings.** `#1A1C1E` without quotes breaks YAML.
- **Negative dimensions need quotes.** `letterSpacing: -0.02em` → `letterSpacing: "-0.02em"`.
- **Section order is enforced.** Reorder if necessary.
- **`version: alpha`** is the current spec version (Apr 2026).
- **Override is NOT standalone.** Without `extends: global`, agent treats it as complete spec.
- **Token references resolve by dotted path.** `{colors.primary}` ✓, `{primary}` ✗.

---

## References

- Google DESIGN.md spec: `google-labs-code/design.md` (Apache-2.0) — [github.com/nicolo-ribaudo/tc39-proposal-structs](https://github.com/nicolo-ribaudo/tc39-proposal-structs) for format definition.
- Current spec version: `alpha` (Apr 2026).

## Verification

- [ ] Global `DESIGN.md` readable and YAML-valid
- [ ] Micro override has `extends: global` when present
- [ ] Cascade resolves correctly (micro overrides global, no token loss)
- [ ] Hex colors quoted in YAML
- [ ] WRITE operation logged in scope's `log.md` with timestamp
- [ ] LINT passes with zero critical violations
- [ ] EXPORT generates valid JSON (parseable with `python3 -m json.tool`)
- [ ] Sections follow canonical order
