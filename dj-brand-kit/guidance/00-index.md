# DataJockey Dashboard Brand Guidelines

Source of truth: DataJockey Brand Book v1.0 (2026), extracted for use in
data-led dashboards and publishing workflows.

## Files in this set

These guidance files live in `dj-brand-kit/guidance/`. The kit also carries the
canonical token file (`tokens/dj-design.css`), font files (`fonts/`), and
logo/icon SVGs (`assets/`) — see `dj-brand-kit/README.md` for Git-based use.

- `01-voice-and-principles.md` — governing thesis, tone, vocabulary, what to avoid
- `02-color-system.md` — core palette (locked), extended palette, surface themes (ink-on-background pairings)
- `03-typography.md` — typeface, scale, weights, font file usage
- `04-components.md` — cards, inputs, buttons, motif, icon system
- `05-dashboard-application.md` — dashboard-specific rules: lit/recessed states, card discipline, hero patterns
- `06-index-pages.md` — per-project home page: thumbnail grid, tile anatomy, ordering, no pagination
- `07-export-application.md` — fixed-canvas static exports (LinkedIn cards, link previews): canvas sizes, footer trace-back bar, tier/source line
- `08-carousel-application.md` — LinkedIn carousel decks: fixed Hook/Beats/Synthesis/CTA shape, portrait canvas, story brief format
- `09-implementation-checklist.md` — pre-ship audit for any generated dashboard, export card, index page, or carousel

## Governing implementation rule

Brand book principle, applied literally to code: if a colour, weight, size, or copy choice cannot be traced to one of these files, it does not ship. When a decision isn't covered here, default to the plainest, most restrained option consistent with the four core colours and DM Sans — do not introduce new colours, fonts, shadows, gradients, or decorative elements to fill a gap.

## Status

Core identity (colour, type, voice, components) extracted from the brand book and locked. Three-typeface system: DM Sans (primary), DM Mono (accent/eyebrow, corrected from brand book's weight framing), PP Neue Machina Ultra Bold Italic (restricted emphasis) — see `03-typography.md`. Extended highlight palette and surface themes locked — see `02-color-system.md`. Font files live in `dj-brand-kit/fonts/`; logo/symbol assets in `dj-brand-kit/assets/`. Four application contexts defined: persistent dashboard (`05`), index pages (`06`), fixed-canvas exports (`07`), and carousel decks (`08`) — all trace back to the same core tokens and components, none introduces new colours or type.
