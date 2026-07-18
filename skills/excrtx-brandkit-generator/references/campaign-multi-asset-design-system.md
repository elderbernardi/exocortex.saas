# Campaign identity from multiple visual assets

Use this workflow when the campaign identity is expressed across banners, social templates, tags, photography and an institutional brand manual rather than a single logo.

## Scope decision

Place the operational `DESIGN.md` at the campaign/project root when the tokens should govern that campaign across web, social, presentations and documents. Do not promote campaign colors to a workspace-global or Exocórtex-global design system: that contaminates future campaigns. Add pointers from `AGENTS.md`, the asset index and the domain Acervo entry so the harness discovers the file.

## Extraction pipeline

1. Inventory the visual sources and separate four classes:
   - campaign lockup and flat-color templates;
   - photographic pieces;
   - institutional marks and their manual;
   - governance constraints such as electoral or legal guidance.
2. Extract exact repeated RGBA values from flat-color pieces. Prefer exact pixel counts when the artwork uses solid fills; K-Means can blur canonical colors through antialiasing.
3. Run deterministic K-Means on photography to recover treatment tones, not the core campaign palette. Use the flat pieces as authority for primary/secondary/tertiary.
4. Treat the campaign lockup as an asset unless the actual font is supplied. Never approximate custom lettering with a similar UI font.
5. Keep institutional mark colors as protected tokens. Do not reuse them as campaign decoration or recolor the mark.
6. Derive accessible functional colors separately from expressive campaign colors. Bright source colors may fail with white text even when they work as artwork.

## Accessibility derivation

For every component with text:

- resolve token references;
- calculate WCAG contrast from final hex values;
- require at least 4.5:1 for normal text;
- use a darker tone sampled from photography for actions when the bright campaign hue fails with white;
- document when a color pairing belongs only to supplied artwork and cannot be reused for functional text.

Unused protected institutional colors may produce lint warnings. Keep them if their non-use is intentional and documented; zero errors is mandatory, but an explicit protected-token warning is not a failure.

## Google DESIGN.md verification

Use the locally available CLI first to avoid installing packages implicitly:

```bash
npx --no-install @google/design.md lint DESIGN.md
npx --no-install @google/design.md export --format dtcg DESIGN.md
```

Then verify:

- YAML frontmatter parses;
- canonical sections are ordered and unique;
- every `{token.reference}` resolves;
- source palette tokens exactly match pixels in authority assets;
- all local links resolve;
- all text-bearing components meet WCAG AA;
- DTCG export parses as JSON;
- a temporary visual board passes pre-flight for hierarchy, coherence and generic-template drift.

## Implementation contract

- Declare implementation colors as CSS custom properties inside `:root`.
- Do not hardcode color literals elsewhere.
- Preserve source assets, manuals and governance documents as higher authority than derived tokens.
- Record the design-system pointer in the domain Acervo and refresh semantic indexing after the canonical update.
