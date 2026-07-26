# Index Pages

Rules for the per-project home page: a thumbnail grid linking to every published piece in that project. The reader's entry point — not a data view, not an export.

## Purpose

Every project gets exactly one index page. It answers "what has DataJockey published for this project," nothing else.

## Layout

Fluid, responsive grid — not a fixed canvas (contrast `07-export-application.md`). Reuses the standard container width/breakpoints already in use on dashboard views (`05-dashboard-application.md`); no new grid system.

## Page header

- Eyebrow (`.dj-eyebrow`): project name, e.g. "DUBAI BOUNCEBACK INDEX"
- Title: 72px/500 (Title scale, `03-typography.md`), scaled down per the dashboard scale on narrow viewports — a plain statement of what the project is, not a tagline
- Wordmark: inline in the header, per the existing non-scrolling hub-page rule already in `05-dashboard-application.md` (flexbox, `align-items: flex-start; justify-content: space-between`). That rule was written for exactly this page type.

## Thumbnail tile

Reuses the standard tile anatomy from `04-components.md` — no new card component:

1. Metric slot → the piece's headline finding, shortened if the full export headline doesn't fit
2. Delta slot → publish date + series tag, e.g. "Aviation · 3 Jul 2026"
3. Source slot → tier, read time, or whichever single line is most useful at a glance — decide per project

Entire tile is the link to that piece's hosted page (`{slug}.html`). No separate "read more" affordance — the tile is the click target.

## Ordering

Reverse-chronological, most recent first. No pagination. At a two-week publishing cadence a flat list stays short for a long time — revisit only if it stops working.

## Grouping

Flat list by default, not grouped by series. Each tile's delta line already carries the series tag, so the information isn't lost — just not used to partition the page. Add series filtering later only if the flat list becomes unwieldy.

## What this page does not have

- No decorative hero image
- No icons beyond the tile pattern already defined
- No footer watermark from `07-export-application.md` — the page already lives at its own traceable URL, so the export footer's job doesn't apply