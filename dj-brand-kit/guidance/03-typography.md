# Typography

## Typeface

Primary: DM Sans (Indian Type Foundry). Used for headlines, body, UI, metric numbers.

Weights: 300 (light), 400 (regular), 500 (medium). No bold (700) — 500 is the heaviest weight.

Italic (DM Sans) is reserved for emphasis only, never decoration.

## Accent / eyebrow typeface — DM Mono

Used for eyebrows, labels, tags, and small accent text (source lines, timestamps, category tags). The brand book lists this within the DM Sans weight set, but it is a distinct typeface — DM Mono, not a DM Sans weight. Treat as separate.

Weight: 400 (Regular) unless a specific need for 500 (Medium) is identified.

Use cases: eyebrow labels above headings, card source/freshness lines, tags, timestamps, small caps-style category markers. Not for body text, headlines, or metric numbers.

```css
@font-face {
  font-family: 'DM Mono';
  src: url('/fonts/DMMono-Regular.ttf') format('truetype');
  font-weight: 400;
  font-style: normal;
}

.dj-eyebrow {
  font-family: 'DM Mono', monospace;
  font-weight: 400;
  font-size: 12px;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
```

## Secondary typeface — restricted use

PP Neue Machina Ultra Bold Italic. This is the wordmark typeface. Use only for special emphasis, sparingly, almost never in body UI. Default casing: all caps.

Rules:
- Never for body text, labels, card metrics, or any recurring UI element
- Never combined with DM Sans italic in the same block
- One instance per screen maximum, typically a single word or short phrase
- Approved uses: standalone callout statements, section dividers, print/merch applications, one-off emphasis moments equivalent to the brand book's tagline treatment ("Trust your numbers.")
- Not for buttons, form fields, chart labels, or navigation

```css
@font-face {
  font-family: 'PP Neue Machina';
  src: url('/fonts/PPNeueMachina-PlainUltraboldItalic.ttf') format('truetype');
  font-weight: 800;
  font-style: italic;
}

.dj-emphasis {
  font-family: 'PP Neue Machina', sans-serif;
  font-weight: 800;
  font-style: italic;
  text-transform: uppercase;
}
```

## Type scale (from brand book, presentation context)

| Role | Size | Weight | Use |
|---|---|---|---|
| Display | 220px / 500 | 500 | Covers and section openings only — not for dashboard UI |
| Title | 72px / 500 | 500 | Primary titles |
| Subtitle | 44px / 400 | 400 | Leads and pull copy |
| Body | 28px / 400 | 400 | Long-form text |

These are presentation/print sizes. For dashboard UI, scale down proportionally while preserving the weight logic: 500 for titles/numbers-that-matter, 400 for body and labels, 300 reserved for large low-emphasis text only. Suggested dashboard scale, derive and adjust against real layouts rather than treating as fixed:

| Role | Size | Weight |
|---|---|---|
| Page title | 32–40px | 500 |
| Section header | 20–24px | 500 |
| Card metric (the number) | 28–36px | 500 |
| Card label | 12–14px | 400, small |
| Body / description | 14–16px | 400 |
| Micro (footer, timestamps) | 11–12px | 400 |

## Numbers

Numbers lead. In card components the metric number is the largest, heaviest element on the card — see `04-components.md`.

## Colour in type

Headings and body run on the Carbon text ramp (`02-color-system.md`), with one exception: H1 / display headlines at 34px or larger on Parchment may be set in Regal Navy. One Navy headline per page — section titles, panel titles, and body remain on the Carbon ramp. Below 34px Navy reads as murky near-black, not brand blue; use the ramp instead.

## Font files

Pending. When supplied, place files here and reference by weight:

```
/fonts/DMSans-Light.ttf                      (300)
/fonts/DMSans-Regular.ttf                    (400)
/fonts/DMSans-Medium.ttf                     (500)
/fonts/DMSans-Italic.ttf                     (italic, emphasis only)
/fonts/DMMono-Regular.ttf                    (accent/eyebrow, 400)
/fonts/PPNeueMachina-UltraBoldItalic.ttf     (restricted use, see above)
```

```css
@font-face {
  font-family: 'DM Sans';
  src: url('/fonts/DMSans-Regular.ttf') format('truetype');
  font-weight: 400;
  font-style: normal;
}
@font-face {
  font-family: 'DM Sans';
  src: url('/fonts/DMSans-Medium.ttf') format('truetype');
  font-weight: 500;
  font-style: normal;
}
@font-face {
  font-family: 'DM Sans';
  src: url('/fonts/DMSans-Light.ttf') format('truetype');
  font-weight: 300;
  font-style: normal;
}