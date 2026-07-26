# Components

## Logo / symbol assets

Filenames state the colour pairing: `<asset>-<mark>-on-<background>.svg`. The name is the usage rule — if the background in the filename isn't the surface you're placing it on, it's the wrong file.

**Full-bleed variants** (background rectangle baked in) live in `dj-brand-kit/assets/logo/` and `dj-brand-kit/assets/icons/` — presentation and print use only, never dashboard UI:

| Pairing | Logo | Icons (× Plot, Sort, Scan, Converge, Balance, Support) | Role |
|---|---|---|---|
| Navy on Parchment | `logo-navy-on-parchment.svg` | `<mark>-navy-on-parchment.svg` | primary |
| Parchment on Carbon | `logo-parchment-on-carbon.svg` | `<mark>-parchment-on-carbon.svg` | dark mode |
| Parchment on Navy | `logo-parchment-on-navy.svg` | `<mark>-parchment-on-navy.svg` | feature use |
| Carbon on Parchment | `logo-carbon-on-parchment.svg` | `<mark>-carbon-on-parchment.svg` | secondary light |

**Transparent-background variants** for dashboard UI live in `viz/public/`, named by mark colour only: `logo-navy.svg` (default on Parchment pages — see `02-color-system.md`), `logo-carbon.svg` (fallback where Navy is saturated), `logo-parchment.svg` (on Carbon/Navy surfaces). The kit also carries tight-cropped transparent wordmarks (`assets/logo/wordmark-<colour>.svg`, 5:1, no padding) for contexts that size the mark exactly, e.g. carousel covers.

## Reduced monogram

The wordmark's bar cluster alone, without the letterforms — the compact trace-back mark. Full-bleed tiles live in `dj-brand-kit/assets/monogram/`, same `monogram-<mark>-on-<background>.svg` naming; transparent variants live in `viz/public/` as `monogram-<colour>.svg` (navy, carbon, parchment, alabaster).

Eight full-bleed pairings exist — the four wordmark pairings plus four the wordmark doesn't have:

| Mark | Backgrounds | Role |
|---|---|---|
| Navy / Carbon | Parchment, Alabaster | Light-surface monogram |
| Parchment | Navy, Carbon | Dark-surface monogram |
| Alabaster | Navy, Carbon | **Subdued** dark-surface variant — for repeating marks (carousel corner marks) where even Parchment competes with content |

Usage:
- The monogram appears where the full wordmark would repeat or crowd: carousel corner marks (`08-carousel-application.md`), export and Synthesis footer bars (`07`/`08`), favicon-scale contexts. It never replaces the wordmark on dashboard views — the logo placement rule in `05-dashboard-application.md` stands.
- Monogram and wordmark never share a surface, with one exception: a footer trace-back bar's monogram may coexist with URL text, because the URL carries the name in words.
- Alabaster-mark variants are for marks, never text — the Alabaster-is-never-ink rule (`02-color-system.md`) is unchanged.
- Same handling rules as the wordmark: no recolouring, stretching, rotating, or fencing.

- Approved backgrounds only: Carbon, Navy, Parchment, Alabaster
- No recolouring, stretching, rotating, or fencing
- Approved pairings: Navy mark on Parchment (primary), Parchment mark on Carbon (dark mode), Parchment mark on Navy (feature use)

## Cards and tiles

Numbers first. Labels small. One idea per tile. If a tile doesn't help someone decide something, it doesn't earn its place.

Standard tile anatomy, top to bottom:
1. Metric — the number, largest/heaviest text on the card
2. Delta line — direction + comparison (e.g. "+12.4% vs last month")
3. Source/freshness line — smallest text, states data source and recency (e.g. "Last 7 weeks · trusted source")

No decorative icons on tiles. No shadows beyond the brand's flat system (see Inputs below — solid 1px rules, no drop shadow, applies system-wide).

## Inputs and states

Fields ask plain questions. Placeholder text is plain, not instructional-generic.

States:
- **Default:** solid 1px rule, no drop shadow
- **Focused:** 2px Navy border
- **Filled:** Alabaster fill at 40% ink for auto-filled/inferred values, with a caption noting the source (e.g. "Auto-filled from previous step")
- **Disabled:** reduced-opacity, non-interactive
- **Error:** plain-language explanation of what's wrong, not a blame statement (e.g. "Looks like a half-finished email — give us the rest," not "Invalid input")

## Buttons

Variants: Primary, Secondary, Ghost/text-only.
States per variant: Default, Hover, Disabled.
Primary and Secondary also need on-dark variants for Navy/Carbon backgrounds.

Only one primary action per screen. Secondary and ghost buttons never compete visually with the primary CTA.

## Imagery and motif

The slanted bars from the wordmark are the graphic system: patterns, dividers, field textures. Never decorative filler — every use should carry structure (divide sections, mark a field, form a diagram) not just fill space.

Approved motif applications:
- Pattern field: Parchment bars on Navy
- Bars over field: Navy bars on Parchment
- Reduced monogram: the wordmark's bar cluster alone (see Reduced monogram above — real assets exist in `dj-brand-kit/assets/monogram/`)
- Geometric, monochrome diagrams built from the same bar logic

Number-led single-fact callouts (e.g. "+412 HOURS SAVED · Q1 — Across 14 client teams") are an approved standalone pattern: one big number, one line of context.

## Icon system

Six marks exist for the work itself: Plot, Sort, Scan, Converge, Balance, Support. Built on the same grid as the wordmark. No outlines, no flourishes. Do not introduce additional icon styles (outline icons, filled icons from a generic icon library, emoji) into dashboard UI — if an icon is needed outside these six concepts, prefer no icon over an off-system one.
