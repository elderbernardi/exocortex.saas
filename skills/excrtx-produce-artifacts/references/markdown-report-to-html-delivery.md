# Markdown report to standalone HTML delivery

Use when the user asks for an HTML version of a Markdown report, especially for email/Telegram forwarding or stakeholder review.

## Procedure

1. Keep Markdown as canonical source under the artifact package:

```text
_artifacts/items/{artifact_id}/source/source.md
```

2. Resolve visual tokens before generating HTML.
   - For report/email/Telegram reading, default to light theme.
   - Prefer `micro/estudio-criativo/DESIGN.md` `palette_light` if the active project has no own `DESIGN.md`.
   - Document the token source in `manifest.design_tokens`.

3. Generate standalone HTML.
   - Inline CSS in `<style>` for portability.
   - No external fonts, JS, CDN or image dependencies unless explicitly required.
   - Include hero, metadata cards, sticky/inline table of contents, readable body, table styles and print styles.

4. Keep all raw hex colors inside `:root` only.
   - All other CSS must use `var(--color-*)`.
   - Run a hex audit after generation.

5. Validate technically.
   - HTML file exists and size > 0.
   - Browser opens local file.
   - Title loads.
   - Count expected headings/TOC links/tables/code blocks.
   - Check there are no empty `<pre>` blocks.

6. Validate visually.
   - Use browser screenshot/vision for hierarchy, legibility and obvious layout failures.
   - Long reports may produce very tall screenshots; verify structure via DOM counts as well as visual inspection.

7. Create a ZIP for forwarding.

```text
exports/report.html
exports/report.md
exports/html-build-metadata.json
exports/report-html.zip
```

8. Update `manifest.json` with every export:
   - path;
   - kind;
   - MIME;
   - size;
   - SHA-256;
   - design token source;
   - validation notes.

## Durable pitfalls

- Do not publish HTML without preserving the Markdown source.
- Do not use arbitrary colors from taste examples; use resolved cascade tokens.
- Do not leave the manifest with only the Markdown export after generating HTML.
- Do not treat visual screenshot alone as sufficient for long reports; DOM validation catches missing sections and rendering anomalies.
- If one execution mechanism is unavailable in the active profile, write a deterministic build script into `source/` and run it through the allowed shell path. Capture the script as part of the artifact source.

## Recommended build metadata

Create `exports/html-build-metadata.json` with:

```json
{
  "generated_at": "ISO-8601",
  "html_path": "exports/report.html",
  "design_tokens": "micro/estudio-criativo/DESIGN.md palette_light",
  "hex_audit": "passed: zero hardcoded hex outside :root",
  "markdown_extensions": ["extra", "toc", "sane_lists", "smarty"]
}
```
