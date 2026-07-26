# Carousel generator

Turns a story brief (YAML) into a LinkedIn-ready carousel PDF — fixed deck shape, on-brand slides, vector text. Design rules live in `../guidance/08-carousel-application.md`; this folder is the machinery that enforces them.

## Usage

```bash
python3 generate.py briefs/my-brief.yaml
```

Output lands next to the brief in `out/` under a structured, sortable name (see below; override the directory with `--out`). Upload the PDF as a LinkedIn **document post** — that's what triggers the swipeable carousel treatment.

`--keep-html` keeps the rendered page for browser inspection. `--chrome` overrides the browser binary.
`--validate-only` checks the brief and exits without requiring Chrome.

Install the Python dependency from the repository root with
`python3 -m pip install -r requirements.txt`. PDF rendering requires
Chrome/Chromium. There is no npm or frontend build step.

## Output filename

The PDF name is derived from the brief, never hand-set, so every deck in a series files and sorts the same way. `generate.py` builds it as:

```
{series}-{sector}[-{chapter}]-c{NN}-{slug}.pdf
```

- **series** · **sector** — the two eyebrow fields (`Dubai Bounceback`, `Property`).
- **chapter** — optional sub-theme within the sector (`Rentals`); omitted from the name if absent.
- **cNN** — `carousel:`, the deck's number in the series, zero-padded (`c03`).
- **slug** — the deck title (`why-some-cut-deeper`).

Every segment is lowercased and hyphen-slugified. Example:

```
dubai-bounceback-property-rentals-c03-why-some-cut-deeper.pdf
```

So a series lists in reading order (`…-c01-…`, `…-c02-…`) grouped by sector and chapter. Set `carousel:` (and, if used, `chapter:`) at the top of each brief. If `carousel:` is omitted the name falls back to `<slug>.pdf`, so older briefs still render.

## The brief

Format spec and a full example: `../guidance/08-carousel-application.md` and `briefs/example-brief.yaml`. The generator validates the structure before rendering and refuses briefs that break it: fixed deck shape (1–5 beats), `series`/`sector`/`takeaway` for the every-slide eyebrow, a `judgment` sentence on every data slide, exactly one accented series per multi-series chart, and a content-driven `cta` (a named next piece, or `default` for the series-rotation close — never a bare follow-ask).

The bundled brief is synthetic and exists to document and test the format.
Keep real project briefs outside this repository.

Chart kinds currently implemented: `bar` (horizontal bars, signed values), `slope` (before/after per series), `beeswarm` (distribution — one dot per item along a signed x-axis, size = weight), and `scatter` (relationship — x vs y, size = weight, optional OLS trend line). Data is inline in the brief. On multi-series `bar`/`slope` charts exactly one element carries colour: `protagonist: true` (Navy), `highlight: true` (Honey Bronze), or `accent: true` (directional delta colour); the rest render muted.

`beeswarm` and `scatter` are the exceptions to the one-accent rule: colour marks a *group* or the few labelled points worth reading, not a named series, so they answer "how broad?" / "what's the relationship?" at a glance. `beeswarm` data is a flat list of `[value, weight]` pairs (or `{value, weight}`); dots below zero take the Navy protagonist ink, the rest stay muted. `scatter` data is `[x, y, weight]` — append `label, anchor, dy` to a point to highlight and label it (Navy over the muted field); a trend line is drawn only when |correlation| ≥ 0.3.

`table` renders a ranked list: `columns` (header row) + `data` (rows, first cell left-aligned label, the rest right-aligned mono figures). `bar` takes `signed: false` to print raw values (e.g. an index) instead of the default signed delta.

**Honey Bronze pop — the deck's one emphasis accent.** Honey Bronze (`--accent-highlight`) marks the single thing the eye should land on, in three fixed places:
- **Hook number** (`hook.number`) always renders Honey Bronze — every deck must lead with one (the generator rejects a hook without a number).
- **Hero-chart number** — the first chart beat carries a `stat` (+ optional `stat_label`), a Honey-Bronze figure set beside the title. Always give the hero chart a number.
- **One phrase** in the hook headline and in the `so_what` — wrap it in `*asterisks*` and it renders Honey Bronze (`*almost everywhere*`). One phrase per slide, never a whole sentence.

Don't spread it further — it directs, it doesn't decorate. Everything else stays on the theme's ink.

**Chart pairing.** Every chart beat renders as two slides: a **setup** slide (`setup` — plainly, what the data is) then the chart slide, which carries only the takeaway (`judgment`) at the top with the plot below. This primes the reader and keeps the chart slide to one idea — no title on the chart slide. `setup` falls back to `title` if omitted. Big Number and Concept beats stay single slides.

**Axis labels — always name what the data is.** Ticks are computed from the data domain, but the axis *titles* come from the brief, so set them:
- `scatter` — `x_label` and `y_label` (the renderer adds a rotated y-title); `x_suffix`/`y_suffix` append a unit to the tick numbers (e.g. `"%"`).
- `beeswarm` — `x_label` (centred axis title) and `x_suffix` (default `"%"`); the `← Cheaper / Dearer →` end cues default on, override with `left_label`/`right_label` or hide with `left_label: ""`. Add a third element to a data point (`[value, weight, "Name"]`) to draw a few named markers on top — keep it to a handful.
- `bar` — `x_label` renders a caption under the bars naming the metric (essential when the value is an index, not a percent).

**Concept slides** (`type: concept` beat, or `kind: concept` synthesis) carry an argument, not a figure — a `ladder` (list of steps drawn as a vertical chain) or `columns: [{label, steps:[…]}]` (parallel ladders, e.g. Luxury vs Affordable). They are exempt from the judgment rule; use them for a mechanism or causal chain, sparingly — a deck is data first.

## How it renders

`renderer/slides.html` + `slides.css` + `slides.js` — a static page with no framework, built directly on the kit's `tokens/dj-design.css`, fonts, and logo assets via relative paths. The monogram is inlined in `slides.js`, so the renderer is fully self-contained inside the kit. `generate.py` injects the brief as JSON, prints the page to PDF with headless Chrome (`@page: 1080px 1350px`), and cleans up.

Because it lives inside `dj-brand-kit/`, Git subtree/submodule updates carry the
renderer and guidance together.

## Extending

New chart kind = one function in `slides.js` returning an SVG string, registered in `CHARTS`, plus a line in the guidance file. Colour only through semantic tokens (`--protagonist`, `--delta-pos/neg`, `--accent-highlight`) — never raw hex.
