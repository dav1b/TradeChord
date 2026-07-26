# Color System

## Core palette (locked, from brand book)

Four colours, used with restraint. Carbon Black and Regal Navy carry the brand. No other colours appear in the brand book's visual style.

| Name | Hex | RGB | Role |
|---|---|---|---|
| Carbon Black | #13181B | 19, 24, 27 | Primary text / dark-mode ink / brand carrier |
| Regal Navy | #003A6C | 0, 58, 108 | Primary brand colour / focus states / primary actions / brand carrier |
| Parchment | #EFEEEA | 239, 238, 234 | Dark-mode background / light hero background |
| Alabaster Grey | #CCD5DA | 204, 213, 218 | Light-mode background / subtle accents / supporting surfaces only |

Rules:
- Alabaster Grey is never a substitute for Navy or Carbon. It does not carry brand weight or serve as an accent/highlight colour.
- **Alabaster is a surface/border colour, never a text colour.** On a Parchment background (#EFEEEA), Alabaster (#CCD5DA) achieves approximately 1.3:1 contrast — functionally invisible as text. Use it only for borders, subtle fills, and disabled input backgrounds.
- Approved logo/wordmark colour pairings: Navy on Parchment (primary), Parchment on Carbon (dark mode), Parchment on Navy (feature use). Do not place brand marks on unapproved colours.
- Dashboard pages on Parchment use the Navy wordmark (`logo-navy.svg`) by default; the Carbon variant is a fallback for contexts where Navy is already saturated.

## Grey ramp for text on Parchment

Parchment (#EFEEEA) is the primary page background. Any text placed on it must come from this ramp — not from Alabaster.

| Token | Value | Approx contrast vs Parchment | Use |
|---|---|---|---|
| `--text-1` | #13181B (Carbon) | ~21:1 | Primary text, headings, data figures |
| `--text-2` | #3D4347 | ~11:1 | Secondary body copy |
| `--text-3` | #6B7276 | ~3.75:1 | Supporting labels, eyebrows, axis text |
| `--text-4` | #888885 | ~2.85:1 | Micro / disabled / ghost — footer attribution, control row labels, intentionally subdued metadata |

The four-token ramp is sufficient for all DataJockey dashboard contexts. Do not introduce ad-hoc hex values for text — pick the nearest token. If an element needs to be less prominent than text-4, it probably should not exist at all (see the data-density rule in `05-dashboard-application.md`).

Alabaster sits at ~1.3:1 against Parchment. It is below the threshold of useful text contrast at any font size and weight in the system. If you are tempted to use it as text, use `--text-4` instead.

## CSS variables (core)

```css
:root {
  --dj-carbon: #13181B;
  --dj-navy: #003A6C;
  --dj-parchment: #EFEEEA;
  --dj-alabaster: #CCD5DA;
}
```

## Surface themes — ink-on-background pairings

Parchment is the default page background, but a surface may run on any approved mark background from `04-components.md` (Carbon, Navy, Parchment, Alabaster). The surface pairings follow the same ink-on-background logic the logo filenames encode — a theme is an approved logo pairing applied to a whole surface.

| Theme class | Background | Ink | Role (mirrors the logo pairing) | Wordmark |
|---|---|---|---|---|
| *(default, none)* | Parchment #EFEEEA | Carbon ramp | Primary light | `logo-navy.svg` |
| `.dj-theme-alabaster` | Alabaster #CCD5DA | Carbon ramp | Secondary light / supporting | `logo-navy.svg` |
| `.dj-theme-navy` | Regal Navy #003A6C | Parchment ramp | Feature use — heroes, section bands, export dark variant | `logo-parchment.svg` |
| `.dj-theme-carbon` | Carbon #13181B | Parchment ramp | Dark mode | `logo-parchment.svg` |

The classes live in `tokens/dj-design.css` and remap the semantic tokens (`--bg`, `--surface`, `--border`, `--text-1…4`, `--accent`, `--active`, `--protagonist`), so components written against tokens re-theme without edits. Apply on `<body>` for a full page or on a section container for a band.

### Parchment ink ramp (Navy and Carbon themes)

The dark-surface equivalent of the grey ramp — Parchment at stepped opacity, no new hues:

| Token | Value on dark themes | Use |
|---|---|---|
| `--text-1` | #EFEEEA (Parchment) | Primary text, headings, data figures |
| `--text-2` | rgba(239,238,234,0.80) | Secondary body copy |
| `--text-3` | rgba(239,238,234,0.60) | Supporting labels, eyebrows |
| `--text-4` | rgba(239,238,234,0.42) | Micro / intentionally subdued |

Card surfaces lift the background one step rather than switching hue: `--surface` is #0D4677 on Navy, #1C2327 on Carbon. Borders are Parchment at 0.25/0.14 (Navy) and 0.20/0.12 (Carbon) alpha. These are the only approved derived values; do not invent further tints.

### Alabaster theme adjustments

The Carbon text ramp carries over unchanged, with two derived values because default borders vanish against Alabaster: `--border` #AEB9BF, `--border-faint` #BDC7CC, and `--surface` stays #FFFFFF. Avoid `--text-4` on Alabaster — it drops below useful contrast; use `--text-3` as the floor.

### Rules

- **Data-dense chart panels stay on the Parchment default.** Themed surfaces carry headlines, heroes, index headers, number-led callouts, and export dark variants — not full chart panels. The chart token set (`--box-fill`, delta colours, etc.) is derived against Parchment and is not re-derived per theme.
- **The brand carrier inverts on dark surfaces.** On Navy or Carbon, Parchment is the brand carrier: `--accent`, `--active`, and `--protagonist` remap to Parchment, and the eye should meet Parchment before Honey Bronze. Active/selected fills on dark themes pair `var(--active)` with `var(--active-ink)` (Navy) — never Parchment-on-Parchment.
- **The Navy headline allowance (`03-typography.md`) applies to Parchment surfaces only.** On Navy or Carbon themes, headlines are Parchment.
- **Alabaster remains a surface, never ink** — a Navy or Carbon mark sits *on* Alabaster; Alabaster text exists in no theme.
- One theme per surface. A themed band inside a Parchment page is fine; nesting themes inside each other is not.

## Navy before secondary — the colour priority rule

Regal Navy (#003A6C) is the primary brand colour. In any DataJockey dashboard, a viewer's eye must encounter Navy before it encounters any extended/secondary colour (Honey Bronze, Ember Copper, Lagoon Teal, etc.).

In practice this means:

- **Structural anchors carry Navy**: the thick rule below the main header (`2px solid var(--active)`), the selected/active state of every interactive pill and tab (`var(--active)` background), and modal header rules all use Navy. These are the first coloured elements a viewer sees.
- **Interactive active states are always Navy**: when a pill, tab, or toggle is selected, its filled state is Navy with Parchment text. Carbon is never used as a selected-state fill.
- **Secondary colours only appear inside data**: Honey Bronze = off-plan share, Lagoon Teal = positive growth / new leases / cash payments, Ember Copper = negative growth, Fern Green = renewed leases, and Plum Violet = ready/non-off-plan status. These appear within cards, never in chrome (controls, headers, labels).
- **The CSS token `--active: var(--dj-navy)` exists for this purpose.** All interactive selected states must reference `var(--active)`, not `var(--text-1)` or a raw hex value.

If you add a new interactive element and its selected/active state is Carbon instead of Navy, that is a violation of this rule.

### The protagonist series — Navy's one data role

When one series is the subject of the page headline, that series may carry Regal Navy. One Navy series per chart, maximum; supporting series use the extended palette. Navy marks identity ("this is the line the page is about"), Honey Bronze remains the attention colour, and Ember Copper remains negative movement. If no single series is the protagonist, no series gets Navy.

Use the CSS token `--protagonist: var(--dj-navy)` for this, not `--active` or a raw hex — the two roles (interaction chrome vs protagonist data) must stay separately traceable.

## Extended palette — highlight / attention colours

Role: highlight and call attention. Not for body copy, page backgrounds, or primary brand carrying — those remain Carbon/Navy/Parchment/Alabaster only. Standalone coloured data labels may use an approved mark-safe value under the restrictions below. Use Honey Bronze first; use the remaining four only when their fixed semantic role calls for them.

| Priority | Name | Hex | RGB | Role |
|---|---|---|---|---|
| 1 | Honey Bronze | #FFBF65 | 255, 191, 101 | Primary highlight / attention — off-plan share |
| 2 | Lagoon Teal | #3EC5E0 | 62, 197, 224 | Positive delta, new leases, cash payments |
| 3 | Ember Copper | #F76A45 | 247, 106, 69 | Negative delta |
| 4 | Fern Green | #4BB814 | 75, 184, 20 | Renewed leases |
| 5 | Plum Violet | #B234A7 | 178, 52, 167 | Ready/non-off-plan status |

Lagoon Teal deliberately retains three related-but-distinct roles. Those roles
rarely need differentiation within one chart. Ready/non-off-plan moved to Plum
Violet so the off-plan/ready pairing no longer borrows the positive-delta hue.
Do not infer new meanings from the colours: use their semantic CSS aliases.

```css
:root {
  --dj-honey-bronze: #FFBF65;
  --dj-lagoon-teal: #3EC5E0;
  --dj-ember-copper: #F76A45;
  --dj-fern-green: #4BB814;
  --dj-plum-violet: #B234A7;
}
```

## Base colours and mark-safe variants

Base extended colours are the vivid categorical colours. Use them for fills,
bars, boxes, and badges when the shape remains identifiable through sufficient
contrast, a contrasting outline, separation, or an adjacent label.

Mark-safe variants are darker versions for thin lines, small marks, dots, and
standalone coloured text directly on Parchment. All clear 4.5:1 against
Parchment, so one variant works for normal text as well as the 3:1 graphical
threshold. They are not additional categories and must never carry a different
meaning from their base colour.

| Base colour | Parchment mark token | Value | Contrast on Parchment |
|---|---|---:|---:|
| Honey Bronze | `--dj-honey-bronze-mark` | `#885207` | 5.55:1 |
| Lagoon Teal | `--dj-lagoon-teal-mark` | `#0A6476` | 5.84:1 |
| Ember Copper | `--dj-ember-copper-mark` | `#912308` | 7.39:1 |
| Fern Green | `--dj-fern-green-mark` | `#0E622A` | 6.46:1 |
| Plum Violet | `--dj-plum-violet` | `#B234A7` | 4.59:1 |

The mark variants are **Parchment-only**. Their contrast is insufficient on
Navy and Carbon. Components should prefer semantic aliases such as
`--delta-pos-mark`, `--delta-neg-mark`, `--new-mark`, `--renewed-mark`,
`--op-mark`, `--re-mark`, and `--cash-mark` rather than palette primitives.

`--dj-ember-copper-mark` and `--dj-lagoon-teal-mark` intentionally match the
dark endpoints of the diverging scale. They remain independent literal values:
gradient tuning and mark legibility are separate concerns and must not silently
change together.

## Background and usage restrictions

The distinction is functional:

- **Normal standalone text** requires at least 4.5:1 contrast.
- **Large text and meaningful graphical objects** require at least 3:1.
- **Fills** may use the vivid base colour only when their boundary and meaning
  remain unambiguous. If the fill boundary itself communicates data and does
  not reach 3:1 against its neighbour, add an approved contrasting outline,
  separation, or direct label.

| Colour | On Parchment | On Carbon | On Navy |
|---|---|---|---|
| Honey Bronze | Mark token for lines, dots, and text; base for supported fills | Base permitted | Base permitted |
| Lagoon Teal | Mark token for lines, dots, and text; base for supported fills | Base permitted | Base permitted |
| Ember Copper | Mark token for lines, dots, and text; base for supported fills | Base permitted | Fills and large elements only; no normal text or thin marks |
| Fern Green | Mark token for lines, dots, and text; base for supported fills | Base permitted | Fills and large elements only; no normal text or thin marks |
| Plum Violet | Base permitted; it already clears 4.5:1 | Fills and large elements only | **Never use on Navy** |

The Ember and Fern restrictions on Navy are intentionally more conservative
than the 3:1 graphical minimum. Their measured contrast is 3.90:1 and 4.48:1,
respectively, but thin marks on saturated Navy are not stable enough for this
system. Plum Violet measures 2.16:1 on Navy and fails even the graphical-object
minimum, so it is excluded there entirely. Data-dense charts remain on
Parchment by default; do not invent alternate accent hex values to force them
onto themed surfaces.

## Gradients

Use only these two ordered scales:

- **Sequential:** magnitude without a natural zero, such as density or route
  intensity. `--sequential-1` through `--sequential-5` run from light blue to
  Regal Navy.
- **Diverging:** deviation from a meaningful centre, such as percent change
  against a baseline. `--diverging-neg-2` through `--diverging-pos-2` run from
  Ember Copper through Alabaster to Lagoon Teal.

Gradients encode ordered values, never unordered categories. Do not use a
gradient decoratively or interpolate new stops outside the declared scale.
