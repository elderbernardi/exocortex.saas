# Editorial book-cover pre-flight

Use this gate for trade books, manuals, reports sold or distributed as books, and any artifact that includes front, spine, and fourth cover/back.

## Required inputs

Before designing, resolve:

- title, subtitle or method seal, front quote, author name, back-cover copy and author bio;
- final or provisional page count;
- trim size, binding, paper, grammage/caliper, bleed and printer template when available;
- ISBN, barcode, publisher mark, QR destination and endorsements — or explicit placeholders when absent;
- source brand assets and the public audience they must reach.

If technical, ASCII, CLI or developer-facing brand assets must become a public book identity, load `excrtx-brandkit-generator` and its reference `editorial-book-cover-from-technical-brand.md` first.

## Front-cover gate

Require all of the following:

1. The commercial title carries the public promise; framework, method and runtime names remain secondary.
2. The title survives at 160 px width and does not rely on subtitle reading.
3. The composition has one dominant center of gravity; art, quote, title and mark do not compete.
4. Development labels, build numbers, compilation dates and “alpha” status stay off the commercial front.
5. Academic credentials move to the bio unless commercially essential.
6. Provocation creates tension without insulting the intended reader.
7. Art rejects generic AI shortcuts: glowing brain, circuits, robot face, neon cyberpunk, random nodes and stock holograms.
8. Symbols are checked for unintended readings such as target, eye, cage, prison, medical device or surveillance.

## Fourth-cover gate

The back cover must progress through:

1. **recognition** — the reader sees a real situation;
2. **tension** — the consequence or unresolved discomfort becomes concrete;
3. **method** — the book explains what changes;
4. **application** — cases, exercises, tools or outcomes become visible;
5. **invitation** — the closing gives the reader a reason to continue.

Also require:

- readable text at print scale;
- author bio separated from sales copy;
- reserved ISBN/barcode area at the base;
- no fabricated ISBN, QR, publisher, testimonial or endorsement;
- concept/version labels only on comparison boards and filenames, never in printable artwork.

## Spine gate

For a provisional perfect-bound spine:

`spine_mm = (page_count / 2) × paper_caliper_mm`

Record page count and caliper assumptions. Final width always comes from the printer after pagination, paper and binding are fixed.

Verify:

- reading orientation follows the chosen market/printer convention;
- title remains legible at actual spine width;
- author and micro-mark do not crowd trim or bleed;
- unsupported CSS such as `writing-mode` is replaced by verified rotation when necessary.

## Three-concept comparison

When the user asks for variants, produce different positioning systems, not colorways. Keep title, copy, trim, spine assumption and technical zones constant.

Recommended territories:

- conceptual/durable;
- authorial/premium;
- popular/provocative.

The comparison board must label concepts outside the printable artwork.

## Render and evidence gate

1. Capture renderer stderr and require zero warnings.
2. Rasterize every spread.
3. Create a front-only contact sheet for shelf and thumbnail judgment.
4. Create a full-spread contact sheet for back/spine/front inspection.
5. Measure contrast for every text/background pair. Decorative colors may fail only when they carry no text.
6. Validate front, back and spine after every structural correction.
7. Reject flex, fixed, sticky or unsupported layout behavior when the export proves it rendered differently.
8. Require editable source, DESIGN.md, raw assets, generated assets, exports and evaluation record.

## Positioning assessment

Separate technical PASS from market recommendation. Evaluate:

- shelf interruption;
- fit with the thesis;
- public clarity;
- originality;
- quality of brand adaptation;
- visual longevity.

Label scores as internal editorial judgment, never buyer research. Recommend one primary cover and identify reusable campaign elements from the others.

## Verification checklist

- [ ] Front, spine and fourth cover all rendered
- [ ] Title legible at 160 px width
- [ ] No collision, cut, overflow or unsafe margin
- [ ] Back copy follows recognition → tension → method → application → invitation
- [ ] ISBN/barcode area reserved at the base
- [ ] Spine assumption documented and marked provisional
- [ ] Brand assets translated for the public rather than copied literally
- [ ] Renderer produced zero warnings
- [ ] Contrast measured on final token values
- [ ] Front and spread contact sheets approved
- [ ] Technical PASS separated from positioning recommendation
