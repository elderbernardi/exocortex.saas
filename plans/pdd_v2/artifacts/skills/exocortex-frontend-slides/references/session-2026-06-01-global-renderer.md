# Session 2026-06-01 — Global Frontend Slides Renderer

## Context

The user evaluated `zarazhangrui/frontend-slides` as a possible Exocórtex capability. Initial framing around `~/ensino` and Marp was corrected: this should be a global Exocórtex feature, not an ensino-only workflow.

## Durable Decisions

1. Frontend Slides becomes a global Markdown-to-premium-HTML renderer.
2. Markdown remains canonical source by default.
3. HTML, PDF and ZIP are exports.
4. Marp remains the production line for routine maintainable decks.
5. Frontend Slides is the premium renderer for designed browser presentations.
6. The capability adapts by microverso via Design System and local contracts.
7. Creative freedom is allowed when user intent calls for it, but still grounded in Design System.
8. Google Drive is the default publication/export destination.
9. Vercel is not default because account creation and login are user friction. It remains optional advanced deploy and Draft-First gated.
10. Estúdio Criativo and Frontend Slides are peer capabilities and can request help from one another.

## Practical Routing

```text
Routine aula / code-heavy material -> Marp
Premium aula opening / palestra    -> Frontend Slides
Institutional briefing             -> Frontend Slides strict mode
Creative deck / visual thesis      -> Estúdio Criativo + Frontend Slides
Browser deliverable export         -> Frontend Slides
Private distribution               -> Drive via personal-artifact-workspace
Public URL                         -> explicit approval only
```

## Implementation Implication

A future implementation should create a wrapper skill rather than copy upstream behavior raw. The wrapper must add:

- microverso awareness;
- Design System resolve/lint;
- taste gate;
- Markdown source preservation;
- artifact manifest and receipt;
- Google Drive default export;
- Vercel as optional, not default;
- Estúdio Criativo cross-awareness.

## Source Repo Studied

`https://github.com/zarazhangrui/frontend-slides`, commit observed during session: `24e420e`, plugin version `2.1.0`.

Observed components:

- `SKILL.md` — prompt workflow.
- `STYLE_PRESETS.md` — 12 safe presets.
- `bold-template-pack/selection-index.json` — 34 bold templates.
- `viewport-base.css` — fixed 1920×1080 stage.
- `html-template.md` — HTML/JS architecture.
- `animation-patterns.md` — motion references.
- `scripts/extract-pptx.py` — PPTX text/images/notes extraction.
- `scripts/export-pdf.sh` — Playwright screenshot-to-PDF pipeline.
- `scripts/deploy.sh` — Vercel deploy; not default for Exocórtex.

## Key Caution

Do not let the upstream Vercel-first sharing path leak into Exocórtex defaults. The user's canonical export path is Drive-backed artifact workspace.
