# Frontend Slides Global Capability Implementation Plan

> **For Hermes:** Use this as the implementation handoff for a global Exocórtex capability. Do not treat Frontend Slides as an ensino-only workflow.

**Goal:** Add a global Exocórtex capability that keeps Markdown as canonical source and exports premium HTML/PDF/ZIP presentations through a Frontend Slides adapter, adapting visual behavior by microverso.

**Architecture:** Markdown remains the source of truth. Marp remains the production renderer for routine decks. Frontend Slides becomes a premium renderer for HTML-first visual decks, always resolved through Exocórtex Design System and microverso cascade. Local HTML/PDF/ZIP exports are produced first; the agent offers private Google Drive upload as the standard next step, using Exocórtex Drive path rules. Vercel is optional and Draft-First gated. Estúdio Criativo and Frontend Slides are peer capabilities: each can request the other for visual direction, templates, moodboards, or deck execution.

**Tech Stack:** Hermes skills, Acervo v2, Markdown, HTML/CSS/JS, Python 3 + python-pptx, Node.js + npm/npx, Playwright/Chromium, optional Marp CLI, optional Vercel gated by Draft-First.

---

## Core Decisions

1. Scope is global, not ensino-specific.
2. Markdown remains canonical source for documents, talks, classes, reports and deck briefs.
3. Frontend Slides output is an export artifact, not the primary editable source by default.
4. Every generated visual output must resolve Exocórtex Design System first.
5. Microverso rules can constrain or relax the visual language.
6. User intent can authorize more creative freedom, but never bypasses design-system grounding.
7. External sharing, deploy, public links or permission changes require Draft-First approval.
8. Local HTML/PDF/ZIP delivery comes first; private Google Drive upload is offered as the standard next step and uses Exocórtex path rules.
9. Estúdio Criativo and Frontend Slides must be mutually aware.

---

## Capability Model

### Canonical source types

```text
source.md              # narrative/content source
slides.marp.md         # Marp-compatible source, when available
brief.md               # intent, audience, density, tone, constraints
assets/                # logos, images, data, screenshots
```

### Export targets

```text
exports/deck.html      # premium browser presentation
exports/deck.pdf       # static export via Playwright
exports/deck.zip       # distributable package with assets
previews/style-a.html  # visual option A
previews/style-b.html  # visual option B
previews/style-c.html  # visual option C
manifest.json          # artifact traceability
```

### Renderer routing

```text
Routine instructional deck         -> Marp
Code-heavy technical class         -> Marp
Institutional/board/report deck    -> Frontend Slides, restrained mode
Talk/keynote/pitch                 -> Frontend Slides, expressive mode
Creative visual exploration        -> Estúdio Criativo + Frontend Slides
Existing Marp upgrade              -> Marp source -> premium HTML export
```

---

## Microverso Adaptation Contract

The global skill must read microverso context before generation:

1. Resolve active microverso.
2. Read global DESIGN.md.
3. Read micro/{slug}/DESIGN.md if present.
4. Read local contracts/persona/workflows if relevant.
5. Determine visual freedom level:
   - `strict`: institutional, legal, official documents.
   - `balanced`: default Exocórtex mode.
   - `expressive`: creative, talks, ideation, explicit user intent.
   - `experimental`: estúdio-criativo or user-approved exploration.
6. Generate previews and deck within that envelope.

### Example envelopes

```text
ensino:
  default: balanced
  constraints: didactic clarity, code readability, IFSul identity, avoid visual excess

gabinete:
  default: strict
  constraints: institutional tone, restrained green, red rare, no noisy motion

estudio-criativo:
  default: expressive/experimental
  constraints: still lint tokens, still avoid slop, make design thesis explicit

dev:
  default: balanced
  constraints: architecture clarity, diagrams, code/terminal aesthetics allowed
```

---

## New Skill: exocortex-frontend-slides

Suggested path:

```text
~/.hermes/skills/exocortex/exocortex-frontend-slides/SKILL.md
```

Supporting files:

```text
references/upstream-frontend-slides/
  SKILL.md
  STYLE_PRESETS.md
  viewport-base.css
  html-template.md
  animation-patterns.md
  bold-template-pack/
  LICENSE
scripts/
  setup-frontend-slides.sh
  extract-pptx.py
  export-pdf.sh
  package-deck.sh
```

Skill responsibilities:

1. Convert Markdown or Marp Markdown into a deck brief.
2. Generate 3 real visual previews.
3. Ask user to choose or mix visual direction.
4. Generate fixed-stage 1920x1080 HTML deck.
5. Export PDF/ZIP when requested.
6. Preserve source Markdown in artifact package.
7. Apply design/taste gate before delivery.
8. Block deploy/publication until explicit approval.

---

## Estúdio Criativo Cross-Awareness

Add references in both directions:

### In exocortex-frontend-slides

- If the task asks for unusual visual language, campaign-like narrative, brand exploration, posters, moodboards or experimental aesthetics, consult `micro/estudio-criativo` context or the `estudio-criativo` skill/workflow before finalizing style.
- If no strong visual thesis exists, request creative direction from Estúdio Criativo before generating final deck.

### In estudio-criativo

- If the creative output should become a presentation, talk, deck, lesson, pitch or browser-deliverable visual artifact, route execution to `exocortex-frontend-slides`.
- Estúdio Criativo owns exploration; Frontend Slides owns presentation packaging and export.

---

## Setup Playbook

### Required checks

```bash
command -v python3
command -v node
command -v npm
command -v npx
```

### Python dependency

```bash
python3 -m pip install --user python-pptx
```

### Node dependencies

Use project-local or cache-local install. Avoid global installs unless user approves.

```bash
npm --version
npx playwright --version || true
npx playwright install chromium
```

### Marp optional dependency

Needed only for Marp rendering/compatibility checks:

```bash
npx @marp-team/marp-cli --version
```

### Vercel optional dependency

Vercel is not the default export path. Local HTML/PDF/ZIP delivery comes first; private Google Drive upload is offered as the standard next step. Vercel is only for explicitly approved public URLs.

Drive uploads must never target the root folder. Use `exocortex/{microverso}/{ano}/apresentacoes` when the microverso is known, specialized paths such as `exocortex/ensino/{ano}/{disciplina}/slides-premium` when context is richer, and `exocortex/inbox` as the fallback.

```bash
npx vercel --version
npx vercel whoami
```

Do not call deploy automatically from setup.

---

## Suggested Setup Script Behavior

Script name:

```text
setup-frontend-slides.sh
```

Modes:

```bash
setup-frontend-slides.sh --check
setup-frontend-slides.sh --install-local
setup-frontend-slides.sh --install-python
setup-frontend-slides.sh --install-playwright
```

Rules:

1. `--check` never installs anything.
2. `--install-local` installs only non-global dependencies.
3. No global npm install by default.
4. No Vercel login or deploy.
5. Print exact next action when dependency is missing.
6. Exit non-zero only for missing required dependency in install mode or failed install.

---

## Implementation Tasks

### Task 1: Vendor upstream safely

Create a local reference copy of upstream Frontend Slides under the new skill references directory. Preserve MIT LICENSE.

Verification:

```bash
test -f ~/.hermes/skills/exocortex/exocortex-frontend-slides/references/upstream-frontend-slides/LICENSE
test -f ~/.hermes/skills/exocortex/exocortex-frontend-slides/references/upstream-frontend-slides/SKILL.md
```

### Task 2: Write wrapper SKILL.md

Create Exocórtex-native `SKILL.md` that references upstream files but adds:

- global capability scope;
- microverso adaptation contract;
- Markdown source preservation;
- Design System resolve/lint;
- taste gate;
- artifact workspace integration;
- Draft-First publication gate;
- Estúdio Criativo cross-awareness.

### Task 3: Add setup script

Create `scripts/setup-frontend-slides.sh` with `--check` and install modes.

Verification:

```bash
bash -n scripts/setup-frontend-slides.sh
scripts/setup-frontend-slides.sh --check
```

### Task 4: Add package script

Create `scripts/package-deck.sh` to zip HTML + assets + manifest.

Verification:

```bash
bash -n scripts/package-deck.sh
```

### Task 5: Add Acervo global contract

Create:

```text
~/.hermes/acervo/global/contracts/frontend-slides-global-capability.md
```

It should declare renderer routing, Markdown source rule, microverso cascade and Draft-First constraints.

### Task 6: Add Estúdio Criativo cross-reference

Create or update a shared/global cross-reference so both capabilities know each other.

Preferred locations:

```text
~/.hermes/acervo/shared/cross-refs/frontend-slides-estudio-criativo.md
```

or, if shared cross-refs are not present yet:

```text
~/.hermes/acervo/global/knowledge/frontend-slides-estudio-criativo.md
```

### Task 7: Smoke test

Use a short Markdown source and generate:

```text
previews/style-a.html
previews/style-b.html
previews/style-c.html
exports/deck.html
exports/deck.pdf
exports/deck.zip
```

Run checks:

- HTML exists and non-empty.
- PDF exists and non-empty.
- ZIP exists and contains source Markdown + HTML.
- No deploy was attempted.
- Design System was resolved.
- Visual output passes taste gate.

---

## Non-goals

1. Do not replace Marp.
2. Do not make HTML the canonical source for every deck.
3. Do not publish to Vercel by default.
4. Do not hardcode ensino assumptions into the global skill.
5. Do not bypass microverso visual constraints.
6. Do not create a mandatory heavy web app or server.

---

## Final Operating Principle

Marp is the reliable production line. Frontend Slides is the premium renderer. Estúdio Criativo is the direction-of-art partner. The Exocórtex Design System is the constraint layer that keeps freedom from turning into slop.
