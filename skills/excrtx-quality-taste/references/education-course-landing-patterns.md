# Education Course Landing Patterns

Use this reference for institutional landings that present several technical, undergraduate, postgraduate, or continuing-education offers.

## Information architecture

Use two complementary depths:

1. **Comparison surface:** course, level, duration, schedule, modality, and regulated or publication-dependent status. Keep placeholders explicit; never copy prior-cycle vacancies into a new selection cycle.
2. **Detailed profile surface:** group courses by a meaningful taxonomy such as area, trajectory, or prerequisite level. Show only one group at a time when the full portfolio would create excessive length, but keep the active group's decision content visible.

Each course profile should cover:

| Field | Purpose |
|---|---|
| Audience/prerequisite | Who can enter the course |
| Affinity | Interests and working modes that may fit the visitor |
| Plain-language summary | What kind of formation the course provides |
| What the course teaches | Concrete content areas |
| Professional capabilities | Actions the graduate is trained to perform, within the source's scope |
| Fields of work | Informative settings and sectors, never an employment promise |
| Verified links | Catalog, course portal, process portal, or contact |
| Review state | Approved, review, placeholder, or blocked |

Do not hide affinity, learning, capabilities, or fields of work behind accordions solely to reduce page height. Tabs or filters may limit the active group; the active profile should remain readable without another click.

## Evidence taxonomy

Separate indicators by what they actually measure:

- **Institution/campus/school:** ENEM results, campus rankings, infrastructure, faculty composition. State that they do not score each course individually.
- **Course:** MEC concept, ENADE, CPC, recognition act, accreditation, or professional-body evaluation.
- **Selection cycle:** vacancies, dates, exam format, quotas, and enrollment rules. These come from the current official notice.
- **Context:** employment or regional-sector data. Name methodology, geography, and date; avoid employability promises.

For every prominent metric, inventory:

- scope/entity measured;
- indicator name;
- value and scale;
- edition/reference year;
- act or methodology where applicable;
- primary source URL;
- validation state.

An official institutional post can support a campus result when it reproduces the complete result and edition. A course portal saying only "maximum concept" does not identify the MEC indicator, act, or edition. In an internal DRAFT, display the unresolved gate beside the metric. Before publication, resolve the primary act or remove the unsupported precision.

Use grammatical precision in rankings: write "3ª maior média" rather than converting it to a generic "3º lugar". Preserve "melhor desempenho" as published instead of inventing a numerical rank.

## Visual composition

Use a data-dense, flat evidence board:

- one dominant institutional result area;
- a separate stack or column for course-level scores;
- a source and scope row attached to the board;
- solid tokenized surfaces, borders, and typography instead of shadows or decorative badges;
- captions large enough to remain readable on mobile.

A score's size must not imply stronger provenance than the source provides. Keep DRAFT or review gates visible.

For course profiles, a three-column desktop pattern works well:

1. what the visitor learns;
2. what the formation prepares the visitor to do;
3. where that professional may work.

Collapse to one column on mobile. Keep list text at the design system's body-small size or larger.

## Fixed mobile actions

Reserve the fixed mobile bar for two service actions with the highest conversion or orientation value:

1. application/process portal;
2. direct support, commonly WhatsApp.

If social media makes the bar visually heavy, remove it from the fixed surface and preserve it in navigation and the channel/evidence section. Requirements:

- minimum 44 px target; 56 px is a strong default;
- opaque backgrounds and explicit text labels;
- accurate destination label when the direct application URL is not yet available;
- body bottom padding equal to or greater than bar height;
- accessible navigation label such as "Application and contact shortcuts".

## QA sequence

1. Parse HTML and count all course profiles and required fields.
2. Test taxonomy controls by click and keyboard; exactly one panel should remain active.
3. Measure desktop and a real mobile viewport, plus a narrow edge width such as 320 px.
4. Verify fixed-action labels, destinations, position, height, and mobile-only visibility.
5. Check document-level horizontal scrolling and list elements outside the viewport.
6. Treat child overflow inside an intentional `overflow-x: auto` tablist as expected only when the document itself does not scroll horizontally.
7. Inspect screenshots of the evidence board and one full course profile. Full-page screenshots may misplace sticky or fixed elements; use viewport or clipped section captures for judgment.
8. Check console errors, focus order, touch targets, contrast, and reduced-motion behavior.
9. Re-run source and wording checks after visual edits; typography changes must not alter factual scope.
