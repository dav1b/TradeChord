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
