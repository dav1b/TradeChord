# Export Application

Rules for fixed-canvas, non-interactive, single-capture artifacts (LinkedIn cards, link-preview images). The opposite context from `05-dashboard-application.md`: no scroll, no interaction, no persistent presence — one shot, then it leaves the system as a static file.

## Canvas

Two fixed sizes only. No responsive behaviour, no breakpoints — content that doesn't fit is cut down, never reflowed.

| Name | Dimensions | Use |
|---|---|---|
| Square | 1080×1080 | Feed post (single image) |
| Link preview | 1200×627 | URL unfurl card |

Carousel slides are not an export format — they run portrait 1080×1350 with their own attribution rules, see `08-carousel-application.md`.

## Safe area

64px outer margin on the square format, ~48px on the link-preview format's shorter axis. Nothing meaningful sits inside it — capture/export can clip a pixel or two at the edge depending on renderer. The footer trace-back bar is exempt: it is full-bleed by design, and losing an edge pixel of it costs nothing.

## Card content

One idea per card, stricter than dashboard tiles. Top to bottom:

1. Eyebrow (`.dj-eyebrow`, DM Mono) — series/category, e.g. "DUBAI BOUNCEBACK INDEX · AVIATION"
2. Headline finding — number-led pattern from `04-components.md` (metric largest/heaviest), or a short plain-English finding statement. Never both competing for size on the same card.
3. Delta/context line — one line, same weight logic as the dashboard delta line
4. Footer bar — mandatory, see below

No body copy beyond these four elements. If a finding needs more explanation than headline + one context line, it's a dashboard piece, not a social card.

## Footer bar — mandatory trace-back

`05-dashboard-application.md`'s corner-mark rule (opacity 0.7, `pointer-events: none`) does not apply here. That rule assumes a scrolling, clickable page. An export is a static image that can be screenshotted and reposted with zero surrounding context — the mark inside the image is the only trace-back that survives.

Full-width bar, bottom of canvas:

- Height: 56px (square) / 44px (link preview)
- Background: always the inverse of the card body — Navy if body is Parchment, Parchment if body is Navy/Carbon. Never a third colour.
- Left: reduced monogram (single row of bars, approved motif per `04-components.md`), full opacity
- Right: URL text, `.dj-eyebrow` styling, full opacity — literal domain text (`datajockey.co/...`), not a button. No click target exists in a static image.
- Monogram only, not full wordmark — the URL text carries the name in words; the mark doesn't need to repeat it.

## Colour

Inherits `02-color-system.md` in full. Default: Parchment body, Carbon/Navy text ramp. Dark variant (Carbon or Navy body, Parchment text) permitted for visual variety across a series — implement it with the surface theme classes (`.dj-theme-navy` / `.dj-theme-carbon`, see `02-color-system.md`), nothing new introduced.

## Type

Inherits `03-typography.md`, with one exception: the "one Navy headline per page" allowance (≥34px, `03-typography.md`) is not optional here — it's the default. The headline is the reason the card exists. On a Parchment-body export card, it is Navy.

## What this context does not have

- No interactive states — nothing on an export card is interactive
- No lit/recessed pattern — that governs guided dashboard sequences, not a single static card
- No buttons — the footer URL is the only trace-back, not a CTA component
- No responsive behaviour

## Rendering

Export cards use the same component set as dashboard cards (`04-components.md`), inside a fixed-dimension container instead of a fluid one. Capture via in-browser screenshot of the rendered component, not a separate charting library or design tool.