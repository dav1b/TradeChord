# Implementation Checklist

Run against any dashboard before it ships.

## Colour
- [ ] Only core palette (Carbon, Navy, Parchment, Alabaster) or approved extended palette in use
- [ ] Alabaster used only for subtle accents/supporting surfaces, never as Navy/Carbon substitute
- [ ] No arbitrary/one-off hex values introduced ad hoc
- [ ] On Parchment, thin lines, small marks, dots, and standalone coloured text use the appropriate semantic `-mark` token; vivid base colours are reserved for supported fills
- [ ] Meaningful fills below 3:1 against their neighbour have a contrasting outline, separation, or direct label
- [ ] Extended-palette background restrictions in `02-color-system.md` are respected
- [ ] Any non-Parchment background uses an approved surface theme class (`.dj-theme-navy/carbon/alabaster`), never an ad-hoc dark style
- [ ] Data-dense chart panels sit on the Parchment default — themed surfaces carry headlines, heroes, and single-metric content only

## Type
- [ ] DM Sans only, weights limited to 300/400/500
- [ ] Italic used for emphasis only, not decoration
- [ ] Metric numbers are the largest, heaviest element on their card

## Copy
- [ ] Every headline is plain English, states the finding directly
- [ ] No marketing-speak, no hedged findings the data supports
- [ ] One primary CTA per screen
- [ ] Field labels/placeholders are plain questions, not generic instructions
- [ ] Error states explain, don't blame

## Components
- [ ] Cards follow number → delta → source pattern, one idea per tile
- [ ] Inputs use the four defined states (default/focused/filled/disabled/error) with correct border/fill treatment
- [ ] No drop shadows; flat, 1px-rule system throughout
- [ ] No off-system icons; six-mark system or no icon

## Dashboard-specific
- [ ] Layout constant across all modes/states
- [ ] If guided/story mode exists: lit/recessed only, squint-test passes, constant anchors never recede, escape hatch present
- [ ] Every data-bearing card/chart has a source/freshness line
- [ ] No element present that doesn't help someone decide something

## Carousel
- [ ] Canvas is exactly 1080×1350 — no other dimensions
- [ ] Deck follows the fixed shape: one Hook, optional Context (always second), 1–5 Beats (each chart beat = setup + chart), one Synthesis, one So What, one CTA, one Appendix, in that order
- [ ] So What slide present, always Carbon, penultimate — states the decision/action the numbers inform, without the phrase "actionable insight"
- [ ] Eyebrow on every slide, top-left, fixed position: SERIES · SECTOR; takeaway appended on data slides only
- [ ] Slide index (n/N) on every slide, top-right, fixed position
- [ ] Full wordmark lower-right on cover and CTA (the close); monogram on interior slides and the Appendix — no drift in position or scale
- [ ] Hook slide leads with a Honey Bronze headline number (required) above the statement — no chart, no card
- [ ] Honey Bronze pop present and contained: hook number, one hero-chart `stat` number, and exactly one popped phrase each on the hook and So What — nowhere else
- [ ] Context slide, when present: always Alabaster, always slide 2, statement-only — states what the series tracks and its event anchor, same wording across the sector's decks
- [ ] Hook passes the report-title test: a reframe or stake that stops a scroll, one–two short sentences, and the deck cashes whatever it promises
- [ ] Every Beat slide carries exactly one Big Number or one Simple Chart, never both
- [ ] Every chart beat is preceded by a setup slide (what the data is); the chart slide itself carries only the takeaway + plot, no title
- [ ] Every data slide carries one judgment sentence — interpretation, not description — at the top on chart slides, bottom-anchored on Big Number slides
- [ ] Deck source + time frame declared exactly once, on the Appendix slide (with optional method notes) — never on the CTA, never repeated per slide
- [ ] Multi-series charts accent exactly one element; the rest stay muted — colour directs, never decorates
- [ ] Slide fields are approved surface themes: cover and CTA always Navy; Alabaster only ever the Context slide and the final Appendix slide; ink/marks/chart colours follow the theme's tokens
- [ ] CTA is content-driven — names a concrete next piece, or falls back to a series-rotation close; never a bare follow-ask — carries the trace-back URLs, Navy field, no source line
- [ ] Exactly one CTA slide (penultimate) and one Appendix slide (last, Alabaster, source + method)
- [ ] No tier tags anywhere in the deck — not part of carousel structure
- [ ] Slides assembled into a single PDF for upload, not posted as separate images

## Traceability
- [ ] Every colour, weight, size, and copy pattern used can be pointed to a specific line in `00-index.md` through `08-carousel-application.md`

## Export
- [ ] Canvas is exactly 1080×1080 or 1200×627 — no intermediate or custom dimensions
- [ ] Safe area respected — no meaningful content within 64px (square) / 48px (link preview) of the edge
- [ ] Exactly one headline element (number-led metric or finding statement) — never both competing on one card
- [ ] Footer bar present, full width, correct height (56px square / 44px link preview), inverse-colour to card body
- [ ] Footer bar contains only the reduced monogram (left) and literal URL text (right) — no button, no CTA
- [ ] Tier + source combined into one line; tier shown is Chartable or Partial only — Hypothesis-tier data never appears on an export card
- [ ] No interactive states, no hover/focus treatment, no lit/recessed pattern
- [ ] Headline runs in Navy if card body is Parchment — mandatory default for this context, not the general "one Navy headline" allowance
- [ ] Card is a static capture of the same components used elsewhere — not output from a separate charting library or design tool

## Index
- [ ] Exactly one index page per project, at `{project}/index.html`
- [ ] Page header carries project eyebrow, title, and inline wordmark per the hub-page placement rule
- [ ] Tiles use the standard tile anatomy — no new card component introduced
- [ ] Tile third line is tier + format ("Chartable · Video," "Partial · Article") — consistent field across every project, not decided per project
- [ ] Tiles ordered reverse-chronological, most recent first, no pagination
- [ ] Entire tile is the click target — no separate "read more" link
- [ ] No footer trace-back bar on the page itself — the page's own URL is the trace-back
- [ ] Every tile links to a real, resolvable `{slug}.html` — no placeholder links
