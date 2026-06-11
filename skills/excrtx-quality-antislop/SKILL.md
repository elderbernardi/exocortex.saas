---
name: excrtx-quality-antislop
description: Remove AI writing patterns from prose. Use when drafting, editing, or reviewing text to eliminate predictable AI tells.
version: 1.0.0
category: excrtx
platforms: [linux]
metadata:
  hermes:
    tags: [exocortex, quality, anti-slop, writing]
    related_skills: [excrtx-quality-gate, excrtx-quality-taste]
compiled_rules: |
  Cut filler phrases, throat-clearing openers, emphasis crutches, all adverbs.
  Break formulaic structures: no binary contrasts, no dramatic fragmentation, no rhetorical setups.
  Active voice only. Be specific — no vague declaratives. Vary rhythm.
  Trust readers: state facts directly, skip softening and hand-holding.
  Score 1-10 on: Directness, Rhythm, Trust, Authenticity, Density. Min: 35/50.
---

# Stop Slop

Eliminate predictable AI writing patterns from prose.

## When to Use

Apply when drafting, editing, or reviewing text that will be read by the executive. Called by `excrtx-quality-gate` as part of the output quality pipeline.

**Don't use for:** Code, technical documentation (README, ADR, SKILL.md, docstrings), raw data, CSV, logs, system messages, literal quotes from external sources.

## Procedure

1. **Cut filler phrases.** Remove throat-clearing openers, emphasis crutches, and all adverbs.
2. **Break formulaic structures.** Avoid binary contrasts, negative listings, dramatic fragmentation, rhetorical setups, false agency.
3. **Use active voice.** Every sentence needs a human subject doing something. No passive constructions.
4. **Be specific.** No vague declaratives. Name the specific thing.
5. **Put the reader in the room.** No narrator-from-a-distance voice.
6. **Vary rhythm.** Mix sentence lengths. Two items beat three. No em dashes.
7. **Trust readers.** State facts directly. Skip softening, justification, hand-holding.
8. **Cut quotables.** If it sounds like a pull-quote, rewrite it.

## Quick Checks

Before delivering prose:
- Any adverbs? Kill them.
- Any passive voice? Find the actor, make them the subject.
- Inanimate thing doing a human verb? Name the person.
- Sentence starts with a Wh- word? Restructure it.
- Any throat-clearing? Cut to the point.
- Any "not X, it is Y" contrasts? State Y directly.
- Three consecutive sentences match length? Break one.
- Paragraph ends with punchy one-liner? Vary it.
- Em-dash anywhere? Remove it.
- Vague declarative? Name the specific implication.

## Scoring

Rate 1-10 on each dimension:

| Dimension | Question |
|-----------|----------|
| Directness | Statements or announcements? |
| Rhythm | Varied or metronomic? |
| Trust | Respects reader intelligence? |
| Authenticity | Sounds human? |
| Density | Anything cuttable? |

Below 35/50: revise.

## Pitfalls

- **False positives on technical prose**: Technical documents, code comments, and system messages have different quality criteria. Don't apply anti-slop to them.
- **Over-correction**: Removing ALL adverbs can strip necessary precision ("approximately 40%" → "40%" loses the uncertainty). Context matters.
- **Cultural blindness**: PT-BR prose has different natural rhythms than English. Three-item lists and em-dashes may be natural in Portuguese formal writing.
- **Scoring rigidity**: The 35/50 threshold is a floor for production quality. Don't optimize for "just above 35" — aim for genuinely good prose.
- **Quotability trap**: Not all memorable phrases are slop. The test is whether the phrase carries specific information or is generic filler.

## Verification

- [ ] Prose output contains no filler phrases ("it's important to note", "significantly")
- [ ] No passive voice without clear reason
- [ ] No inanimate subjects with human verbs
- [ ] Score ≥ 35/50 across 5 dimensions
- [ ] Technical docs/code NOT filtered by anti-slop
- [ ] PT-BR prose evaluated with PT-BR rhythm expectations

