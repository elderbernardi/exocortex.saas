# Visual Design System Resolution — pre-flight for visual artifacts

Required reading before generating **any** visual artifact (HTML, PDF, SVG, slide deck, dashboard, image, slide templates, branded document). The full token set, cascade, and lint flow live in `excrtx-quality-designsys`; this reference is the operational recipe that makes the pre-flight hard to skip.

## When this reference fires

The "Before executing" block in `SKILL.md` lists `excrtx-quality-designsys` as required for visual artifacts. That gate is non-negotiable. Do not skip it because the artifact "looks small", "is a quick mockup", or "is just an internal report." Skip it once and the cost is a full regeneration, as documented below.

## The pre-flight (run before any HTML/CSS generation)

```bash
# 1. Confirm paths
ACERVO="${ACERVO:-$HOME/exocortex/acervo}"
[ -d "$ACERVO" ] || ACERVO="$HOME/.hermes/acervo"
DESIGN_GLOBAL="$ACERVO/global/_meta/DESIGN.md"
DESIGN_MICRO="$ACERVO/micro/{slug}/DESIGN.md"

# 2. Read both
cat "$DESIGN_GLOBAL"
test -f "$DESIGN_MICRO" && cat "$DESIGN_MICRO" || echo "NO MICRO OVERRIDE — use global 100%"

# 3. Resolve tokens
#    If micro exists → micro overrides global, others inherited
#    If micro missing → use global 100%
#    Document the source in the artifact manifest under `design_tokens`

# 4. Lint both
npx -y @google/design.md lint "$DESIGN_GLOBAL"
test -f "$DESIGN_MICRO" && npx -y @google/design.md lint "$DESIGN_MICRO"

# 5. Export to CSS custom properties if needed
npx -y @google/design.md export --format tailwind "$DESIGN_GLOBAL"
```

If the active microverso has no `DESIGN.md` of its own, pick the **closest sibling with one** and document the inheritance in the manifest. Do not pick tokens from memory or invent a palette. The "I'll just pick colors that look right" path is the failure mode this gate prevents.

## Common cascade paths (so the agent doesn't have to think)

- `acervo/micro/comercial/` — **no DESIGN.md** as of 2026-06-22. Inherit from `estudio-criativo` (most semantically aligned: both produce institutional client-facing material).
- `acervo/micro/ensino/` — check for `DESIGN.md`; if missing, inherit from global.
- `acervo/micro/excortex-dev/` — no DESIGN.md. Inherit from global or `estudio-criativo` (dev artifacts often need institutional polish).
- `acervo/micro/estudio-criativo/` — has its own DESIGN.md (midnight + accent + DM Sans + JetBrains Mono). Always use it for anything C-level.
- `acervo/micro/hermes-setup/` — technical artifact, global tokens are appropriate.

When you must inherit from a sibling, **state it explicitly in the manifest**:

```yaml
design_tokens:
  source: "acervo/micro/estudio-criativo/DESIGN.md (inherited — comercial has no override)"
  resolved_at: "2026-06-22T17:30:00-03:00"
  tokens_used: [midnight, accent, warn, crit, offwhite, muted, neutral, dark, white]
  typography: [DM Sans, JetBrains Mono]
  spacing_unit: "8px"
  hardcoded_hex_outside_root: 0
```

## HTML generation rules that match the cascade

```css
/* Block 1: token definitions (always inside :root) */
:root {
  --color-midnight: #03123f;       /* from estudio-criativo */
  --color-accent: #1376ed;          /* from estudio-criativo */
  /* ... etc — ALL colors live here ... */
}

/* Rule 1: every color in the rest of the stylesheet uses var(--color-*) */
.kpi { background: var(--color-midnight); color: var(--color-text); }

/* Rule 2: <button> styled controls need appearance: none */
.pill {
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
  border: 1px solid var(--color-line);
}

/* Rule 3: @media print inverts via tokens, not hardcoded hex */
@media print {
  body { background: #ffffff !important; color: var(--color-midnight) !important; }
  .module { background: var(--color-offwhite) !important; }
}
```

## Verification before publishing

```bash
# Hardcoded hex outside :root and @media print should be 0
python3 -c "
import re
html = open('exports/report.html').read()
root = re.search(r':root\s*\{[^}]+\}', html, re.DOTALL).group(0)
print_match = re.search(r'@media print\s*\{[^}]*\{[^}]*\}\s*\}', html, re.DOTALL)
out = html.replace(root, '').replace(print_match.group(0) if print_match else '', '')
hexes = re.findall(r'#[0-9a-fA-F]{6}', out)
print(f'Hardcoded hex outside :root and @media print: {len(hexes)}')
for h in set(hexes): print(f'  {h}')
"
```

If the count is > 0, the artifact is not aligned with the cascade — fix and regenerate before publishing.

## Observed failure mode (2026-06-22, session 20260622_155814_c7dd67)

An agent was asked to produce a commercial intelligence report as interactive HTML. Steps taken:

1. Loaded `excrtx-produce-artifacts` (correct).
2. Loaded `excrtx-quality-taste` and routed to `brutalist` (a taste sub-skill for data-heavy UIs).
3. Generated the HTML with `brutalist`'s default sample palette: `#080888` near-black background, `#5cd0ff` cyan accent, red/orange/lime tag colors.
4. Published to Drive as the v1.
5. User flagged: "aparentemente vc ignorou todas as regras de design que temos no exocortex. Pq?"

What went wrong:

- `excrtx-quality-designsys` was not loaded at all. The "When to Use" section listed it as relevant but did not mark it as required.
- The agent took `brutalist.md`'s example palette as if it were a token source, instead of treating the taste sub-skill as one of three inputs (taste, designsys, brandkit).
- The agent did not check whether `comercial` had a `DESIGN.md` of its own before generating.

The fix (now in `SKILL.md`) makes the pre-flight a hard requirement, not a suggestion. The token audit at the end of the workflow makes the failure visible in `remediation_tip` form before publishing.

## Related

- `excrtx-quality-designsys/SKILL.md` — the canonical design system operations (RESOLVE, WRITE, LINT, EXPORT).
- `acervo/global/knowledge/ecossistema-visual-design-system.md` — the format spec and cascade rules in narrative form.
- `acervo/global/_meta/DESIGN.md` — base tokens (read every time).
- Active microverso's `DESIGN.md` (or closest sibling override).
