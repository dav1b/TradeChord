# Architecture

TradeChord is one repository with two independent toolchains joined by an
immutable, versioned data release.

## Runtime

The SvelteKit application under `web/` requires Node only. It reads
`web/static/data/current.json`, then fetches either:

- `<version>/overview.json` for `/all`, or
- `<version>/countries/<ISO3>.json` for `/`.

The browser never downloads the canonical matrix and never performs canonical
trade aggregation.

The production target is Vercel with `web/` configured as the project root.
The primary experience should be prerendered and served through Vercel's CDN;
runtime server functions are reserved for future requirements that cannot be
served statically. Python, WITS access, and data publication never run during
the Vercel build.

## Offline data production

The Python package under `pipeline/` is an offline release tool:

```
WITS API
  → explicit request outcomes
  → data/staging/<run>          (ignored, ephemeral)
  → validation gate
  → normalized canonical matrix
  → canonical + browser artifacts
```

The collector ranks export and import partners independently, takes their
union, and fetches both reported flows for every named partner. Flow-specific
ROW values reconcile explicit partners to WITS world totals.

## Published release

`data/releases/<version>/` contains the deterministic canonical matrix,
manifest, and checksums. `web/static/data/<version>/` contains browser
projections. The manifest hashes both representations; `current.json` is
updated last and selects the active version.

## Ownership

The pipeline owns units, flows, reconciliation, totals, shares, availability,
and projection generation. The web app owns selection, top-N presentation,
layout, formatting, interaction, and accessibility.

## Continuous-scene frontend foundation

The frontend is evolving as one continuous visual scene rather than a set of
independent dashboard drill-downs. Country, partner, flow, product, year,
value, share, and balance objects keep stable semantic identities while their
visual representations transform between overview, bilateral, composition,
history, and contribution states.

The implemented foundation is:

```text
SceneState + SceneAction reducer
  → derived TradeSceneGraph with stable entity IDs
  → pure geometry contracts
  → Svelte SceneStage
      ├── shallow URL history
      ├── responsive viewport context
      ├── transition direction/revision
      ├── semantic announcements
      └── entity-based focus transfer
  → representation renderers
```

Analytical actions use SvelteKit shallow routing. This updates a shareable URL
and browser history without rerunning the country page loader or detaching the
scene. Direct entry remains server-loadable, country changes remain full data
navigations, and browser Back reparses the URL into the same reducer.

`scene.ts` owns normalized state, actions, reducer semantics, direction,
focus target, and accessible scene descriptions. `scene-graph.ts` derives the
country, partner, flow, product, and selected-path entities exactly once.
`geometry.ts` defines renderer-independent rectangle, path, and line
contracts. `SceneStage.svelte` owns responsive mode, transition revision,
announcements, and focus movement. D3 continues to calculate layout; Svelte
continues to own DOM lifecycle.

The route now presents this machinery through one full-width
`TradeExplorer` surface. The active scene is the dominant object and its
question is persistent scene chrome. The former partner, product, and trend
cards are supporting evidence panes driven by the same selection. On narrow
screens they become a snap-scrolling evidence tray instead of lengthening the
page into a stack of independent dashboards.

The first evidence-to-primary transformation is also implemented. Selecting a
partner in the history evidence, or choosing History for an active
relationship, opens a full-width bilateral export/import timeline. `year` is
authoritative scene state: it updates the hero, relationship graph,
contextual evidence, accessible summary, and shallow URL together. Scrubbing
uses URL replacement so it does not flood browser Back history; entering and
leaving the history representation still creates reversible history entries.
Product context remains explicitly labeled with `crossYear` when it cannot
follow the selected historical year.

`/motion-lab` is an intentionally isolated interaction laboratory alongside
the production explorer. It renders one full-viewport chord from the active
country projection and exercises interruptible Svelte-driven geometry
preservation, visual focus, and spatial extraction. It has no independent analytical state or
data contract: partner identity uses the same semantic keys, D3 calculates
the value-derived chord layout, Svelte owns the SVG and motion lifecycle, and
the shared reduced-motion policy applies. Once one response model is selected
through visual and touch review, it can be folded into the production chord
without coupling the future drill-down architecture to a disposable demo.

The next laboratory increment separates three responsibilities that must not
collapse into one chart component:

```text
ChordLayer
  → HighlightStrategy (fixed geometry; presentation only)
  → RelationshipBridge (foreground extraction and reversal)
  → BilateralComposition (export/import representations)
```

Selection and navigation are different events. Selecting a ribbon moves the
scene from `network` to `focused`; opening it advances through `extracting` to
`relationship`. The bridge temporarily owns the selected partner entity while
the national chord recedes. It resolves into stable export and import flow
entities that a later increment can render as two product treemaps. Highlight
strategies may alter opacity, saturation, stroke, shadow, or a transient sheen,
but never the value-derived ribbon path or thickness.

Bridge geometry and choreography are representation contracts rather than
data contracts. They consume the same stable partner and flow keys and can be
replaced without changing projections or analytical state. The first bridge
increment deliberately stops at a central bilateral band so its continuity,
interruption, reversal, responsiveness, and reduced-motion behavior can be
judged before product geometry is introduced.

This direction does not change the ownership boundary above. The pipeline
continues to produce validated analytical projections; the scene layer owns
state, geometry, visual continuity, URL navigation, motion, and accessible
alternatives. See the frontend direction in the
[refactor roadmap](./refactor-roadmap.md#7-revised-frontend-direction-one-continuous-visual-scene).

See [data-methodology.md](./data-methodology.md) for analytical semantics and
[data-release.md](./data-release.md) for operating instructions. The
[refactor roadmap](./refactor-roadmap.md) records completed work, immediate
next steps, possible improvements, and open decisions.
See [deployment-performance.md](./deployment-performance.md) for Vercel
configuration, caching, payload strategy, performance budgets, build gates,
and production measurement.
