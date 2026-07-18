# Editorial book covers from technical or terminal-native brand assets

Use this reference when a publishing project must adapt product, CLI, ASCII, diagrammatic, or developer-facing brand assets for a general readership.

## 1. Inventory beyond image extensions

Do not search only for `logo*.png` and SVG files. Technical brands may live as:

- `.txt` ASCII studies;
- shell scripts that print ANSI marks;
- README lockups;
- terminal banners;
- micro-marks such as `[cx]`;
- diagrams or naming conventions that contain the actual identity.

Read every candidate and render text assets into a neutral monospace contact sheet before judging them visually.

## 2. Extract semantics, not surface style

Classify each source element as one of:

- **preserve:** durable semantic mark or wordmark;
- **redesign:** good idea trapped in a medium-specific form;
- **texture:** useful only as crop, pattern, or background material;
- **discard:** implementation/runtime detail that does not belong in the public promise.

Typical translation:

- brackets can represent an external cognitive layer;
- a central ASCII block can become a geometric core;
- a block wordmark can become texture;
- runtime signatures, console diagnostics, and dependency names should usually leave the retail cover.

Reject literal adaptations that still look like terminal banners, architecture diagrams, dashboards, or generic hacker branding.

## 3. Build genuinely distinct territories

When the user requests multiple concepts, create positioning systems, not colorways. For a three-concept exploration, a useful spread is:

1. **conceptual/durable:** restrained typography, mark-led geometry, high brand continuity;
2. **authorial/premium:** exclusive illustration, human tension, quieter method mark;
3. **popular/provocative:** aggressive hierarchy, high shelf interruption, brand assets used as texture.

Keep title, copy, trim size, spine assumption, and technical zones constant so the comparison measures positioning rather than changing content.

## 4. Complete-cover architecture

Each proposal includes:

- fourth cover/back;
- provisional spine;
- front;
- ISBN/barcode reserve;
- author block;
- method/publisher mark;
- editable source and rendered exports.

Concept labels belong on comparison boards and filenames, never in the printable artwork.

For a provisional perfect-bound spine:

`spine_mm = (page_count / 2) × paper_caliper_mm`

State the page count and caliper assumption. Never present the result as print-ready. Final width must come from the printer after paper, grammage, binding, and final pagination are fixed.

## 5. Cover-specific editorial discipline

- The title carries the public promise; the framework or method becomes a secondary seal.
- Remove development status, build number, “alpha,” and compilation date from the commercial front.
- Credentials that make the book look academic belong in the bio unless they are commercially essential.
- The front quote may provoke; the back copy must convert provocation into recognition, method, and invitation.
- Do not invent ISBN, barcode, publisher, QR destination, testimonials, or endorsements.

## 6. Renderer-safe production

Treat every renderer warning as a failed gate.

For print HTML/PDF engines with partial CSS support:

- replace `writing-mode` with absolutely positioned, rotated spine text;
- replace text shadows with real contrast planes or gradients;
- anchor author, barcode, and footer blocks with absolute bottom positions when flex auto margins render inconsistently;
- keep all CSS color literals in `:root` and consume variables elsewhere;
- preserve local or embedded fonts when reproducibility matters.

Do not encode a transient renderer failure as a permanent limitation. Use a supported construction and verify the output.

## 7. Verification sequence

1. Render the complete multi-page PDF with stderr captured; require zero warnings.
2. Rasterize every page.
3. Produce a front-only contact sheet for shelf/thumbnail judgment.
4. Produce a full-spread contact sheet for back/spine/front inspection.
5. Run visual pre-flight after every structural correction.
6. Measure WCAG contrast for all text/background pairs; decorative brand colors may fail only when they carry no text.
7. Lint `DESIGN.md`; aim for zero errors and zero warnings by placing typography, spacing, rounded, and primary color tokens in frontmatter.
8. Split individual concept PDFs and verify page size/count.
9. Package source, raw brand evidence, generated assets, evaluations, receipts, exports, manifest, and ZIP.
10. Verify hashes and archive integrity before delivery.

## 8. Decision reporting

Separate execution quality from market positioning. A technically approved cover may still serve a narrower audience.

Evaluate at least:

- shelf interruption;
- fit with the thesis;
- public clarity;
- originality;
- quality of brand adaptation;
- visual longevity.

Label scores as internal editorial judgment, not buyer research. Recommend one primary cover and identify elements from the other concepts that can serve campaign and launch materials.
