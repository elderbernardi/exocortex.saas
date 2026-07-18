# Full-wrap editorial artifact package

Use this workflow when an artifact includes fourth cover/back, spine and front, especially for print books or commercial publishing proposals.

## Package contract

Create:

```text
_artifacts/items/{artifact_id}/
├── source/
│   ├── DESIGN.md
│   ├── README.md
│   ├── cover.html|svg|indd-reference
│   └── cover.css|generator.*
├── assets/
│   ├── raw/          # original brand evidence
│   ├── generated/    # illustrations and redesigned marks
│   ├── fonts/        # when redistribution is permitted
│   └── logos/
├── exports/
│   ├── all-concepts.pdf
│   ├── concept-01.pdf
│   ├── concept-02.pdf
│   ├── concept-03.pdf
│   ├── fronts-contact-sheet.png
│   ├── spreads-contact-sheet.png
│   └── delivery.zip
├── evaluations/
│   └── editorial.md
├── receipts/
│   ├── renderer.stderr
│   ├── design-lint.json
│   └── color-audit.txt
├── delivery-manifest.json
└── manifest.json
```

Keep raw evidence separate from redesigned/generated assets. Use relative paths so the package remains portable.

## Geometry

For a print mockup with bleed:

`spread_width = back_width + spine_width + front_width + 2 × bleed`

`spread_height = trim_height + 2 × bleed`

For provisional perfect binding:

`spine_mm = (page_count / 2) × paper_caliper_mm`

Record every assumption in `manifest.json`. The artifact remains `draft` until the printer supplies final template, paper, binding and spine measurements.

## Source and export requirements

Preserve editable source. A PDF alone is not reproducible.

For HTML/CSS production:

- define color literals only in `:root` and consume tokens elsewhere;
- use local or embedded fonts when reproducibility matters;
- capture renderer stderr and fail on any warning;
- replace unsupported CSS with constructions proved by the export;
- rasterize the resulting PDF, not the browser preview, for final visual judgment.

Generate one combined PDF and individual concept PDFs. Verify page size and count for both.

## Visual evidence

Produce two comparison surfaces:

1. **fronts contact sheet** — equal-scale fronts for shelf/thumbnail comparison;
2. **spreads contact sheet** — complete back/spine/front layouts for production inspection.

The visual quality gate uses `excrtx-quality-taste/references/editorial-book-cover-preflight.md`. A technically valid PDF without these views is not complete.

## Manifest requirements

In addition to normal artifact fields, record:

```json
{
  "assumptions": {
    "page_count": 180,
    "sheet_count": 90,
    "paper_caliper_mm": 0.10,
    "spine_mm": 9,
    "bleed_mm": 3,
    "final_printer_template_required": true
  },
  "evaluation": {
    "visual_gate": "pass|fail",
    "design_lint": "...",
    "recommended_concept": "..."
  }
}
```

Do not mark `ready` solely because the design gate passed. Print readiness also requires real ISBN/barcode, publisher data, printer geometry, final pagination and author approval.

## ZIP and checksum rule

Create `delivery-manifest.json` before the archive. It lists the package contents but never the ZIP's own hash. Then:

1. build the ZIP outside `exports/` or exclude its target path;
2. move the completed archive into `exports/`;
3. compute SHA-256, MIME and size;
4. record those values only in canonical `manifest.json`;
5. test archive integrity.

This avoids checksum recursion.

## Delivery gate

On Telegram, deliver at least:

- fronts contact sheet;
- spreads contact sheet;
- combined PDF;
- complete ZIP.

Individual PDFs may be included when the user needs separate review. Publication, printer submission, public links or third-party sharing remain Draft-First.

## Verification checklist

- [ ] Editable source and DESIGN.md preserved
- [ ] Raw and generated assets separated
- [ ] Geometry and provisional spine assumptions recorded
- [ ] Combined and individual PDFs verified
- [ ] Renderer stderr empty
- [ ] Front and spread contact sheets generated
- [ ] Cover-specific taste gate passed
- [ ] Contrast and DESIGN.md lint recorded
- [ ] ISBN/barcode placeholders identified as placeholders
- [ ] ZIP integrity and manifest hashes verified
- [ ] Artifact remains DRAFT until printer and author gates pass
