---
name: excrtx-quality-taste
description: Visual Quality Gate — auto-selects the correct sub-skill for premium visual outputs
version: 1.0.0
metadata:
  hermes:
    tags: [exocortex, quality, visual, design, anti-slop]
---

# Taste Skill — Visual Quality Gate

Sub-skills that break LLM statistical defaults in UI and visual output generation.

## Sub-Skills

### gpt-taste (premium UI / landing pages)
Activate when the output is a landing page, web product, or user interface.
Rules: varied layout via randomization, AIDA structure, hero max 2-3 lines, bento grid without gaps, GSAP motion, no meta-labels like SECTION 01.
Full details: gpt-taste.md

### brandkit (visual identity / branding)
Activate when the output involves visual identity, logos, brand boards, or color/typography systems.
Full details: brandkit.md

### brutalist (data-heavy / dashboards)
Activate when the output presents metrics, dashboards, data visualization, or data-heavy interfaces.
Style: Swiss typography, raw structure, high contrast, mechanical visual language.
Full details: brutalist.md

## Auto-Routing

The orchestrator selects the sub-skill by context:
- Data/metrics output → brutalist
- Identity/branding output → brandkit
- Landing/product/UI output → gpt-taste

## Design System Integration

Before generating any visual output, check whether `excrtx-quality-designsys`
has resolved tokens for the active microverso:

1. Call RESOLVE from `excrtx-quality-designsys`
2. If tokens exist → use as base for colors, typography, and spacing
3. If tokens don't exist → apply defaults from the active sub-skill (gpt-taste/brutalist)

Flow: `brandkit` (creation) → `excrtx-quality-designsys` (tokens) → `excrtx-quality-taste` (validation)

## Anti-Slop Checks

Before delivering any visual output:
- Headings longer than 3 lines? Widen container.
- Grid with empty spaces? Apply grid-flow-dense.
- Generic meta-labels (SECTION 01)? Remove.
- Invisible button text? Fix contrast.
- Repetitive layout (always left/right)? Vary.
