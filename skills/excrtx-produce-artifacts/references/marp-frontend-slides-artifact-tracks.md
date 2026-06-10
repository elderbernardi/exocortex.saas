# Marp and Frontend Slides — Artifact Tracks

## Principle

Marp is the production line. Frontend Slides is the premium renderer.

Both preserve Markdown as canonical source whenever possible. The renderer choice depends on the artifact's goal, not the microverso alone.

## When to Use Marp

Use Marp for:

- Recurring lectures;
- Technical material with lots of code;
- Frequent manual maintenance;
- Quick PDF;
- Serial production per unit/discipline;
- Decks where consistency and speed matter more than visual direction.

## When to Use Frontend Slides

Use `exocortex-slides` for:

- Premium presentations;
- Talks;
- Pitches;
- Executive briefings;
- Special lectures;
- Unit opening/closing;
- Artifacts with strong visual narrative;
- Navigable HTML as the primary deliverable.

## Export Rule

Private Google Drive is the default destination for final delivery to regular users.

Vercel or public publication only enters when the user requests a public URL and approves the DRAFT.

## Recommended Package

```text
_artifacts/{artifact_id}/
├── source/
│   ├── source.md
│   ├── brief.md
│   └── slides.marp.md
├── assets/
├── previews/
├── exports/
│   ├── deck.html
│   ├── deck.pdf
│   └── deck.zip
└── manifest.json
```

## Relationship with Creative Studio

If the deck needs a strong visual thesis, Frontend Slides consults Creative Studio. If Creative Studio needs to deliver a presentation, it calls Frontend Slides to package and export.
