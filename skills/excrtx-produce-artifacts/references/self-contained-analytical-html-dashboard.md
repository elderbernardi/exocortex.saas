# Self-contained analytical HTML dashboards

Use this pattern for executive BI, account reviews, commercial scorecards, or operational dashboards delivered as a single offline HTML file.

## Package architecture

Preserve four distinct layers:

```text
source/
├── source.md             # scope, definitions, sources, limitations
├── build_data.py         # raw payload -> normalized dashboard model
├── build_dashboard.py    # normalized model + assets -> final HTML
└── qa_dashboard.py       # deterministic browser probes
assets/
├── data/
│   ├── raw-source.*      # untouched source snapshot
│   └── dashboard_data.json
└── images/               # optimized local assets
exports/
└── dashboard.html        # primary self-contained delivery
evaluations/
├── qa-results.json
├── qa-report.md
└── screenshots/
```

Do not author a large final dashboard directly from transient tool output. First preserve the raw payload, then normalize it deterministically. This makes schema drift, corrections, and regeneration auditable.

## Data modeling gates

1. Read the source system's glossary or metric contract before calculating or naming KPIs.
2. Resolve the business entity before research: legal name, identifier, location, brand aliases, and explicit exclusions for similarly named companies.
3. Separate entity-level, parent/group-level, branch-level, and product-level metrics. Never compare them as if they share scope.
4. Compare historical snapshots only when metric semantics are stable. If a metric changed definition, block the comparison and explain why.
5. Add a visible data-quality ledger for missing fields, conflicting dates, schema changes, and model-generated estimates.
6. Label derived values as proxies. Do not rename a proxy as an official source KPI.
7. When a source omits a human identifier, display the available operational key (for example ERP code plus a shortened internal ID) instead of fabricating a CNPJ, branch name, or label.

## HTML delivery rules

- Embed CSS, JavaScript, normalized data, and essential images in the final HTML.
- Avoid external scripts, fonts, chart libraries, and runtime CDN dependencies.
- Keep source links as optional outbound references; the analytical content must remain readable offline.
- Use CSS custom properties from the resolved DESIGN.md cascade. Hardcoded colors outside `:root` are a gate failure.
- Provide print/PDF behavior, responsive layouts, accessible controls, and keyboard-visible focus.
- For large branch/product sets, include search, filters, and CSV export rather than truncating the evidence.
- Persist user-editable action-plan state locally only when useful and clearly local to the browser.

## Recommended executive information architecture

1. Identity and desambiguation.
2. Executive KPIs with explicit analysis window.
3. Diagnostic narrative: what changed, why it matters, what not to infer.
4. Margin/risk by operational entity.
5. Mix, concentration, ranking, and modeled opportunities.
6. Action plan with priority, horizon, owner, and completion KPI.
7. External radar translated into commercial implications.
8. Data-quality and methodology tab.

## Browser QA

Run deterministic checks at minimum in desktop and mobile BrowserContexts:

- expected title and primary heading;
- tab count and active-panel transitions;
- expected row counts for branch/product/news datasets;
- filter results for one known bucket;
- no console errors or `pageerror` events;
- `document.body.scrollWidth <= window.innerWidth + 1`;
- all required images embedded as `data:` URIs;
- viewport and full-page screenshots.

Capture the initial viewport before testing interactions. Tab clicks may trigger smooth scrolling; a post-interaction screenshot can otherwise start mid-page and misrepresent the first-load experience.

## Verification gates

- Normalized JSON parses.
- Build scripts compile and run from the package.
- Final HTML exists and is non-empty.
- Browser QA passes on desktop and mobile.
- No color literals exist outside `:root`.
- Manifest lists source, data, assets, output, evaluations, and publication state.
- SHA-256 and size are recorded after the final rebuild.

## Common pitfalls

- Treating multiple articles about one event as multiple events. Consolidate into one event and keep all corroborating sources.
- Using a cached browser page after rebuilding the HTML. Add a query-string cache buster during QA.
- Displaying blank columns because a branch schema changed. Inspect live keys and rename the column to the identifier actually present.
- Showing a precise metric with a formatter that rounds away the decision-relevant difference.
- Capturing a mobile screenshot by cropping desktop. Use an isolated mobile BrowserContext with explicit viewport, touch, and device scale factor.
