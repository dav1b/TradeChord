# Dashboard Application

Rules specific to dashboard UI, synthesised from the brand book's web application spread and the studio's story-mode dashboard pattern.

## Logo placement

Every DataJockey dashboard carries the wordmark in the **upper-right corner** of every view.

- **Variant**: use `logo-navy.svg` (Navy letterforms, transparent background) by default on Parchment or white surfaces — see the wordmark rule in `02-color-system.md`. `logo-carbon.svg` is the fallback where Navy is already saturated. Use `logo-parchment.svg` (Parchment letterforms, transparent background) only on Carbon or Navy header bars.
- **Size**: `height: 22px` (the width scales automatically from the 5:1 aspect ratio of the wordmark).
- **Position**: `position: fixed; top: 16px; right: 20px; z-index: 50` for scrollable dashboard views, so the mark stays visible as the reader scrolls. On non-scrolling hub/index pages, position it inline within the header bar using flexbox (`align-items: flex-start; justify-content: space-between`).
- **Opacity**: 0.7 — present but never competing with data.
- **Pointer events**: none — the mark is never a click target on a data view.

The mark is sourced from `viz/public/logo-navy.svg`, `viz/public/logo-carbon.svg`, and `viz/public/logo-parchment.svg`. The original full-bleed variants (with background rectangles) live in `dj-brand-kit/assets/logo/`, named by colour pairing (`logo-navy-on-parchment.svg` etc. — see `04-components.md`), and are for presentation and print use only — do not use them in dashboard UI.

## Hero / header

Headline states the finding or the value proposition with edge. Body line brings credibility, one sentence. One call to action — never two competing. Where a dashboard opens with summary stat callouts (e.g. "3.2× faster decisions," "−40h per month," "£0 setup"), each stat follows the number-led single-fact pattern from `04-components.md`: number first, label small, one line of context.

## Layout discipline

Layout stays constant across any mode/state a dashboard supports (filtered view, story/walkthrough view, drill-down). Only colour/contrast and top-bar configuration change between states — never reflow structure. The reader should learn the layout once.

## Lit / recessed state pattern (for guided/story dashboards)

When a dashboard walks a reader through findings in sequence before releasing them to free exploration:

- Two visual states only: **lit** (full colour, full contrast) and **recessed** (near-background grey, low contrast, still present). No intermediate "dimmed" state.
- Recessed must genuinely recede — squint test: only the lit element(s) should read as foreground. If recessed elements still compete for attention, the grey is too dark.
- Constant anchors (identifying labels, key volume numbers, audit-trail/source footer) never recede in any mode — they are the floor under every state.
- An explicit escape hatch releases the guided state back to free-explore ("Dashboard" mode) on interaction with top-level controls (filters, sort, view switch).
- Free-explore/default mode: every element lit, all controls live.

## Data-density rule

If a chart element or card doesn't help someone decide something, it doesn't earn its place. Prefer fewer, larger, decision-relevant numbers over dense multi-metric grids. This applies to chart legends, axis labels, and tooltip content, not only top-level cards.

## Source and trust signalling

Every card or chart with a number carries a source/freshness line (smallest text weight, per `04-components.md`). This is not optional footer boilerplate — it is the brand's trust mechanism ("data you don't have to take on faith") and should appear on every data-bearing component, not just the page footer.

## What not to do

- No dashboard-theatre patterns: decorative gauges, vanity metrics without a source line, animated counters with no informational purpose
- No competing CTAs
- No colour outside the locked core palette / approved extended palette (see `02-color-system.md`) for brand-carrying elements
- No icon styles outside the six-mark system for anything claiming to be on-brand chrome
