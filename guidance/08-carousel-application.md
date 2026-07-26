# Carousel Application

Rules for LinkedIn document-post carousels: a fixed-shape sequence of slides that tells one story, built from a story brief rather than authored slide-by-slide.

## Canvas

1080×1350 (4:5 portrait) only — the standard LinkedIn carousel convention. No other dimensions.

## Safe area

64px on all four edges. Nothing meaningful sits inside it — capture/export can clip a pixel or two at the edge depending on renderer. Deck chrome (eyebrow, slide index, corner marks, footer bar) is exempt: it is edge-anchored by design, and losing an edge pixel of it costs nothing.

## Deck shape — fixed, not flexible

Every carousel has exactly this shape:

1. **Hook** — always slide 1
2. **Context** — optional; when present, always slide 2
3. **Beats** — 1 to 5 slides, order and content follow the story brief
4. **Synthesis** — the story's summary read
5. **So What** — always the penultimate slide
6. **CTA** — always the last slide

5–10 slides total. The shape is fixed; only the Beats count varies with the story, and Context is the one optional slide.

## Deck chrome — every slide, no exceptions

A viewer landing mid-scroll with no memory of slide 1 must know what series and sector this belongs to. Three fixed elements, identical position and scale on every slide in the deck — no drift:

| Element | Position | Content |
|---|---|---|
| Eyebrow | Top-left | `SERIES · SECTOR` on every slide. Data slides (Beats, Synthesis) append the glib takeaway (e.g. `DUBAI BOUNCEBACK · PROPERTY · READY TOOK THE HIT`) — they travel out of context; statement slides carry their own words |
| Slide index | Top-right | `n/N` — signals remaining length to encourage swipe-through |
| Brand mark | Lower-right | Full wordmark on the cover and the CTA (the deck's close); reduced monogram on all interior slides including Synthesis and the Appendix (24px, 24px inset, 45% opacity). Mark colour follows the field: Navy mark on light fields, subdued Alabaster mark on dark fields (`04-components.md`) |

## Hook slide

Statement only. No chart, no card — deck chrome only. Same pattern as the brand book's tagline pages ("Trust your numbers.") — large type, brand-colour field (an approved surface theme per `02-color-system.md`). Rendered verbatim from the brief's `hook` field.

**The hook is the deck.** It is the single highest-leverage line in the artifact — it decides whether the other slides exist for the reader at all. Write it to stop a stranger mid-scroll, not to summarise the analysis. Craft rules:

- **Lead with the reframe, not the finding.** The Sutherland move: state the angle that makes a familiar thing suddenly strange, the contradiction, or the stake the reader didn't know they had. "Ready sales fell 41%" is a finding; "The war didn't stop Dubai buying homes — it stopped Dubai moving into them" is a hook.
- **Concrete beats abstract.** One behaviour, one consequence, one number. No category words ("market dynamics," "trends").
- **The curiosity gap must be honest.** The deck has to cash whatever the hook promises — a hook the Synthesis can't back is clickbait and it burns the trust the brand sells.
- **Report-title test**: read it aloud; if it could caption a chart in a bank's quarterly PDF, rewrite it.
- One or two short sentences, never more. No hedging (voice rules apply in full).

**Headline number — required**: every hook leads with a number, set large on the cover above the statement in Honey Bronze (`hook.number` + `hook.number_label` in the brief). The number stops the scroll, the statement reframes. Choose the deck's most arresting figure — not a routine percentage, and not one that merely repeats the hero-chart number.

## Context slide — always Alabaster

The series premise, expanded from the eyebrow, for the viewer who has never seen the series before. The eyebrow says `DUBAI BOUNCEBACK · LOGISTICS`; this slide says what that means — what the series tracks, its event anchor, and which chapter this deck is (e.g. tracking the health of Dubai's economy sector by sector since the war closed the Strait of Hormuz on Feb 28, 2026).

- **Optional, but always slide 2 when present** — context comes after the stop, before the numbers. Never anywhere else in the deck.
- **Statement only.** No chart, no number, no card. Mono kicker ("THE SERIES"), then two or three short sentences from the brief's `context` field. Max 240 characters.
- **Field: always Alabaster** — structural, like the Navy cover and the Carbon So What. This is one of only two Alabaster slides a deck may carry (the other is the CTA).
- **Consistent across a sector's decks.** The premise doesn't change deck to deck; reuse the same wording so the series reads as one artifact. The last sentence may name the chapter ("This chapter: logistics — whether goods can still move.").
- Chrome: standard interior treatment — eyebrow without takeaway, index, corner monogram (Navy mark on Alabaster).

## Beat slides

Each Beat is exactly one of:
- **Big Number** — full-slide version of the number-led pattern in `04-components.md` (metric → delta → source)
- **Simple Chart** — full-slide chart frame, one chart, minimal decoration, styled per `04-components.md`
- **Concept** — an explanatory slide that carries an argument, not a figure: a single vertical ladder of steps (a causal chain), or two parallel ladders (a contrast, e.g. Luxury vs Affordable). No chart, no metric, no judgment line. Use it to explain a mechanism the data implies — sparingly. A deck is data first; at most one or two concept slides, and never in place of the evidence.

Never mix these on one slide. One idea per slide, same discipline as dashboard tiles. Order and type come directly from the brief's `beats` list.

**Chart beats are paired.** Every chart beat renders as *two* slides: a **setup** slide first (the `setup` line — plainly, what the data is), then the chart slide. This primes the reader before the plot, and keeps the chart slide to one idea. The setup carries no chart; the chart slide carries no title — just the takeaway and the plot (see below). Big Number and Concept beats are single slides, unpaired.

## Judgment sentence — every data slide

Each slide showing a number, chart, or comparison carries one sentence of interpretation — what the data *means*, not what it shows. A slide with numbers and no interpretation is a dashboard, not a DataJockey artifact.

**Fixed position**: on Big Number slides the judgment closes the slide, bottom-anchored. On **chart slides it sits at the top** — the takeaway leads, the chart below proves it, and there's no separate title (the setup slide already framed the data). One text block on the chart slide, never a title *and* a judgment.

## Source — once per deck, on the close

The deck is consumed as one artifact, so the data source and time frame (e.g. "SOURCE: DLD TRANSACTIONS · JAN–JUN 2026") are declared once: mono line on the final Appendix slide (not the CTA). Data slides don't repeat it — a Big Number's delta line may carry the time frame where the number needs it.

Data-slide anatomy, top to bottom: content (metric or chart) → judgment sentence closing the slide foot, fixed position across the deck; only the content region flexes.

Title vs judgment on chart slides: the title states what the chart shows; the judgment states what it means. Never write two judgments.

## Colour — directional, not decorative

When a chart has two or more series/bars, colour directs the eye to the one element that carries the insight: exactly one element gets an accent, the rest stay muted/neutral. Uniform accent across all elements flattens the read and is a violation. The accent draws from the current approved palette in `02-color-system.md` (core + extended + surface themes — not the original four-colour-only constraint).

Distribution and relationship charts (beeswarm, scatter) are the exception: colour there encodes a *group* or the few points worth reading, not a named series — the side of the story (e.g. communities that got cheaper, in Navy; the rest muted), or a handful of labelled, recognisable points over a muted field. The eye still reads one signal, so the rule's intent holds; it just splits on a threshold or a shortlist rather than a single element.

## Honey Bronze — the emphasis pop

Honey Bronze is the deck's one attention accent, used sparingly and only in fixed places: the **hook number**, the **hero-chart number** (every hero chart carries one), and **a single phrase** in the hook headline and the So What statement. Nothing else takes it. It is a pop, not a highlighter — one phrase, never a whole sentence, and never on body copy, judgments, axis labels, or more than one element per slide. Directional chart accents (Navy protagonist, delta colours) are unchanged; Honey Bronze sits on top of them as the reader's entry point, not a competing series colour.

## Synthesis slide

The story's summary read, directly before the So What slide. Standard data-slide anatomy and attribution — corner monogram, judgment sentence at the foot — same as any Beat. It carries no special footer bar and no URL; the deck's trace-back URLs live on the CTA and its source line on the Appendix. (An earlier version gave Synthesis a full-width inverse footer bar for screenshot-survival; that was retired in favour of consistent interior chrome.)

## So What slide — always Carbon

The slide the deck exists for: what the reader can *do* with these numbers — the decision or action they inform. The judgment sentence interprets a chart; this slide answers the whole story. DataJockey never says "actionable insight" — this slide is the plain-English version of that job, and the phrase itself is banned copy.

- Field: **always Carbon** — structural, not part of the discretionary colour mix. The one dark-mode slide every deck has.
- Content: small mono kicker ("SO WHAT?"), then one plain statement of the decision/action, addressed to the reader. No chart, no metric, no card.
- Chrome: standard interior treatment — eyebrow, index, corner monogram (subdued Alabaster mark on Carbon).

## Field colour — the deck mix

Every slide field is an approved surface theme (`02-color-system.md`); ink ramps, chart muting, monogram and wordmark variants all follow the theme's tokens — never hand-picked per slide.

Three hard rules:
- **The cover is always Navy, and so is the CTA** — the deck's two Navy bookends.
- **The So What slide is always Carbon.**
- **Alabaster, if used at all, is only ever the Context slide and the final Appendix slide.**

Other interior slides default to Parchment. Across a series aim for roughly **70% Parchment · 20% Navy · 5% Alabaster · 5% Carbon** on the discretionary slides — variation is deliberate but Parchment stays the home key. This is editorial guidance across decks, not a per-deck quota.

On dark fields, chart colour still follows the directional rule: muted elements
take the theme's faint ink, and the accent must be approved for that surface.
Honey Bronze and Lagoon Teal carry on Navy; Ember Copper and Fern Green are
limited to fills and large elements there; Plum Violet is never used on Navy.
See `02-color-system.md` for the complete background and usage restrictions.

## CTA slide

Always **Navy**, full wordmark lower-right (per Deck chrome), one plain-English line — content-driven, never generic engagement copy:

- **When a concrete next piece is known**: name it ("Next in Dubai Bounceback: rentals — what moving actually costs now.")
- **Fallback**: directional, low-commitment reference to the ongoing series/rotation — never a bare follow-ask ("follow for more," "like and share") as placeholder copy.

Below the line: both trace-back URLs, stacked — `thedatajockey.substack.com` and `www.thedatajockey.com` — `.dj-eyebrow` styling. LinkedIn's document viewer rasterises the PDF, so treat them as brand text, not link targets. Nothing else: no chart, no metric, no card, no source line. The CTA is the clean emotional close — the boring trace-back lives on the Appendix that follows.

## Appendix slide — always Alabaster, always last

The deck's trace-back and reference material, pulled off the CTA so nothing dull competes with the call to action. Always Alabaster, always the final slide, corner monogram (the CTA already carried the wordmark). Content: a mono "Sources & method" kicker, the single source + time-frame line, then optional `notes` — metric definitions, the core-set cutoff, and any honest caveat (e.g. "elasticity is illustrative, not a fitted model"). No chart, no headline, no CTA. This is the one slide allowed to be boring.

## Story brief

Input format — a few lines referencing findings already explored, not raw data authoring:

```yaml
project: dubai-bounceback
slug: ready-sales-took-the-hit
series: Dubai Bounceback        # eyebrow, every slide
sector: Property                # eyebrow, every slide
takeaway: Ready took the hit    # eyebrow glib-takeaway, data slides only
source: "DLD Transactions · Jan–Jun 2026"   # once per deck, on the Appendix slide
notes:                                      # optional Appendix method notes / definitions
  - "Metric X = a ÷ b."
hook_stat: "−41%"                            # optional — only when the number itself is the hook
hook: "The war didn't stop Dubai buying homes. It stopped Dubai moving into them."
context: "Dubai Bounceback tracks the health of Dubai's economy, sector by sector, since the war with Iran closed the Strait of Hormuz on Feb 28, 2026."   # optional — slide 2, always Alabaster
beats:
  - type: big_number
    value: "−41%"
    label: "Ready-property sales, transactions per month"
    delta: "Jan–Feb → Mar–Jun 2026"
    judgment: "Buyers who need keys today stepped back; buyers of promises didn't."
  - type: chart
    kind: bar
    title: "The dip wasn't evenly shared"
    unit: "%"
    data:
      - { label: "Ready sales", value: -41, accent: true }   # exactly one accent
      - { label: "Off-plan sales", value: -12 }
    judgment: "The shock sorted buyers by urgency, not by confidence."
synthesis:
  kind: slope
  title: "Off-plan's market share expanded through the shock"
  data:
    - { label: "Off-plan share", from: 71, to: 79, protagonist: true }
    - { label: "Ready share", from: 29, to: 21 }
  judgment: "Four-fifths of Dubai property sales are now promises, not keys."
so_what: "Negotiating a ready purchase now? The room is a third emptier than in winter — that's leverage."
cta:
  next: "Next in Dubai Bounceback: rentals — what moving actually costs now."
  # cta theme is always Navy (default); alabaster is now the Appendix slide only
# cta: default   ← fallback: directional series-rotation close, never a follow-ask
```

Any beat or the synthesis may set `theme: navy|carbon` (default `parchment`) per the Field colour rules; the cover has no theme field — it is always Navy.

## Rendering

Each slide captures from the same token set used everywhere in the kit, at the 1080×1350 canvas. Slides assemble into a single PDF for upload as a LinkedIn document post — that's what triggers the swipeable carousel treatment; separate image posts don't. Machinery: `dj-brand-kit/carousel/` (see its README).

## What this context does not have

- No canvas sizes other than portrait 1080×1350
- No buttons, no interactive states
- No lit/recessed pattern
- No variation in deck shape — Hook, Synthesis, So What, and CTA are never optional, never reordered; Context is the only optional slide, and only ever second
- No tier tags (Chartable/Partial/Hypothesis) — not part of carousel structure
- No falsifiable-call slide or line — not part of carousel structure
